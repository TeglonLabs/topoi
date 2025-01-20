# MICROWORLD: Hypergraph Visualization in topos-mcp

This document describes the hypergraph visualization component of topos-mcp, which provides an interactive TUI for exploring and understanding hypergraph structures using DisCoPy.

## Core Concepts

### Hypergraphs in Category Theory

The visualization represents hypergraphs as categorical structures with:

- **Types** (x, y, z): Representing base objects in the category
- **Morphisms**: Maps between types (f: x → y, g: y → z, etc.)
- **Spiders**: Special morphisms that allow splitting/joining of types
- **Composition**: Both sequential (>>) and parallel (@) composition of morphisms

### Bidirectional Structure

The hypergraph implements a bidirectional structure where:

1. Forward morphisms (f, g, h) create a cyclic path:
   ```
   x --f--> y --g--> z --h--> x
   ```

2. Backward morphisms (f*, g*, h*) provide reverse paths:
   ```
   y --f*--> x
   z --g*--> y
   x --h*--> z
   ```

This creates a fully connected graph where every vertex can reach every other vertex.

## Interactive Features

### Random Walks

The TUI supports random walks on the hypergraph that:

- Start from any vertex (x, y, or z)
- Follow available morphisms (both forward and backward)
- Track the path and display statistics
- Demonstrate the mixing properties of the graph

### Visualization

The visualization provides:

- ASCII art rendering of the hypergraph structure
- Clear labeling of types and morphisms
- Real-time updates during random walks
- Event logging for tracking interactions

## Integration with topos-mcp

This visualization serves as a microworld for understanding:

1. **Type Systems**: How types flow and transform through morphisms
2. **Composition**: How complex structures emerge from simple components
3. **Symmetry**: Bidirectional relationships and their properties
4. **Dynamics**: How information propagates through connected structures

## Technical Implementation

The implementation uses:

- **DisCoPy**: For hypergraph construction and manipulation
- **Textual**: For the terminal user interface
- **PIL**: For image processing and ASCII art conversion

### Key Components

1. **HypergraphViewer**: Main widget for visualization
   - Manages hypergraph state
   - Handles rendering and updates
   - Processes random walks

2. **EventLog**: Tracks interactions and state changes
   - Records walk paths
   - Shows statistics
   - Maintains history

3. **Controls**: Interactive elements
   - Random Walk generation
   - Reset functionality
   - Clear log option

## Usage in Development

This visualization helps developers:

1. Understand hypergraph structures visually
2. Test composition operations
3. Verify connectivity properties
4. Explore random walk behavior

## Future Extensions

Potential enhancements include:

1. More complex hypergraph structures
2. Additional visualization modes
3. Integration with other topos-mcp components
4. Extended analysis tools

## References

- DisCoPy documentation
- Category theory fundamentals
- Hypergraph theory
- Random walk theory
