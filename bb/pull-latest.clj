#!/usr/bin/env bb

(ns pull-latest
  (:require [babashka.fs :as fs]
            [clojure.java.shell :refer [sh]]
            [clojure.string :as str]))

(def topos-root (str (fs/home) "/infinity-topos/.topos"))

(defn git-repo? [dir]
  (fs/exists? (fs/path dir ".git")))

(defn pull-repo [dir]
  (println "\nPulling" (str/replace (str dir) topos-root ""))
  (let [{:keys [exit out err]} (sh "git" "-C" (str dir) "pull")]
    (if (zero? exit)
      (println out)
      (println "Error:" err))))

(defn find-and-pull-repos []
  (println "Scanning for git repositories under" topos-root)
  (->> (fs/glob topos-root "**/.git")
       (map fs/parent)
       (filter git-repo?)
       (run! pull-repo)))

(defn -main [& _args]
  (find-and-pull-repos))

(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
