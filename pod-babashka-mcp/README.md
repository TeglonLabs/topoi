# pod-babashka-mcp

A Babashka pod for interacting with MCP (Model Context Protocol) servers. This pod provides idiomatic Clojure interfaces for MCP client operations.

## Features

- Connect to MCP servers over stdio, WebSocket, or SSE transports
- Manage server capabilities and resources
- Execute tools with proper error handling
- Subscribe to resource and tool updates
- Handle JSON-RPC messaging with proper serialization

## Installation

Add to your `bb.edn`:

```clojure
{:deps {org.babashka/mcp-pod {:mvn/version "0.1.0"}}}
```

Or load directly:

```clojure
(require '[babashka.pods :as pods])
(pods/load-pod 'org.babashka/mcp "0.1.0")
```

## Usage

```clojure
(require '[pod.babashka.mcp :as mcp])

;; Connect to an MCP server
(def session 
  (mcp/connect {:command "python"
                :args ["server.py"]
                :env {"DEBUG" "1"}}))

;; List available tools
(mcp/list-tools session)

;; Call a tool
(mcp/call-tool session "list_directory" {:path "."})

;; Subscribe to resource updates
(mcp/subscribe session "resource://example" 
               (fn [update] (println "Resource updated:" update)))

;; Clean up
(mcp/disconnect session)
```

## Development

### Prerequisites

- Go 1.19+
- Babashka 1.0.0+

### Building

```bash
# Build the pod
$ go build -o pod-babashka-mcp

# Run tests
$ bb test
```

### Project Structure

```
pod-babashka-mcp/
├── src/
│   ├── mcp/           # Go implementation
│   │   ├── client.go  # MCP client logic
│   │   └── pod.go     # Pod interface
│   └── bb/            # Babashka integration
│       └── mcp.clj    # Clojure API
├── test/              # Tests
├── examples/          # Usage examples
└── resources/         # Additional resources
```

## Design Decisions

1. **Why a Pod?**
   - Reuse existing Go MCP client implementations
   - Better performance for JSON handling
   - Clean separation of concerns
   - Consistent with other Babashka database pods

2. **API Design**
   - Follow Clojure idioms
   - Support both sync and async operations
   - Provide data-oriented interfaces
   - Match existing MCP client patterns

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a PR

See CONTRIBUTING.md for detailed guidelines.

## License

Copyright © 2025 Contributors

Distributed under the EPL License. See LICENSE.
