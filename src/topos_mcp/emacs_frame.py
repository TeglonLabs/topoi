#!/usr/bin/env python3

from textual.app import App
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static
from textual.binding import Binding
from textual.reactive import reactive
from rich.syntax import Syntax
from rich.text import Text

class Buffer(Static):
    """Emacs buffer representation"""
    content = reactive("")
    mode = reactive("fundamental")
    modified = reactive(False)
    
    def __init__(self, name="*scratch*", content="", mode="fundamental"):
        super().__init__()
        self.name = name
        self.content = content
        self.mode = mode
    
    def render(self):
        if self.mode in ["lisp", "scheme", "racket"]:
            return Syntax(
                self.content or "",
                "lisp",
                theme="monokai",
                line_numbers=True,
                word_wrap=True
            )
        return Text(self.content)

class ModeLine(Static):
    """Emacs-style mode line"""
    def __init__(self, buffer: Buffer):
        super().__init__()
        self.buffer = buffer
    
    def render(self):
        modified = "**" if self.buffer.modified else "--"
        return Text(
            f"{modified} {self.buffer.name}    ({self.buffer.mode})    "
            f"Bot L1     (Fundamental)"
        )

class MiniBuffer(Static):
    """Emacs mini-buffer for commands and messages"""
    content = reactive("")
    
    def render(self):
        return Text(self.content or "[No active minibuffer]")

class EmacsFrame(App):
    """Emacs-like frame using Textual"""
    
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
    
    Buffer {
        background: #2d2d2d;
        color: #d4d4d4;
        height: 1fr;
        border: solid #404040;
    }
    
    ModeLine {
        background: #404040;
        color: #d4d4d4;
        height: 1;
    }
    
    MiniBuffer {
        background: #1a1a1a;
        color: #d4d4d4;
        dock: bottom;
        height: 1;
    }
    
    #main-container {
        height: 100%;
        background: #2d2d2d;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+x,ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+g", "keyboard_quit", "Keyboard Quit", show=True),
        Binding("alt+x", "execute_extended_command", "M-x", show=True),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_buffer = Buffer(
            name="*scratch*",
            content=";; This buffer is for text that is not saved\n"
                   ";; and for Lisp evaluation.\n\n",
            mode="lisp"
        )
    
    def compose(self):
        """Create the Emacs-like frame layout"""
        yield Header("GNU Emacs")
        
        with Container(id="main-container"):
            yield self.current_buffer
            yield ModeLine(self.current_buffer)
        
        yield MiniBuffer()
    
    def action_keyboard_quit(self):
        """Handle C-g (keyboard-quit)"""
        self.query_one(MiniBuffer).content = "Quit"
    
    def action_execute_extended_command(self):
        """Handle M-x"""
        self.query_one(MiniBuffer).content = "M-x "
    
    def action_quit(self):
        """Handle C-x C-c"""
        self.exit()

def main():
    app = EmacsFrame()
    app.run()

if __name__ == "__main__":
    main()
