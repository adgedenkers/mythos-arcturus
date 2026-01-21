#!/usr/bin/env python3
"""
MCP Server for Mythos Diagnostics
Exposes system diagnostic tools to LLM via Model Context Protocol
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

# Add graph logging to path
sys.path.insert(0, '/opt/mythos/graph_logging/src')

from diagnostics import Diagnostics

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: MCP library not installed. Run: pip install mcp")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/mythos/llm_diagnostics/logs/mcp_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MCPServer')


class MythosM CPServer:
    """MCP Server exposing Mythos diagnostic tools"""
    
    def __init__(self):
        self.server = Server("mythos-diagnostics")
        self.diagnostics = None
        self._setup_tools()
    
    def _setup_tools(self):
        """Register all diagnostic tools with MCP server"""
        
        # Tool 1: Get System Health
        @self.server.tool()
        async def get_system_health() -> List[TextContent]:
            """
            Get current system health status including metrics and recent issues.
            Returns health score (0-100), active processes, service statuses, and recent problems.
            """
            try:
                if not self.diagnostics:
                    self.diagnostics = Diagnostics()
                
                health = self.diagnostics.get_system_health()
                
                return [TextContent(
                    type="text",
                    text=json.dumps(health, indent=2, default=str)
                )]
            except Exception as e:
                logger.error(f"Error in get_system_health: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        # Tool 2: Trace Failure
        @self.server.tool()
        async def trace_failure(service_name: str) -> List[TextContent]:
            """
            Trace the root cause of a service failure.
            
            Args:
                service_name: Name of the failed service (e.g., "neo4j-backup", "mythos_api")
            
            Returns detailed causality chain showing what led to the failure.
            """
            try:
                if not self.diagnostics:
                    self.diagnostics = Diagnostics()
                
                trace = self.diagnostics.trace_failure(service_name=service_name)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(trace, indent=2, default=str)
                )]
            except Exception as e:
                logger.error(f"Error in trace_failure: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        # Tool 3: Get Recent Events
        @self.server.tool()
        async def get_recent_events(
            minutes: int = 60,
            event_types: Optional[str] = None
        ) -> List[TextContent]:
            """
            Get recent system events.
            
            Args:
                minutes: Look back this many minutes (default: 60)
                event_types: Comma-separated event types to filter by (optional)
                            Examples: "high_cpu,high_memory" or "service_failure"
            
            Returns list of events with timestamps and details.
            """
            try:
                if not self.diagnostics:
                    self.diagnostics = Diagnostics()
                
                types_list = None
                if event_types:
                    types_list = [t.strip() for t in event_types.split(',')]
                
                events = self.diagnostics.get_recent_events(
                    minutes=minutes,
                    event_types=types_list
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(events, indent=2, default=str)
                )]
            except Exception as e:
                logger.error(f"Error in get_recent_events: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        # Tool 4: Get Service Status
        @self.server.tool()
        async def get_service_status(service_name: Optional[str] = None) -> List[TextContent]:
            """
            Get current status of systemd service(s).
            
            Args:
                service_name: Specific service to check (optional, returns all if not provided)
                            Examples: "neo4j", "postgresql", "mythos_api"
            
            Returns service status, substate, and recent issues.
            """
            try:
                if not self.diagnostics:
                    self.diagnostics = Diagnostics()
                
                status = self.diagnostics.get_service_status(service_name=service_name)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(status, indent=2, default=str)
                )]
            except Exception as e:
                logger.error(f"Error in get_service_status: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        # Tool 5: Get High Resource Processes
        @self.server.tool()
        async def get_high_resource_processes(
            memory_threshold: float = 10.0,
            cpu_threshold: float = 50.0
        ) -> List[TextContent]:
            """
            Get processes using high CPU or memory resources.
            
            Args:
                memory_threshold: Memory percent threshold (default: 10%)
                cpu_threshold: CPU percent threshold (default: 50%)
            
            Returns list of high-resource processes with their usage stats.
            """
            try:
                if not self.diagnostics:
                    self.diagnostics = Diagnostics()
                
                processes = self.diagnostics.get_high_resource_processes(
                    memory_threshold=memory_threshold,
                    cpu_threshold=cpu_threshold
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(processes, indent=2, default=str)
                )]
            except Exception as e:
                logger.error(f"Error in get_high_resource_processes: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        # Tool 6: Predict Failure
        @self.server.tool()
        async def predict_failure(
            service_name: str,
            lookback_days: int = 30
        ) -> List[TextContent]:
            """
            Predict potential service failure based on historical patterns.
            
            Args:
                service_name: Service to analyze (e.g., "neo4j-backup", "mythos_api")
                lookback_days: How far back to analyze patterns (default: 30)
            
            Returns prediction with risk level and warning patterns.
            """
            try:
                if not self.diagnostics:
                    self.diagnostics = Diagnostics()
                
                prediction = self.diagnostics.predict_failure(
                    service_name=service_name,
                    lookback_days=lookback_days
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(prediction, indent=2, default=str)
                )]
            except Exception as e:
                logger.error(f"Error in predict_failure: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting Mythos MCP Server")
        
        # Initialize diagnostics connection
        try:
            self.diagnostics = Diagnostics()
            logger.info("Connected to Neo4j diagnostics")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
        
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP Server ready and listening")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point"""
    try:
        server = MythosMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
