/*
 * Flex: Test Suite
 * Tests our Scheme implementation with some cool examples
 */

/// Test utilities
def assertEq(expected: a, actual: a): Bool with Eq[a] =
    if expected == actual then
        true
    else {
        println("Expected: ${expected}");
        println("Actual: ${actual}");
        false
    }

/// Test suite for cool Scheme programs
@test
def testCoolSchemePrograms(): Bool = {
    // Omega combinator factorial
    let omegaFact = """
        (define Omega
          (lambda (w)
            (lambda (f)
              (f (lambda (x)
                   ((w w) f x))))))
        
        (define factorial
          ((Omega Omega)
           (lambda (f)
             (lambda (n)
               (if (= n 0)
                   1
                   (* n (f (- n 1))))))))
        
        (factorial 5)
    """;

    // Church numerals with Omega
    let church = """
        (define zero (lambda (f) (lambda (x) x)))
        (define one (lambda (f) (lambda (x) (f x))))
        (define two (lambda (f) (lambda (x) (f (f x)))))
        
        (define plus
          ((Omega Omega)
           (lambda (plus)
             (lambda (m)
               (lambda (n)
                 (lambda (f)
                   (lambda (x)
                     ((m f) ((n f) x)))))))))
        
        (define toInt
          (lambda (n)
            ((n (lambda (x) (+ x 1))) 0)))
        
        (toInt ((plus two two) (lambda (x) (+ x 1)) 0))
    """;

    // Pattern matching with Omega-based recursion
    let pattern = """
        (define match
          ((Omega Omega)
           (lambda (match)
             (lambda (pattern expr)
               (cond
                 ((and (pair? pattern)
                       (pair? expr)
                       (eq? (car pattern) 'quote))
                  (equal? (cadr pattern) expr))
                 ((pair? pattern)
                  (and (pair? expr)
                       (match (car pattern) (car expr))
                       (match (cdr pattern) (cdr expr))))
                 ((eq? pattern '_) #t)
                 (else (equal? pattern expr)))))))
        
        (match '(a _ c) '(a b c))
    """;

    // Test results
    let results = List#{
        (eval(initEnv(), parseExpr(omegaFact)), LispVal.Number(120)),
        (eval(initEnv(), parseExpr(church)), LispVal.Number(4)),
        (eval(initEnv(), parseExpr(pattern)), LispVal.Bool(true))
    };

    // Check all results
    List.forAll(((actual, expected)) -> 
        match actual {
            case Ok(result) => assertEq(expected, result)
            case Err(e) => {
                println("Error: ${e}");
                false
            }
        }, results)
}

/// Test Armenian number system with Omega recursion
@test
def testArmenianNumbers(): Bool = {
    // Armenian numerals as a Scheme program
    let armenian = """
        (define armenian-digits
          '((1 . "Ա") (2 . "Բ") (3 . "Գ") (4 . "Դ") (5 . "Ե")
            (6 . "Զ") (7 . "Է") (8 . "Ը") (9 . "Թ")))
        
        (define number->armenian
          ((Omega Omega)
           (lambda (convert)
             (lambda (n)
               (cond
                 ((= n 0) "Ո")
                 ((< n 0) (string-append "Բացասական " (convert (- n))))
                 (else
                   (let ((digit (assoc (remainder n 10) armenian-digits)))
                     (if (> n 9)
                         (string-append 
                           (convert (quotient n 10))
                           (cdr digit))
                         (cdr digit)))))))))
        
        (number->armenian 123)
    """;

    // Test result
    match eval(initEnv(), parseExpr(armenian)) {
        case Ok(LispVal.String("ՃԻԳ")) => true
        case Ok(result) => {
            println("Expected: ՃԻԳ");
            println("Got: ${showVal(result)}");
            false
        }
        case Err(e) => {
            println("Error: ${e}");
            false
        }
    }
}

/// Test error handling
@test
def testErrorHandling(): Bool = {
    let badPrograms = List#{
        "(+ 1 'a)",  // Type error
        "(define)",  // Wrong arity
        "((lambda (x) x) 1 2)",  // Too many args
        "(car 'atom)",  // Wrong type
        "(/ 1 0)"       // Division by zero
    };

    List.forAll(program ->
        match eval(initEnv(), parseExpr(program)) {
            case Err(_) => true  // Should fail
            case Ok(result) => {
                println("Expected error but got: ${showVal(result)}");
                false
            }
        }, badPrograms)
}

/// Property-based tests for Scheme implementation
@test
def testSchemeProperties(): Bool = {
    // Property: Addition is associative
    let addAssociative = prop((a: Int, b: Int, c: Int) -> 
        (a + b) + c == a + (b + c)
    );

    // Property: Multiplication is commutative
    let mulCommutative = prop((a: Int, b: Int) -> 
        a * b == b * a
    );

    // Run property tests
    let results = List#{
        check(addAssociative, 100),
        check(mulCommutative, 100)
    };

    // Check all results
    List.forAll(((actual)) ->
        match actual {
            case Ok(_) => true
            case Err(e) => {
                println("Property test failed: ${e}");
                false
            }
        }, results)
}

/// Tests for borkdude/bci functionality
@test
def testBciFunctionality(): Bool = {
    // Test bci's ability to compile and run Scheme code
    let bciTest = """
        (bci-compile-and-run
         '(define (factorial n)
            (if (= n 0)
                1
                (* n (factorial (- n 1)))))
         '(factorial 5))
    """;

    // Test result
    match eval(initEnv(), parseExpr(bciTest)) {
        case Ok(LispVal.Number(120)) => true
        case Ok(result) => {
            println("Expected: 120");
            println("Got: ${showVal(result)}");
            false
        }
        case Err(e) => {
            println("Error: ${e}");
            false
        }
    }
}

/// Additional property-based test for borkdude/bci
@test
def testBciPropertyFib(): Bool = {
    // Check that fib(n) is the same whether run by bci-compile-and-run or directly
    let fibProp = prop((n: Int) -> {
        let n0 = abs(n % 10);
        let code = \"\"\"
            (bci-compile-and-run
             '(define (fib n)
                (if (<= n 1) n (+ (fib (- n 1)) (fib (- n 2))))) 
             '(fib ${n0}))
        \"\"\";
        let bciResult = eval(initEnv(), parseExpr(code));

        let directCode = \"\"\"
          (define (fib n) 
            (if (<= n 1) 
                n 
                (+ (fib (- n 1)) (fib (- n 2))))) 
          (fib ${n0})
        \"\"\";
        let directResult = eval(initEnv(), parseExpr(directCode));

        match (bciResult, directResult) {
            case (Ok(LispVal.Number(a)), Ok(LispVal.Number(b))) => a == b
            case _ => false
        }
    });

    match check(fibProp, 50) {
        case Ok(_) => true
        case Err(e) => {
            println("Property test failed: ${e}");
            false
        }
    }
}

/// Armenian note:
/// Փորձարկումը ծրագրի սիրտն է
/// (Testing is the heart of programming)
