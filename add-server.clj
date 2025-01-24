#!/usr/bin/env bb

(ns add-server
  (:require [babashka.fs :as fs]
            [clojure.java.shell :refer [sh]]
            [clojure.string :as str]
            [cheshire.core :as json]))

(def mcp-config-path
  (let [home (System/getProperty "user.home")
        os-name (System/getProperty "os.name")]
    (if (str/includes? os-name "Linux")
      (str home "/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json")
      (str home "/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"))))

(def server-templates
  {"say" {:command "node"
          :args ["build/index.js"]
          :env {"SPEAK_OVER" "false"
                "DEFAULT_VOICE" "Serena (Premium)"}}
   
   "discopy-mcp-server" {:command "python"
                        :args ["src/server.py"]
                        :env {"PYTHONPATH" "src"}}
   
   "penrose" {:command "node"
              :args ["build/index.js"]}
   
   "exa" {:command "npx"
          :args ["build/index.js"]
          :prompt-env ["EXA_API_KEY"]}})

(defn read-config []
  (json/parse-string (slurp mcp-config-path) true))

(defn write-config [config]
  (spit mcp-config-path 
        (json/generate-string config {:pretty true})))

(defn test-server [name config]
  (println "Testing" name "...")
  (try
    (let [result (sh "node" "-e" 
                     (str "const server = require('./" name "/build/index.js');"
                          "server.test()"))]
      (= 0 (:exit result)))
    (catch Exception e
      false)))

(defn prompt-env-vars [template]
  (when-let [vars (:prompt-env template)]
    (into {} 
          (for [var vars]
            [var (do
                  (print (str "Enter " var ": "))
                  (flush)
                  (read-line))]))))

(defn add-server [name]
  (if-let [template (get server-templates name)]
    (let [config (read-config)
          env-vars (prompt-env-vars template)
          server-config (merge template
                             {:args (mapv #(str "~/infinity-topos/mcp-servers/" name "/" %) 
                                        (:args template))}
                             (when env-vars
                               {:env env-vars}))]
      
      ;; Copy server files
      (println "Copying server files...")
      (fs/copy-tree (str "../" name) 
                    (str "mcp-servers/" name))
      
      ;; Build server
      (println "Building server...")
      (sh "npm" "install" :dir (str "mcp-servers/" name))
      (sh "npm" "run" "build" :dir (str "mcp-servers/" name))
      
      ;; Test server
      (if (test-server name config)
        (do
          ;; Add to config
          (write-config (update config :mcpServers assoc name server-config))
          (println "Successfully added" name))
        (println "Server test failed for" name)))
    (println "Unknown server template:" name)))

(when (= *file* (System/getProperty "babashka.file"))
  (when-let [server-name (first *command-line-args*)]
    (add-server server-name)))
