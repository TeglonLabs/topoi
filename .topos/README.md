# .topos Directory

This directory contains the ontological foundation and operational loops that guide the development of topos-mcp. It provides both theoretical grounding and practical patterns for MCP server implementations.

## Structure

```
.topos/
├── ontology/           # Core ontological concepts
│   ├── autopoiesis/   # Self-organization principles
│   ├── ergodicity/    # Convergence properties
│   └── topology/      # Geometric structures
├── loops/             # Operational loops
│   ├── gmgn.md       # Session initialization
│   ├── compose.md    # Task composition
│   └── iterate.md    # Incremental improvement
└── mcp/              # MCP server implementations
    ├── examples/     # Reference implementations
    ├── schemas/      # API schemas
    └── servers/      # Server code
```

## Development Model

The development process follows three main loops:

1. **GMGN (Good Morning/Good Night)**
   - Sets up initial session context
   - Focuses on autopoietic systems
   - Discusses ergodicity and convergence
   - Themes: Collaborative intelligence, stigmergy, mutual recursion

2. **Compose**
   - Structures tasks into Done/Next/Upcoming
   - Evaluates work impact bidirectionally
   - Focuses on shared player arena and collaboration
   - Includes feedback on progress and impact

3. **Iterate**
   - Includes systematic improvements
   - Structured task management
   - Strong focus on research and planning
   - Supports multiple formal languages

## Theoretical Foundations

The development is guided by several key theoretical concepts:

### Autopoiesis
- System self-organization and self-maintenance
- Dynamic adaptation to changing situations
- Convergence towards optimal states

### Ergodicity
- Time and ensemble averages equivalence
- Convergence properties in system evolution
- Long-term behavior characterization

### Category Theory
- Morphisms represent transformations
- Composition captures interaction
- Functors describe system relationships

## Usage

When developing new MCP servers or modifying existing ones:

1. Follow the loop structure for development sessions
2. Reference relevant ontological concepts
3. Ensure implementations respect theoretical foundations
4. Use provided patterns and examples