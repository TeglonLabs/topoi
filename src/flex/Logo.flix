/*
 * Flex: ASCII Art Logo with Active Inference
 * Using 2-3-5-7 timing and aperiodic monotile patterns
 */

/// Animation frames using hat monotile-inspired patterns
pub def frames(): List[List[String]] = List#{
    // Frame 1 (2ms): Starting position - Hat monotile base
    List#{
        "    /\\__/\\      ",
        "   /      \\     ",
        "  /  FLEX  \\    ",
        " /    ||    \\   ",
        "|     ||     |  ",
        "|    _||_    |  ",
        " \\  /    \\  /   ",
        "  \\/      \\/    "
    },
    
    // Frame 2 (3ms): Mid curl - Aperiodic transition
    List#{
        "    /\\__/\\      ",
        "   /  ||  \\     ",
        "  /  FLEX  \\    ",
        " /   _||_   \\   ",
        "|    \\  /    |  ",
        "|     \\/     |  ",
        " \\    ||    /   ",
        "  \\/\\/  \\/\\/    "
    },
    
    // Frame 3 (5ms): Full flex - Polykite formation
    List#{
        "    /\\__/\\__    ",
        "   /  ||    \\   ",
        "  /  FLEX    \\  ",
        " /   _||___   \\ ",
        "|    \\    /    |",
        "|     \\  /     |",
        " \\     \\/     / ",
        "  \\/\\/\\/\\/\\/\\/  "
    },
    
    // Frame 4 (7ms): Peak tension - Spectra pattern
    List#{
        "    /\\__/\\___   ",
        "   /  ||     \\  ",
        "  /  FLEX     \\ ",
        " /   _||____   \\",
        "|    \\     /    |",
        "|     \\   /     |",
        " \\     \\ /     / ",
        "  \\/\\/\\/V\\/\\/\\/ "
    }
}

/// Frame timing in milliseconds following 2-3-5-7 rule
pub def timings(): List[Int32] = List#{2, 3, 5, 7}

/// Active inference with aperiodic pattern recognition
pub def predictNextFrame(current: List[String], history: List[List[String]]): List[String] =
    match history {
        case prev :: rest =>
            // Analyze pattern transitions
            let deltaLines = List.map2((curr, prev) -> 
                if curr != prev then Some(curr) else None,
                current, prev);
            
            // Predict next aperiodic state
            List.map2((line, delta) ->
                match delta {
                    case None => line
                    case Some(d) => predictPattern(line, d)
                }, current, deltaLines)
        case Nil => current
    }

/// Pattern prediction using monotile properties
def predictPattern(current: String, delta: String): String =
    if String.contains("/\\", current) and String.contains("\\/", delta) then
        // Predict hat tile rotation
        String.replace("/\\", "\\/", current)
    else if String.contains("||", current) and String.contains("__", delta) then
        // Predict flex motion
        String.replace("||", "__", current)
    else if String.contains("\\/", current) and String.contains("/\\", delta) then
        // Predict aperiodic tiling
        String.replace("\\/", "/\\", current)
    else
        current

/// Draw logo with active inference
pub def drawLogo(): Tui[Unit] = {
    // Initialize with empty history
    let initState = {frames = frames(), history = Nil};
    
    // Animation loop with prediction
    let animate = ((Omega Omega) (lambda (loop) (lambda (state)
        match state.frames {
            case Nil => Free.pure(())
            case frame :: rest => {
                // Draw current frame
                let drawFrame = frame |> List.foldLeft((acc, line) ->
                    acc `Free.flatMap` (_ ->
                    withColor(cyan, println(line))), Free.pure(()));
                
                // Predict and prepare next state
                let nextFrame = predictNextFrame(frame, state.history);
                let nextState = {
                    frames = rest,
                    history = frame :: state.history
                };
                
                // Animate with timing
                drawFrame `Free.flatMap` (_ ->
                sleep(List.head(timings())) `Free.flatMap` (_ ->
                clear() `Free.flatMap` (_ ->
                loop(nextState))))
            }
        })));
    
    // Run animation
    animate(initState)
}

/// Armenian note:
/// Անկանոն նախշերով շարժում
/// (Motion with aperiodic patterns)
