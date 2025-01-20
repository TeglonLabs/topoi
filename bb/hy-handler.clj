#!/usr/bin/env bb

(require '[babashka.deps :as deps])
(require '[clojure.java.shell :refer [sh]])
(require '[clojure.edn :as edn])
(require '[clojure.core.async :as async])

;; Load bridge specification
(def bridge-spec
  (edn/read-string (slurp "bb/hy-bridge.edn")))

;; State management
(def current-state (atom :init))
(def state-data (atom {}))

(defn transition! [to-state]
  (let [valid-transitions (get-in bridge-spec [:bridge-spec :state-machine :states @current-state :transitions])
        transition (first (filter #(= (:to %) to-state) valid-transitions))]
    (when transition
      (reset! current-state to-state)
      (println "Transitioned to state:" to-state)
      true)))

;; Action handlers
(defmulti handle-action
  (fn [action & _] action))

(defmethod handle-action :process-llm-stream
  [_ {:keys [prompt system-prompt]}]
  (println "Processing LLM stream with prompt:" prompt)
  (swap! state-data assoc :llm-stream {:prompt prompt
                                      :system-prompt system-prompt})
  (transition! :processing))

(defmethod handle-action :send-to-babashka
  [_ {:keys [chunk]}]
  (println "Sending chunk to Babashka:" chunk)
  (try
    (let [result (sh "jet" "--from" "json" "--to" "edn"
                     :in (pr-str chunk))]
      (if (zero? (:exit result))
        (do
          (swap! state-data update :processed-chunks conj chunk)
          (println "Successfully sent chunk to Babashka")
          (transition! :processing))
        (do
          (println "Error sending chunk to Babashka:" (:err result))
          (transition! :error)))
    (catch Exception e
      (println "Exception while sending to Babashka:" (.getMessage e))
      (transition! :error))))

(defmethod handle-action :log-transaction
  [_ {:keys [chunk result]}]
  (swap! state-data update :transaction-log conj
         {:timestamp (java.time.Instant/now)
          :chunk chunk
          :result result})
  (println "Logged transaction:" chunk result)
  true)

;; Generator management
(defn create-generator [spec]
  (case (:type spec)
    :async-generator (async/chan 1)
    :subprocess (async/chan 1)))

(def generators
  (into {}
        (map (fn [[k v]]
               [k (create-generator v)])
             (get-in bridge-spec [:bridge-spec :generators]))))

;; Main processing loop
(defn process-chunk [chunk]
  (let [current-protocol (get-in bridge-spec [:bridge-spec :protocols :llm])
        transform-spec (first (get-in bridge-spec [:bridge-spec :transformations]))]
    (when (= (:format current-protocol) :stream)
      (handle-action :send-to-babashka {:chunk chunk})
      (handle-action :log-transaction {:chunk chunk
                                     :result @state-data}))))

(defn start-processing! []
  (let [llm-chan (get generators :llm-stream)
        process-chan (async/chan 1)
        timeout-chan (async/timeout 30000)] ; 30s timeout
    
    (async/go-loop []
      (async/alt!
        llm-chan ([chunk]
                 (when chunk
                   (println "Received chunk:" chunk)
                   (process-chunk chunk)
                   (recur)))
        
        timeout-chan
        ([_]
         (println "Processing timeout")
         (transition! :error))
        
        process-chan
        ([_] (println "Processing complete"))))
    
    process-chan))

;; Entry point
(defn -main [& args]
  (println "Starting Hy-Babashka handler...")
  (let [process-chan (start-processing!)]
    (async/<!! process-chan))

(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
