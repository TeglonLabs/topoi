#!/usr/bin/env bb

(ns run
  (:require [babashka.process :as p]
            [clojure.string :as str]
            [clojure.java.io :as io]
            [clojure.tools.cli :as cli]))

(def cli-options
  [["-h" "--help" "Show help"]
   ["-e" "--env ENV" "Environment type (dev/prod)" :default "dev"]
   ["-p" "--port PORT" "Port number for TypeScript drand server"
    :default 3000
    :parse-fn #(Integer/parseInt %)
    :validate [#(< 0 % 0x10000) "Must be a number between 0 and 65536"]]
   ["-r" "--root ROOT" "Root directory for infinity-topos"
    :default "/Users/barton/infinity-topos"]
   ["-d" "--db DB" "Path to DuckDB database"
    :default ".topos/topos.db"]])

(defn ensure-directories []
  (println "Ensuring required directories exist...")
  (doseq [dir ["typescript" "python" ".topos/unified" ".topos/features"
               ".topos/ontology" ".topos/mermaid"]]
    (.mkdirs (io/file dir))))

(defn init-database [{:keys [db-path]}]
  (println "Initializing DuckDB database...")
  (require '[topos-db :as db])
  (db/init-db db-path))

(defn run-topos-sync [{:keys [root db-path] :as opts}]
  (println "Running topos sync...")
  (require '[topos-sync :as sync])
  (sync/sync-topos-files opts)
  (sync/sync-mcp-features opts))

(defn setup-servers []
  (println "Setting up MCP servers...")
  @(p/process ["bb" "manage.clj" "setup"] {:inherit true}))

(defn start-servers [{:keys [port env]}]
  (println "Starting MCP servers...")
  @(p/process ["bb" "manage.clj" "start" "-p" (str port) "-e" env] {:inherit true}))

(defn stop-servers []
  (println "Stopping MCP servers...")
  @(p/process ["bb" "manage.clj" "stop"] {:inherit true}))

(defn sync-mcp-features [{:keys [db-path] :as opts}]
  (println "Syncing MCP features from reference implementations...")
  (require '[topos-sync :as sync])
  (sync/sync-mcp-features opts))

(defn replicate-features []
  (println "Replicating MCP features...")
  (let [features-dir (io/file ".topos" "mcp-features")
        servers-dir (io/file features-dir "servers" "src")]
    (when (.exists servers-dir)
      (doseq [feature-dir (.listFiles servers-dir)]
        (when (.isDirectory feature-dir)
          (let [feature-name (.getName feature-dir)
                target-dir (io/file "src" "bmorphism-mcp" "features" feature-name)]
            (println "Replicating feature:" feature-name)
            (.mkdirs target-dir)
            @(p/process ["cp" "-r" (str feature-dir "/*") (str target-dir)])))))))

(defn generate-mermaid-diagrams [{:keys [db-path]}]
  (println "Generating Mermaid diagrams...")
  (require '[topos-db :as db])
  
  ;; Generate schema diagrams
  (doseq [schema (db/query db-path "SELECT * FROM category_schemas")]
    (let [objects (db/get-schema-objects db-path (:id schema))
          morphisms (db/get-schema-morphisms db-path (:id schema))
          diagram (str "graph TD\n"
                      (str/join "\n"
                        (for [obj objects]
                          (format "  %s[%s]" (:name obj) (:type obj))))
                      "\n"
                      (str/join "\n"
                        (for [morph morphisms]
                          (format "  %s --> |%s| %s"
                                 (:domain morph)
                                 (:name morph)
                                 (:codomain morph)))))]
      (db/store-mermaid db-path (:id schema) nil diagram))))

(defn run-all [{:keys [root] :as options}]
  (let [opts (assoc options :db-path ".topos/topos.db")]
    (ensure-directories)
    (init-database opts)
    (sync-mcp-features opts)
    (replicate-features)
    (run-topos-sync opts)
    (generate-mermaid-diagrams opts)
    (setup-servers)
    (try
      (start-servers options)
      (catch Exception e
        (println "Error starting servers:" (ex-message e))
        (stop-servers)))))

(defn usage [options-summary]
  (->> ["Bmorphism MCP Server Runner"
        ""
        "Usage: bb run.clj [options] action"
        ""
        "Options:"
        options-summary
        ""
        "Actions:"
        "  start     Start everything (sync, setup, servers)"
        "  stop      Stop all servers"
        "  sync      Only run topos sync"
        "  setup     Only setup servers"
        "  diagrams  Generate Mermaid diagrams"]
       (str/join \newline)))

(defn -main [& args]
  (let [{:keys [options arguments errors summary]} (cli/parse-opts args cli-options)]
    (cond
      (:help options)
      (println (usage summary))
      
      errors
      (do (println errors)
          (System/exit 1))
      
      :else
      (case (first arguments)
        "start" (run-all options)
        "stop" (stop-servers)
        "sync" (run-topos-sync options)
        "setup" (do (sync-mcp-features options)
                   (replicate-features)
                   (setup-servers))
        "diagrams" (generate-mermaid-diagrams options)
        (do
          (println "Unknown action. Use --help for usage information.")
          (System/exit 1))))))

(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
