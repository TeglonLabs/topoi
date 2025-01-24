# Babashka MCP Implementation

This directory contains a Babashka-based implementation of the Model Context Protocol (MCP), providing tools for directory traversal, git repository management, and MCP server capabilities.

## Files

### mcp_server.clj
Core MCP server implementation that handles:
- JSON-RPC message parsing and formatting
- Basic MCP protocol implementation (initialize, resources, tools)
- stdin/stdout transport layer
- Error handling and responses

### example_mcp_server.clj
Example implementation showing how to create an MCP server that provides directory listing capabilities:
- Implements the IMCPServer protocol
- Provides a "list_directory" tool
- Shows proper error handling and response formatting

### pull-latest.clj
Git repository management script that:
- Recursively finds git repositories under ~/infinity-topos/.topos
- Pulls latest changes for each repository
- Provides status output

### dir_to_duckdb.clj
Directory traversal and storage script that:
- Uses babashka.fs to walk directory trees
- Stores file metadata in DuckDB
- Provides SQL querying capabilities

### capabilities_server.clj
HTTP server that exposes available capabilities:
- Lists available scripts and tools
- Provides descriptions and locations
- Serves JSON over HTTP

## Usage

1. Pull latest changes from all repositories:
```bash
bb pull-latest.clj
```

2. Start the MCP directory server:
```bash
bb example_mcp_server.clj
```

3. Start the capabilities HTTP server:
```bash
bb capabilities_server.clj
```

4. Index directory structure to DuckDB:
```bash
bb dir_to_duckdb.clj [optional_directory_path]
```

## Integration with MCP Ecosystem

The Babashka MCP implementation follows the same patterns as other language SDKs (Python, TypeScript, Kotlin) while leveraging Babashka's unique capabilities:

- **Pods Integration**: Can be extended to use Babashka pods for additional functionality
- **File System Operations**: Native support through babashka.fs
- **Database Integration**: DuckDB support for persistent storage
- **HTTP Capabilities**: Built-in HTTP server support
- **JSON Processing**: Native JSON handling through cheshire

## Protocol Support

Implements core MCP features:
- Initialize/handshake
- Resource listing and reading
- Tool listing and execution
- Error handling
- Capabilities advertisement

## Development

To add new capabilities:
1. Create a new implementation of IMCPServer
2. Define your tools and resources
3. Handle tool calls and resource requests
4. Update capabilities_server.clj to list new functionality

## Future Improvements

- Add support for WebSocket transport
- Implement resource subscriptions
- Add more tool implementations
- Integrate with more Babashka pods
- Add support for prompts and completion
