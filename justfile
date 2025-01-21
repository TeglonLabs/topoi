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

# Database operations for hypergraph storage
# Տվյալների բազայի գործողություններ հիպերգրաֆի պահպանման համար

# Import Cline history
# Ներմուծել Cline պատմությունը
cline:
    @chmod +x src/db_ops.py
    @python3 src/db_ops.py import-cline test_cline_history.json

# Import Claude history
# Ներմուծել Claude պատմությունը
claude:
    @chmod +x src/db_ops.py
    @python3 src/db_ops.py import-claude

# Database operations
db *ARGS='':
    @chmod +x src/db_ops.py
    @python3 src/db_ops.py {{ARGS}}

# Grow the knowledge base by importing all histories
# Աճեցնել գիտելիքների բազան՝ ներմուծելով բոլոր պատմությունները
grow: cline claude
    @echo "🌱 Growing knowledge base across DuckDB, Kuzu, and LanceDB..."
    @python3 src/db_ops.py analyze

# Armenian note:
# Ճկուն ծրագրավորում սկսվում է այստեղից
# (Flexible programming starts here)
