#!/usr/bin/env bb

(ns process
  (:require [babashka.process :as p]
            [clojure.string :as str]
            [clojure.java.io :as io]
            [clojure.tools.cli :as cli]))

(def cli-options
  [["-h" "--help" "Show help"]
   ["-e" "--env ENV" "Environment type (dev/prod)" :default "dev"]
   ["-p" "--port PORT" "Port number"
    :default 3000
    :parse-fn #(Integer/parseInt %)
    :validate [#(< 0 % 0x10000) "Must be a number between 0 and 65536"]]])

(defn find-python []
  (let [venv-python (str (io/file ".venv" "bin" "python"))]
    (if (.exists (io/file venv-python))
      venv-python
      "python")))

(defn start-server [{:keys [port env]}]
  (let [python (find-python)
        server-file (str (io/file "src" "topos_mcp" "__main__.py"))]
    (println "Starting server with" python "on port" port "in" env "mode")
    @(p/process [python server-file "--port" (str port) "--env" env]
                {:inherit true})))

(defn start-client [{:keys [port env]}]
  (let [python (find-python)
        client-file (str (io/file "src" "topos_mcp" "client.py"))]
    (println "Starting client with" python "on port" port "in" env "mode")
    @(p/process [python client-file "--port" (str port) "--env" env]
                {:inherit true})))

(defn usage [options-summary]
  (->> ["Topos MCP Process Manager"
        ""
        "Usage: bb process.clj [options] action"
        ""
        "Options:"
        options-summary
        ""
        "Actions:"
        "  server    Start the MCP server"
        "  client    Start the MCP client"
        "  all       Start both server and client"]
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
           (#{"server" "client" "all"} (first arguments)))
      {:action (first arguments) :options options}
      
      :else
      {:exit-message (usage summary)})))

(defn exit [status msg]
  (println msg)
  (System/exit status))

(defn -main [& args]
  (let [{:keys [action options exit-message ok?]} (validate-args args)]
    (if exit-message
      (exit (if ok? 0 1) exit-message)
      (case action
        "server" (start-server options)
        "client" (start-client options)
        "all" (do
                (future (start-server options))
                (Thread/sleep 2000)  ; Wait for server to start
                (start-client options))))))

(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
