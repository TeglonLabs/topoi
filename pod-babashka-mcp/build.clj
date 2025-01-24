#!/usr/bin/env bb

(ns build
  (:require [babashka.fs :as fs]
            [babashka.process :refer [shell]]
            [clojure.string :as str]))

(def version "0.1.0")

(defn clean [_]
  (fs/delete-tree "target")
  (println "Cleaned target directory"))

(defn compile-go [_]
  (println "Compiling Go code...")
  (shell "go build -o target/pod-babashka-mcp src/mcp/pod.go"))

(defn copy-clj [_]
  (println "Copying Clojure files...")
  (fs/create-dirs "target/classes/pod/babashka")
  (fs/copy-tree "src/bb/pod/babashka" "target/classes/pod/babashka"))

(defn package [_]
  (println "Packaging pod...")
  (let [target-dir (str "target/pod-babashka-mcp-" version)]
    (fs/create-dirs target-dir)
    (fs/copy "target/pod-babashka-mcp" target-dir)
    (fs/copy-tree "target/classes" target-dir)
    (fs/copy "README.md" target-dir)
    (fs/copy "LICENSE" target-dir)))

(defn install [_]
  (println "Installing pod...")
  (let [pod-dir (str (fs/home) "/.babashka/pods")]
    (fs/create-dirs pod-dir)
    (fs/copy "target/pod-babashka-mcp" pod-dir)))

(defn test [_]
  (println "Running tests...")
  (shell "bb test"))

(def tasks
  {:clean clean
   :compile-go compile-go
   :copy-clj copy-clj
   :package package
   :install install
   :test test})

(defn -main [& args]
  (let [task-name (first args)
        task-fn (get tasks (keyword task-name))]
    (if task-fn
      (task-fn args)
      (println "Available tasks:" (str/join ", " (keys tasks))))))

(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
