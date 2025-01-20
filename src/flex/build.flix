/*
 * Flex: Build configuration
 * Builds a Scheme implementation in Flix with Armenian flair
 */

def main(): Unit \ IO = {
    // Print banner
    println("Building Flex...");
    println("Ճկուն Լիսպ (Flexible Lisp)");
    println("----------------------------");

    // Register source files
    let sources = #{
        "Main.flix",
        "Parser.flix",
        "Primitives.flix", 
        "Environment.flix"
    };

    // Build options
    let opts = #{
        "target": "jar",
        "main-class": "Main",
        "output": "flex.jar",
        "version": "0.1.0"
    };

    // Build project
    match build(sources, opts) {
        case Ok(_) => 
            println("Build successful!");
            println("Run with: java -jar flex.jar")
        case Err(e) => 
            println("Build failed:");
            println(e)
    }
}

/// Helper to build project
def build(sources: Set[String], opts: Map[String, String]): Result[String, Unit] = {
    // Verify all source files exist
    forM (
        source <- sources
    ) {
        match File.exists(source) {
            case true => Ok(())
            case false => Err("Source file not found: ${source}")
        }
    };

    // Compile sources
    let result = compile(sources);

    // Create JAR if compilation succeeds
    match result {
        case Ok(_) => createJar(opts)
        case Err(e) => Err(e)
    }
}

/// Helper to compile sources
def compile(sources: Set[String]): Result[String, Unit] = {
    // Flix compiler options
    let compilerOpts = #{
        "optimize": true,
        "verify": true,
        "warn-unused": true,
        "target": "1.8"  // For wider JVM compatibility
    };

    // Run compiler
    match Compiler.compile(sources, compilerOpts) {
        case Ok(_) => Ok(())
        case Err(e) => Err("Compilation failed: ${e}")
    }
}

/// Helper to create JAR
def createJar(opts: Map[String, String]): Result[String, Unit] = {
    // JAR manifest
    let manifest = #{
        "Main-Class": Map.getWithDefault("main-class", "Main", opts),
        "Created-By": "Flix ${Version.current}",
        "Implementation-Title": "Flex",
        "Implementation-Version": Map.getWithDefault("version", "0.1.0", opts),
        "Implementation-Vendor": "Flex Contributors"
    };

    // Create JAR file
    match Jar.create(
        Map.getWithDefault("output", "flex.jar", opts),
        manifest,
        "build/"
    ) {
        case Ok(_) => Ok(())
        case Err(e) => Err("JAR creation failed: ${e}")
    }
}

/// Armenian note:
/// Կառուցում ենք մեր Լիսպը սիրով
/// (Building our Lisp with love)
