#!/usr/bin/env python3

from textual.app import App
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, Input
from textual.binding import Binding
from rich.syntax import Syntax
from rich.text import Text
from .guile_bridge import setup_environment, SchemeResult

class SchemeBuffer(Static):
    """Buffer for Scheme code"""
    
    def __init__(self):
        super().__init__()
        self.content = ""
        self.result = None
        self.guile = setup_environment()
    
    def on_mount(self):
        """Initialize buffer"""
        self.content = ";; Guile Scheme REPL\n;; Type expressions to evaluate\n\n"
        self.refresh()
    
    def evaluate(self, code: str):
        """Evaluate Scheme code"""
        result = self.guile.eval_string(code)
        if result.error:
            self.content += f"\n;; Error: {result.error}"
        else:
            self.content += f"\n{code}\n;; => {result.value}"
        self.content += "\n"
        self.refresh()
    
    def render(self):
        """Render buffer content"""
        return Syntax(
            self.content,
            "scheme",
            theme="monokai",
            line_numbers=True,
            word_wrap=True
        )

class InputBar(Input):
    """Input bar for Scheme expressions"""
    
    def __init__(self):
        super().__init__(placeholder="Enter Scheme expression...")
    
    def on_input_submitted(self, event):
        """Handle input submission"""
        if event.value.strip():
            self.app.evaluate_expression(event.value)
            self.value = ""

class SchemeTUI(App):
    """Simple Scheme TUI"""
    
    CSS = """
    Screen {
        background: #2d2d2d;
    }
    
    Header {
        background: #1a1a1a;
        color: #d4d4d4;
        dock: top;
        height: 1;
        content-align: center middle;
    }
    
    Footer {
        background: #1a1a1a;
        color: #d4d4d4;
        dock: bottom;
        height: 1;
    }
    
    SchemeBuffer {
        background: #2d2d2d;
        color: #d4d4d4;
        height: 1fr;
        border: solid #404040;
    }
    
    InputBar {
        background: #1a1a1a;
        color: #d4d4d4;
        height: 3;
        border: solid #404040;
        padding: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+l", "clear", "Clear", show=True),
    ]
    
    def compose(self):
        """Create the TUI layout"""
        yield Header("Guile Scheme")
        
        with Container():
            self.buffer = SchemeBuffer()
            yield self.buffer
            self.input = InputBar()
            yield self.input
        
        yield Footer()
    
    def evaluate_expression(self, expr: str):
        """Evaluate Scheme expression"""
        self.buffer.evaluate(expr)
    
    def action_clear(self):
        """Clear the buffer"""
        self.buffer.content = ";; Buffer cleared\n\n"
        self.buffer.refresh()
    
    def action_quit(self):
        """Quit the application"""
        self.exit()

def main():
    app = SchemeTUI()
    app.run()

if __name__ == "__main__":
    main()
