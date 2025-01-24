#!/usr/bin/env bb

(ns mcp-server
  (:require [cheshire.core :as json]
            [clojure.java.io :as io]
            [clojure.string :as str]
            [babashka.fs :as fs]))

;; JSON-RPC message handling
(defn parse-message [line]
  (json/parse-string line true))

(defn write-message [msg]
  (let [json-str (json/generate-string msg)]
    (println json-str)
    (flush)))

(defn make-response [id result]
  {:jsonrpc "2.0"
   :id id
   :result result})

(defn make-error [id code message]
  {:jsonrpc "2.0"
   :id id
   :error {:code code
           :message message}})

;; MCP Server implementation
(defprotocol IMCPServer
  (initialize [this options])
  (list-resources [this])
  (read-resource [this uri])
  (list-tools [this])
  (call-tool [this name args]))

(defrecord MCPServer [name version capabilities]
  IMCPServer
  (initialize [_this options]
    {:serverInfo {:name name
                 :version version}
     :capabilities capabilities
     :protocolVersion "0.1.0"})

  (list-resources [_this]
    {:resources []})

  (read-resource [_this uri]
    (make-error nil -32601 "Method not implemented"))

  (list-tools [_this]
    {:tools []})

  (call-tool [_this tool-name args]
    (make-error nil -32601 "Method not implemented")))

(defn handle-request [server msg]
  (let [{:keys [id method params]} msg]
    (case method
      "initialize"
      (make-response id (initialize server params))

      "resources/list"
      (make-response id (list-resources server))

      "resources/read" 
      (make-response id (read-resource server (:uri params)))

      "tools/list"
      (make-response id (list-tools server))

      "tools/call"
      (make-response id (call-tool server (:name params) (:arguments params)))

      ;; Default - method not found
      (make-error id -32601 (str "Method not found: " method)))))

(defn create-server [name version]
  (->MCPServer 
    name 
    version
    {:resources {:subscribe true}
     :tools {:listChanged true}}))

(defn process-stdin [server]
  (try
    (loop []
      (when-let [line (read-line)]
        (when-not (str/blank? line)
          (let [msg (parse-message line)
                response (handle-request server msg)]
            (write-message response)))
        (recur)))
    (catch Exception e
      (write-message 
        (make-error nil -32603 (str "Internal error: " (.getMessage e)))))))

(defn -main [& args]
  (let [server (create-server "babashka-mcp" "0.1.0")]
    (process-stdin server)))

(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
