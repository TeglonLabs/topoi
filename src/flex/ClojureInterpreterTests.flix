// Test cases for Clojure Interpreter in Flix

import ClojureInterpreter

def testParseNumber(): Unit = {
    let input = "42"
    let expected = ClojureAst.Number(42)
    let result = ClojureInterpreter.parseClojure(input)
    assert result == expected
}

def testParseSymbol(): Unit = {
    let input = "foo"
    let expected = ClojureAst.Symbol("foo")
    let result = ClojureInterpreter.parseClojure(input)
    assert result == expected
}

def testParseString(): Unit = {
    let input = "\"bar\""
    let expected = ClojureAst.Symbol("bar")
    let result = ClojureInterpreter.parseClojure(input)
    assert result == expected
}

def testParseList(): Unit = {
    let input = "(+ 1 2)"
    let expected = ClojureAst.List(List(
        ClojureAst.Symbol("+"),
        ClojureAst.Number(1),
        ClojureAst.Number(2)
    ))
    let result = ClojureInterpreter.parseClojure(input)
    assert result == expected
}

def testEvalNumber(): Unit = {
    let input = ClojureAst.Number(42)
    let expected = ClojureAst.Number(42)
    let result = ClojureInterpreter.evalClojure(input)
    assert result == expected
}

def testEvalSymbol(): Unit = {
    let input = ClojureAst.Symbol("foo")
    let expected = ClojureAst.Symbol("foo")
    let result = ClojureInterpreter.evalClojure(input)
    assert result == expected
}

def testEvalPrintln(): Unit = {
    let input = ClojureAst.List(List(
        ClojureAst.Symbol("println"),
        ClojureAst.Symbol("Hello, Clojure!")
    ))
    let expected = ClojureAst.List(List())
    let result = ClojureInterpreter.evalClojure(input)
    assert result == expected
}

def main(): Unit = {
    testParseNumber()
    testParseSymbol()
    testParseString()
    testParseList()
    testEvalNumber()
    testEvalSymbol()
    testEvalPrintln()
    println("All tests passed successfully!")
}
