import asyncio
import subprocess
import json
import tomllib
from pathlib import Path
from typing import Dict, List, Optional
import modal
from fastapi import FastAPI
from pydantic import BaseModel

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

def ensure_modal_auth():
    """Ensure Modal is authenticated by reading ~/.modal.toml or triggering auth flow."""
    modal_toml = Path.home() / ".modal.toml"
    
    # If .modal.toml doesn't exist, attempt headless creation
    if not modal_toml.exists():
        print("Modal authentication required. Triggering auth flow...")
        try:
            subprocess.run(["modal", "token", "new", "--headless"], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to authenticate with Modal: {e}")
    
    if not modal_toml.exists():
        raise RuntimeError("Modal authentication failed - no .modal.toml present after auth flow.")
    
    # Parse the TOML to verify presence of token_id and token_secret
    try:
        with open(modal_toml, "rb") as f:
            config = tomllib.load(f)
        # Typically looks like:
        # [profile-name]
        # token_id = ...
        # token_secret = ...
        
        # Check each section for valid tokens
        any_valid = False
        for section_name, section_data in config.items():
            if isinstance(section_data, dict):  # Ensure it's a table section
                tid = section_data.get("token_id")
                tsec = section_data.get("token_secret")
                if tid and tsec:
                    any_valid = True
                    print(f"Found valid token configuration in profile: {section_name}")
                    break
        
        if not any_valid:
            raise RuntimeError("No valid token found in .modal.toml. Please run 'modal token new'.")
        
        print("Modal authentication verified via .modal.toml.")
        return True
    except Exception as e:
        raise RuntimeError(f"Failed parsing .modal.toml: {e}")

# Store Modal state
class ModalState:
    def __init__(self):
        self.functions: Dict[str, modal.Function] = {}
        self.endpoints: Dict[str, modal.Endpoint] = {}
        self.jobs: Dict[str, modal.Job] = {}
        self.queues: Dict[str, modal.Queue] = {}

state = ModalState()
server = Server("modal-mcp-server")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available Modal resources."""
    resources = []
    
    # Add function resources
    for name in state.functions:
        resources.append(
            types.Resource(
                uri=AnyUrl(f"modal://functions/{name}"),
                name=f"Function: {name}",
                description=f"Modal cloud function {name}",
                mimeType="application/json",
            )
        )
    
    # Add endpoint resources
    for name in state.endpoints:
        resources.append(
            types.Resource(
                uri=AnyUrl(f"modal://endpoints/{name}"),
                name=f"Endpoint: {name}",
                description=f"Modal web endpoint {name}",
                mimeType="application/json",
            )
        )
        
    # Add job resources
    for name in state.jobs:
        resources.append(
            types.Resource(
                uri=AnyUrl(f"modal://jobs/{name}"),
                name=f"Job: {name}",
                description=f"Modal scheduled job {name}",
                mimeType="application/json",
            )
        )
        
    return resources

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Read Modal resource status."""
    if uri.scheme != "modal":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    parts = uri.path.lstrip("/").split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid Modal resource URI: {uri}")
        
    resource_type, name = parts
    
    if resource_type == "functions":
        if name not in state.functions:
            raise ValueError(f"Function not found: {name}")
        return {"status": "active", "name": name}
        
    elif resource_type == "endpoints":
        if name not in state.endpoints:
            raise ValueError(f"Endpoint not found: {name}")
        return {"status": "running", "name": name, "url": f"https://{name}.modal.run"}
        
    elif resource_type == "jobs":
        if name not in state.jobs:
            raise ValueError(f"Job not found: {name}")
        return {"status": "scheduled", "name": name}
        
    else:
        raise ValueError(f"Invalid resource type: {resource_type}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available Modal tools."""
    return [
        types.Tool(
            name="deploy_function",
            description="Deploy a Python function to Modal",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "code": {"type": "string"},
                    "requirements": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["name", "code"]
            }
        ),
        types.Tool(
            name="create_endpoint",
            description="Create a web endpoint using FastAPI",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "code": {"type": "string"},
                    "requirements": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["name", "code"]
            }
        ),
        types.Tool(
            name="schedule_job",
            description="Create a scheduled job",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "code": {"type": "string"},
                    "schedule": {"type": "string"},
                    "requirements": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["name", "code", "schedule"]
            }
        ),
        types.Tool(
            name="create_container",
            description="Define a custom container environment",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "base_image": {"type": "string"},
                    "packages": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["name", "base_image"]
            }
        ),
        types.Tool(
            name="request_gpu",
            description="Request GPU resources",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "gpu_type": {"type": "string"},
                    "count": {"type": "integer"}
                },
                "required": ["name", "gpu_type"]
            }
        ),
        types.Tool(
            name="create_queue",
            description="Create a distributed job queue",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "max_size": {"type": "integer"}
                },
                "required": ["name"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle Modal tool execution requests."""
    if not arguments:
        raise ValueError("Missing arguments")

    if name == "deploy_function":
        function_name = arguments.get("name")
        code = arguments.get("code")
        requirements = arguments.get("requirements", [])
        
        # Create Modal function
        app = modal.App(function_name)
        
        # Create container with requirements
        image = modal.Image.debian_slim()
        if requirements:
            image = image.pip_install(*requirements)
            
        # Deploy function
        state.functions[function_name] = app.function(image=image)(code)
        
        return [types.TextContent(
            type="text",
            text=f"Deployed function '{function_name}' to Modal"
        )]

    elif name == "create_endpoint":
        endpoint_name = arguments.get("name")
        code = arguments.get("code")
        requirements = arguments.get("requirements", [])
        
        # Create Modal endpoint
        app = modal.App(endpoint_name)
        
        # Create container with FastAPI and requirements
        image = modal.Image.debian_slim().pip_install("fastapi[standard]", *requirements)
        
        # Create FastAPI app
        web_app = FastAPI()
        
        # Deploy endpoint
        state.endpoints[endpoint_name] = app.asgi_app(image=image)(web_app)
        
        return [types.TextContent(
            type="text",
            text=f"Created endpoint '{endpoint_name}' on Modal"
        )]

    elif name == "schedule_job":
        job_name = arguments.get("name")
        code = arguments.get("code")
        schedule = arguments.get("schedule")
        requirements = arguments.get("requirements", [])
        
        # Create Modal scheduled job
        app = modal.App(job_name)
        
        # Create container with requirements
        image = modal.Image.debian_slim()
        if requirements:
            image = image.pip_install(*requirements)
            
        # Deploy scheduled job
        state.jobs[job_name] = app.schedule(schedule, image=image)(code)
        
        return [types.TextContent(
            type="text",
            text=f"Created scheduled job '{job_name}' on Modal"
        )]

    elif name == "create_container":
        container_name = arguments.get("name")
        base_image = arguments.get("base_image")
        packages = arguments.get("packages", [])
        
        # Create Modal container
        image = modal.Image.from_registry(base_image)
        if packages:
            image = image.pip_install(*packages)
            
        return [types.TextContent(
            type="text",
            text=f"Created container '{container_name}' with base image {base_image}"
        )]

    elif name == "request_gpu":
        name = arguments.get("name")
        gpu_type = arguments.get("gpu_type")
        count = arguments.get("count", 1)
        
        # Request GPU resources
        app = modal.App(name)
        stub = app.stub(gpu=modal.gpu.T4(count=count))
        
        return [types.TextContent(
            type="text",
            text=f"Requested {count} {gpu_type} GPU(s) for '{name}'"
        )]

    elif name == "create_queue":
        queue_name = arguments.get("name")
        max_size = arguments.get("max_size", 100)
        
        # Create Modal queue
        app = modal.App(queue_name)
        state.queues[queue_name] = app.queue(max_size=max_size)
        
        return [types.TextContent(
            type="text",
            text=f"Created queue '{queue_name}' with max size {max_size}"
        )]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    print("Starting Modal MCP server...")
    if ensure_modal_auth():
        print("Modal authentication successful - token verified.")
    else:
        raise RuntimeError("Modal authentication incomplete or invalid.")
    
    print("Initializing server on stdin/stdout...")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="modal-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
