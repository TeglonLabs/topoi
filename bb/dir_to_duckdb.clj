; This script demonstrates how to traverse the current directory tree in Babashka,
; gather file metadata using babashka.fs, and store it into a DuckDB database using JDBC.
; Ensure you have DuckDB dependencies set up in bb.edn, for example:
; {:deps {org.clojure/clojure {:mvn/version "1.11.1"}
;         org.duckdb/duckdb_jdbc {:mvn/version "0.7.1"}
;         seancorfield/next.jdbc {:mvn/version "1.3.847"}}}

(ns dir-to-duckdb
  (:require
    [babashka.fs :as fs]
    [clojure.string :as str]
    [next.jdbc :as jdbc]))

(def db-file "topos_structure.duckdb") ; The DuckDB file we will create or open

(def db-spec
  {:dbtype "duckdb"
   :dbname db-file})

(defn create-table!
  [datasource]
  ;; Add a #_{:clj-kondo/ignore [:unresolved-symbol]} on the SQL vector to silence
  ;; clj-kondo on the SQL syntax
  (jdbc/execute!
   datasource
   #_{:clj-kondo/ignore [:unresolved-symbol]}
   ["CREATE TABLE IF NOT EXISTS files (
       path TEXT PRIMARY KEY,
       is_directory BOOLEAN,
       size BIGINT,
       last_modified TIMESTAMP
     )"]))

(defn insert-file!
  [datasource {:keys [path is-dir size last-modified]}]
  (jdbc/execute!
   datasource
   #_{:clj-kondo/ignore [:unresolved-symbol]}
   ["INSERT INTO files(path, is_directory, size, last_modified)
     VALUES (?, ?, ?, ?)
     ON CONFLICT(path) DO UPDATE SET
       is_directory=excluded.is_directory,
       size=excluded.size,
       last_modified=excluded.last_modified"
    path is-dir size last-modified]))

(defn store-directory-tree!
  [datasource root-path]
  (println (str "Traversing " root-path " and storing file info to " db-file " ..."))
  (doseq [f (fs/glob root-path "**")]  ; Recursively gather all files/dirs
    (when (fs/exists? f)
      (let [attrs (fs/metadata f)
            file-info {:path (str (fs/absolutize f))
                       :is-dir (fs/directory? f)
                       :size (:size attrs)
                       ;; Convert epoch millis to date or nil if no date
                       :last-modified (some-> (:last-modified-time attrs)
                                              (java.util.Date.))}]
        (insert-file! datasource file-info)))))

(defn -main
  [& [directory]]
  (let [dir (or directory
                (str (fs/current-dir)))     ; Default to current directory
        datasource (jdbc/get-datasource db-spec)]
    (create-table! datasource)
    (store-directory-tree! datasource dir)
    (println (str "Done storing directory tree to DuckDB."))))

(comment
  ;; How to run:
  ;; bb -m dir-to-duckdb
  ;; or provide a specific path:
  ;; bb -m dir-to-duckdb "/path/to/other/directory"
  )
