/*
 * Flex: TUI Effects and Handlers
 * Captures terminal UI interactions as Flix effects
 */

/// TUI effect type
pub enum TuiEffect[a] with Eq {
    case ReadLine,
    case Print(String),
    case PrintLn(String),
    case Clear,
    case SetColor(String),
    case ResetColor,
    case MoveCursor(Int32, Int32),
    case SaveCursor,
    case RestoreCursor
}

/// TUI effect handler
pub def handleTui(e: TuiEffect[a]): a \ IO = match e {
    case TuiEffect.ReadLine => readLine()
    case TuiEffect.Print(s) => print(s)
    case TuiEffect.PrintLn(s) => println(s)
    case TuiEffect.Clear => println("\u001b[2J\u001b[H")
    case TuiEffect.SetColor(c) => print("\u001b[${c}m")
    case TuiEffect.ResetColor => print("\u001b[0m")
    case TuiEffect.MoveCursor(x, y) => print("\u001b[${y};${x}H")
    case TuiEffect.SaveCursor => print("\u001b[s")
    case TuiEffect.RestoreCursor => print("\u001b[u")
}

/// TUI monad
pub type alias Tui[a] = Free[TuiEffect, a]

/// TUI operations
pub def readLine(): Tui[String] = Free.liftF(TuiEffect.ReadLine)

pub def print(s: String): Tui[Unit] = Free.liftF(TuiEffect.Print(s))

pub def println(s: String): Tui[Unit] = Free.liftF(TuiEffect.PrintLn(s))

pub def clear(): Tui[Unit] = Free.liftF(TuiEffect.Clear)

pub def setColor(c: String): Tui[Unit] = Free.liftF(TuiEffect.SetColor(c))

pub def resetColor(): Tui[Unit] = Free.liftF(TuiEffect.ResetColor)

pub def moveCursor(x: Int32, y: Int32): Tui[Unit] = Free.liftF(TuiEffect.MoveCursor(x, y))

pub def saveCursor(): Tui[Unit] = Free.liftF(TuiEffect.SaveCursor)

pub def restoreCursor(): Tui[Unit] = Free.liftF(TuiEffect.RestoreCursor)

/// Color helpers
pub def red: String = "31"
pub def green: String = "32"
pub def yellow: String = "33"
pub def blue: String = "34"
pub def magenta: String = "35"
pub def cyan: String = "36"

/// TUI combinators
pub def withColor(color: String, action: Tui[a]): Tui[a] =
    setColor(color) `Free.flatMap` (_ -> 
    action `Free.flatMap` (result ->
    resetColor() `Free.map` (_ -> 
    result)))

pub def box(width: Int32, height: Int32, content: Tui[a]): Tui[a] = {
    let drawBorder = {
        // Top border
        print("┌") `Free.flatMap` (_ ->
        print("─" |> String.repeat(width)) `Free.flatMap` (_ ->
        println("┐") `Free.flatMap` (_ ->
        // Side borders
        List.range(0, height) |> List.foldLeft((acc, _) ->
            acc `Free.flatMap` (_ ->
            print("│") `Free.flatMap` (_ ->
            moveCursor(width + 1, getCursorY()) `Free.flatMap` (_ ->
            println("│")))), Free.pure(())) `Free.flatMap` (_ ->
        // Bottom border
        print("└") `Free.flatMap` (_ ->
        print("─" |> String.repeat(width)) `Free.flatMap` (_ ->
        println("┘"))))))
    };
    
    saveCursor() `Free.flatMap` (_ ->
    drawBorder `Free.flatMap` (_ ->
    restoreCursor() `Free.flatMap` (_ ->
    content)))
}

/// Armenian note:
/// Էֆեկտները ծրագրի հոգին են
/// (Effects are the soul of programming)
