(ns pod.babashka.mcp
  "Babashka pod for interacting with MCP (Model Context Protocol) servers."
  (:require [babashka.pods :as pods]))

(def ^:private pod-name "pod-babashka-mcp")

(defn connect
  "Connect to an MCP server using the provided options.
   
   Options:
   - :command - Command to start the server (e.g. \"python\")
   - :args - Vector of command arguments (e.g. [\"server.py\"])
   - :env - Map of environment variables"
  [opts]
  (pods/invoke pod-name 'pod.babashka.mcp/connect opts))

(defn disconnect
  "Disconnect from an MCP server session."
  [session]
  (pods/invoke pod-name 'pod.babashka.mcp/disconnect {:session session}))

(defn list-tools
  "List available tools from the MCP server."
  [session]
  (pods/invoke pod-name 'pod.babashka.mcp/list-tools {:session session}))

(defn call-tool
  "Call a tool on the MCP server with the given name and arguments."
  [session name args]
  (pods/invoke pod-name 'pod.babashka.mcp/call-tool 
               {:session session
                :name name
                :args args}))

(defn subscribe
  "Subscribe to updates for a resource URI.
   The callback function will be called with update events."
  [session uri callback]
  (pods/invoke pod-name 'pod.babashka.mcp/subscribe
               {:session session
                :uri uri
                :callback callback}))

(defn list-resources
  "List available resources from the MCP server."
  [session]
  (pods/invoke pod-name 'pod.babashka.mcp/list-resources
               {:session session}))

(defn read-resource
  "Read a resource from the MCP server by URI."
  [session uri]
  (pods/invoke pod-name 'pod.babashka.mcp/read-resource
               {:session session
                :uri uri}))

(defn list-prompts
  "List available prompts from the MCP server."
  [session]
  (pods/invoke pod-name 'pod.babashka.mcp/list-prompts
               {:session session}))

(defn get-prompt
  "Get a specific prompt by name."
  [session name]
  (pods/invoke pod-name 'pod.babashka.mcp/get-prompt
               {:session session
                :name name}))

(defn with-session
  "Execute body with an MCP server session, ensuring proper cleanup.
   
   Example:
   (with-session [session {:command \"python\" :args [\"server.py\"]}]
     (call-tool session \"list_directory\" {:path \".\"}))"
  [[binding opts] & body]
  `(let [~binding (connect ~opts)]
     (try
       ~@body
       (finally
         (disconnect ~binding)))))

;; Async versions of key functions
(defn call-tool-async
  "Asynchronously call a tool. Returns a promise of the result."
  [session name args]
  (pods/invoke pod-name 'pod.babashka.mcp/call-tool-async
               {:session session
                :name name
                :args args}))

(defn read-resource-async
  "Asynchronously read a resource. Returns a promise of the result."
  [session uri]
  (pods/invoke pod-name 'pod.babashka.mcp/read-resource-async
               {:session session
                :uri uri}))
