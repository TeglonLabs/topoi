# Write Ourselves a Scheme in 3 Hours (Flix Edition)

Following the 2-3-5-7 rule for section timing (in minutes):

## Hour 1: Foundations (2+3+5+7 = 17min)

### Parser Basics (2min)
```flix
def tokenize(input: String): List[String] = 
    // Flix's pattern matching makes this cleaner than Haskell
    input |> String.split(" ") |> List.filter(x -> x != "")
```

### AST Definition (3min)
```flix
enum LispVal {
    case Atom(String)
    case List(List[LispVal])
    case Number(Int32)
    case String(String)
    case Bool(Bool)
}
```

### Basic Evaluation (5min)
```flix
def eval(env: Map[String, LispVal], expr: LispVal): Result[String, LispVal] = 
    match expr {
        case LispVal.Number(n) => Ok(expr)
        case LispVal.String(s) => Ok(expr)
        case LispVal.Bool(b) => Ok(expr)
        case LispVal.List(Nil) => Ok(expr)
        case _ => Err("Unimplemented")
    }
```

### Environment Setup (7min)
```flix
def primitives: Map[String, LispVal] = 
    Map#{"+" => LispVal.PrimitiveFn(add),
         "-" => LispVal.PrimitiveFn(subtract)}
```

## Hour 2: Core Features (2+3+5+7 = 17min)

### Special Forms (2min)
```flix
def evalSpecialForm(form: String, args: List[LispVal], env: Map[String, LispVal]): Result[String, LispVal] =
    match form {
        case "define" => evalDefine(args, env)
        case "lambda" => evalLambda(args, env)
        case _ => Err("Unknown special form")
    }
```

### Function Application (3min)
```flix
def apply(fn: LispVal, args: List[LispVal]): Result[String, LispVal] =
    match fn {
        case LispVal.PrimitiveFn(f) => f(args)
        case LispVal.Closure(params, body, env) => 
            evalClosure(params, body, env, args)
        case _ => Err("Not a function")
    }
```

### Error Handling (5min)
```flix
enum LispError {
    case Syntax(String)
    case UnboundVar(String)
    case BadSpecialForm(String)
    case NotFunction(String)
    case NumArgs(Int32, List[LispVal])
}
```

### REPL Foundation (7min)
```flix
def repl(env: Map[String, LispVal]): Unit = 
    // Flix's IO monad makes this cleaner
    println("> ");
    let input = readLine();
    match parse(input) {
        case Ok(expr) => 
            match eval(env, expr) {
                case Ok(result) => println(show(result))
                case Err(e) => println("Error: ${e}")
            }
        case Err(e) => println("Parse error: ${e}")
    };
    repl(env)
```

## Hour 3: Extensions (2+3+5+7 = 17min)

### Standard Library (2min)
```flix
def stdLib: String = """
    (define map
        (lambda (f lst)
            (if (null? lst)
                '()
                (cons (f (car lst))
                      (map f (cdr lst))))))
"""
```

### Type System Integration (3min)
```flix
def typeOf(val: LispVal): Type = 
    // Leverage Flix's type system
    match val {
        case LispVal.Number(_) => Type.Number
        case LispVal.String(_) => Type.String
        case LispVal.List(_) => Type.List
        case _ => Type.Any
    }
```

### Pattern Matching (5min)
```flix
def matchPattern(pattern: LispVal, value: LispVal): Option[Map[String, LispVal]] =
    match (pattern, value) {
        case (LispVal.Atom(x), v) => Some(Map#{x => v})
        case (LispVal.List(ps), LispVal.List(vs)) if length(ps) == length(vs) =>
            zipWithMatch(ps, vs)
        case _ => None
    }
```

### Meta Programming (7min)
```flix
def quasiquote(expr: LispVal): Result[String, LispVal] =
    match expr {
        case LispVal.List(LispVal.Atom("unquote") :: rest) => 
            eval(env, List.head(rest))
        case LispVal.List(xs) =>
            xs |> List.map(quasiquote) |> sequence >>= (ys -> Ok(LispVal.List(ys)))
        case _ => Ok(expr)
    }
```

## Armenian Note
Երեք ժամում Լիսպ՝ Flix-ով
(A Lisp in three hours with Flix)

## Advantages Over Haskell Version
1. Effect system makes IO cleaner
2. Pattern matching more ergonomic
3. Built-in immutable maps
4. Gradual typing helps prototyping

## Limitations
1. JVM startup time
2. Less mature ecosystem
3. Smaller community
4. Documentation gaps

The 2-3-5-7 rule helped maintain focus while exploring Flix's suitability for this task.
