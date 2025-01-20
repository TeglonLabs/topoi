"""
Topos MCP Server - Core Implementation

Feature DAG (A → B means A must be implemented before B):

Core (implemented)
├── Basic Behaviors
└── State Management

Modal Logic
├── Modal Operators (□,◇) → World Accessibility
├── World Accessibility → Formula Validation
└── Formula Validation → Behavioral Reasoning

Probability
├── JAX Integration → Transition Matrices
└── Transition Matrices → Local Sections

Category Theory
├── Sheaf Structure → Functorial Maps
├── String Diagrams → Categorical Composition
└── Functorial Maps → Behavioral Homology

Analysis
├── Chain Complexes → Boundary Maps
├── Boundary Maps → Homology Groups
└── Local Sections → Chain Complexes

Each feature increment adds capabilities:
- Modal Logic: Formal behavioral verification
- Probability: Quantitative behavioral analysis
- Category Theory: Structural relationships
- Analysis: Behavioral invariants
"""

import asyncio
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, AnyUrl, Field
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent
from functools import partial as curry

class Behavior(BaseModel):
    """Core behavior representation"""
    id: str = Field(..., description="Unique identifier for the behavior")
    name: str = Field(..., description="Name of the behavior")
    description: Optional[str] = Field(None, description="Description of the behavior")

class ToposState(BaseModel):
    """Core state representation"""
    id: str = Field(..., description="Unique identifier for the state")
    behaviors: List[str] = Field(..., description="List of behavior IDs associated with the state")

# State management
behaviors: Dict[str, Behavior] = {}
states: Dict[str, ToposState] = {}

# Initialize server with topos capabilities
server = Server("topos-mcp")

@curry
@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available behaviors and states"""
    resources = [
        Resource(
            uri=AnyUrl(f"topos://behavior/{behavior.id}"),
            name=behavior.name,
            description=behavior.description,
            mimeType="application/json"
        )
        for behavior in behaviors.values()
    ] + [
        Resource(
            uri=AnyUrl(f"topos://state/{state.id}"),
            name=f"State {state.id}",
            description=f"State with {len(state.behaviors)} behaviors",
            mimeType="application/json"
        )
        for state in states.values()
    ]
    return resources

@curry
@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Read behavior or state content"""
    if uri.scheme != "topos":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    path = uri.path.lstrip("/") if uri.path else ""
    resource_type, resource_id = path.split("/", 1) if "/" in path else (path, "")

    if resource_type == "behavior" and resource_id in behaviors:
        return behaviors[resource_id].json()
    elif resource_type == "state" and resource_id in states:
        return states[resource_id].json()
    else:
        raise ValueError(f"Resource not found: {path}")

@curry
@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="add-behavior",
            description="Add a new behavior",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["id", "name"],
            },
        ),
        Tool(
            name="add-state",
            description="Add a new state",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "behaviors": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["id", "behaviors"],
            },
        )
    ]

@curry
@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[dict]) -> List[TextContent]:
    """Handle tool execution requests"""
    if not arguments:
        raise ValueError("Missing arguments")

    if name == "add-behavior":
        behavior = Behavior(
            id=arguments["id"],
            name=arguments["name"],
            description=arguments.get("description")
        )
        behaviors[behavior.id] = behavior
        response = f"Added behavior {behavior.name}"
    
    elif name == "add-state":
        state = ToposState(
            id=arguments["id"],
            behaviors=arguments["behaviors"]
        )
        states[state.id] = state
        response = f"Added state with {len(state.behaviors)} behaviors"
    
    else:
        raise ValueError(f"Unknown tool: {name}")

    await server.request_context.session.send_resource_list_changed()
    return [TextContent(type="text", text=response)]

async def main():
    """Run the server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            initializationOptions=InitializationOptions(
                server_name="topos-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
