#!/usr/bin/env python3

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class TokenType(Enum):
    """Token types for the meta-language"""
    LPAREN = "("
    RPAREN = ")"
    SYMBOL = "symbol"
    NUMBER = "number"
    STRING = "string"
    QUOTE = "quote"
    DOT = "."
    COMMENT = ";"
    SPECIAL = "special"

@dataclass
class Token:
    """Token representation"""
    type: TokenType
    value: str
    line: int
    column: int

@dataclass
class AST:
    """Abstract Syntax Tree node"""
    type: str
    value: Any
    children: List['AST']
    meta: Dict[str, Any]

class MetaLanguage:
    """Meta-language implementation foundation"""
    
    def __init__(self):
        self.special_forms = {
            'define': self.eval_define,
            'lambda': self.eval_lambda,
            'if': self.eval_if,
            'quote': self.eval_quote,
            'begin': self.eval_begin
        }
        self.environment = {}
    
    def tokenize(self, code: str) -> List[Token]:
        """Tokenize input code"""
        tokens = []
        line = 1
        column = 1
        i = 0
        
        while i < len(code):
            char = code[i]
            
            # Handle whitespace
            if char.isspace():
                if char == '\n':
                    line += 1
                    column = 1
                else:
                    column += 1
                i += 1
                continue
            
            # Handle comments
            if char == ';':
                while i < len(code) and code[i] != '\n':
                    i += 1
                continue
            
            # Handle parens
            if char in '()':
                tokens.append(Token(
                    type=TokenType.LPAREN if char == '(' else TokenType.RPAREN,
                    value=char,
                    line=line,
                    column=column
                ))
                column += 1
                i += 1
                continue
            
            # Handle symbols and numbers
            if char.isalnum() or char in '+-*/=<>!?':
                start = i
                while i < len(code) and (code[i].isalnum() or code[i] in '+-*/=<>!?'):
                    i += 1
                value = code[start:i]
                
                # Determine if number or symbol
                token_type = TokenType.NUMBER if value.replace('.','',1).isdigit() else TokenType.SYMBOL
                tokens.append(Token(type=token_type, value=value, line=line, column=column))
                column += i - start
                continue
            
            # Handle strings
            if char == '"':
                start = i
                i += 1
                while i < len(code) and code[i] != '"':
                    if code[i] == '\\':
                        i += 2
                    else:
                        i += 1
                i += 1
                tokens.append(Token(
                    type=TokenType.STRING,
                    value=code[start:i],
                    line=line,
                    column=column
                ))
                column += i - start
                continue
            
            i += 1
        
        return tokens
    
    def parse(self, tokens: List[Token]) -> Optional[AST]:
        """Parse tokens into AST"""
        if not tokens:
            return None
        
        def parse_expr(index: int) -> tuple[AST, int]:
            token = tokens[index]
            
            if token.type == TokenType.LPAREN:
                children = []
                index += 1
                while index < len(tokens) and tokens[index].type != TokenType.RPAREN:
                    child, index = parse_expr(index)
                    children.append(child)
                return AST(type='list', value=None, children=children, meta={}), index + 1
            
            elif token.type in (TokenType.SYMBOL, TokenType.NUMBER, TokenType.STRING):
                return AST(
                    type=token.type.value,
                    value=token.value,
                    children=[],
                    meta={'line': token.line, 'column': token.column}
                ), index + 1
            
            raise SyntaxError(f"Unexpected token: {token}")
        
        ast, _ = parse_expr(0)
        return ast
    
    def eval_define(self, ast: AST, env: Dict[str, Any]) -> Any:
        """Evaluate define special form"""
        if len(ast.children) != 2:
            raise SyntaxError("define requires 2 arguments")
        name = ast.children[0].value
        value = self.evaluate(ast.children[1], env)
        env[name] = value
        return value
    
    def eval_lambda(self, ast: AST, env: Dict[str, Any]) -> Any:
        """Evaluate lambda special form"""
        if len(ast.children) < 2:
            raise SyntaxError("lambda requires parameters and body")
        params = [param.value for param in ast.children[0].children]
        body = ast.children[1:]
        return lambda *args: self.evaluate(
            body[-1],
            {**env, **dict(zip(params, args))}
        )
    
    def eval_if(self, ast: AST, env: Dict[str, Any]) -> Any:
        """Evaluate if special form"""
        if len(ast.children) != 3:
            raise SyntaxError("if requires 3 arguments")
        condition = self.evaluate(ast.children[0], env)
        return self.evaluate(
            ast.children[1] if condition else ast.children[2],
            env
        )
    
    def eval_quote(self, ast: AST, env: Dict[str, Any]) -> Any:
        """Evaluate quote special form"""
        if len(ast.children) != 1:
            raise SyntaxError("quote requires 1 argument")
        return ast.children[0]
    
    def eval_begin(self, ast: AST, env: Dict[str, Any]) -> Any:
        """Evaluate begin special form"""
        result = None
        for child in ast.children:
            result = self.evaluate(child, env)
        return result
    
    def evaluate(self, ast: AST, env: Dict[str, Any]) -> Any:
        """Evaluate AST"""
        if ast.type == 'symbol':
            return env.get(ast.value)
        elif ast.type == 'number':
            return float(ast.value)
        elif ast.type == 'string':
            return ast.value[1:-1]  # Remove quotes
        elif ast.type == 'list':
            if not ast.children:
                return []
            
            operator = self.evaluate(ast.children[0], env)
            if operator in self.special_forms:
                return self.special_forms[operator](ast, env)
            
            args = [self.evaluate(arg, env) for arg in ast.children[1:]]
            return operator(*args)
        
        raise ValueError(f"Unknown AST type: {ast.type}")

def create_standard_environment() -> Dict[str, Any]:
    """Create standard environment with basic operations"""
    import operator as op
    env = {
        '+': op.add,
        '-': op.sub,
        '*': op.mul,
        '/': op.truediv,
        '=': op.eq,
        '<': op.lt,
        '>': op.gt,
        '<=': op.le,
        '>=': op.ge,
        'list': lambda *x: list(x),
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x, y: [x] + y,
        'null?': lambda x: len(x) == 0,
        'display': print
    }
    return env
