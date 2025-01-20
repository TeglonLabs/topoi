#!/usr/bin/env bb
(ns random-walk-plurigrid
  "A Babashka script for random walking through plurigrid repositories,
   with direction compass compression of nearby topics."
  (:require [babashka.fs :as fs]
            [clojure.string :as str]
            [cheshire.core :as json]))

(def plurigrid-repos
  ["plurigrid/plurigrid"
   "plurigrid/dkg"
   "plurigrid/plurigrid-js"
   "plurigrid/tap"
   "plurigrid/docs"])

(defn fetch-repo-info [repo]
  (try
    (let [url (str "https://api.github.com/repos/" repo)
          result (-> (str "curl -s " url)
                    (shell/sh)
                    :out
                    (json/parse-string true))]
      {:name (:name result)
       :description (:description result)
       :topics (or (:topics result) [])})
    (catch Exception _
      {:name (last (str/split repo #"/"))
       :description "Unable to fetch"
       :topics []})))

(defn random-walk []
  (let [repo (rand-nth plurigrid-repos)
        info (fetch-repo-info repo)]
    (println "\nRandom walk landed on:" (:name info))
    (println "Description:" (:description info))
    (when (seq (:topics info))
      (println "Topics:" (str/join ", " (:topics info))))))

(defn direction-compass []
  (println "\nDirection Compass (Topic Compression):")
  (let [all-repos (map fetch-repo-info plurigrid-repos)
        all-topics (mapcat :topics all-repos)]
    (->> all-topics
         frequencies
         (sort-by val >)
         (take 5)
         (map first)
         (str/join " → ")
         println)))

(defn -main [& _args]
  (println "🌐 Random Walk through Plurigrid")
  (println "--------------------------------")
  (random-walk)
  (direction-compass)
  (println "\nՀաջողություն:") ; Armenian: "Success/Good luck"
  (System/exit 0))

(when (= *file* (System/getProperty "babashka.file"))
  (-main))
