; A small Babashka-based HTTP server that provides a list of "capabilities."
; You can run this script by: bb capabilities_server.clj
; Then visit http://localhost:8080/capabilities

(ns capabilities-server
  (:require
    [org.httpkit.server :as http]
    [cheshire.core :as json]
    [babashka.fs :as fs]))

(def capabilities
  [{:name "Directory Indexer"
    :description "Traverse directory trees and gather file metadata using babashka.fs and store in DuckDB."
    :script "bb/dir_to_duckdb.clj"}
   {:name "Random Walk"
    :description "Random walk script for ephemeral analysis (example)."
    :script "src/random-walk-mcp-server.clj"}
   {:name "Cloning Repos"
    :description "Demonstrates cloning GitHub repositories using babashka and gh CLI."
    :script "src/random-walk-mcp-server.clj"}
   {:name "MCP Client"
    :description "Client script for connecting to MCP servers (e.g. topoi-mcp)."
    :script "src/topos_mcp/client.py"}])

(defn handler [req]
  (case (:uri req)
    "/capabilities"
    {:status  200
     :headers {"Content-Type" "application/json"}
     :body    (json/generate-string capabilities)}
    {:status 404 :body "Not Found"}))

(defn -main [& args]
  (let [port 8080]
    (println "Starting Babashka capabilities server on port" port)
    (http/run-server handler {:port port})
    (println "Visit http://localhost:8080/capabilities to see the capabilities.")))

; When run as bb script:
(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
