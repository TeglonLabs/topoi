#!/usr/bin/env python3

from textual.app import App
from textual.containers import Grid, Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, Label
from textual.reactive import reactive
from textual.binding import Binding
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich.syntax import Syntax
import json
from functools import partial
from typing import Optional, Dict, Set
import hy

from .world_model import WorldModel, handle_click, handle_time_tick
from .hypergraph import HyperGraph
from shapely.geometry import Point, Polygon

class WorldTile(Static):
    """Interactive tile widget for world visualization"""
    selected = reactive(False)
    x = reactive(0)
    y = reactive(0)
    entity_id = reactive(None)
    
    class Selected(Message):
        """Message sent when tile is selected"""
        def __init__(self, tile: "WorldTile"):
            self.tile = tile
            super().__init__()
    
    def __init__(self, world: WorldModel, *args, **kwargs):
        super().__init__()
        self.world = world
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
    
    def on_mount(self):
        """Initialize tile state"""
        point = Point(self.x, self.y)
        entities = self.world.spatial_query(point)
        if entities:
            self.entity_id = entities[0][0]
    
    def on_click(self):
        """Handle click events"""
        self.selected = not self.selected
        if self.selected:
            self.post_message(self.Selected(self))
    
    def watch_selected(self, old_value: bool, new_value: bool):
        """Update display when selection changes"""
        if new_value:
            self.styles.background = "blue"
        else:
            self.styles.background = self.get_tile_color()
    
    def get_tile_color(self) -> str:
        """Get tile color based on entity type"""
        if not self.entity_id:
            return "#1a1a1a"
        entity = self.world.graph.backends['duckdb'].get_vertex(self.entity_id)
        if not entity:
            return "#1a1a1a"
        
        entity_type = entity.get('type', 'default')
        colors = {
            'region': "#4a9eff",
            'tile': "#2a2a2a",
            'default': "#3a3a3a"
        }
        return colors.get(entity_type, "#3a3a3a")

class InfoPanel(Static):
    """Panel showing information about selected entities"""
    
    def __init__(self):
        super().__init__()
        self.selected_tile = None
    
    def update_info(self, tile: WorldTile):
        """Update displayed information"""
        self.selected_tile = tile
        self.refresh()
    
    def render(self):
        """Render panel content"""
        if not self.selected_tile or not self.selected_tile.entity_id:
            return Panel("No tile selected")
        
        entity_id = self.selected_tile.entity_id
        neighbors = self.selected_tile.world.get_neighbors(entity_id)
        
        content = [
            f"Entity: {entity_id}",
            "Neighbors:",
            *[f"- {n}" for backend_neighbors in neighbors.values() 
              for n in backend_neighbors],
            "",
            "Properties:",
            *[f"{k}: {v}" for k, v in 
              self.selected_tile.world.graph.backends['duckdb']
                  .get_vertex(entity_id).items()]
        ]
        
        return Panel("\n".join(content))

class ToposTUI(App):
    """Main application"""
    CSS = """
    Screen {
        layout: grid;
        grid-size: 1 2;
        grid-columns: 4fr 1fr;
    }
    
    Grid {
        grid-size: 10 10;
        grid-gutter: 1;
        padding: 1;
    }
    
    WorldTile {
        width: 100%;
        height: 100%;
        content-align: center middle;
        background: #1a1a1a;
    }
    
    InfoPanel {
        dock: right;
        width: 30;
        height: 100%;
        background: $boost;
        color: $text;
        padding: 1;
    }
    
    Header {
        dock: top;
        background: $boost;
        color: $text;
        text-align: center;
        text-style: bold;
    }
    
    Footer {
        dock: bottom;
        background: $boost;
        color: $text;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("space", "toggle_time", "Toggle Time"),
        Binding("c", "create_region", "Create Region")
    ]
    
    def __init__(self):
        super().__init__()
        self.world = WorldModel()
        self.selected_tiles: Set[WorldTile] = set()
        self.time_running = False
    
    def compose(self):
        """Compose the interface"""
        header = Header()
        header.tall = False
        header.title = "Topos MCP - World Model Visualization"
        
        # Create initial world state
        for x in range(10):
            for y in range(10):
                self.world.create_tile(x, y, type="tile")
        
        # Create grid of tiles
        grid = Grid()
        tiles = [
            WorldTile(self.world, x=x, y=y, id=f"tile-{x}-{y}")
            for x in range(10)
            for y in range(10)
        ]
        
        info_panel = InfoPanel()
        
        return Container(
            header,
            Horizontal(
                grid,
                info_panel,
                id="main-container"
            ),
            *tiles,
            Footer()
        )
    
    def on_world_tile_selected(self, message: WorldTile.Selected):
        """Handle tile selection"""
        if message.tile.selected:
            self.selected_tiles.add(message.tile)
        else:
            self.selected_tiles.remove(message.tile)
        
        # Update info panel
        info_panel = self.query_one(InfoPanel)
        info_panel.update_info(message.tile)
    
    def action_create_region(self):
        """Create region from selected tiles"""
        if len(self.selected_tiles) < 2:
            return
        
        vertices = {tile.entity_id for tile in self.selected_tiles}
        self.world.create_region(vertices, {"type": "region"})
        
        # Clear selection
        for tile in self.selected_tiles:
            tile.selected = False
        self.selected_tiles.clear()
        
        # Refresh display
        self.action_refresh()
    
    def action_toggle_time(self):
        """Toggle time advancement"""
        self.time_running = not self.time_running
        if self.time_running:
            self.advance_time()
    
    def advance_time(self):
        """Advance world time"""
        if self.time_running:
            handle_time_tick(self.world)
            self.action_refresh()
            self.call_later(1, self.advance_time)
    
    def action_refresh(self):
        """Refresh all tiles"""
        for x in range(10):
            for y in range(10):
                tile = self.query_one(f"#tile-{x}-{y}")
                if tile:
                    tile.refresh()
    
    def action_quit(self):
        """Clean up and quit"""
        self.exit()

def main():
    app = ToposTUI()
    app.run()

if __name__ == "__main__":
    main()
