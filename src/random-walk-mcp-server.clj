(ns random-walk-mcp-server
  (:require [clojure.java.io :as io]
            [clojure.string :as str]
            [clojure.data.json :as json]
            [clojure.tools.cli :refer [parse-opts]]
            [clojure.java.shell :refer [sh]]
            [clojure.edn :as edn]))

(defn fetch-repositories []
  (let [response (sh "gh" "api" "-H" "Accept: application/vnd.github.v3+json" "/orgs/Teglon-Labs/repos")]
    (if (= (:exit response) 0)
      (json/read-str (:out response) :key-fn keyword)
      (throw (Exception. (str "Failed to fetch repositories: " (:err response)))))))

(defn process-repository [repo]
  (let [name (:name repo)
        clone-url (:clone_url repo)]
    (println (str "Processing repository: " name))
    (sh "git" "clone" clone-url (str "/tmp/" name))
    (println (str "Cloned repository: " name " to /tmp/" name))))

(defn main [& args]
  (let [repos (fetch-repositories)]
    (doseq [repo repos]
      (process-repository repo))))

(when (= *file* (System/getProperty "babashka.file"))
  (apply main *command-line-args*))
