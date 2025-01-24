# infinity-topos MCP Installation

A streamlined installation process for infinity-topos MCP servers, focusing on easy distribution and setup for macOS and Linux users.

## Quick Start

```bash
# Download and run the installer
curl -LsSf https://raw.githubusercontent.com/infinity-topos/topoi-mcp/main/install.sh | sh
```

## What Gets Installed

1. Core Dependencies:
   - uv (Python package manager)
   - Babashka (Clojure scripting)

2. Initial MCP Servers:
   - babashka-mcp-server
   - coin-flip-mcp

## Adding More Servers

After the initial installation, you can progressively add more servers using the Babashka script:

```bash
# Make the script executable
chmod +x add-server.clj

# Add servers one by one
./add-server.clj say
./add-server.clj discopy-mcp-server
./add-server.clj penrose
./add-server.clj exa  # Will prompt for API key
```

## Server Templates

Currently supported server templates:

1. `say` - Text-to-speech server using Serena (Premium) voice
2. `discopy-mcp-server` - Categorical diagram creation and manipulation
3. `penrose` - Diagram visualization
4. `exa` - AI-powered search (requires API key)

## Directory Structure

```
~/infinity-topos/
├── mcp-servers/
│   ├── babashka-mcp-server/
│   ├── coin-flip-mcp/
│   └── [additional servers]/
├── init.clj
└── add-server.clj
```

## Configuration

MCP settings are stored in:
- macOS: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- Linux: `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

## Testing

After installation, you can test the core functionality:

```bash
# Test coin-flip
uv pip install -e ~/infinity-topos/mcp-servers/coin-flip-mcp

# Use the coin-flip tool
bb -e '(require "[coin-flip-mcp.core :as cf]") (cf/flip-coin 3)'
```

## Troubleshooting

1. If a server fails to install:
   ```bash
   # Check the logs
   tail -f ~/infinity-topos/mcp-servers/[server-name]/npm-debug.log
   ```

2. If configuration is not found:
   ```bash
   # Ensure directory exists
   mkdir -p ~/Library/Application\ Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/
   ```

3. For permission issues:
   ```bash
   # Fix permissions
   sudo chown -R $USER ~/infinity-topos
   ```

## Contributing

To add support for new servers:

1. Add a server template to `add-server.clj`:
   ```clojure
   (def server-templates
     {"new-server" {:command "node"
                    :args ["build/index.js"]
                    :env {"KEY" "value"}}})
   ```

2. Test the server installation:
   ```bash
   ./add-server.clj new-server
