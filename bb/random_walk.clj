#!/usr/bin/env bb

(ns random-walk
  (:require [babashka.fs :as fs]
            [clojure.string :as str]
            [cheshire.core :as json]
            [sci.core :as sci]))

;; Scheme expressions for random walking
(def scheme-expressions
  ["(define (fact n) (if (= n 0) 1 (* n (fact (- n 1)))))"
   "(define (fib n) (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2)))))"
   "(map (lambda (x) (* x x)) '(1 2 3 4 5))"
   "(define compose (lambda (f g) (lambda (x) (f (g x)))))"
   "(define (curry f x) (lambda (y) (f x y)))"
   "(define (flip f) (lambda (x y) (f y x)))"
   "(define (Y f) ((lambda (x) (f (lambda (y) ((x x) y)))) (lambda (x) (f (lambda (y) ((x x) y)))))"])

;; Armenian programming concepts
(def concepts
  ["Ճկուն ծրագրավորում" ; Flexible programming
   "Ֆունկցիոնալ մտածելակերպ" ; Functional mindset
   "Վերացական մտածողություն" ; Abstract thinking
   "Ռեկուրսիվ լուծումներ" ; Recursive solutions
   "Մաքուր ֆունկցիաներ" ; Pure functions
   "Անփոփոխ տվյալներ" ; Immutable data
   "Բարձր կարգի ֆունկցիաներ"]) ; Higher-order functions

;; Random walk through concepts
(defn random-walk []
  (println "\n🌀 Random Walk through Flex Concepts")
  (println "------------------------------------")
  
  ;; Pick a random concept
  (let [concept (rand-nth concepts)]
    (println (format "Concept: %s" concept)))
  
  ;; Show a random Scheme expression
  (let [expr (rand-nth scheme-expressions)]
    (println "\nScheme Expression:")
    (println expr))
  
  ;; Generate a random tensor position
  (let [pos [(rand-int 3) (rand-int 3) (rand-int 3)]]
    (println "\nTensor Position:" pos))
  
  ;; Show some Armenian wisdom
  (println "\nArmenian Programming Wisdom:")
  (println "Ծրագրավորումը արվեստ է, ոչ թե գիտություն")
  (println "(Programming is an art, not just a science)"))

;; Main entry point
(defn -main [& args]
  (println "\nFlex: A Scheme in Flix")
  (println "Ճկուն Լիսպ (Flexible Lisp)")
  (println "-------------------------")
  (random-walk)
  (println "\nՀաջողություն (Success)!"))

;; Run if executed directly
(when (= *file* (System/getProperty "babashka.file"))
  (-main))
