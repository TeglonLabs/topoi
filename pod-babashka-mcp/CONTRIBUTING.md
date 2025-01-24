# Contributing to pod-babashka-mcp

Thank you for your interest in contributing to pod-babashka-mcp! This document provides guidelines and instructions for contributing.

## Development Setup

1. Prerequisites:
   - Go 1.19+
   - Babashka 1.0.0+
   - Git

2. Clone the repository:
   ```bash
   git clone https://github.com/babashka/pod-babashka-mcp
   cd pod-babashka-mcp
   ```

3. Install dependencies:
   ```bash
   go mod download
   bb install
   ```

## Project Structure

```
pod-babashka-mcp/
├── src/
│   ├── mcp/           # Go implementation
│   │   ├── client.go  # MCP client logic
│   │   └── pod.go     # Pod interface
│   └── bb/            # Babashka integration
│       └── pod/
│           └── babashka/
│               └── mcp.clj    # Clojure API
├── test/              # Tests
├── examples/          # Usage examples
└── resources/         # Additional resources
```

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following these guidelines:
   - Follow Go style guidelines for Go code
   - Follow Clojure style guidelines for Clojure code
   - Add tests for new functionality
   - Update documentation as needed

3. Build and test:
   ```bash
   # Build everything
   bb compile

   # Run tests
   bb test

   # Install locally
   bb install
   ```

4. Commit your changes:
   - Use clear commit messages
   - Reference any relevant issues
   - Keep commits focused and atomic

5. Submit a Pull Request:
   - Provide a clear description of the changes
   - Link to any related issues
   - Ensure CI passes

## Testing

- Write tests for all new functionality
- Run the full test suite before submitting PRs
- Include both unit tests and integration tests where appropriate

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions
- Include examples in docstrings
- Update CHANGELOG.md for notable changes

## Code Style

### Go Code
- Follow standard Go formatting (gofmt)
- Use meaningful variable names
- Add comments for non-obvious code
- Handle errors appropriately

### Clojure Code
- Follow [The Clojure Style Guide](https://github.com/bbatsov/clojure-style-guide)
- Use meaningful names
- Add docstrings to public vars
- Use spec for function contracts where appropriate

## Release Process

1. Update version in:
   - bb.edn
   - build.clj
   - README.md

2. Update CHANGELOG.md

3. Create a release PR

4. After merge, tag the release:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

## Getting Help

- Open an issue for bugs or feature requests
- Join the Babashka Discord for discussions
- Check existing issues and PRs before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the EPL License.
