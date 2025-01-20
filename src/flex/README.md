# Flex: A Scheme in Flix

Flex is a Scheme implementation written in Flix, combining the elegance of Scheme with Flix's modern type system and effect tracking. Created in 3 hours as a reimagining of "Write Yourself a Scheme in 48 Hours".

## Features

- 🎯 Pure functional core with effect tracking
- 🧬 Pattern matching for elegant syntax handling
- 🔄 Immutable data structures by default
- 🌈 Armenian-inspired error messages
- 🚀 JVM-powered performance

## Quick Start

```bash
# Build Flex
cd src/flex
flix build.flix

# Run the REPL
java -jar flex.jar
```

## Example Session

```scheme
Flex v0.1.0
Ճկուն Լիսպ (Flexible Lisp)
> (define factorial
    (lambda (n)
      (if (= n 0)
          1
          (* n (factorial (- n 1))))))
=> factorial

> (factorial 5)
=> 120

> (map (lambda (x) (* x x)) '(1 2 3 4 5))
=> (1 4 9 16 25)
```

## Implementation Notes

1. Parser (2min)
   - Flix pattern matching for tokens
   - Recursive descent parsing

2. Core Types (3min)
   - LispVal with effect tracking
   - Environment handling

3. Evaluator (5min)
   - Pattern-based evaluation
   - Pure functional core

4. Standard Library (7min)
   - Core Scheme primitives
   - List operations

## Why Flex?

- **Effect System**: Track side effects explicitly
- **Pattern Matching**: More elegant than Haskell's case expressions
- **JVM Integration**: Access to Java ecosystem
- **Modern Types**: Gradual typing for rapid development

## Armenian Connection

The name "Flex" connects to the Armenian word "Ճկուն" (tchkun), meaning flexible or adaptable. This reflects both Scheme's minimalist flexibility and Flix's adaptable type system.

## Build System

```bash
# Development build
flix build.flix

# Run tests
flix test.flix

# Create JAR
flix package.flix
```

## Contributing

Areas for exploration:
1. Macro system implementation
2. Tail call optimization
3. Additional type system integration
4. REPL improvements

## License

MIT

---

*"Ճկուն միտքը ծրագրավորման արվեստն է"*
(Flexible thinking is the art of programming)
