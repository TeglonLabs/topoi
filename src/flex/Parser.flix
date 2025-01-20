/*
 * Flex: Parser implementation
 * Handles parsing of Scheme expressions with Flix's pattern matching
 */

/// Parser type alias
type alias Parser[a] = String -> Result[String, (a, String)]

/// Basic string utilities
def symbol(x: Char): Bool = 
    Char.isLetter(x) or 
    List.memberOf(x, ['!', '$', '%', '&', '*', '+', '-', '/', ':', '<', '=', '>', '?', '@', '^', '_', '~'])

/// Skip whitespace
def spaces(input: String): Result[String, (Unit, String)] = 
    Ok(((), String.trimLeft(input)))

/// Parse a string literal
def parseString: Parser[LispVal] = input -> {
    if String.isEmpty(input) then 
        Err("Empty input")
    else match String.charAt(0, input) {
        case '"' => 
            let rest = String.slice(1, String.length(input), input);
            let endQuote = String.indexOf("\"", rest);
            if endQuote == -1 then
                Err("No matching quote")
            else
                let str = String.slice(0, endQuote, rest);
                let remaining = String.slice(endQuote + 1, String.length(rest), rest);
                Ok((LispVal.String(str), remaining))
        case _ => Err("String must start with quote")
    }
}

/// Parse an atom
def parseAtom: Parser[LispVal] = input -> {
    let first = String.takeWhile(c -> symbol(c) or Char.isDigit(c), input);
    let rest = String.dropWhile(c -> symbol(c) or Char.isDigit(c), input);
    if String.isEmpty(first) then
        Err("Invalid atom")
    else match first {
        case "#t" => Ok((LispVal.Bool(true), rest))
        case "#f" => Ok((LispVal.Bool(false), rest))
        case atom => {
            let maybeNum = Int32.parse(atom);
            match maybeNum {
                case Some(n) => Ok((LispVal.Number(n), rest))
                case None => Ok((LispVal.Atom(atom), rest))
            }
        }
    }
}

/// Parse a list
def parseList: Parser[LispVal] = input -> {
    if String.isEmpty(input) then 
        Err("Empty input")
    else match String.charAt(0, input) {
        case '(' => {
            let rest = String.slice(1, String.length(input), input);
            parseListElements(rest, Nil)
        }
        case _ => Err("List must start with (")
    }
}

/// Helper to parse list elements
def parseListElements(input: String, acc: List[LispVal]): Result[String, (LispVal, String)] = {
    match spaces(input) {
        case Ok((_, trimmed)) => 
            if String.isEmpty(trimmed) then
                Err("Unclosed list")
            else match String.charAt(0, trimmed) {
                case ')' => 
                    Ok((LispVal.List(List.reverse(acc)), 
                       String.slice(1, String.length(trimmed), trimmed)))
                case '.' => 
                    parseDottedList(String.slice(1, String.length(trimmed), trimmed), acc)
                case _ => 
                    match parseExpr(trimmed) {
                        case Ok((expr, rest)) => 
                            parseListElements(rest, expr :: acc)
                        case Err(e) => Err(e)
                    }
            }
        case Err(e) => Err(e)
    }
}

/// Parse a dotted list
def parseDottedList(input: String, acc: List[LispVal]): Result[String, (LispVal, String)] = {
    match parseExpr(input) {
        case Ok((expr, rest)) => 
            match spaces(rest) {
                case Ok((_, trimmed)) =>
                    if String.isEmpty(trimmed) then
                        Err("Unclosed dotted list")
                    else match String.charAt(0, trimmed) {
                        case ')' => 
                            Ok((LispVal.DottedList(List.reverse(acc), expr),
                               String.slice(1, String.length(trimmed), trimmed)))
                        case _ => Err("Expected )")
                    }
                case Err(e) => Err(e)
            }
        case Err(e) => Err(e)
    }
}

/// Main expression parser
def parseExpr: Parser[LispVal] = input -> {
    match spaces(input) {
        case Ok((_, trimmed)) =>
            if String.isEmpty(trimmed) then
                Err("Empty expression")
            else match String.charAt(0, trimmed) {
                case '"' => parseString(trimmed)
                case '(' => parseList(trimmed)
                case '\'' => parseQuoted(trimmed)
                case _ => parseAtom(trimmed)
            }
        case Err(e) => Err(e)
    }
}

/// Parse quoted expressions
def parseQuoted: Parser[LispVal] = input -> {
    match parseExpr(String.slice(1, String.length(input), input)) {
        case Ok((expr, rest)) => 
            Ok((LispVal.List(LispVal.Atom("quote") :: expr :: Nil), rest))
        case Err(e) => Err(e)
    }
}

/// Armenian note:
/// Վերլուծությունը արվեստ է
/// (Parsing is an art)
