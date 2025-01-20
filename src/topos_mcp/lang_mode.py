#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from .meta_lang import MetaLanguage, Token, AST
from rich.syntax import Syntax
from rich.text import Text

@dataclass
class Position:
    """Buffer position"""
    line: int
    column: int

class LangMode:
    """Language mode for meta-language integration"""
    
    def __init__(self):
        self.lang = MetaLanguage()
        self.env = self.lang.environment
        self.current_form: Optional[AST] = None
        self.error_positions: List[Position] = []
        self.highlights: Dict[Position, str] = {}
    
    def evaluate_buffer(self, content: str) -> tuple[Any, List[str]]:
        """Evaluate buffer content"""
        try:
            tokens = self.lang.tokenize(content)
            ast = self.lang.parse(tokens)
            if ast:
                result = self.lang.evaluate(ast, self.env)
                return result, []
            return None, []
        except Exception as e:
            return None, [str(e)]
    
    def get_current_form(self, content: str, pos: Position) -> Optional[AST]:
        """Get the current form at position"""
        try:
            tokens = self.lang.tokenize(content)
            for i, token in enumerate(tokens):
                if token.line == pos.line and token.column <= pos.column:
                    if i + 1 < len(tokens) and tokens[i + 1].line == pos.line:
                        continue
                    # Find the enclosing form
                    depth = 0
                    start = i
                    while start >= 0:
                        if tokens[start].type == self.lang.TokenType.RPAREN:
                            depth += 1
                        elif tokens[start].type == self.lang.TokenType.LPAREN:
                            if depth == 0:
                                break
                            depth -= 1
                        start -= 1
                    if start >= 0:
                        form_tokens = tokens[start:i+1]
                        return self.lang.parse(form_tokens)
            return None
        except Exception:
            return None
    
    def get_documentation(self, symbol: str) -> Optional[str]:
        """Get documentation for a symbol"""
        if symbol in self.env:
            value = self.env[symbol]
            if hasattr(value, '__doc__'):
                return value.__doc__
            return f"Value: {value}"
        return None
    
    def format_code(self, content: str) -> str:
        """Format code with proper indentation"""
        try:
            tokens = self.lang.tokenize(content)
            depth = 0
            formatted = []
            current_line = []
            
            for token in tokens:
                if token.type == self.lang.TokenType.LPAREN:
                    if current_line:
                        formatted.append(''.join(current_line))
                        current_line = []
                    current_line.append('  ' * depth + token.value)
                    depth += 1
                elif token.type == self.lang.TokenType.RPAREN:
                    depth = max(0, depth - 1)
                    current_line.append(token.value)
                    if depth == 0:
                        formatted.append(''.join(current_line))
                        current_line = []
                else:
                    if not current_line:
                        current_line.append('  ' * depth)
                    current_line.append(token.value)
                    if token.type == self.lang.TokenType.COMMENT:
                        formatted.append(''.join(current_line))
                        current_line = []
            
            if current_line:
                formatted.append(''.join(current_line))
            
            return '\n'.join(formatted)
        except Exception:
            return content
    
    def get_syntax_highlighted(self, content: str) -> Syntax:
        """Get syntax highlighted content"""
        return Syntax(
            content,
            "lisp",
            theme="monokai",
            line_numbers=True,
            word_wrap=True
        )
    
    def get_completion_items(self, prefix: str) -> List[str]:
        """Get completion items for prefix"""
        items = []
        for symbol in self.env:
            if symbol.startswith(prefix):
                items.append(symbol)
        return items
    
    def check_syntax(self, content: str) -> List[str]:
        """Check syntax and return errors"""
        errors = []
        try:
            tokens = self.lang.tokenize(content)
            depth = 0
            for token in tokens:
                if token.type == self.lang.TokenType.LPAREN:
                    depth += 1
                elif token.type == self.lang.TokenType.RPAREN:
                    depth -= 1
                    if depth < 0:
                        errors.append(f"Unexpected closing parenthesis at line {token.line}")
            if depth > 0:
                errors.append(f"Missing {depth} closing parenthesis")
            
            # Try parsing if basic syntax is okay
            if not errors:
                self.lang.parse(tokens)
        except Exception as e:
            errors.append(str(e))
        return errors
    
    def get_signature_help(self, content: str, pos: Position) -> Optional[str]:
        """Get signature help for current form"""
        form = self.get_current_form(content, pos)
        if form and form.type == 'list' and form.children:
            first = form.children[0]
            if first.type == 'symbol' and first.value in self.env:
                value = self.env[first.value]
                if hasattr(value, '__doc__'):
                    return value.__doc__
        return None

def create_mode() -> LangMode:
    """Create a new language mode instance"""
    mode = LangMode()
    mode.env.update(MetaLanguage.create_standard_environment())
    return mode
