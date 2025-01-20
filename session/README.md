# Topos Session MCP Server

An MCP server mode for analyzing Cline and Claude Desktop sessions, designed to integrate with topos-mcp. This server provides tools for analyzing interaction patterns, tool usage, and context preservation in accordance with the deciding sheaves on presheaves paper.

## Features

- Session data analysis using DuckDB 0.9.2
- Tool usage pattern analysis
- MCP interaction tracking
- Context preservation metrics
- Cross-client compatibility

## Installation

1. Clone into topos-mcp:
```bash
cd ~/infinity-topos/topos-mcp
git clone https://github.com/yourusername/topos-session-mcp.git
```

2. Install dependencies:
```bash
uv pip install -e .
```

## Usage

### As a Server Mode

Add to your topos-mcp configuration:

```json
{
  "server_modes": {
    "session-analysis": {
      "module": "topos_session_mcp.server",
      "class": "ToposSessionServer",
      "config": {
        "db_path": "/Users/barton/topos/topos.db"
      }
    }
  }
}
```

Run with:
```bash
topos-mcp --mode session-analysis
```

### Available Tools

1. `analyze_sessions`
   - Analyze Cline/Claude Desktop sessions
   - Parameters:
     - sessions_dir: Directory containing session data
     - output_dir: Directory for analysis output (optional)

2. `get_session_stats`
   - Get summary statistics for sessions
   - No parameters required

3. `analyze_tool_patterns`
   - Analyze tool usage patterns
   - Parameters:
     - tool_name: Optional specific tool to analyze

4. `analyze_mcp_usage`
   - Analyze MCP server usage patterns
   - Parameters:
     - server_name: Optional specific server to analyze

### Example Usage

```python
from mcp.client import Client

async with Client() as client:
    # Analyze all sessions
    result = await client.call_tool("analyze_sessions", {
        "sessions_dir": "/path/to/sessions"
    })
    print(result.content[0].text)

    # Get usage patterns for a specific tool
    patterns = await client.call_tool("analyze_tool_patterns", {
        "tool_name": "write_to_file"
    })
    print(patterns.content[0].text)
```

## Schema

The server uses a DuckDB schema optimized for session analysis:

- `sessions`: Core session metadata
- `messages`: Individual message content and metadata
- `tool_usage`: Tool invocation tracking
- `mcp_interactions`: MCP server interaction tracking
- `environment_changes`: Environment context changes

Materialized views provide efficient access to:
- Message trajectories
- Tool usage patterns
- Context preservation metrics
- MCP server effectiveness

## Integration with Topos

This server mode integrates with the broader topos ecosystem by:
1. Using the same database as other topos components
2. Supporting cross-client analysis
3. Maintaining compatibility with MCP protocols
4. Following sheaf-theoretic principles for data organization

## Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/topos-session-mcp.git
cd topos-session-mcp
```

2. Install development dependencies:
```bash
uv pip install -e ".[dev]"
```

3. Run tests:
```bash
pytest tests/
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
