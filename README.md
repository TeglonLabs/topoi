# Topos MCP Client

A friendly terminal interface for interacting with MCP servers. This client lets you connect to any MCP server and use its tools through a simple command-line interface.

## What is this?

Think of this client as a universal remote control - it can connect to any MCP server (which provide various capabilities like searching the web, checking the weather, or managing files) and let you use their features through a simple interface.

## Quick Start

### 1. Install Python

If you don't have Python installed:
1. Visit [python.org](https://python.org)
2. Download Python for your system (version 3.9 or higher)
3. Run the installer

To verify Python is installed, open your terminal and run:
```bash
python --version  # Should show 3.9 or higher
```

### 2. Install uv

First, install the uv package manager:

<CodeGroup>
```bash MacOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
</CodeGroup>

Restart your terminal after installation.

### 3. Install the Client

```bash
# Install from PyPI
uv pip install topos-mcp

# Or install from source
git clone https://github.com/your-org/topos-mcp
cd topos-mcp
uv pip install -e .
```

### 4. Connect to a Server

You can connect to any MCP server. For example, to connect to a weather server:

```bash
# If using an installed server package
uvx weather-server

# If using a local server file
uv run path/to/server.py

# If using a server directory
uv --directory path/to/server run server
```

### 5. Using the Interface

Once connected, you'll see a terminal interface with:
- A status bar showing connection state and current mode
- Available tools from the server
- A command prompt

Basic commands:
```
:help              # Show all commands
:list tools        # Show available tools
:call tool {...}   # Use a tool
:quit              # Exit the client
```

Navigation:
- `ESC` - Normal mode (for commands)
- `i` - Insert mode (for typing)
- `:` - Start a command
- Up/Down - Browse command history

### 6. Example Usage

Let's say you're connected to a weather server:

```bash
# List available tools
:list tools

# Check weather in San Francisco
:call get-forecast {"latitude": 37.7749, "longitude": -122.4194}

# Check alerts in California
:call get-alerts {"state": "CA"}
```

## Features

### Easy to Use
- Simple command-line interface
- Command history and auto-completion
- Clear error messages
- Help system

### Reliable
- Automatic reconnection if server disconnects
- Proper error handling
- Clean resource management
- Connection status indicator

### Universal
- Works with any MCP server
- Supports both Python and Node.js servers
- Cross-platform (Windows, macOS, Linux)
- No configuration needed

## Troubleshooting

### Connection Issues

If you see "Failed to connect":
1. Check if the server path is correct
2. Make sure the server is running
3. Check if you have permission to access the server
4. Look for error messages in the output

### Command Errors

If a command fails:
1. Check the command syntax (`:help` shows correct usage)
2. Make sure you're connected (status bar shows "Connected")
3. Try listing available tools again (`:list tools`)
4. Check if the tool arguments are valid JSON

### Common Error Messages

- "Server script must be a .py or .js file"
  - Make sure you're pointing to a valid server file
  - Check the file extension

- "Failed to parse JSON arguments"
  - Check your JSON syntax
  - Make sure to use double quotes for strings
  - Example: `{"name": "value"}`

- "Not connected to server"
  - Wait for automatic reconnection
  - Check if server is still running
  - Try restarting the client

## Development

### Setting up a Development Environment

```bash
# Clone the repository
git clone https://github.com/your-org/topos-mcp
cd topos-mcp

# Create virtual environment
uv venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix or MacOS:
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run tests with uv
uv run pytest
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - feel free to use and modify this client for your own needs.

## Need Help?

- Check the [documentation](https://docs.example.com)
- Join our [Discord community](https://discord.gg/example)
- Open an [issue](https://github.com/example/issues)
- Email support: support@example.com
