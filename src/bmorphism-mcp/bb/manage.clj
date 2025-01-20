#!/usr/bin/env bb

(ns manage
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
    :validate [#(< 0 % 0x10000) "Must be a number between 0 and 65536"]]])

(defn find-python []
  (let [venv-python (str (io/file ".venv" "bin" "python"))]
    (if (.exists (io/file venv-python))
      venv-python
      "python")))

(defn setup-typescript []
  (println "Setting up TypeScript server...")
  (let [ts-dir (str (io/file "typescript"))]
    @(p/process ["npm" "install"] {:dir ts-dir :inherit true})
    @(p/process ["npm" "run" "build"] {:dir ts-dir :inherit true})))

(defn setup-python []
  (println "Setting up Python server...")
  (let [py-dir (str (io/file "python"))]
    @(p/process ["uv" "pip" "install" "-e" "."] {:dir py-dir :inherit true})))

(defn create-tmux-session [session-name]
  (try
    @(p/process ["tmux" "new-session" "-d" "-s" session-name])
    (catch Exception _
      (println "Session" session-name "already exists"))))

(defn start-servers [{:keys [port env]}]
  (let [session-name "bmorphism-mcp"]
    ; Create tmux session
    (create-tmux-session session-name)
    
    ; Start TypeScript drand server
    (println "Starting TypeScript drand server on port" port)
    @(p/process ["tmux" "send-keys" "-t" session-name:0.0
                (str "cd typescript && PORT=" port " npm start")
                "C-m"])
    
    ; Create new window for Python server
    @(p/process ["tmux" "new-window" "-t" session-name])
    
    ; Start Python slowtime server
    (println "Starting Python slowtime server")
    @(p/process ["tmux" "send-keys" "-t" session-name:1.0
                (str "cd python && DRAND_TS_PORT=" port " " (find-python) " -m server")
                "C-m"])
    
    ; Attach to tmux session
    @(p/process ["tmux" "attach" "-t" session-name] {:inherit true})))

(defn stop-servers []
  (try
    @(p/process ["tmux" "kill-session" "-t" "bmorphism-mcp"])
    (println "Servers stopped")
    (catch Exception _
      (println "No active server session found"))))

(defn setup []
  (println "Setting up Bmorphism MCP servers...")
  (setup-typescript)
  (setup-python)
  (println "Setup complete"))

(defn usage [options-summary]
  (->> ["Bmorphism MCP Server Manager"
        ""
        "Usage: bb manage.clj [options] action"
        ""
        "Options:"
        options-summary
        ""
        "Actions:"
        "  setup     Install dependencies and build servers"
        "  start     Start both TypeScript and Python servers in tmux"
        "  stop      Stop all servers"
        "  restart   Restart all servers"]
       (str/join \newline)))

(defn error-msg [errors]
  (str "The following errors occurred while parsing your command:\n\n"
       (str/join \newline errors)))

(defn validate-args [args]
  (let [{:keys [options arguments errors summary]} (cli/parse-opts args cli-options)]
    (cond
      (:help options)
      {:exit-message (usage summary) :ok? true}
      
      errors
      {:exit-message (error-msg errors)}
      
      (and (= 1 (count arguments))
           (#{"setup" "start" "stop" "restart"} (first arguments)))
      {:action (first arguments) :options options}
      
      :else
      {:exit-message (usage summary)})))

(defn -main [& args]
  (let [{:keys [action options exit-message ok?]} (validate-args args)]
    (if exit-message
      (println exit-message)
      (case action
        "setup" (setup)
        "start" (start-servers options)
        "stop" (stop-servers)
        "restart" (do (stop-servers)
                     (Thread/sleep 1000)
                     (start-servers options))))))

(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
