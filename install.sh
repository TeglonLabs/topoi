#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Installing infinity-topos MCP system...${NC}"

# Step 1: Install uv (Python package manager)
echo -e "${BLUE}Installing uv...${NC}"
curl -LsSf https://astral.sh/uv/install.sh | sh

# Step 2: Install Babashka
echo -e "${BLUE}Installing Babashka...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if [[ $(uname -m) == 'arm64' ]]; then
        # Apple Silicon
        curl -LO https://github.com/babashka/babashka/releases/download/v1.3.189/babashka-1.3.189-macos-aarch64.tar.gz
        tar xzvf babashka-1.3.189-macos-aarch64.tar.gz
    else
        # Intel
        curl -LO https://github.com/babashka/babashka/releases/download/v1.3.189/babashka-1.3.189-macos-amd64.tar.gz
        tar xzvf babashka-1.3.189-macos-amd64.tar.gz
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    curl -LO https://github.com/babashka/babashka/releases/download/v1.3.189/babashka-1.3.189-linux-amd64-static.tar.gz
    tar xzvf babashka-1.3.189-linux-amd64-static.tar.gz
fi

# Move Babashka to a proper location
sudo mkdir -p /usr/local/bin
sudo mv bb /usr/local/bin/
sudo chmod +x /usr/local/bin/bb

# Step 3: Create infinity-topos directory structure
echo -e "${BLUE}Setting up infinity-topos directory structure...${NC}"
mkdir -p ~/infinity-topos
cd ~/infinity-topos

# Step 4: Initialize MCP servers directory
echo -e "${BLUE}Initializing MCP servers...${NC}"
mkdir -p mcp-servers

# Step 5: Set up initial working servers
echo -e "${BLUE}Setting up core MCP servers...${NC}"

# Create babashka initialization script
cat > init.clj << 'EOL'
(ns infinity-topos.init
  (:require [babashka.fs :as fs]
            [clojure.java.shell :refer [sh]]
            [clojure.string :as str]))

(defn setup-mcp-server [name]
  (println (str "Setting up " name "..."))
  (let [server-dir (str "mcp-servers/" name)]
    (fs/create-dirs server-dir)
    (spit (str server-dir "/package.json")
          (str "{\"name\": \"" name "\",\"version\": \"0.1.0\",\"type\": \"module\"}"))))

;; Initialize core servers
(doseq [server ["coin-flip-mcp" "babashka-mcp-server"]]
  (setup-mcp-server server))

(println "Core MCP servers initialized!")
EOL

# Run Babashka initialization
bb init.clj

# Step 6: Set up MCP configuration
echo -e "${BLUE}Setting up MCP configuration...${NC}"
mkdir -p ~/Library/Application\ Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/

# Create initial MCP settings
cat > ~/Library/Application\ Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json << 'EOL'
{
  "mcpServers": {
    "babashka": {
      "command": "node",
      "args": [
        "~/infinity-topos/mcp-servers/babashka-mcp-server/build/index.js"
      ],
      "env": {
        "BABASHKA_PATH": "/usr/local/bin/bb"
      }
    },
    "coin-flip": {
      "command": "node",
      "args": [
        "~/infinity-topos/mcp-servers/coin-flip-mcp/build/index.js"
      ]
    }
  }
}
EOL

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo "1. Test the core MCP servers"
echo "2. Add additional servers progressively"
echo "3. Configure API keys as needed"
