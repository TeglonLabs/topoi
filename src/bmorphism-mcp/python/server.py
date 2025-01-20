#!/usr/bin/env python3
"""
Bmorphism MCP Server - Python Implementation
Handles slowtime operations and integrates with TypeScript drand server
"""

import os
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from mcp.server import Server
import httpx

class BmorphismPythonServer:
    """Python implementation of Bmorphism MCP server focusing on slowtime operations"""
    
    def __init__(self):
        self.app = Server("bmorphism-python-mcp")
        self.client = httpx.AsyncClient(timeout=10.0)
        self.drand_ts_port = os.getenv("DRAND_TS_PORT", "3000")
        self.setup_tools()

    def setup_tools(self):
        """Configure available tools"""
        
        @self.app.tool()
        async def get_slowtime_info(timestamp: Optional[str] = None) -> str:
            """Get slowtime information based on current or provided timestamp
            
            Args:
                timestamp: Optional ISO format timestamp to analyze
            """
            try:
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    dt = datetime.now(timezone.utc)

                # Get latest randomness from TypeScript drand server
                async with self.client.get(f"http://localhost:{self.drand_ts_port}/drand/latest") as response:
                    drand_data = response.json()
                    
                slowtime_data = {
                    "timestamp": dt.isoformat(),
                    "unix_timestamp": int(dt.timestamp()),
                    "drand_round": drand_data.get("round"),
                    "entropy": drand_data.get("randomness"),
                    "temporal_distance": self._calculate_temporal_distance(dt),
                    "morphism_state": self._analyze_morphism_state(dt, drand_data)
                }
                
                return json.dumps(slowtime_data, indent=2)
            except Exception as e:
                return f"Error processing slowtime: {str(e)}"

        @self.app.tool()
        async def analyze_temporal_morphism(start_time: str, end_time: str) -> str:
            """Analyze temporal morphism between two timestamps
            
            Args:
                start_time: ISO format start timestamp
                end_time: ISO format end timestamp
            """
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                
                # Get drand data for both timestamps
                async with self.client.get(f"http://localhost:{self.drand_ts_port}/drand/latest") as response:
                    drand_data = response.json()
                
                analysis = {
                    "interval": {
                        "start": start_dt.isoformat(),
                        "end": end_dt.isoformat(),
                        "duration_seconds": (end_dt - start_dt).total_seconds()
                    },
                    "morphism_properties": {
                        "entropy_delta": self._calculate_entropy_delta(start_dt, end_dt, drand_data),
                        "temporal_coherence": self._analyze_temporal_coherence(start_dt, end_dt),
                        "phase_shift": self._calculate_phase_shift(start_dt, end_dt)
                    },
                    "drand_context": {
                        "reference_round": drand_data.get("round"),
                        "entropy_snapshot": drand_data.get("randomness")
                    }
                }
                
                return json.dumps(analysis, indent=2)
            except Exception as e:
                return f"Error analyzing temporal morphism: {str(e)}"

    def _calculate_temporal_distance(self, dt: datetime) -> float:
        """Calculate normalized temporal distance from reference point"""
        now = datetime.now(timezone.utc)
        delta = abs((now - dt).total_seconds())
        # Normalize to a 0-1 scale using a 24-hour window
        return min(delta / (24 * 3600), 1.0)

    def _analyze_morphism_state(self, dt: datetime, drand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the current morphism state based on timestamp and drand data"""
        entropy = int(drand_data.get("randomness", "0"), 16)
        timestamp = int(dt.timestamp())
        
        return {
            "phase": (entropy + timestamp) % 360,
            "amplitude": (entropy % 100) / 100.0,
            "frequency": ((timestamp % 86400) / 86400.0) * 2 * 3.14159
        }

    def _calculate_entropy_delta(self, start_dt: datetime, end_dt: datetime, drand_data: Dict[str, Any]) -> float:
        """Calculate entropy change between two timestamps"""
        entropy = int(drand_data.get("randomness", "0"), 16)
        start_ts = int(start_dt.timestamp())
        end_ts = int(end_dt.timestamp())
        
        return abs(((entropy + start_ts) % 1000) - ((entropy + end_ts) % 1000)) / 1000.0

    def _analyze_temporal_coherence(self, start_dt: datetime, end_dt: datetime) -> float:
        """Analyze temporal coherence between two timestamps"""
        delta = abs((end_dt - start_dt).total_seconds())
        # Coherence decreases with larger time intervals
        return max(1.0 - (delta / (7 * 24 * 3600)), 0.0)

    def _calculate_phase_shift(self, start_dt: datetime, end_dt: datetime) -> float:
        """Calculate phase shift between two timestamps"""
        start_phase = (int(start_dt.timestamp()) % 86400) / 86400.0
        end_phase = (int(end_dt.timestamp()) % 86400) / 86400.0
        return abs(end_phase - start_phase) * 360  # Convert to degrees

    async def start(self):
        """Start the MCP server"""
        try:
            await self.app.start()
        finally:
            await self.client.aclose()

def main():
    """Entry point for the server"""
    server = BmorphismPythonServer()
    asyncio.run(server.start())

if __name__ == "__main__":
    main()
