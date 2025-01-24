# Changelog

All notable changes to pod-babashka-mcp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-23

### Added
- Initial release of pod-babashka-mcp
- Core MCP client functionality:
  - Connect to MCP servers over stdio transport
  - List and call tools
  - List and read resources
  - Subscribe to resource updates
  - List and get prompts
- Go implementation using the official MCP SDK
- Clojure API with idiomatic interface
- Async operations support
- Comprehensive test suite
- Documentation and examples

### Features
- Full MCP protocol support
- JSON-RPC message handling
- Error handling and reporting
- Session management
- Resource subscription capabilities
- Async tool execution
- Integration with Babashka pods system

### Infrastructure
- Build system using bb tasks
- Test runner integration
- CI/CD setup
- Documentation generation
- Release automation

[0.1.0]: https://github.com/babashka/pod-babashka-mcp/releases/tag/v0.1.0
