#!/usr/bin/env python3
"""
Post-modern MCP client using prompt_toolkit and rich.
Inspired by Kakoune's modal editing and Plan9's structural approach.
"""

import asyncio
import json
import sys
from typing import Dict, List, Optional, Any
from contextlib import AsyncExitStack
from mcp import Client as MCPBaseClient
from mcp.client.stdio import stdio_client
from mcp.client.models import StdioServerParameters, ClientSession
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table

# Modal states
class Mode:
    NORMAL = "NORMAL"  # For navigation and commands
    INSERT = "INSERT"  # For text input
    VISUAL = "VISUAL"  # For selection

class MCPClient:
    """Post-modern MCP client with modal interface"""
    
    def __init__(self):
        # Core state
        self.mode = Mode.NORMAL
        self.console = Console()
        self.command_history: List[str] = []
        self.command_index = 0
        
        # MCP state
        self.mcp_client: Optional[MCPBaseClient] = None
        self.session: Optional[ClientSession] = None
        self.stdio: Optional[Any] = None
        self.write: Optional[Any] = None
        self.exit_stack = AsyncExitStack()
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
        
        # Command completions
        self.command_completer = WordCompleter([
            'call', 'list', 'help', 'quit',
            'tools', 'resources', 'prompts'
        ], ignore_case=True)
        
        # Style definitions
        self.style = Style.from_dict({
            'status': 'reverse',
            'status.mode': '#ffffff bg:#000000',
            'status.key': '#aaaaaa',
            'output-field': 'bg:#202020',
        })

        # Create UI components
        self.output_field = TextArea(
            style='output-field',
            focusable=False,
            wrap_lines=True,
        )
        
        self.status_bar = Window(
            content=FormattedTextControl(self.get_status),
            height=1,
            style='status'
        )

        # Layout
        self.container = HSplit([
            self.output_field,
            self.status_bar,
        ])

        # Key bindings
        self.kb = KeyBindings()
        self.setup_keybindings()

        # Create application
        self.app = Application(
            layout=Layout(self.container),
            key_bindings=self.kb,
            style=self.style,
            full_screen=True,
            mouse_support=True,
        )

    def setup_keybindings(self):
        # Mode switching
        @self.kb.add('escape')
        def _(event):
            self.mode = Mode.NORMAL
            
        @self.kb.add('i')
        def _(event):
            if self.mode == Mode.NORMAL:
                self.mode = Mode.INSERT
                
        @self.kb.add('v')
        def _(event):
            if self.mode == Mode.NORMAL:
                self.mode = Mode.VISUAL

        # Command execution
        @self.kb.add(':', filter=lambda: self.mode == Mode.NORMAL)
        async def _(event):
            """Handle command input"""
            command = await self._get_command_input()
            if command:
                await self._execute_command(command)

        # Command history
        @self.kb.add('up', filter=lambda: self.mode == Mode.NORMAL)
        def _(event):
            """Navigate command history up"""
            if self.command_history and self.command_index > 0:
                self.command_index -= 1
                self.output_field.text = self.command_history[self.command_index]

        @self.kb.add('down', filter=lambda: self.mode == Mode.NORMAL)
        def _(event):
            """Navigate command history down"""
            if self.command_index < len(self.command_history) - 1:
                self.command_index += 1
                self.output_field.text = self.command_history[self.command_index]

    def get_status(self):
        """Return the status bar content"""
        mode_indicators = {
            Mode.NORMAL: "NOR",
            Mode.INSERT: "INS",
            Mode.VISUAL: "VIS"
        }
        
        connection_status = "[green]Connected[/green]" if self.connected else "[red]Disconnected[/red]"
        
        return [
            ('class:status.mode', f" {mode_indicators[self.mode]} "),
            ('class:status.key', f" {connection_status} | ^X:Exit"),
        ]

    def format_output(self, content: str, syntax: Optional[str] = None):
        """Format output using rich"""
        if syntax:
            syntax_obj = Syntax(content, syntax, theme="monokai")
            self.console.print(syntax_obj)
        else:
            self.console.print(content)

    async def _get_command_input(self) -> Optional[str]:
        """Get command input with completion"""
        session = PromptSession(completer=self.command_completer)
        try:
            command = await session.prompt_async("> ")
            if command:
                self.command_history.append(command)
                self.command_index = len(self.command_history)
            return command
        except (EOFError, KeyboardInterrupt):
            return None

    def _format_json(self, data: Any) -> str:
        """Format JSON data with syntax highlighting"""
        return Syntax(
            json.dumps(data, indent=2),
            "json",
            theme="monokai",
            word_wrap=True
        )

    async def ensure_connected(self):
        """Ensure connection is active, attempt reconnect if needed"""
        if not self.connected and self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                await self.connect_to_server(sys.argv[1])
            except Exception as e:
                self.console.print(f"[red]Failed to reconnect: {str(e)}[/red]")

    async def _execute_command(self, command: str):
        """Execute MCP command with rich formatting and connection management"""
        try:
            await self.ensure_connected()
            if not self.connected:
                self.console.print("[red]Not connected to server[/red]")
                return
                
            # Parse command
            parts = command.split()
            if not parts:
                return
                
            cmd, *args = parts
            
            # Handle MCP commands
            if cmd == "call":
                if len(args) < 2:
                    self.output_field.text += "\nUsage: call <tool> <args...>"
                    return
                    
                tool = args[0]
                tool_args = json.loads(" ".join(args[1:]))
                result = await self.session.call_tool(tool, tool_args)
                
                # Rich formatting for tool results
                panel = Panel(
                    self._format_json(result),
                    title=f"[cyan]Tool Result: {tool}[/cyan]",
                    border_style="green"
                )
                self.console.print(panel)
                
            elif cmd == "list":
                what = args[0] if args else "tools"
                if what == "tools":
                    tools = await self.session.list_tools()
                    table = Table(
                        title="[bold cyan]Available Tools[/bold cyan]",
                        show_header=True,
                        header_style="bold magenta"
                    )
                    table.add_column("Name")
                    table.add_column("Description")
                    table.add_column("Schema", overflow="fold")
                    
                    for tool in tools:
                        table.add_row(
                            f"[green]{tool.name}[/green]",
                            tool.description or "",
                            Syntax(
                                json.dumps(tool.input_schema, indent=2),
                                "json",
                                theme="monokai"
                            )
                        )
                    self.console.print(table)
                
                elif what == "resources":
                    resources = await self.session.list_resources()
                    table = Table(title="[bold cyan]Available Resources[/bold cyan]")
                    table.add_column("URI", style="green")
                    table.add_column("Description")
                    table.add_column("Type")
                    
                    for resource in resources:
                        table.add_row(
                            resource.uri,
                            resource.description or "",
                            f"[dim]{resource.mime_type}[/dim]"
                        )
                    self.console.print(table)
                
            elif cmd == "help":
                help_text = """
                [bold cyan]Available Commands[/bold cyan]
                
                [green]call[/green] <tool> <args>  Execute MCP tool
                [green]list[/green] [tools|resources]  List available tools/resources
                [green]help[/green]  Show this help
                [green]quit[/green]  Exit client
                
                [bold cyan]Modal Keys[/bold cyan]
                
                ESC  Normal mode
                i    Insert mode
                v    Visual mode
                :    Command mode
                """
                self.console.print(Panel(help_text, title="Help"))
                
            elif cmd == "quit":
                self.app.exit()
                
            else:
                self.console.print(f"[red]Unknown command:[/red] {cmd}")
                
        except Exception as e:
            self.console.print(f"[red]Error executing command:[/red] {str(e)}")
            if not self.connected:
                self.console.print("[yellow]Connection lost, attempting to reconnect...[/yellow]")
                await self.ensure_connected()

    async def connect_to_server(self, server_script_path: str, retry: bool = True):
        """Connect to MCP server with proper lifecycle management and retry logic"""
        # Validate server script
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
            
        # Setup server process
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        while True:
            try:
                # Initialize transport
                stdio_transport = await self.exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                self.stdio, self.write = stdio_transport
                
                # Create and initialize client
                self.mcp_client = MCPBaseClient()
                self.session = await self.exit_stack.enter_async_context(
                    ClientSession(self.stdio, self.write)
                )
                await self.session.initialize()
                
                self.connected = True
                self.reconnect_attempts = 0
                
                # List available tools
                response = await self.session.list_tools()
                tools = response.tools
                self.console.print(
                    Panel(
                        "\n".join([
                            f"[green]{tool.name}[/green]: {tool.description}" 
                            for tool in tools
                        ]),
                        title="[bold]Available Tools[/bold]",
                        border_style="cyan"
                    )
                )
                break

            except Exception as e:
                await self.cleanup()
                self.reconnect_attempts += 1
                
                if not retry or self.reconnect_attempts >= self.max_reconnect_attempts:
                    raise RuntimeError(f"Failed to connect to server after {self.reconnect_attempts} attempts: {str(e)}")
                
                wait_time = min(2 ** self.reconnect_attempts, 30)  # Exponential backoff
                self.console.print(f"[yellow]Connection failed, retrying in {wait_time}s...[/yellow]")
                await asyncio.sleep(wait_time)

    async def cleanup(self):
        """Clean up resources properly"""
        if self.exit_stack:
            await self.exit_stack.aclose()
            self.stdio = None
            self.write = None
            self.mcp_client = None
            self.session = None
            self.connected = False

    async def run(self):
        """Run the client application with proper cleanup"""
        try:
            await self.app.run_async()
        finally:
            await self.cleanup()

async def main():
    """Main entry point with error handling"""
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
        
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.run()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        await client.cleanup()

def entry_point():
    """Entry point for console_scripts"""
    asyncio.run(main())

if __name__ == "__main__":
    main()
