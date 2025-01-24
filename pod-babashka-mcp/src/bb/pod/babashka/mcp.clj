(ns pod.babashka.mcp
  "Babashka pod for MCP server interactions"
  (:require [babashka.pods :as pods]))

(def pod-name "pod-babashka-mcp")

(defn ensure-pod []
  (when-not (pods/known-pod? pod-name)
    (pods/load-pod ["target/pod-babashka-mcp"])))

(defn connect
  "Connect to an MCP server using the provided options.
   
   Options:
   - :command - Command to start the server
   - :args - Vector of command arguments
   - :env - Map of environment variables
   - :timeout - Connection timeout in ms (default: 30000)
   - :retry - Retry settings {:max-attempts n :backoff-ms n}"
  [opts]
  (ensure-pod)
  (pods/invoke pod-name 'pod.babashka.mcp/connect {:opts opts}))

(defn disconnect
  "Disconnect from an MCP server session."
  [session]
  (ensure-pod)
  (pods/invoke pod-name 'pod.babashka.mcp/disconnect {:session session}))

(defn list-tools
  "List available tools from the MCP server."
  [session]
  (ensure-pod)
  (pods/invoke pod-name 'pod.babashka.mcp/list-tools {:session session}))

(defn call-tool
  "Call a tool on the MCP server with the given name and arguments.
   
   Optional callback for streaming responses.
   Optional opts map for additional settings like timeout."
  ([session name args]
   (call-tool session name args nil))
  ([session name args callback]
   (call-tool session name args callback {}))
  ([session name args callback opts]
   (ensure-pod)
   (pods/invoke pod-name 'pod.babashka.mcp/call-tool
                {:session session
                 :name name
                 :args args
                 :callback callback
                 :opts opts})))

(defn subscribe
  "Subscribe to updates for a resource URI.
   The callback function will be called with update events."
  [session uri callback]
  (ensure-pod)
  (pods/invoke pod-name 'pod.babashka.mcp/subscribe
               {:session session
                :uri uri
                :callback callback}))

(defn list-resources
  "List available resources from the MCP server."
  [session]
  (ensure-pod)
  (pods/invoke pod-name 'pod.babashka.mcp/list-resources
               {:session session}))

(defn read-resource
  "Read a resource from the MCP server by URI."
  [session uri]
  (ensure-pod)
  (pods/invoke pod-name 'pod.babashka.mcp/read-resource
               {:session session
                :uri uri}))

(defmacro with-session
  "Execute body with an MCP server session, ensuring proper cleanup.
   
   Example:
   (with-session [session {:command \"python\" :args [\"server.py\"]}]
     (call-tool session \"list_directory\" {:path \".\"}))
   
   Options:
   - :timeout - Session timeout in ms
   - :retry - Retry settings {:max-attempts n :backoff-ms n}
   - :env - Environment variables"
  [[binding opts] & body]
  `(let [session# (connect ~opts)
         ~binding session#]
     (try
       ~@body
       (finally
         (disconnect session#)))))
