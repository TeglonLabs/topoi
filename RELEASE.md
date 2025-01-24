# Release Process

## Configuration

The topos system uses EDN-based configuration to manage installation paths and preferences. The default configuration is stored in `config.edn`, which can be overridden by user-specific settings.

### Core Configuration Options

- `:topos-root`: Default location for topos installation (default: "~/topos")
- `:paths`: System paths for various components
- `:bootstrap`: Method selection for system initialization
- `:server-priorities`: Ordered list of MCP servers for progressive installation
- `:working-memory`: Settings for preserving user state

## Installation Methods

The system supports two primary installation methods:

### 1. Babashka-First Installation
- Uses Babashka's self-contained binary approach
- Manages MCP server installation progressively
- Preserves working memory during updates
- Command: `bb install.clj`

### 2. Flox-First Installation
- Leverages Flox environment management
- Provides reproducible development environments
- Integrates with Nix ecosystem
- Command: `flox install`

The installation method is chosen either:
1. Explicitly through configuration
2. Randomly at runtime if no preference is set
3. Falling back to Babashka if primary method fails

## Backup and Update Process

1. Before any update:
   ```clojure
   bb -m topos-mcp.core --mode backup
   ```
   This creates a timestamped backup: `backup.topoi.<timestamp>.tar.gz`

2. Working memory preservation:
   - Personal .topos working memory is preserved
   - Located at ~/.topos/memory (configurable)
   - Backed up automatically at configured intervals

3. Update sequence:
   ```bash
   # Backup current state
   bb -m topos-mcp.core --mode backup
   
   # Update core system
   bb update.clj
   
   # Progressive server updates
   bb update-servers.clj
   ```

## Release Checklist

1. Version Bump
   - Update version in project files
   - Update changelog
   - Tag release

2. Package Distribution
   - Create Babashka package
   - Create Flox package
   - Verify both installation paths

3. Testing
   - Run automated tests
   - Verify backup/restore
   - Test both installation methods
   - Validate server priorities

4. Documentation
   - Update README.md
   - Update installation guides
   - Document new features
   - Update configuration examples

## Making a Release

```bash
# 1. Create backup
bb -m topos-mcp.core --mode backup

# 2. Run test suite
bb test.clj

# 3. Package for distribution
bb package.clj

# 4. Create release
bb release.clj

# 5. Publish
bb publish.clj
```

## Verification

After installation, verify:
1. Core system functionality
2. MCP server availability
3. Working memory persistence
4. Configuration loading
5. Backup/restore capability

## Troubleshooting

Common issues and solutions:
1. Path conflicts: Check config.edn paths
2. Server priorities: Verify progressive installation
3. Memory persistence: Check backup intervals
4. Bootstrap method: Verify fallback behavior
