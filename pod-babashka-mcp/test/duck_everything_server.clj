#!/usr/bin/env bb

(ns duck-everything-server
  "A server that implements all MCP features using duck typing principles"
  (:require [cheshire.core :as json]
            [clojure.string :as str]
            [clojure.java.io :as io]))

(def capabilities
  {:tools
   [{:name "sync_tool"
     :description "Synchronous tool example"
     :inputSchema {:type "object"
                  :properties {"arg" {:type "string"}}
                  :required ["arg"]}}
    
    {:name "async_tool"
     :description "Asynchronous tool example"
     :inputSchema {:type "object"
                  :properties {"delay" {:type "number"}}
                  :required ["delay"]}}
    
    {:name "streaming_tool"
     :description "Streaming output tool"
     :inputSchema {:type "object"
                  :properties {"count" {:type "number"}}
                  :required ["count"]}}
    
    {:name "error_tool"
     :description "Tool that demonstrates error handling"
     :inputSchema {:type "object"
                  :properties {"error_type" {:type "string"
                                           :enum ["validation" "runtime" "timeout"]}}
                  :required ["error_type"]}}]
   
   :resources
   [{:uri "duck://static/data"
     :name "Static Data Resource"
     :mimeType "application/json"
     :description "Static data example - behaviorally equivalent to any static JSON resource"}
    
    {:uri "duck://dynamic/{param}"
     :name "Dynamic Resource Template"
     :mimeType "application/json"
     :description "Dynamic data with parameters - behaviorally equivalent to parameterized endpoints"}
    
    {:uri "duck://stream/events"
     :name "Event Stream Resource"
     :mimeType "text/event-stream"
     :description "Server-sent events example - behaviorally equivalent to any SSE stream"}]})

;; Protocol for resource behavior
(defprotocol ResourceBehavior
  (read-resource [this] "Read resource content")
  (supports-streaming? [this] "Check if resource supports streaming")
  (get-mime-type [this] "Get resource MIME type"))

;; Record types implementing the protocol
(defrecord StaticResource [uri data mime-type]
  ResourceBehavior
  (read-resource [_] data)
  (supports-streaming? [_] false)
  (get-mime-type [_] mime-type))

(defrecord DynamicResource [uri params mime-type]
  ResourceBehavior
  (read-resource [_]
    {:param (:param params)
     :timestamp (System/currentTimeMillis)})
  (supports-streaming? [_] false)
  (get-mime-type [_] mime-type))

(defrecord StreamingResource [uri mime-type]
  ResourceBehavior
  (read-resource [_] nil) ; Streaming resources don't support direct reading
  (supports-streaming? [_] true)
  (get-mime-type [_] mime-type))

(defn write-json [data]
  (json/generate-string data))

(defn read-json [s]
  (json/parse-string s true))

(defn handle-sync-tool [args]
  {:content [{:type "text"
             :text (str "Processed: " (:arg args))}]})

(defn handle-async-tool [args]
  (Thread/sleep (* 1000 (:delay args)))
  {:content [{:type "text"
             :text "Async operation complete"}]})

(defn handle-streaming-tool [args]
  (doseq [i (range (:count args))]
    (println (write-json
              {:content [{:type "text"
                         :text (str "Stream item " i)}]}))
    (Thread/sleep 100))
  {:content [{:type "text"
             :text "Stream complete"}]})

(defn handle-error-tool [args]
  (case (:error_type args)
    "validation" (throw (ex-info "Validation error"
                               {:code "invalid_params"}))
    "runtime" (throw (ex-info "Runtime error"
                            {:code "internal_error"}))
    "timeout" (do (Thread/sleep 5000)
                 {:content [{:type "text"
                           :text "Should timeout"}]})))

(defn create-resource [uri]
  (cond
    (= uri "duck://static/data")
    (->StaticResource uri {:data "Static content"} "application/json")
    
    (str/starts-with? uri "duck://dynamic/")
    (let [param (last (str/split uri #"/"))]
      (->DynamicResource uri {:param param} "application/json"))
    
    (= uri "duck://stream/events")
    (->StreamingResource uri "text/event-stream")))

(defn handle-resource [resource]
  (if (supports-streaming? resource)
    (doseq [i (range 5)]
      (println (write-json
                {:contents [{:uri (.-uri resource)
                           :mimeType (get-mime-type resource)
                           :text (str "data: Event " i "\n\n")}]}))
      (Thread/sleep 1000))
    {:contents [{:uri (.-uri resource)
                :mimeType (get-mime-type resource)
                :text (write-json (read-resource resource))}]}))

(defn handle-request [req]
  (case (:method req)
    "list_tools" {:tools (:tools capabilities)}
    "list_resources" {:resources (:resources capabilities)}
    "call_tool"
    (let [{:keys [name arguments]} (:params req)]
      (case name
        "sync_tool" (handle-sync-tool arguments)
        "async_tool" (handle-async-tool arguments)
        "streaming_tool" (handle-streaming-tool arguments)
        "error_tool" (handle-error-tool arguments)))
    
    "read_resource"
    (let [uri (get-in req [:params :uri])
          resource (create-resource uri)]
      (handle-resource resource))))

(defn -main []
  (with-open [rdr (io/reader *in*)]
    (loop []
      (when-let [line (.readLine rdr)]
        (when-not (str/blank? line)
          (let [req (read-json line)
                resp (handle-request req)]
            (when resp
              (println (write-json resp)))))
        (recur)))))

(when (= *file* (System/getProperty "babashka.file"))
  (-main))
