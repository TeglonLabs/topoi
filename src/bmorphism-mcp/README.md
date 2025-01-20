# Bmorphism MCP Server

A dual-runtime MCP server implementation that combines drand randomness beacons with slowtime operations. Uses TypeScript for drand integration and Python for slowtime calculations, with babashka for runtime management and topos synchronization.

## Features

1. **Dual Runtime Architecture**
   - TypeScript drand server for randomness beacons
   - Python server for slowtime operations
   - Babashka-managed runtime coordination

2. **Topos Integration with DuckDB**
   - Structured directory tree in DuckDB
   - Automatic synchronization of .topos files
   - Mermaid diagram generation and tracking
   - Feature relationship mapping
   - Schema versioning and metadata

3. **MCP Feature Replication**
   - Automatic sync from reference implementations
   - Feature-by-feature replication with dependency tracking
   - Integrated testing and validation
   - Feature relationship analysis

4. **Directory Structure Templates**
   - Standardized MCP server layout
   - Foundry integration templates
   - Custom template support
   - Automatic directory creation and tracking

## Architecture

The server consists of three main components:

1. **TypeScript Drand Server**
   - Integrates with League of Entropy's drand service
   - Provides randomness beacon functionality
   - Exposes tools:
     - `get_latest_randomness`: Get latest randomness from drand
     - `get_round_info`: Get current round information

2. **Python Slowtime Server**
   - Handles temporal morphism calculations
   - Integrates with TypeScript drand server
   - Exposes tools:
     - `get_slowtime_info`: Get slowtime information for a timestamp
     - `analyze_temporal_morphism`: Analyze morphism between timestamps

3. **DuckDB Integration**
   - Tracks directory structure and relationships
   - Manages feature metadata and dependencies
   - Provides schema versioning
   - Enables complex queries across topos files

## Setup

The project uses babashka for runtime management and requires:
- Node.js & npm
- Python 3.10+
- uv (Python package manager)
- tmux
- babashka
- git
- DuckDB

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd bmorphism-mcp

# Full setup (includes feature sync and server setup)
bb bb/run.clj setup

# Start everything (sync, setup, servers)
bb bb/run.clj start

# Stop all servers
bb bb/run.clj stop

# Only run topos sync
bb bb/run.clj sync
```

### Available Scripts

1. `bb/run.clj` - Main runner script
   - `start`: Start everything (sync, setup, servers)
   - `stop`: Stop all servers
   - `sync`: Only run topos sync
   - `setup`: Only setup servers

2. `bb/manage.clj` - Server management
   - `setup`: Install dependencies and build servers
   - `start`: Start both servers in tmux
   - `stop`: Stop servers
   - `restart`: Restart servers

3. `bb/topos_sync.clj` - Topos synchronization
   - Collects and organizes .topos files
   - Generates mermaid diagrams
   - Creates unified documentation

4. `bb/topos_db.clj` - DuckDB integration
   - Manages directory structure
   - Tracks feature relationships
   - Provides schema versioning
   - Enables complex queries

## Directory Structure
```
bmorphism-mcp/
├── typescript/           # TypeScript drand server
│   ├── server.ts
│   ├── package.json
│   └── tsconfig.json
├── python/              # Python slowtime server
│   ├── server.py
│   └── pyproject.toml
├── bb/                  # Babashka management scripts
│   ├── run.clj         # Main runner
│   ├── manage.clj      # Server management
│   ├── topos_sync.clj  # Topos file sync
│   └── topos_db.clj    # DuckDB integration
└── .topos/              # Topos directory tree
    ├── unified/        # Assembled documentation
    │   └── mermaid/   # Generated diagrams
    ├── features/      # MCP feature tracking
    ├── ontology/      # Schema definitions
    ├── mermaid/       # Visualization source
    └── topos.db       # DuckDB database
```

### DuckDB Schema
```sql
-- Key tables in topos.db
topos_directories     # Directory structure tracking
topos_files          # File metadata and content hashes
mcp_features         # MCP feature tracking
mermaid_diagrams     # Generated diagrams
feature_relationships # Feature dependencies
directory_templates   # Structure templates
```

## VSCode Integration

Add to VSCode MCP settings (`/Users/barton/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`):

```json
{
  "mcpServers": {
    "bmorphism": {
      "command": "bb",
      "args": ["src/bmorphism-mcp/bb/manage.clj", "start"],
      "env": {}
    }
  }
}
```

## Tool Usage Examples

### Get Latest Randomness
```typescript
// TypeScript drand server
const randomness = await use_mcp_tool({
  name: "get_latest_randomness"
});
```

### Analyze Temporal Morphism
```python
# Python slowtime server
analysis = await use_mcp_tool({
  name: "analyze_temporal_morphism",
  arguments: {
    start_time: "2024-02-20T10:00:00Z",
    end_time: "2024-02-20T15:00:00Z"
  }
});
```

### Query Topos Structure
```sql
-- Get feature relationships
SELECT 
  f1.name as source,
  f2.name as target,
  r.relationship_type
FROM feature_relationships r
JOIN mcp_features f1 ON r.source_feature_id = f1.id
JOIN mcp_features f2 ON r.target_feature_id = f2.id;

-- Get directory structure
WITH RECURSIVE dir_tree AS (
  SELECT id, path, type, 0 as level
  FROM topos_directories
  WHERE path NOT LIKE '%/%'
  UNION ALL
  SELECT d.id, d.path, d.type, t.level + 1
  FROM topos_directories d
  JOIN dir_tree t ON d.path LIKE t.path || '/%'
)
SELECT * FROM dir_tree ORDER BY level, path;
```

## Theory

The server implements bmorphism concepts by:
1. Using drand's League of Entropy as a source of randomness
2. Calculating temporal morphisms between timestamps
3. Analyzing slowtime characteristics using both entropy and temporal data
4. Providing tools for temporal coherence analysis
5. Tracking feature relationships and dependencies in DuckDB
6. Maintaining structured documentation with mermaid visualizations

## License

Apache 2.0
