# Default recipe
default:
    @just --list

# Play: Start with random walk and launch Flex
play:
    @echo "🌀 Starting with Babashka random walk..."
    bb bb/random_walk.clj
    @echo "\n🎲 Building and launching Flex..."
    cd src/flex && flix build.flix

# Clean temporary files
clean:
    @echo "Cleaning temporary files..."
    rm -f **/*.pyc
    rm -rf **/__pycache__
    rm -rf .pytest_cache
    rm -rf dist
    rm -rf build
    rm -f src/flex/*.jar

# Setup development environment
setup:
    @echo "Setting up development environment..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv pip install -e ".[dev]"

# Run tests
test:
    @echo "Running tests..."
    cd src/flex && flix test.flix

# Build Flex
build:
    @echo "Building Flex..."
    cd src/flex && flix build.flix

# Run Flex REPL
flex: build
    @echo "Starting Flex..."
    cd src/flex && java -jar flex.jar

# Armenian note:
# Ճկուն ծրագրավորում սկսվում է այստեղից
# (Flexible programming starts here)
