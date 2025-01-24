#!/usr/bin/env bb

(ns example-mcp-server
  (:require [mcp-server :as mcp]
            [babashka.fs :as fs]
            [clojure.string :as str]))

;; Example MCP server that implements directory listing as a tool
(defrecord DirectoryServer [name version capabilities]
  mcp/IMCPServer
  (initialize [this options]
    {:serverInfo {:name name
                 :version version}
     :capabilities capabilities
     :protocolVersion "0.1.0"})

  (list-resources [_this]
    {:resources []})

  (read-resource [_this uri]
    (mcp/make-error nil -32601 "Method not implemented"))

  (list-tools [_this]
    {:tools [{:name "list_directory"
             :description "List contents of a directory"
             :inputSchema {:type "object"
                         :properties {"path" {:type "string"
                                            :description "Directory path to list"}}
                         :required ["path"]}}]})

  (call-tool [_this tool-name args]
    (case tool-name
      "list_directory"
      (try
        (let [path (:path args)
              files (fs/list-dir path)
              file-list (mapv (fn [f]
                              {:name (str (fs/file-name f))
                               :type (if (fs/directory? f) "directory" "file")
                               :size (fs/size f)
                               :modified (str (fs/last-modified-time f))})
                            files)]
          {:content [{:type "text"
                     :text (str "Directory listing for: " path "\n"
                               (str/join "\n" (map #(str (:type %) ": " (:name %)) file-list)))}]})
        (catch Exception e
          (mcp/make-error nil -32603 (str "Error listing directory: " (.getMessage e)))))

      (mcp/make-error nil -32601 (str "Tool not found: " tool-name)))))

(defn -main [& args]
  (let [server (->DirectoryServer
                "directory-server"
                "0.1.0"
                {:tools {:listChanged true}})]
    (mcp/process-stdin server)))

(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
