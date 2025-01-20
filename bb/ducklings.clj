(ns ducklings
  (:require [clojure.string :as str]))

(def ducklings
  [\"Python\"
   \"Janet\"
   \"Racket\"
   \"Clojure\"
   \"Datalog\"])

(defn pick-duckling []
  (rand-nth ducklings))

(defn -main [& _args]
  (let [chosen (pick-duckling)]
    (println \"Flipping a coin and your random duckling is:\" chosen)))
