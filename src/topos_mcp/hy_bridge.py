#!/usr/bin/env python3

import json
import subprocess
import openai
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
import backoff

# Configuration
SYSTEM_PROMPT = "You are an AI assistant integrating with a Model Context Protocol system."
INITIAL_PROMPT = "Hello, how can I help you today?"
BABASHKA_PATH = "bb/hy-handler.clj"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BridgeState(Enum):
    INIT = "init"
    PROCESSING = "processing"
    TRANSFORMING = "transforming"
    ERROR = "error"

@dataclass
class BridgeMetrics:
    latency: float = 0.0
    throughput: int = 0
    error_rate: float = 0.0

class DataTransformer:
    """Handle data transformations between formats"""
    
    @staticmethod
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def json_to_edn(data: Dict[str, Any]) -> Optional[str]:
        """Convert JSON to EDN with retry logic"""
        try:
            proc = subprocess.run(
                ["jet", "--from", "json", "--to", "edn"],
                input=json.dumps(data).encode("utf-8"),
                capture_output=True,
                check=True
            )
            return proc.stdout.decode("utf-8")
        except subprocess.CalledProcessError as e:
            logger.error(f"EDN conversion failed: {e}")
            raise
    
    @staticmethod
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def edn_to_json(data: str) -> Optional[Dict[str, Any]]:
        """Convert EDN to JSON with retry logic"""
        try:
            proc = subprocess.run(
                ["jet", "--from", "edn", "--to", "json"],
                input=data.encode("utf-8"),
                capture_output=True,
                check=True
            )
            return json.loads(proc.stdout.decode("utf-8"))
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.error(f"JSON conversion failed: {e}")
            raise

class LLMHandler:
    """Handle LLM interactions with streaming support"""
    
    def __init__(self):
        self.client = openai.Client()
    
    async def stream_response(self, prompt: str, system_prompt: str):
        """Stream LLM responses"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"LLM streaming error: {e}")
            raise

class BabashkaBridge:
    """Enhanced bridge between Python and Babashka with state management"""
    
    def __init__(self):
        self.state = BridgeState.INIT
        self.transaction_log = []
        self.metrics = BridgeMetrics()
        self.transformer = DataTransformer()
        self.llm_handler = LLMHandler()
        self.start_time = datetime.now()
        
    def transition_state(self, new_state: BridgeState):
        """Handle state transitions with validation"""
        valid_transitions = {
            BridgeState.INIT: [BridgeState.PROCESSING],
            BridgeState.PROCESSING: [BridgeState.TRANSFORMING, BridgeState.ERROR],
            BridgeState.TRANSFORMING: [BridgeState.PROCESSING, BridgeState.ERROR],
            BridgeState.ERROR: [BridgeState.INIT]
        }
        
        if new_state in valid_transitions.get(self.state, []):
            logger.info(f"State transition: {self.state.value} -> {new_state.value}")
            self.state = new_state
            return True
        return False
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def send_to_babashka(self, data: Dict[str, Any]):
        """Send data to Babashka with retry logic"""
        try:
            edn_str = self.transformer.json_to_edn(data)
            if not edn_str:
                raise ValueError("EDN conversion failed")
            
            proc = await asyncio.create_subprocess_exec(
                "bb", "bb/process.clj",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate(edn_str.encode("utf-8"))
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(
                    proc.returncode, "bb", stdout, stderr
                )
            
            logger.info(f"Babashka response - stdout: {stdout.decode()}")
            if stderr:
                logger.warning(f"Babashka stderr: {stderr.decode()}")
                
            # Update metrics
            self.metrics.throughput += 1
            self.metrics.latency = (datetime.now() - self.start_time).total_seconds()
            
        except Exception as e:
            self.metrics.error_rate += 1
            logger.error(f"Babashka communication error: {e}")
            raise
    
    async def process_llm(self, prompt: str, system_prompt: str):
        """Process LLM response with streaming and state management"""
        try:
            self.transition_state(BridgeState.PROCESSING)
            self.start_time = datetime.now()
            
            async for chunk in self.llm_handler.stream_response(prompt, system_prompt):
                if self.state == BridgeState.ERROR:
                    break
                    
                self.transition_state(BridgeState.TRANSFORMING)
                await self.send_to_babashka({
                    "type": "llm-chunk",
                    "content": chunk,
                    "timestamp": datetime.now().isoformat()
                })
                self.transaction_log.append(chunk)
                self.transition_state(BridgeState.PROCESSING)
                
        except Exception as e:
            self.transition_state(BridgeState.ERROR)
            logger.error(f"LLM processing error: {e}")
            raise

async def main():
    """Asynchronous main entry point"""
    bridge = BabashkaBridge()
    
    if not Path(BABASHKA_PATH).exists():
        raise FileNotFoundError(f"Babashka handler not found at {BABASHKA_PATH}")
    
    try:
        await bridge.process_llm(INITIAL_PROMPT, SYSTEM_PROMPT)
        logger.info(f"Final metrics - Latency: {bridge.metrics.latency:.2f}s, "
                   f"Throughput: {bridge.metrics.throughput}, "
                   f"Error rate: {bridge.metrics.error_rate:.2%}")
    except Exception as e:
        logger.error(f"Bridge execution failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
