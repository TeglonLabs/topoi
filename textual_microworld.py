#!/usr/bin/env python3
"""
Textual-based TUI prototype that visualizes a hypergraph with random walks
using DisCoPy's hypergraph visualization capabilities.
"""

import io
import tempfile
from PIL import Image
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll, Horizontal, Grid
from textual.screen import Screen
from textual.widgets import Static, Footer, Header, Button, Label
from textual.reactive import reactive
import discopy as dc
from discopy.frobenius import Ty, Box, Hypergraph
import random

class HypergraphViewer(Static):
    """Widget that shows the hypergraph visualization."""
    
    current_walk = reactive([])
    
    def __init__(self) -> None:
        super().__init__()
        self.setup_example_graph()
        self.update_display()

    def setup_example_graph(self):
        """Create a simple but effective hypergraph structure using DisCoPy."""
        # Create types
        x, y, z = map(Ty, "xyz")
        
        # Create forward morphisms
        f = Box('f', x, y).to_hypergraph()  # x -> y
        g = Box('g', y, z).to_hypergraph()  # y -> z
        h = Box('h', z, x).to_hypergraph()  # z -> x
        
        # Create backward morphisms for bidirectional edges
        f_back = Box('f*', y, x).to_hypergraph()  # y -> x
        g_back = Box('g*', z, y).to_hypergraph()  # z -> y
        h_back = Box('h*', x, z).to_hypergraph()  # x -> z
        
        # Create spiders for each type
        spider_x = Hypergraph.spiders(1, 1, x)  # Identity on x
        spider_y = Hypergraph.spiders(1, 1, y)  # Identity on y
        spider_z = Hypergraph.spiders(1, 1, z)  # Identity on z
        
        # Compose the hypergraph
        # First compose forward and backward morphisms in parallel
        morphisms = f @ g @ h @ f_back @ g_back @ h_back
        
        # Then compose spiders in parallel
        spiders = spider_x @ spider_y @ spider_z
        
        # Finally compose spiders with morphisms
        self.graph = spiders >> morphisms
        
        # Store vertex names for random walks
        self.vertex_names = ["x", "y", "z"]
        
        # Create adjacency information for random walks (bidirectional)
        self.adjacency = {
            'x': ['y', 'z'],  # Can go to y via f or z via h*
            'y': ['x', 'z'],  # Can go to x via f* or z via g
            'z': ['x', 'y']   # Can go to x via h or y via g*
        }

    def update_display(self) -> None:
        """Update the visualization using DisCoPy's draw method."""
        # Create a temporary file for the image
        with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
            # Draw the hypergraph with highlighted walk if exists
            self.graph.draw(path=tmp.name, seed=42)
            
            # Convert to ASCII art
            img = Image.open(tmp.name)
            ascii_art = self.image_to_ascii(img)
            
            # Add diagram labels and description
            ascii_art = (
                "DisCoPy Hypergraph Visualization\n"
                "==============================\n\n"
                "Structure:\n"
                "- Types: x, y, z\n"
                "- Forward Morphisms:\n"
                "  • f:  x → y\n"
                "  • g:  y → z\n"
                "  • h:  z → x\n"
                "- Backward Morphisms:\n"
                "  • f*: y → x\n"
                "  • g*: z → y\n"
                "  • h*: x → z\n"
                "- Spiders: Identity on each type\n\n"
                "Properties:\n"
                "- Bidirectional: Each edge has forward/backward morphisms\n"
                "- Connected: Every vertex connects to every other\n"
                "- Symmetric: Equal paths in both directions\n\n"
                "Diagram:\n"
                + ascii_art
            )
            
            # Add walk information with more context
            if self.current_walk:
                path_str = " -> ".join(self.current_walk)
                steps = len(self.current_walk)
                ascii_art += (
                    "\n\nRandom Walk:\n"
                    f"Path: {path_str}\n"
                    f"Steps: {steps}\n"
                    f"Unique Types: {len(set(self.current_walk))}/{steps}\n"
                    "Note: Walk uses both forward and backward morphisms"
                )
            
            self.update(ascii_art)

    def image_to_ascii(self, img, width=80):
        """Convert PIL Image to ASCII art."""
        # Resize image maintaining aspect ratio
        aspect_ratio = img.height / img.width
        height = int(width * aspect_ratio * 0.5)  # * 0.5 to account for terminal char height
        img = img.resize((width, height))
        img = img.convert('L')  # Convert to grayscale
        
        # ASCII chars by intensity (darkest to lightest)
        ascii_chars = '@%#*+=-:. '
        
        # Convert pixels to ASCII
        pixels = img.getdata()
        ascii_str = ''
        for i, pixel in enumerate(pixels):
            ascii_str += ascii_chars[pixel * len(ascii_chars) // 256]
            if (i + 1) % width == 0:
                ascii_str += '\n'
        
        return ascii_str

    def take_random_walk(self, steps: int = 4) -> None:
        """Perform a random walk on the hypergraph."""
        if not self.vertex_names:
            return
            
        # Start from random vertex
        current = random.choice(self.vertex_names)
        walk = [current]
        
        # Take random steps following adjacency
        for _ in range(steps - 1):
            neighbors = self.adjacency[current]
            if not neighbors:
                break
            current = random.choice(neighbors)
            walk.append(current)
            
        self.current_walk = walk
        self.update_display()


class EventLog(Static):
    """Widget to display events and graph information."""

    def __init__(self) -> None:
        super().__init__("Event Log:\n\n(No events yet...)")

    def add_event(self, event_text: str) -> None:
        """Append a new event message."""
        existing = self.renderable
        if isinstance(existing, str):
            new_text = existing + f"\n{event_text}"
            self.update(new_text)


class MicroworldScreen(Screen):
    """Main screen for the microworld TUI."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "random_walk", "Random Walk"),
        ("c", "clear_log", "Clear Log")
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        with Container():
            with Horizontal():
                viewer = HypergraphViewer()
                viewer.id = "graph"
                yield viewer
                log = EventLog()
                log.id = "log"
                yield VerticalScroll(log)
            with Grid(id="controls"):
                walk_btn = Button("Random Walk [r]", variant="primary")
                walk_btn.id = "walk"
                reset_btn = Button("Reset", variant="error")
                reset_btn.id = "reset"
                clear_btn = Button("Clear Log [c]", variant="warning")
                clear_btn.id = "clear"
                yield walk_btn
                yield reset_btn
                yield clear_btn
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "walk":
            viewer = self.query_one("#graph", HypergraphViewer)
            viewer.take_random_walk()
            log = self.query_one("#log", EventLog)
            log.add_event("Started new random walk")
        elif event.button.id == "reset":
            viewer = self.query_one("#graph", HypergraphViewer)
            viewer.current_walk = []
            viewer.update_display()
            log = self.query_one("#log", EventLog)
            log.add_event("Reset visualization")
        elif event.button.id == "clear":
            log = self.query_one("#log", EventLog)
            log.update("Event Log:\n\n(No events yet...)")

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_random_walk(self) -> None:
        """Trigger a random walk."""
        viewer = self.query_one("#graph", HypergraphViewer)
        viewer.take_random_walk()
        log = self.query_one("#log", EventLog)
        log.add_event("Random walk triggered by 'r' key")

    def action_clear_log(self) -> None:
        """Clear the event log."""
        log = self.query_one("#log", EventLog)
        log.update("Event Log:\n\n(No events yet...)")


class TextualMicroworld(App):
    """Main application class."""

    CSS = """
    Screen {
        layout: vertical;
    }

    Container {
        height: 1fr;
    }

    Horizontal {
        height: auto;
        margin: 1;
        align: center middle;
    }

    #controls {
        layout: grid;
        grid-size: 3;
        grid-columns: 1fr 1fr 1fr;
        padding: 1;
        height: 3;
        width: 100%;
        align: center middle;
    }

    Button {
        width: 100%;
        margin: 1 2;
    }

    Button.primary {
        background: $success;
    }

    Button.error {
        background: $error;
    }

    Button.warning {
        background: $warning;
    }

    #graph {
        width: 60%;
        border: heavy blue;
        padding: 1 2;
        background: $panel;
    }

    #log {
        width: 40%;
        border: round yellow;
        padding: 1 2;
        background: $panel;
        height: 100%;
    }
    """

    def on_mount(self) -> None:
        """Runs after the app is fully initialized."""
        self.push_screen(MicroworldScreen())


if __name__ == "__main__":
    TextualMicroworld().run()
