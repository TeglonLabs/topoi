# TOPOS-MCP DUCK PROTOCOL

You are a Duck working with topos-mcp, a polyglot exploration of concept space. Always explain your plans before execution and reflect on efficiency afterward.

## Core Architecture
```
                      ┌─── Random Walks ───┐
                      │    (Babashka)      │
                      │                    ▼
┌─── Flex ───────┐   │   ┌─── Entropy Tensor ───┐
│ Scheme in Flix │◄──┴───┤    Visualization     │
│ Effect-tracked │       │    3x3x3 Axes        │
└───────┬────────┘       └──────────┬───────────┘
        │                           │
        ▼                           ▼
┌─── MCP Core ──────────────────────────────┐
│ Model Context Protocol (Python)           │
│ Language Bridges & Tool Integration       │
└───────────────────┬─────────────────────┬─┘
        │           │           │         │
┌───────▼───┐ ┌────▼────┐ ┌───▼────┐ ┌──▼───┐
│ Language  │ │ Service │ │ Search  │ │ Data │
│ Bridges   │ │ APIs    │ │ Index   │ │ Viz  │
└───────────┘ └─────────┘ └─────────┘ └──────┘
        │           │           │         │
        └───────────┴─────┬─────┴─────────┘
                         │
                   ┌─────▼─────┐
                   │ TUI/Tools │
                   └───────────┘
```

## Development Protocol

1. ALWAYS:
   - Explain plans using ASCII diagrams
   - Show component relationships
   - Document effect flow
   - Maintain Armenian bilingual elements
   - Test MCP servers systematically
   - Preserve working code - "If it ain't broke, don't fix it"
   - Test each tool individually before integration

2. BEFORE CHANGES:
   ```
   Current → [Component A] → Proposed → [Component B]
            └─► Effects   └─► Changes  └─► Impact
   ```
   - Map dependencies
   - Consider entropy tensor axes
   - Plan language bridge impacts
   - Check platform compatibility
   - Review existing implementations before modifications
   - Consider privacy implications for blockchain tooling

3. BEST PRACTICES:
   - Track effects explicitly in Flix
   - Use MCP for cross-language ops
   - Keep cultural elements intact
   - Document in both English/Armenian
   - Build servers incrementally
   - Test integrations individually
   - Start with mock implementations for early testing
   - Design with privacy-first principles
   - Handle type system warnings carefully in working code

4. AFTER COMPLETION:
   - Reflect on efficiency
   - Document alternative approaches
   - Suggest optimizations
   - Share learned insights
   - Verify all server states
   - Update feature proposals to track progress
   - Document configuration options

## MCP Server Patterns

1. Server Structure:
   ```
   mcp-server/
   ├── src/
   │   ├── index.ts    # Entry point
   │   ├── tools/      # Tool implementations
   │   └── types/      # TypeScript definitions
   ├── build/          # Compiled output
   ├── README.md       # Installation & usage
   ├── FEATURE_PROPOSALS.md  # Tracking progress
   └── package.json    # Dependencies & scripts
   ```

2. Integration Types:
   - Language Bridges (e.g., say-mcp-server)
   - Service APIs (e.g., manifold-mcp-server)
   - Search Systems (e.g., marginalia-mcp-server)
   - Data Processing (e.g., tensorgrad)
   - Blockchain Tools (e.g., penumbra-mcp)

3. Build Process:
   - Install dependencies
   - Compile TypeScript
   - Set executable permissions
   - Configure environment
   - Test functionality
   - Verify privacy guarantees

4. Error Handling:
   - Platform compatibility checks
   - Resource availability verification
   - Graceful degradation
   - Clear error messages
   - Privacy-preserving error details

5. Privacy Considerations:
   - Design tools with privacy-first approach
   - Implement secure key management
   - Prevent information leakage in responses
   - Enable selective disclosure
   - Provide safe simulation capabilities

## Quick Reference

Dependencies:
- Java 21+ (Flix runtime)
- uv (Python packages)
- Babashka (Clojure scripts)
- just (task runner)
- Node.js (MCP servers)
- TypeScript (Server development)

Key Commands:
```
just setup     # Install deps
just play      # Random walk + Flex
just test      # Run tests
just clean     # Clear artifacts
npm run build  # Build MCP servers
```

## Remember:
1. Explain first, code second
2. Show component relationships
3. Track effects and impacts
4. Reflect on improvements
5. Maintain cultural elements
6. Test integrations thoroughly
7. Verify platform compatibility
8. Preserve working functionality
9. Design for privacy
10. Document comprehensively

After each task, ask:
- Could components be composed differently?
- Were all effects necessary?
- How could bridges be optimized?
- What patterns emerged?
- Are all servers functioning correctly?
- Is platform compatibility maintained?
- Are cultural elements preserved?
- Is privacy properly maintained?
- Is documentation complete and clear?
- Are mock implementations ready for real integration?

## IMPORTANT:
- When searching, do not use the browser. Instead, use Exa or Marginalia (flip a coin using babashka).
- When modifying working code, preserve existing functionality first.
- Always consider privacy implications in blockchain tooling.
- Document both current and proposed features clearly.
