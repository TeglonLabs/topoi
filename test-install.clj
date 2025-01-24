#!/usr/bin/env bb

(ns test-install
  (:require [babashka.fs :as fs]
            [clojure.java.shell :refer [sh]]
            [clojure.string :as str]
            [cheshire.core :as json]))

(defn test-step [name f]
  (print (str "\nTesting " name "... "))
  (flush)
  (try
    (f)
    (println "✓")
    true
    (catch Exception e
      (println "✗")
      (println "Error:" (ex-message e))
      false)))

(defn check-directory [path]
  (when-not (fs/exists? path)
    (throw (ex-info (str "Directory not found: " path) {}))))

(defn check-file [path]
  (when-not (fs/exists? path)
    (throw (ex-info (str "File not found: " path) {}))))

(defn check-executable [path]
  (when-not (fs/executable? path)
    (throw (ex-info (str "Not executable: " path) {}))))

(defn test-installation []
  (println "\nTesting infinity-topos MCP installation...")
  
  ;; Test core dependencies
  (test-step "uv installation" #(sh "uv" "--version"))
  (test-step "babashka installation" #(sh "bb" "--version"))
  
  ;; Test directory structure
  (test-step "directory structure" 
    #(do
       (check-directory "~/infinity-topos")
       (check-directory "~/infinity-topos/mcp-servers")))
  
  ;; Test core servers
  (test-step "core server files" 
    #(do
       (check-directory "~/infinity-topos/mcp-servers/coin-flip-mcp")
       (check-directory "~/infinity-topos/mcp-servers/babashka-mcp-server")))
  
  ;; Test coin-flip functionality
  (test-step "coin-flip server" 
    #(let [result (sh "bb" "-e" 
                      "(require '[babashka.process :refer [shell]])
                       (shell {:out :string} 
                         \"uv\" \"pip\" \"install\" \"-e\" 
                         \"~/infinity-topos/mcp-servers/coin-flip-mcp\")")]
       (when-not (zero? (:exit result))
         (throw (ex-info "Failed to install coin-flip" {})))))
  
  ;; Test MCP configuration
  (test-step "MCP configuration" 
    #(let [config-path (if (str/includes? (System/getProperty "os.name") "Linux")
                        "~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
                        "~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json")]
       (check-file config-path)))
  
  (println "\nInstallation test complete!"))

(when (= *file* (System/getProperty "babashka.file"))
  (test-installation))
