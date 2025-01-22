(ns topos_mcp.core
  (:require [babashka.cli :as cli]
            [babashka.process :refer [process]]
            [babashka.fs :as fs]
            [cheshire.core :as json]
            [clojure.java.io :as io]
            [clojure.string :as str]))

(defn create-backup []
  (let [timestamp (System/currentTimeMillis)
        backup-dir (str "backup.topoi." timestamp)
        tar-name (str backup-dir ".tar.gz")]
    (println "Creating backup directory:" backup-dir)
    (fs/create-dir backup-dir)
    
    ;; Copy all files recursively excluding backups and .git
    (doseq [path (fs/glob "." "**")]
      (when (and (fs/regular-file? path)
                 (not (str/starts-with? (str path) "backup.topoi"))
                 (not (str/starts-with? (str path) ".git")))
        (let [target (fs/path backup-dir path)]
          (fs/create-dirs (fs/parent target))
          (fs/copy path target))))
    
    ;; Create tar.gz archive using shell
    (-> (ProcessBuilder.
         (into-array ["bash" "-c" (str "cd " backup-dir " && tar czf ../" tar-name " .")]))
        (.inheritIO)
        (.start)
        (.waitFor))
    
    ;; Clean up backup directory
    (fs/delete-tree backup-dir)
    
    (println "Backup created:" tar-name)))

(def cli-options
  {:coerce {:port :int}
   :alias {:p :port}
   :require [:mode]
   :validate {:mode #{"server" "client" "backup" "coin-flip"}}})

(defn start-server [opts]
  (println "Starting Topos MCP server...")
  ;; TODO: Implement server startup
  )

(defn start-client [opts]
  (println "Starting Topos MCP client...")
  ;; TODO: Implement client startup
  )

(defn run [opts]
  (let [mode (:mode opts "run")]
    (case mode
      "server" (start-server opts)
      "client" (start-client opts)
      "backup" (create-backup)
      "coin-flip" (println (rand-nth ["+1" "0" "-1"]))
      (println "Running Topos MCP..."))))

(defn -main [& args]
  (let [opts (cli/parse-opts args cli-options)]
    (run opts)))

(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
