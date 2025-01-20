/*
 * Primitive operations for our Scheme implementation
 */

/// Primitive function type
type alias PrimitiveFn = List[LispVal] -> Result[String, LispVal]

/// Numeric operations
def numericBinop(op: (Int32, Int32) -> Int32): PrimitiveFn = args -> 
    match args {
        case Nil => Err("At least one argument required")
        case x :: xs => {
            let nums = List.map(unpackNum, x :: xs);
            match sequence(nums) {
                case Ok(ns) => Ok(LispVal.Number(List.foldLeft(op, List.head(ns), List.tail(ns))))
                case Err(e) => Err(e)
            }
        }
    }

/// Unpack a number from LispVal
def unpackNum(val: LispVal): Result[String, Int32] = match val {
    case LispVal.Number(n) => Ok(n)
    case _ => Err("Expected number")
}

/// Primitive operations map
def primitives: Map[String, PrimitiveFn] = 
    Map#{
        "+" => numericBinop((x, y) -> x + y),
        "-" => numericBinop((x, y) -> x - y),
        "*" => numericBinop((x, y) -> x * y),
        "/" => numericBinop((x, y) -> x / y),
        "mod" => numericBinop((x, y) -> x % y),
        "quotient" => numericBinop((x, y) -> x / y),
        "remainder" => numericBinop((x, y) -> x % y)
    }

/// Apply a primitive function
def applyPrimitive(name: String, args: List[LispVal]): Result[String, LispVal] =
    match Map.get(name, primitives) {
        case None => Err("Not a primitive function: ${name}")
        case Some(fn) => fn(args)
    }

/// Helper for sequencing Results
def sequence(xs: List[Result[e, a]]): Result[e, List[a]] = match xs {
    case Nil => Ok(Nil)
    case x :: rest => 
        match x {
            case Ok(v) => 
                match sequence(rest) {
                    case Ok(vs) => Ok(v :: vs)
                    case Err(e) => Err(e)
                }
            case Err(e) => Err(e)
        }
}

/// Type predicates
def isPair(val: LispVal): Bool = match val {
    case LispVal.List(_ :: _) => true
    case LispVal.DottedList(_, _) => true
    case _ => false
}

def isList(val: LispVal): Bool = match val {
    case LispVal.List(_) => true
    case _ => false
}

def isSymbol(val: LispVal): Bool = match val {
    case LispVal.Atom(_) => true
    case _ => false
}

/// List operations
def car(args: List[LispVal]): Result[String, LispVal] = match args {
    case LispVal.List(x :: _) :: Nil => Ok(x)
    case LispVal.DottedList(x :: _, _) :: Nil => Ok(x)
    case _ :: Nil => Err("car: Expected list")
    case _ => Err("car: Expected exactly one argument")
}

def cdr(args: List[LispVal]): Result[String, LispVal] = match args {
    case LispVal.List(_ :: xs) :: Nil => Ok(LispVal.List(xs))
    case LispVal.DottedList(_ :: xs, x) :: Nil => 
        if List.isEmpty(xs) then Ok(x)
        else Ok(LispVal.DottedList(xs, x))
    case _ :: Nil => Err("cdr: Expected list")
    case _ => Err("cdr: Expected exactly one argument")
}

def cons(args: List[LispVal]): Result[String, LispVal] = match args {
    case x :: LispVal.List(xs) :: Nil => Ok(LispVal.List(x :: xs))
    case x :: LispVal.DottedList(xs, xlast) :: Nil => 
        Ok(LispVal.DottedList(x :: xs, xlast))
    case x :: y :: Nil => Ok(LispVal.DottedList(x :: Nil, y))
    case _ => Err("cons: Expected two arguments")
}
