(ns pod.babashka.mcp
  "Configuration management for pod-babashka-mcp"
  (:require [clojure.edn :as edn]
            [clojure.java.io :as io]
            [babashka.fs :as fs]))

(defn read-config
  "Read and parse the pod configuration file.
   Returns the parsed config map or throws if invalid."
  ([]
   (read-config "pod-config.edn"))
  ([path]
   (let [config-file (fs/file path)]
     (when-not (fs/exists? config-file)
       (throw (ex-info "Config file not found" {:path path})))
     (-> config-file
         slurp
         edn/read-string))))

(defn config->mcp-format
  "Convert pod config to MCP server config format.
   This enables compatibility with Claude/Cline MCP settings."
  [config]
  (let [servers (:mcp-servers config)]
    (->> servers
         (map (fn [[k v]]
                [k (-> v
                      (update :auto-approve #(or % []))
                      (update :disabled #(or % false)))]))
         (into {}))))

(defn validate-config
  "Validate the configuration map structure.
   Throws ex-info with details if invalid."
  [config]
  (when-not (map? config)
    (throw (ex-info "Invalid config: must be a map" {:config config})))
  
  (let [{:keys [mcp-servers pod]} config]
    ;; Validate servers
    (when-not (map? mcp-servers)
      (throw (ex-info "Invalid mcp-servers config" {:mcp-servers mcp-servers})))
    
    (doseq [[name server] mcp-servers]
      (when-not (and (:command server) (sequential? (:args server)))
        (throw (ex-info "Invalid server config" 
                       {:server name :config server}))))
    
    ;; Validate pod config
    (when-not (and (:name pod) (:version pod))
      (throw (ex-info "Missing required pod config" {:pod pod}))))
  config)

(defn load-config!
  "Load, validate and normalize the pod configuration.
   Returns the processed config map."
  [& [path]]
  (-> (read-config path)
      validate-config))

(defn get-server-config
  "Get normalized config for a specific MCP server"
  [config server-name]
  (get-in config [:mcp-servers server-name]))

(defn get-pod-defaults
  "Get the pod's default configuration settings"
  [config]
  (get-in config [:pod :defaults]))

(defn merge-server-config
  "Merge server config with pod defaults"
  [config server-name]
  (let [defaults (get-pod-defaults config)
        server-config (get-server-config config server-name)]
    (merge defaults server-config)))
