/*
 * Flex: A Scheme in Flix
 * Main entry point and REPL with TUI effects
 */

/// Core data types
enum LispVal {
    case Atom(String),
    case List(List[LispVal]),
    case DottedList(List[LispVal], LispVal),
    case Number(Int32),
    case String(String),
    case Bool(Bool),
    case PrimitiveFn(List[LispVal] -> Result[String, LispVal]),
    case Closure(List[String], LispVal, Map[String, LispVal])
}

/// Main entry point
def main(): Unit \ IO = {
    let startup = 
        clear() `Free.flatMap` (_ ->
        drawLogo() `Free.flatMap` (_ ->
        withColor(cyan,
            box(40, 3,
                println("Flex v0.1.0") `Free.flatMap` (_ ->
                println("Ճկուն Լիսպ (Flexible Lisp)") `Free.flatMap` (_ ->
                println("----------------------------")))))));
    
    let repl = ((Omega Omega) (lambda (loop) (lambda (env)
        print("> ") `Free.flatMap` (_ ->
        readLine() `Free.flatMap` (input ->
        if input == "quit" or input == "(quit)" then
            withColor(yellow, println("Ցտեսություն! (Goodbye!)"))
        else
            match parseExpr(input) {
                case Ok((expr, _)) => 
                    match eval(env, expr) {
                        case Ok(result) => 
                            withColor(green, println("=> ${showVal(result)}")) `Free.flatMap` (_ ->
                            loop(env))
                        case Err(e) => 
                            withColor(red, println("Error: ${e}")) `Free.flatMap` (_ ->
                            loop(env))
                    }
                case Err(e) => 
                    withColor(red, println("Parse error: ${e}")) `Free.flatMap` (_ ->
                    loop(env))
            })))));

    // Run the TUI program
    let program = startup `Free.flatMap` (_ -> repl(initEnv()));
    Free.run(handleTui, program)
}

/// Show implementation for LispVal
def showVal(val: LispVal): String = match val {
    case LispVal.String(s) => "\"${s}\""
    case LispVal.Atom(name) => name
    case LispVal.Number(n) => Int32.toString(n)
    case LispVal.Bool(true) => "#t"
    case LispVal.Bool(false) => "#f"
    case LispVal.List(elems) => "(${String.join(" ", List.map(showVal, elems))})"
    case LispVal.DottedList(head, tail) => 
        "(${String.join(" ", List.map(showVal, head))} . ${showVal(tail)})"
    case LispVal.PrimitiveFn(_) => "<primitive>"
    case LispVal.Closure(params, _, _) => "<closure: (${String.join(" ", params)})>"
}

/// Main evaluation function with effect tracking
def eval(env: Map[String, LispVal], val: LispVal): Result[String, LispVal] \ IO = 
    match val {
        case LispVal.String(_) => Ok(val)
        case LispVal.Number(_) => Ok(val)
        case LispVal.Bool(_) => Ok(val)
        case LispVal.List(Nil) => Ok(val)
        case LispVal.List(x :: xs) => evalList(env, x, xs)
        case LispVal.Atom(id) => lookupVar(env, id)
        case LispVal.DottedList(_, _) => Err("Cannot evaluate dotted list")
        case LispVal.PrimitiveFn(_) => Ok(val)
        case LispVal.Closure(_, _, _) => Ok(val)
    }

/// Helper for evaluating lists
def evalList(env: Map[String, LispVal], first: LispVal, rest: List[LispVal]): Result[String, LispVal] \ IO =
    match first {
        case LispVal.Atom("quote") => 
            if List.length(rest) != 1 then
                Err("quote requires exactly one argument")
            else
                Ok(List.head(rest))
        case LispVal.Atom("define") => evalDefine(env, rest)
        case LispVal.Atom("lambda") => evalLambda(env, rest)
        case LispVal.Atom("if") => evalIf(env, rest)
        case _ => {
            match eval(env, first) {
                case Ok(fn) => {
                    let args = List.map(arg -> eval(env, arg), rest);
                    match sequence(args) {
                        case Ok(evaledArgs) => apply(fn, evaledArgs)
                        case Err(e) => Err(e)
                    }
                }
                case Err(e) => Err(e)
            }
        }
    }

/// Armenian note:
/// Ճկուն ծրագրավորումը սկսվում է այստեղից
/// (Flexible programming starts here)
