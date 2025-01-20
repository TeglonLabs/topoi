# S-Expression Core Loops by Runtime

```
Runtime    | Lisp Bridge      | Integration Method        | Core Loop Access
-----------|------------------|--------------------------|------------------
Babashka   | sci             | Direct embedding         | (sci/eval-string "(+ 1 2)")
Julia      | LispSyntax.jl   | Native macro system      | @lisp (+ 1 2)
Python     | hy              | Import-time transform    | (hy.eval '(+ 1 2))
Rust       | ketos           | Embedded interpreter     | eval!("(+ 1 2)")
Dart       | lisp_parser     | AST transformation      | LispMachine.eval("(+ 1 2)")
Haskell    | atto-lisp       | Parser combinators      | evalLisp "(+ 1 2)"
Guile      | native          | It is Scheme            | (eval '(+ 1 2) (interaction-environment))
Flix       | flixlisp*       | Via JVM bridge          | Lisp.eval("(+ 1 2)")
```
*Hypothetical implementation

## Core Loop Examples

### Babashka with sci
```clojure
(require '[sci.core :as sci])

(def sci-ctx (sci/init {:classes {'java.lang.Math java.lang.Math}
                        :namespaces {'clojure.core {'+ +}}}))

(defn eval-in-ctx [form]
  (sci/eval-string* sci-ctx form))

(eval-in-ctx "(+ 1 2 3)")  ; => 6
```

### Julia with LispSyntax
```julia
using LispSyntax

@lisp begin
  (defun factorial (n)
    (if (= n 0)
        1
        (* n (factorial (- n 1)))))
end

@lisp (factorial 5)  # => 120
```

### Python with hy
```python
import hy
from hy.core.language import eval_str

def run_lisp(code):
    return eval_str(code)

# In your TUI core loop:
run_lisp("""
(defn handle-input [key]
  (match key
    "q" (quit)
    "r" (refresh)
    _ (process key)))
""")
```

### Rust with ketos
```rust
use ketos::{Context, Error, Value};

fn main() -> Result<(), Error> {
    let mut ctx = Context::new();
    
    // Define TUI functions
    ctx.define_fn("draw-box", box_drawing::draw)?;
    
    // Evaluate Lisp code
    ctx.eval("(draw-box :width 10 :height 5)")?;
    Ok(())
}
```

### Guile (Native Scheme)
```scheme
(use-modules (ice-9 textual-ports))

(define (process-tui-event event)
  (eval `(handle-event ',event)
        (interaction-environment)))

;; Direct S-expression processing
(process-tui-event '(keypress "q"))
```

## Armenian Note
Լիսպը միշտ կա, նույնիսկ եթե թաքնված է
(Lisp is always there, even if hidden)

## Core Loop Integration

Each runtime can expose its TUI functionality through S-expressions:

1. Event handling:
   ```lisp
   (on-event key (λ (k) ...))
   ```

2. Drawing primitives:
   ```lisp
   (draw-box x y width height)
   ```

3. State management:
   ```lisp
   (define-state counter 0)
   (on-tick (λ () (update! counter inc)))
   ```

This provides a unified way to script TUI behavior across all runtimes while maintaining their native performance characteristics.
