#!/usr/bin/env hy

(import json)
(import subprocess)
(import openai)
(import pathlib [Path])

(setv SYSTEM-PROMPT "You are an AI assistant integrating with a Model Context Protocol system.")
(setv INITIAL-PROMPT "Hello, how can I help you today?")

(setv BABASHKA-PATH "bb/hy-handler.clj")

;; EDN conversion utilities
(defn json->edn [data]
  "Convert JSON string to EDN using jet"
  (let [proc (.run subprocess
                   ["jet" "--from" "json" "--to" "edn"]
                   :input (.encode (json.dumps data) "utf-8")
                   :capture-output True)]
    (when (= proc.returncode 0)
      (.decode proc.stdout "utf-8"))))

(defn edn->json [data]
  "Convert EDN string to JSON using jet"
  (let [proc (.run subprocess
                   ["jet" "--from" "edn" "--to" "json"]
                   :input (.encode data "utf-8")
                   :capture-output True)]
    (when (= proc.returncode 0)
      (json.loads (.decode proc.stdout "utf-8")))))

;; LLM Response Handler
(defn handle-llm-response [prompt system-prompt]
  "Handle LLM response"
  (setv client (openai.Client))
  (setv response (.create client.chat.completions
                          :model "gpt-3.5-turbo"
                          :messages [{"role" "system" "content" system-prompt}
                                     {"role" "user" "content" prompt}]))
  response)

;; Babashka Bridge
(defclass BabashkaBridge []
  "Bridge between Hy and Babashka"
  
  (defn __init__ [self]
    (setv self.transaction-log []))
  
  (defn send-to-babashka [self data]
    "Send data to Babashka process"
    (let [edn-str (json->edn data)
          proc (.create-subprocess-exec subprocess
                                      "bb"
                                      "bb/process.clj"
                                      :stdin subprocess.PIPE
                                      :stdout subprocess.PIPE)]
      (setv [stdout stderr] (.communicate proc (.encode edn-str "utf-8")))
      (print f"Babashka response - stdout: {stdout}, stderr: {stderr})))
  
  (defn process-llm [self prompt system-prompt]
    "Process LLM response and send to Babashka"
    (setv response (handle-llm-response prompt system-prompt))
    (send-to-babashka self {"type" "llm-response"
                             "content" response
                             "timestamp" (str (.now datetime.datetime))})
    (self.transaction-log.append response)))

;; Main loop
(defn main []
  (setv bridge (BabashkaBridge))
  
  (when (not (.exists (Path BABASHKA-PATH)))
    (raise (FileNotFoundError f"Babashka handler not found at {BABASHKA-PATH}")))
  
  (bridge.process-llm INITIAL-PROMPT SYSTEM-PROMPT))

;; Entry point
(when (= __name__ "__main__")
  (main))
