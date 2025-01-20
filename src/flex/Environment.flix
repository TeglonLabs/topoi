/*
 * Environment handling for Flix Scheme
 */

/// Environment type
type alias Env = Map[String, LispVal]

/// Create initial environment with primitives
def initEnv(): Env = 
    let primitiveFns = 
        Map#{
            "car" => LispVal.PrimitiveFn(car),
            "cdr" => LispVal.PrimitiveFn(cdr),
            "cons" => LispVal.PrimitiveFn(cons)
        };
    Map.union(primitiveFns, primitives)

/// Bind a value in the environment
def bind(name: String, val: LispVal, env: Env): Env =
    Map.insert(name, val, env)

/// Define multiple bindings at once
def defineMany(bindings: List[(String, LispVal)], env: Env): Env =
    List.foldLeft((acc, (name, val)) -> bind(name, val, acc), env, bindings)

/// Look up a value in the environment
def lookupVar(name: String, env: Env): Result[String, LispVal] =
    match Map.get(name, env) {
        case None => Err("Unbound variable: ${name}")
        case Some(val) => Ok(val)
    }

/// Create a new scope with given bindings
def makeScope(bindings: List[(String, LispVal)], env: Env): Env =
    defineMany(bindings, env)

/// Helper for creating function closures
def makeClosure(params: List[String], body: LispVal, env: Env): LispVal =
    LispVal.Closure(params, body, env)

/// Evaluate in a new scope
def evalInScope(expr: LispVal, bindings: List[(String, LispVal)], env: Env): Result[String, LispVal] =
    eval(makeScope(bindings, env), expr)

/// Armenian note:
/// Միջավայրը մեր ծրագրի հիշողությունն է
/// (The environment is our program's memory)
