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
from typing import Dict, List, Optional
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl, BaseModel
import mcp.server.stdio

class Behavior(BaseModel):
    """Core behavior representation"""
    id: str
    name: str
    description: Optional[str] = None

class ToposState(BaseModel):
    """Core state representation"""
    id: str
    behaviors: List[str]

# State management
behaviors: Dict[str, Behavior] = {}
states: Dict[str, ToposState] = {}

# Initialize server with topos capabilities
server = Server("topos-mcp")

# Initialize server
server = Server("topos-mcp")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available behaviors and states"""
    resources = []
    
    for behavior_id, behavior in behaviors.items():
        resources.append(
            types.Resource(
                uri=AnyUrl(f"topos://behavior/{behavior_id}"),
                name=behavior.name,
                description=behavior.description,
                mimeType="application/json"
            )
        )
    
    for state_id, state in states.items():
        resources.append(
            types.Resource(
                uri=AnyUrl(f"topos://state/{state_id}"),
                name=f"State {state_id}",
                description=f"State with {len(state.behaviors)} behaviors",
                mimeType="application/json"
            )
        )
    
    return resources

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Read behavior or state content"""
    if uri.scheme != "topos":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    path = uri.path.lstrip("/") if uri.path else ""
    parts = path.split("/")
    
    if len(parts) != 2:
        raise ValueError(f"Invalid resource path: {path}")
        
    resource_type, resource_id = parts
    
    if resource_type == "behavior" and resource_id in behaviors:
        return behaviors[resource_id].json()
    elif resource_type == "state" and resource_id in states:
        return states[resource_id].json()
            
    raise ValueError(f"Resource not found: {path}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
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
        types.Tool(
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

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
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
    return [types.TextContent(type="text", text=response)]

async def main():
    """Run the server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="topos-mcp",
                server_version="0.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
