#!/usr/bin/env hy

(import textual.app)
(import textual.containers)
(import textual.widgets)
(import textual.reactive)
(import textual.binding)
(import numpy)
(import sympy)
(import rich.text)
(import functools)

(setv App textual.app.App)
(setv Grid textual.containers.Grid)
(setv Container textual.containers.Container)
(setv Header textual.widgets.Header)
(setv Footer textual.widgets.Footer)
(setv Static textual.widgets.Static)
(setv Button textual.widgets.Button)
(setv reactive textual.reactive.reactive)
(setv Binding textual.binding.Binding)
(setv np numpy)
(setv sp sympy)
(setv Text rich.text.Text)
(setv partial functools.partial)

;; Automorphic form calculations
(defn calculate-automorphic-form [z k]
  "Calculate automorphic form value at point z with weight k"
  (let [q (sp.exp (* 2 sp.pi sp.I z))
        series (sum (lfor n (range 1 11)
                         (* (** q n) 
                            (/ 1 (** n k)))))]
    series))

;; Tile widget for automorphic form visualization
(defclass AutoFormTile [Static]
  (setv value (reactive 0))
  (setv x (reactive 0))
  (setv y (reactive 0))
  
  (defn __init__ [self #* args #** kwargs]
    (.__init__ (super))
    (setv self.x (get kwargs "x" 0))
    (setv self.y (get kwargs "y" 0)))
  
  (defn compute-value [self]
    "Compute automorphic form value for current position"
    (let [x (/ self.x 10)
          y (/ self.y 10)
          z (complex x y)]
      (abs (calculate-automorphic-form z 4))))
  
  (defn on-mount [self]
    (setv self.value (self.compute-value)))
  
  (defn watch-value [self old-value new-value]
    "Update display when value changes"
    (let [intensity (min (int (* (/ new-value 10) 255)) 255)
          hex-val (.format "{:02x}" intensity)
          color (+ "#" hex-val hex-val hex-val)]
      (setv self.styles.background color))))

;; Main application
(defclass ToposTUI [App]
  ;; CSS styles
  (setv CSS (+ "Grid {"
               "    grid-size: 10 10;"
               "    grid-gutter: 1;"
               "    padding: 1;"
               "}"
               "AutoFormTile {"
               "    width: 100%;"
               "    height: 100%;"
               "    content-align: center middle;"
               "}"
               "Header {"
               "    dock: top;"
               "    background: $boost;"
               "    color: $text;"
               "    text-align: center;"
               "    text-style: bold;"
               "}"
               "Footer {"
               "    dock: bottom;"
               "    background: $boost;"
               "    color: $text;"
               "}"))
  
  ;; Key bindings
  (setv BINDINGS 
    (list [(Binding "q" "quit" "Quit")
           (Binding "r" "refresh" "Refresh")
           (Binding "space" "toggle_animation" "Toggle Animation")]))
  
  (defn compose [self]
    "Compose the interface"
    (setv header (Header))
    (setv header.tall False)
    (setv header.title "Topos MCP - Automorphic Form Visualization")
    (yield header)
    
    (setv grid (Grid))
    (for [x (range 10)
          y (range 10)]
      (setv tile (AutoFormTile #** {"x" x "y" y}))
      (setv tile.id (+ "tile-" (str x) "-" (str y)))
      (.mount grid tile))
    (yield grid)
    
    (setv footer (Footer))
    (yield footer))
  
  (defn on-mount [self]
    "Initialize animation state"
    (setv self.animating False))
  
  (defn action-toggle-animation [self]
    "Toggle animation state"
    (setv self.animating (not self.animating))
    (when self.animating
      (self.animate)))
  
  (defn animate [self]
    "Animate tiles"
    (when self.animating
      (for [x (range 10)
            y (range 10)]
        (let [tile (self.query-one f"#tile-{x}-{y}")
              t (/ (.time self) 1000)
              phase (* (+ x y) (/ sp.pi 5))
              value (* (np.sin (+ t phase)) 0.5 0.5)]
          (setv tile.value value)))
      (.call-later self 0.05 self.animate)))
  
  (defn action-refresh [self]
    "Refresh all tiles"
    (for [x (range 10)
          y (range 10)]
      (let [tile (self.query-one f"#tile-{x}-{y}")]
        (setv tile.value (tile.compute-value)))))
  
  (defn action-quit [self]
    "Clean up and quit"
    (.exit self)))

;; Entry point
(defn main []
  (let [app (ToposTUI)]
    (.run app)))

(when (= __name__ "__main__")
  (main))
