#!/usr/bin/env bb

(ns topos-db
  (:require [babashka.process :as p]
            [clojure.string :as str]
            [clojure.java.io :as io]
            [cheshire.core :as json]))

(def schema-sql "
-- C-Set Schema Tables
CREATE TABLE IF NOT EXISTS category_schemas (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Objects in the category (vertices in the schema graph)
CREATE TABLE IF NOT EXISTS schema_objects (
  id INTEGER PRIMARY KEY,
  schema_id INTEGER REFERENCES category_schemas(id),
  name TEXT NOT NULL,
  type TEXT NOT NULL, -- 'Ob' for objects, 'AttrType' for attribute types
  metadata JSONB,
  UNIQUE(schema_id, name)
);

-- Morphisms in the category (edges in the schema graph)
CREATE TABLE IF NOT EXISTS schema_morphisms (
  id INTEGER PRIMARY KEY,
  schema_id INTEGER REFERENCES category_schemas(id),
  name TEXT NOT NULL,
  domain_id INTEGER REFERENCES schema_objects(id),
  codomain_id INTEGER REFERENCES schema_objects(id),
  type TEXT NOT NULL, -- 'Hom' for homomorphisms, 'Attr' for attributes
  metadata JSONB,
  UNIQUE(schema_id, name)
);

-- Equations between morphism compositions
CREATE TABLE IF NOT EXISTS schema_equations (
  id INTEGER PRIMARY KEY,
  schema_id INTEGER REFERENCES category_schemas(id),
  lhs_path INTEGER[], -- Array of morphism IDs representing composition
  rhs_path INTEGER[],
  metadata JSONB
);

-- ACSet Instances
CREATE TABLE IF NOT EXISTS acset_instances (
  id INTEGER PRIMARY KEY,
  schema_id INTEGER REFERENCES category_schemas(id),
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parts tables for each object in the schema
CREATE TABLE IF NOT EXISTS instance_parts (
  id INTEGER PRIMARY KEY,
  instance_id INTEGER REFERENCES acset_instances(id),
  object_id INTEGER REFERENCES schema_objects(id),
  local_id INTEGER NOT NULL, -- ID within this part collection
  metadata JSONB,
  UNIQUE(instance_id, object_id, local_id)
);

-- Morphism assignments
CREATE TABLE IF NOT EXISTS morphism_assignments (
  id INTEGER PRIMARY KEY,
  instance_id INTEGER REFERENCES acset_instances(id),
  morphism_id INTEGER REFERENCES schema_morphisms(id),
  domain_part_id INTEGER REFERENCES instance_parts(id),
  codomain_part_id INTEGER REFERENCES instance_parts(id)
);

-- Attribute assignments (for data attributes)
CREATE TABLE IF NOT EXISTS attribute_assignments (
  id INTEGER PRIMARY KEY,
  instance_id INTEGER REFERENCES acset_instances(id),
  morphism_id INTEGER REFERENCES schema_morphisms(id),
  domain_part_id INTEGER REFERENCES instance_parts(id),
  value_data TEXT, -- Serialized attribute value
  value_type TEXT  -- Type information for deserialization
);

-- Feature tracking for MCP servers
CREATE TABLE IF NOT EXISTS mcp_features (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  schema_id INTEGER REFERENCES category_schemas(id),
  source_repo TEXT NOT NULL,
  implementation_path TEXT,
  replicated BOOLEAN DEFAULT FALSE,
  last_sync TIMESTAMP,
  metadata JSONB
);

-- Feature relationships (as a graph)
CREATE TABLE IF NOT EXISTS feature_relationships (
  id INTEGER PRIMARY KEY,
  source_feature_id INTEGER REFERENCES mcp_features(id),
  target_feature_id INTEGER REFERENCES mcp_features(id),
  relationship_type TEXT NOT NULL,
  metadata JSONB
);

-- Mermaid diagrams for visualization
CREATE TABLE IF NOT EXISTS mermaid_diagrams (
  id INTEGER PRIMARY KEY,
  schema_id INTEGER REFERENCES category_schemas(id),
  instance_id INTEGER REFERENCES acset_instances(id),
  content TEXT NOT NULL,
  dot_graph TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
")

(defn init-db [db-path]
  (println "Initializing DuckDB at" db-path)
  @(p/process ["duckdb" db-path "-c" schema-sql]))

(defn query [db-path sql]
  (-> (p/process ["duckdb" db-path "-json" "-c" sql]
                 {:out :string})
      deref
      :out
      (json/parse-string true)))

;; Schema management functions
(defn create-schema [db-path name description]
  (let [sql (format "INSERT INTO category_schemas (name, description) 
                    VALUES ('%s', '%s') RETURNING id"
                    name description)]
    (-> (query db-path sql) first :id)))

(defn add-schema-object [db-path schema-id name type metadata]
  (let [sql (format "INSERT INTO schema_objects (schema_id, name, type, metadata)
                    VALUES (%d, '%s', '%s', '%s') RETURNING id"
                    schema-id name type (json/generate-string metadata))]
    (-> (query db-path sql) first :id)))

(defn add-schema-morphism [db-path schema-id name domain-id codomain-id type metadata]
  (let [sql (format "INSERT INTO schema_morphisms 
                    (schema_id, name, domain_id, codomain_id, type, metadata)
                    VALUES (%d, '%s', %d, %d, '%s', '%s') RETURNING id"
                    schema-id name domain-id codomain-id type 
                    (json/generate-string metadata))]
    (-> (query db-path sql) first :id)))

;; ACSet instance management
(defn create-acset [db-path schema-id name description]
  (let [sql (format "INSERT INTO acset_instances 
                    (schema_id, name, description)
                    VALUES (%d, '%s', '%s') RETURNING id"
                    schema-id name description)]
    (-> (query db-path sql) first :id)))

(defn add-part [db-path instance-id object-id local-id metadata]
  (let [sql (format "INSERT INTO instance_parts
                    (instance_id, object_id, local_id, metadata)
                    VALUES (%d, %d, %d, '%s') RETURNING id"
                    instance-id object-id local-id
                    (json/generate-string metadata))]
    (-> (query db-path sql) first :id)))

(defn assign-morphism [db-path instance-id morphism-id domain-id codomain-id]
  (let [sql (format "INSERT INTO morphism_assignments
                    (instance_id, morphism_id, domain_part_id, codomain_part_id)
                    VALUES (%d, %d, %d, %d)"
                    instance-id morphism-id domain-id codomain-id)]
    (query db-path sql)))

(defn assign-attribute [db-path instance-id morphism-id domain-id value type]
  (let [sql (format "INSERT INTO attribute_assignments
                    (instance_id, morphism_id, domain_part_id, value_data, value_type)
                    VALUES (%d, %d, %d, '%s', '%s')"
                    instance-id morphism-id domain-id value type)]
    (query db-path sql)))

;; Feature tracking
(defn track-mcp-feature [db-path name schema-id source-repo impl-path]
  (let [sql (format "INSERT INTO mcp_features 
                    (name, schema_id, source_repo, implementation_path)
                    VALUES ('%s', %d, '%s', '%s')"
                    name schema-id source-repo impl-path)]
    (query db-path sql)))

(defn add-feature-relationship [db-path source-id target-id rel-type metadata]
  (let [sql (format "INSERT INTO feature_relationships
                    (source_feature_id, target_feature_id, relationship_type, metadata)
                    VALUES (%d, %d, '%s', '%s')"
                    source-id target-id rel-type
                    (json/generate-string metadata))]
    (query db-path sql)))

;; Visualization
(defn store-mermaid [db-path schema-id instance-id content]
  (let [sql (format "INSERT INTO mermaid_diagrams
                    (schema_id, instance_id, content)
                    VALUES (%d, %d, '%s')"
                    schema-id instance-id content)]
    (query db-path sql)))

;; Query helpers
(defn get-schema-objects [db-path schema-id]
  (query db-path 
    (format "SELECT * FROM schema_objects WHERE schema_id = %d" schema-id)))

(defn get-schema-morphisms [db-path schema-id]
  (query db-path
    (format "SELECT * FROM schema_morphisms WHERE schema_id = %d" schema-id)))

(defn get-instance-parts [db-path instance-id]
  (query db-path
    (format "SELECT * FROM instance_parts WHERE instance_id = %d" instance-id)))

(defn get-morphism-assignments [db-path instance-id]
  (query db-path
    (format "SELECT * FROM morphism_assignments WHERE instance_id = %d" instance-id)))

(defn -main [& args]
  (let [db-path (or (first args) ".topos/topos.db")]
    (init-db db-path)
    (println "DuckDB initialized at" db-path)))

(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
