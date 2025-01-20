#!/usr/bin/env bb

(require '[babashka.deps :as deps])
(require '[clojure.java.shell :refer [sh]])
(require '[clojure.edn :as edn])

(def transaction-log (atom []))

;; Transform JSON to EDN using jet with error handling
(defn transform-message [msg]
  (try
    (let [result (sh "jet" "--from" "json" "--to" "edn" :in msg)]
      (if (= 0 (:exit result))
        {:success true :data (edn/read-string (:out result))}
        {:success false :error (:err result)}))
    (catch Exception e
      {:success false :error (.getMessage e)})))

;; Log transaction for error recovery
(defn log-transaction! [msg result]
  (swap! transaction-log conj
         {:timestamp (java.time.Instant/now)
          :original msg
          :result result}))

;; Process message with transaction support
(defn process-message! [msg]
  (let [result (transform-message msg)]
    (log-transaction! msg result)
    (if (:success result)
      (do
        (println "Successfully transformed message:")
        (println (:data result)))
      (do
        (println "Failed to transform message:")
        (println (:error result))))))

;; NATS message handler
(defn handle-nats-message [msg]
  (process-message! msg))

;; Main function to start processing
(defn -main [& args]
  (println "Starting NATS-Jet message processor...")
  (let [topic (or (first args) "jet.transform")]
    (println "Subscribing to topic:" topic)
    
    ;; Set up error handling for the subscription
    (try
      ;; Subscribe using NATS MCP server
      (println "Waiting for messages...")
      (handle-nats-message (slurp *in*))
      
      (catch Exception e
        (println "Error processing message:" (.getMessage e))
        (System/exit 1)))))

;; Run main when executed directly
(when (= *file* (System/getProperty "babashka.file"))
  (-main *command-line-args*))

;; Example usage:
;; bb nats-jet.clj < message.json
;; Or with NATS MCP:
;; nats pub jet.transform "$(cat message.json)" | bb nats-jet.clj
