#!/usr/bin/env bb

(ns topos-sync
  (:require [babashka.process :as p]
            [clojure.string :as str]
            [clojure.java.io :as io]
            [clojure.tools.cli :as cli]
            [cheshire.core :as json]))

(def cli-options
  [["-h" "--help" "Show help"]
   ["-r" "--root ROOT" "Root directory for infinity-topos"
    :default "/Users/barton/infinity-topos"]
   ["-d" "--db DB" "Path to DuckDB database"
    :default ".topos/topos.db"]])

;; Schema definitions for common structures
(def graph-schema
  {:name "Graph"
   :description "Basic directed graph schema"
   :objects [{:name "V" :type "Ob"}
            {:name "E" :type "Ob"}]
   :morphisms [{:name "src" :type "Hom" :domain "E" :codomain "V"}
              {:name "tgt" :type "Hom" :domain "E" :codomain "V"}]})

(def attributed-graph-schema
  {:name "AttributedGraph"
   :description "Graph with vertex and edge attributes"
   :objects [{:name "V" :type "Ob"}
            {:name "E" :type "Ob"}
            {:name "VLabel" :type "AttrType"}
            {:name "ELabel" :type "AttrType"}]
   :morphisms [{:name "src" :type "Hom" :domain "E" :codomain "V"}
              {:name "tgt" :type "Hom" :domain "E" :codomain "V"}
              {:name "vlabel" :type "Attr" :domain "V" :codomain "VLabel"}
              {:name "elabel" :type "Attr" :domain "E" :codomain "ELabel"}]})

