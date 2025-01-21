#!/usr/bin/env python3
import duckdb
import json
import random
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, Tree
from textual.widgets.tree import TreeNode
from rich.syntax import Syntax
from rich.text import Text

class FileViewer(Static):
    def __init__(self, path: str = "", content: str = ""):
        super().__init__()
        self.path = path
        self.content = content
    
    def on_mount(self) -> None:
        self.update_content(self.path, self.content)
    
    def update_content(self, path: str, content: str) -> None:
        self.path = path
        self.content = content
        
        if path.endswith(('.py', '.rs', '.ts', '.js')):
            syntax = Syntax(content, path.split('.')[-1], theme="monokai", line_numbers=True)
            self.update(syntax)
        elif path.endswith(('.md', '.txt')):
            self.update(Text(content))
        else:
            self.update(Text(f"Binary or unknown file type: {path}"))

class DirectoryExplorer(Container):
    def __init__(self):
        super().__init__()
        self._tree = None

    def compose(self) -> ComposeResult:
        yield Tree("Workspace")
        
    def on_mount(self) -> None:
        self._tree = self.query_one(Tree)
        self._tree.root.expand()
        
    def update_tree(self, path: str, children: List[Dict[str, Any]]) -> None:
        if not self._tree:
            return
            
        self._tree.clear()
        self._tree.root.label = path
        self._tree.root.expand()
        
        for child in sorted(children, key=lambda x: x['name']):
            node = self._tree.root.add(
                child['name'],
                data={
                    'path': child['path'],
                    'is_dir': child['is_dir'],
                    'modified': child['modified']
                }
            )
            if child['is_dir']:
                node.set_label(f"📁 {child['name']}")
            else:
                node.set_label(f"📄 {child['name']}")

class RandomWalkApp(App):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
    }
    
    DirectoryExplorer {
        height: 100%;
        border: solid green;
    }
    
    FileViewer {
        height: 100%;
        border: solid blue;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.db_dir = Path('../.bmorphism')
        self.duck_conn = duckdb.connect(str(self.db_dir / 'topos.duckdb'))
        self.current_workspace = None
        self.current_path = None
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield DirectoryExplorer()
        yield FileViewer()
        yield Footer()
        
    def on_mount(self) -> None:
        self.explorer = self.query_one(DirectoryExplorer)
        self.viewer = self.query_one(FileViewer)
        self.take_random_step()
        
    def get_random_workspace(self) -> str:
        workspaces = ['infinity_topos', 'topos', 'sheaf', 'worlds']
        return random.choice(workspaces)
        
    def get_workspace_children(self, workspace: str) -> List[Dict[str, Any]]:
        result = self.duck_conn.sql(f"""
            SELECT {workspace}_tree::json->'children' as children
            FROM workspace_snapshots
            ORDER BY timestamp DESC
            LIMIT 1
        """).df()
        
        if len(result) > 0 and result['children'][0]:
            return json.loads(result['children'][0])
        return []
        
    def take_random_step(self) -> None:
        workspace = self.get_random_workspace()
        children = self.get_workspace_children(workspace)
        
        if children:
            self.current_workspace = workspace
            base_path = str(Path.home() / workspace.replace('_', '-'))
            self.explorer.update_tree(base_path, children)
            
            # Try to select a random file to view
            files = [c for c in children if not c['is_dir']]
            if files:
                file = random.choice(files)
                try:
                    with open(file['path']) as f:
                        content = f.read()
                    self.viewer.update_content(file['path'], content)
                except Exception as e:
                    self.viewer.update_content(file['path'], f"Error reading file: {e}")
    
    def key_t(self) -> None:
        """Take a random step when 't' is pressed"""
        self.take_random_step()

if __name__ == "__main__":
    app = RandomWalkApp()
    app.run()
