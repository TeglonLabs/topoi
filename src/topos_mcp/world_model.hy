#!/usr/bin/env hy

(import topos_mcp.hypergraph [HyperGraph HyperEdge])
(import shapely.geometry [Point Polygon MultiPolygon])
(import discopy :as dc)
(import json)
(import datetime [datetime])

(defclass WorldModel []
  "World model using hypergraph as underlying representation"
  
  (defn __init__ [self]
    (setv self.graph (HyperGraph))
    (setv self.current-time (datetime.now))
    (setv self.observers []))
  
  (defn add-entity [self id #** attrs]
    "Add entity to world model"
    (self.graph.add-vertex id #** attrs)
    (self.notify-observers {:type "entity-added" 
                          :id id 
                          :attrs attrs}))
  
  (defn add-relation [self vertices #** attrs]
    "Add relation between entities"
    (self.graph.add-edge vertices #** attrs)
    (self.notify-observers {:type "relation-added"
                          :vertices vertices
                          :attrs attrs}))
  
  (defn spatial-query [self geom]
    "Query entities/relations in spatial region"
    (self.graph.spatial-query geom))
  
  (defn get-neighbors [self entity-id]
    "Get neighboring entities across all backends"
    (self.graph.get-neighbors entity-id))
  
  (defn add-observer [self observer]
    "Add observer function to be called on world changes"
    (.append self.observers observer))
  
  (defn notify-observers [self event]
    "Notify all observers of world change"
    (for [observer self.observers]
      (observer event)))
  
  (defn to-categorical [self]
    "Convert current world state to categorical diagram"
    (get self.graph.backends "discopy"))
  
  (defn advance-time [self delta]
    "Advance world time and update state"
    (+= self.current-time delta)
    (self.notify-observers {:type "time-advanced"
                          :new-time self.current-time})))

;; World model operations
(defn create-tile [world x y #** attrs]
  "Create a tile entity at given coordinates"
  (let [id (str f"tile-{x}-{y}")
        geom (Polygon [(Point x y)
                      (Point (+ x 1) y)
                      (Point (+ x 1) (+ y 1))
                      (Point x (+ y 1))])]
    (world.add-entity id :geometry geom #** attrs)))

(defn create-region [world vertices attrs]
  "Create a region from set of tiles"
  (let [id (str f"region-{(hash vertices)}")
        geom (MultiPolygon (lfor v vertices 
                                (get (world.spatial-query (Point v)) 0)))]
    (world.add-entity id :geometry geom #** attrs)
    (world.add-relation vertices :type "contains")))

(defn get-categorical-slice [world]
  "Get categorical representation of current world state"
  (let [diagram (world.to-categorical)]
    (dc.Box "world-state" 
            (dc.Ty) 
            (dc.Ty.tensor #* (lfor box diagram.boxes box)))))

;; Event handlers for TUI integration
(defn handle-click [world x y]
  "Handle click event in TUI"
  (let [point (Point x y)
        entities (world.spatial-query point)]
    (if entities
      (first entities)
      None)))

(defn handle-time-tick [world]
  "Handle time advancement"
  (world.advance-time (datetime.timedelta :seconds 1)))

;; Hy-Python bridge functions
(defn world->json [world]
  "Convert world state to JSON for Python"
  (json.dumps {"time" (str world.current-time)
               "entities" (lfor [id attrs] (world.graph.vertices.items)
                              {"id" id "attrs" attrs})}))

(defn json->world [data]
  "Create world from JSON data"
  (let [world (WorldModel)
        state (json.loads data)]
    (for [entity (get state "entities")]
      (world.add-entity (get entity "id") 
                       #** (get entity "attrs")))
    world))