(defn ensure-base-schemas [db-path]
  (require '[topos-db :as db])
  
  ;; Create base schemas if they don't exist
  (when-not (db/query db-path "SELECT id FROM category_schemas WHERE name = 'Graph' LIMIT 1")
    (let [schema-id (db/create-schema db-path "Graph" (:description graph-schema))
          v-id (db/add-schema-object db-path schema-id "V" "Ob" {})
          e-id (db/add-schema-object db-path schema-id "E" "Ob" {})]
      (db/add-schema-morphism db-path schema-id "src" e-id v-id "Hom" {})
      (db/add-schema-morphism db-path schema-id "tgt" e-id v-id "Hom" {})))

  (when-not (db/query db-path "SELECT id FROM category_schemas WHERE name = 'AttributedGraph' LIMIT 1")
    (let [schema-id (db/create-schema db-path "AttributedGraph" (:description attributed-graph-schema))
          v-id (db/add-schema-object db-path schema-id "V" "Ob" {})
          e-id (db/add-schema-object db-path schema-id "E" "Ob" {})
          vl-id (db/add-schema-object db-path schema-id "VLabel" "AttrType" {})
          el-id (db/add-schema-object db-path schema-id "ELabel" "AttrType" {})]
      (db/add-schema-morphism db-path schema-id "src" e-id v-id "Hom" {})
      (db/add-schema-morphism db-path schema-id "tgt" e-id v-id "Hom" {})
      (db/add-schema-morphism db-path schema-id "vlabel" v-id vl-id "Attr" {})
      (db/add-schema-morphism db-path schema-id "elabel" e-id el-id "Attr" {}))))

(defn find-topos-files [root]
  (let [topos-dirs (->> (file-seq (io/file root))
                       (filter #(.isDirectory %))
                       (filter #(= (.getName %) ".topos")))]
    (->> topos-dirs
         (mapcat file-seq)
         (filter #(.isFile %))
         (filter #(or (.endsWith (.getName %) ".topos")
                     (.endsWith (.getName %) ".mermaid"))))))

(defn parse-topos-content [file]
  (let [content (slurp file)
        file-type (if (.endsWith (.getName file) ".topos") :topos :mermaid)]
    (case file-type
      :topos {:type :topos
              :path (.getPath file)
              :content content
              :schema "Graph"  ; Default to basic graph schema
              :metadata {}}
      :mermaid {:type :mermaid
                :path (.getPath file)
                :content content
                :metadata {}})))

(defn create-acset-from-topos [db-path file-info]
  (require '[topos-db :as db])
  (let [schema-id (-> (db/query db-path 
                       (format "SELECT id FROM category_schemas WHERE name = '%s'"
                               (:schema file-info)))
                     first
                     :id)
        instance-id (db/create-acset db-path 
                                   schema-id
                                   (.getName (io/file (:path file-info)))
                                   "Generated from .topos file")]
    ;; Parse and store the content based on schema
    ;; This is a simplified version - would need proper parsing based on schema
    (let [lines (str/split-lines (:content file-info))
          vertices (filter #(str/starts-with? % "V ") lines)
          edges (filter #(str/starts-with? % "E ") lines)]
      
      ;; Add vertices
      (doseq [v vertices]
        (let [[_ id & attrs] (str/split v #"\s+")]
          (let [part-id (db/add-part db-path instance-id 
                         (-> (db/get-schema-objects db-path schema-id)
                             (filter #(= (:name %) "V"))
                             first
                             :id)
                         (Integer/parseInt id)
                         {:attributes attrs})])))
      
      ;; Add edges
      (doseq [e edges]
        (let [[_ id src tgt & attrs] (str/split e #"\s+")
              morphisms (db/get-schema-morphisms db-path schema-id)
              src-morph (first (filter #(= (:name %) "src") morphisms))
              tgt-morph (first (filter #(= (:name %) "tgt") morphisms))
              edge-id (db/add-part db-path instance-id
                       (-> (db/get-schema-objects db-path schema-id)
                           (filter #(= (:name %) "E"))
                           first
                           :id)
                       (Integer/parseInt id)
                       {:attributes attrs})]
          (db/assign-morphism db-path instance-id 
                             (:id src-morph) edge-id (Integer/parseInt src))
          (db/assign-morphism db-path instance-id
                             (:id tgt-morph) edge-id (Integer/parseInt tgt)))))
    
    instance-id))

(defn store-mermaid-diagram [db-path file-info]
  (require '[topos-db :as db])
  (db/store-mermaid db-path nil nil (:content file-info)))

(defn sync-topos-files [{:keys [root db-path]}]
  (ensure-base-schemas db-path)
  (let [files (find-topos-files root)]
    (doseq [file files]
      (let [file-info (parse-topos-content file)]
        (case (:type file-info)
          :topos (create-acset-from-topos db-path file-info)
          :mermaid (store-mermaid-diagram db-path file-info))))))

(defn sync-mcp-features [{:keys [db-path]}]
  (require '[topos-db :as db])
  (let [features-dir (io/file ".topos" "mcp-features")]
    (.mkdirs features-dir)
    
    ;; Clone/update reference implementations
    (doseq [repo ["modelcontextprotocol/servers"
                  "wong2/awesome-mcp-servers"]]
      (let [dir (io/file features-dir (last (str/split repo #"/")))
            repo-url (str "https://github.com/" repo)]
        (if (.exists dir)
          (do
            (println "Updating" repo)
            @(p/process ["git" "pull"] {:dir dir}))
          (do
            (println "Cloning" repo)
            @(p/process ["git" "clone" repo-url] {:dir features-dir})))
        
        ;; Track features in DuckDB
        (when (= repo "modelcontextprotocol/servers")
          (let [schema-id (db/create-schema db-path "MCP" "MCP server features")]
            (doseq [feature-dir (.listFiles (io/file dir "src"))]
              (when (.isDirectory feature-dir)
                (db/track-mcp-feature db-path
                                    (.getName feature-dir)
                                    schema-id
                                    repo-url
                                    (str "src/" (.getName feature-dir)))))))))))

(defn usage [options-summary]
  (->> ["Topos Documentation Sync Tool"
        ""
        "Usage: bb topos_sync.clj [options]"
        ""
        "Options:"
        options-summary]
       (str/join \newline)))

(defn -main [& args]
  (let [{:keys [options arguments errors summary]} (cli/parse-opts args cli-options)]
    (cond
      (:help options)
      (println (usage summary))
      
      errors
      (do (println errors)
          (System/exit 1))
      
      :else
      (do
        (sync-topos-files options)
        (sync-mcp-features options)))))

(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
