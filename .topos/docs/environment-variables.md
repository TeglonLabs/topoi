# Environment Variables for pod-babashka-mcp

This document describes the environment variables used in the pod-babashka-mcp configuration.

## Server Environment Variables

### Example Server
- `DEBUG`: Enable debug mode (true/false)
- `LOG_LEVEL`: Logging level for the server

### WebSocket Server
- `WS_PORT`: Port number for WebSocket server
- `WS_HOST`: Host address for WebSocket server

### SSE Server
- `SSE_TIMEOUT`: Stream timeout duration for SSE connections

## Configuration Usage

Environment variables are referenced in pod-config.edn using the `#env` tag reader:

```clojure
:env {"DEBUG" #env "DEBUG"
      "LOG_LEVEL" #env "LOG_LEVEL"}
```

## Setting Up Environment Variables

1. Development Environment
```bash
# Debug settings
export DEBUG=true
export LOG_LEVEL=debug

# WebSocket settings
export WS_PORT=8080
export WS_HOST=localhost

# SSE settings
export SSE_TIMEOUT=30s
```

2. Production Environment
```bash
export DEBUG=false
export LOG_LEVEL=info
export WS_PORT=80
export WS_HOST=0.0.0.0
export SSE_TIMEOUT=60s
```

## Environment File Template

Create a `.env` file:

```bash
# Debug Configuration
DEBUG=true
LOG_LEVEL=debug

# WebSocket Configuration
WS_PORT=8080
WS_HOST=localhost

# SSE Configuration
SSE_TIMEOUT=30s
```

## Loading Environment Variables

1. Using direnv:
```bash
# .envrc
dotenv .env
```

2. Using source:
```bash
source .env
```

## Environment Variable Conventions

1. Naming
- Use UPPERCASE for variable names
- Use underscores for word separation
- Prefix with context (e.g., WS_ for WebSocket)

2. Values
- Use lowercase for boolean values (true/false)
- Use standard port numbers
- Use clear time duration formats

3. Security
- Never commit .env files
- Use separate env files for different environments
- Consider using a secret manager for production

## Validation

The pod validates environment variables during startup:

1. Required Variables
- LOG_LEVEL
- DEBUG (for development)

2. Optional Variables
- WS_PORT (defaults to 8080)
- WS_HOST (defaults to localhost)
- SSE_TIMEOUT (defaults to 30s)

## Troubleshooting

1. Missing Variables
```
Error: Required environment variable LOG_LEVEL not set
Solution: export LOG_LEVEL=info
```

2. Invalid Values
```
Error: Invalid port number: abc
Solution: export WS_PORT=8080
```

## Integration with MCP

The environment variables are used to configure MCP servers and are translated to the appropriate format when converting between EDN and JSON configurations.

Example:

```clojure
;; EDN Config
{"DEBUG" #env "DEBUG"}

;; JSON Output
{"DEBUG": "true"}
```

## References

1. Configuration Files
- pod-config.edn
- .env.example
- .env.test

2. Documentation
- MCP Server Configuration Patterns
- Babashka Pod Best Practices
