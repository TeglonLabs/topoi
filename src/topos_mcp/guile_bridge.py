#!/usr/bin/env python3

import subprocess
from typing import Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SchemeResult:
    """Result from Guile evaluation"""
    value: str
    error: Optional[str] = None

class GuileBridge:
    """Simple bridge to Guile Scheme"""
    
    def __init__(self):
        self.check_guile()
    
    def check_guile(self):
        """Verify Guile is available"""
        try:
            subprocess.run(
                ["guile", "--version"],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError:
            raise RuntimeError("Guile Scheme not found. Please install guile-3.0")
    
    def eval_string(self, code: str) -> SchemeResult:
        """Evaluate Scheme code string"""
        try:
            proc = subprocess.run(
                ["guile", "--no-auto-compile", "-c", code],
                capture_output=True,
                text=True,
                check=False
            )
            if proc.returncode == 0:
                return SchemeResult(proc.stdout.strip())
            return SchemeResult("", proc.stderr.strip())
        except Exception as e:
            return SchemeResult("", str(e))
    
    def load_file(self, path: Path) -> SchemeResult:
        """Load and evaluate Scheme file"""
        try:
            proc = subprocess.run(
                ["guile", "--no-auto-compile", str(path)],
                capture_output=True,
                text=True,
                check=False
            )
            if proc.returncode == 0:
                return SchemeResult(proc.stdout.strip())
            return SchemeResult("", proc.stderr.strip())
        except Exception as e:
            return SchemeResult("", str(e))
    
    def start_repl(self) -> subprocess.Popen:
        """Start interactive Guile REPL"""
        return subprocess.Popen(
            ["guile", "--no-auto-compile"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

def create_initial_environment() -> str:
    """Create initial Scheme environment"""
    return """
(use-modules (ice-9 textual-ports))
(use-modules (ice-9 format))

;; Basic utilities
(define (display-error msg)
  (format (current-error-port) "~a~%" msg))

(define (read-file path)
  (call-with-input-file path
    (lambda (port)
      (get-string-all port))))

(define (write-file path content)
  (call-with-output-file path
    (lambda (port)
      (put-string port content))))

;; REPL utilities
(define (clear-screen)
  (display "\x1B[2J\x1B[H"))

(define (colored-output str color)
  (format #t "\x1B[~am~a\x1B[0m" color str))

;; Simple test framework
(define-syntax test
  (syntax-rules ()
    ((_ name expr expected)
     (let ((result expr))
       (if (equal? result expected)
           (format #t "✓ ~a~%" name)
           (format #t "✗ ~a: expected ~a, got ~a~%" 
                  name expected result))))))

;; Basic error handling
(define-syntax guard
  (syntax-rules ()
    ((_ (var clause ...) e1 e2 ...)
     (call-with-current-continuation
      (lambda (k)
        (with-exception-handler
         (lambda (condition)
           (k (let ((var condition))
                clause ...)))
         (lambda ()
           e1 e2 ...)))))))
"""

def setup_environment() -> GuileBridge:
    """Setup Guile environment with initial definitions"""
    bridge = GuileBridge()
    result = bridge.eval_string(create_initial_environment())
    if result.error:
        raise RuntimeError(f"Failed to setup Guile environment: {result.error}")
    return bridge
