#!/usr/bin/env python3
"""
Arcturus System Monitor
Continuously monitors system metrics and logs events to Neo4j graph
"""

import os
import sys
import time
import signal
import logging
import yaml
import psutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from event_logger import EventLoggerFactory


class SystemMonitor:
    """Main system monitoring loop"""
    
    def __init__(self, config_path: str):
        """Initialize monitor with configuration"""
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.event_logger = None
        self.running = False
        self.last_states = {}  # Track previous states for change detection
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Expand environment variables in config
        self._expand_env_vars(config)
        return config
    
    def _expand_env_vars(self, obj):
        """Recursively expand ${VAR} in config"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                    var_name = value[2:-1]
                    obj[key] = os.environ.get(var_name, value)
                elif isinstance(value, (dict, list)):
                    self._expand_env_vars(value)
        elif isinstance(obj, list):
            for item in obj:
                self._expand_env_vars(item)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging to file"""
        log_config = self.config.get('logging', {})
        log_file = log_config.get('file', '/opt/mythos/graph_logging/logs/monitor.log')
        log_level = log_config.get('level', 'INFO')
        
        # Ensure log directory exists
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger('SystemMonitor')
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def start(self):
        """Start the monitoring loop"""
        self.logger.info("Starting Arcturus System Monitor")
        self.logger.info(f"Configuration: {self.config_path}")
        
        # Initialize event logger
        try:
            neo4j_config = self.config['monitoring']
            self.event_logger = EventLoggerFactory.get_logger(
                uri=neo4j_config['neo4j_uri'],
                user=neo4j_config['neo4j_user'],
                password=neo4j_config['neo4j_password']
            )
            self.logger.info("Connected to Neo4j")
        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {e}")
            return 1
        
        # Start monitoring loop
        self.running = True
        interval = self.config['monitoring']['interval_seconds']
        
        self.logger.info(f"Monitoring started (interval: {interval}s)")
        
        try:
            while self.running:
                self._monitor_cycle()
                time.sleep(interval)
        except Exception as e:
            self.logger.error(f"Monitoring loop error: {e}", exc_info=True)
            return 1
        finally:
            self._cleanup()
        
        return 0
    
    def _monitor_cycle(self):
        """Single monitoring cycle - check all metrics"""
        try:
            self._check_cpu()
            self._check_memory()
            self._check_disk()
            self._check_processes()
            self._check_services()
        except Exception as e:
            self.logger.error(f"Error in monitoring cycle: {e}", exc_info=True)
    
    def _check_cpu(self):
        """Check CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            threshold = self.config['thresholds']['cpu_warning']
            
            if cpu_percent > threshold:
                self.logger.warning(f"High CPU usage: {cpu_percent}%")
                self.event_logger.log_event("high_cpu", {
                    "cpu_percent": cpu_percent,
                    "threshold": threshold
                })
        except Exception as e:
            self.logger.error(f"Error checking CPU: {e}")
    
    def _check_memory(self):
        """Check memory usage"""
        try:
            mem = psutil.virtual_memory()
            threshold = self.config['thresholds']['memory_warning']
            
            if mem.percent > threshold:
                self.logger.warning(f"High memory usage: {mem.percent}%")
                self.event_logger.log_event("high_memory", {
                    "memory_percent": mem.percent,
                    "available_mb": mem.available / (1024 * 1024),
                    "threshold": threshold
                })
        except Exception as e:
            self.logger.error(f"Error checking memory: {e}")
    
    def _check_disk(self):
        """Check disk usage"""
        try:
            disk = psutil.disk_usage('/')
            threshold = self.config['thresholds']['disk_warning']
            
            if disk.percent > threshold:
                self.logger.warning(f"Low disk space: {disk.percent}% used")
                self.event_logger.log_event("low_disk", {
                    "disk_percent": disk.percent,
                    "available_gb": disk.free / (1024 ** 3),
                    "threshold": threshold
                })
        except Exception as e:
            self.logger.error(f"Error checking disk: {e}")
    
    def _check_processes(self):
        """Check running processes for high resource usage"""
        try:
            threshold = self.config['thresholds']['process_memory_warning']
            
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
                try:
                    info = proc.info
                    
                    # Log process state to graph
                    if info['memory_percent'] and info['memory_percent'] > 1:  # >1% memory
                        mem_mb = (info['memory_percent'] / 100) * psutil.virtual_memory().total / (1024 * 1024)
                        self.event_logger.log_process_state(
                            info['pid'],
                            info['name'],
                            mem_mb,
                            info['cpu_percent'] or 0
                        )
                    
                    # Log high memory usage events
                    if info['memory_percent'] and info['memory_percent'] > threshold:
                        # Only log if this is a new occurrence or significantly changed
                        key = f"process_{info['pid']}_memory"
                        if key not in self.last_states or \
                           abs(self.last_states[key] - info['memory_percent']) > 5:
                            
                            self.logger.warning(
                                f"High memory process: {info['name']} "
                                f"(PID {info['pid']}) using {info['memory_percent']:.1f}%"
                            )
                            self.event_logger.log_event("high_memory_process", {
                                "pid": info['pid'],
                                "name": info['name'],
                                "memory_percent": info['memory_percent'],
                                "cpu_percent": info['cpu_percent']
                            })
                            self.last_states[key] = info['memory_percent']
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        except Exception as e:
            self.logger.error(f"Error checking processes: {e}")
    
    def _check_services(self):
        """Check systemd services"""
        try:
            services = self.config['services_to_monitor']
            
            for service in services:
                # Handle wildcard patterns
                if '*' in service:
                    self._check_service_pattern(service)
                else:
                    self._check_single_service(service)
        
        except Exception as e:
            self.logger.error(f"Error checking services: {e}")
    
    def _check_single_service(self, service_name: str):
        """Check a single systemd service"""
        try:
            result = subprocess.run(
                ['systemctl', '--user', 'is-active', service_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            status = result.stdout.strip()
            
            # Get detailed status
            result = subprocess.run(
                ['systemctl', '--user', 'show', service_name, '--property=SubState'],
                capture_output=True,
                text=True,
                timeout=5
            )
            substate = result.stdout.strip().split('=')[1] if '=' in result.stdout else ''
            
            # Log service state
            self.event_logger.log_service_state(service_name, status, substate)
            
            # Check for state changes
            state_key = f"service_{service_name}"
            previous_status = self.last_states.get(state_key)
            
            if previous_status and previous_status != status:
                # Status changed
                if status == 'failed':
                    self.logger.error(f"Service failed: {service_name}")
                    self.event_logger.log_event("service_failure", {
                        "service": service_name,
                        "previous_status": previous_status,
                        "current_status": status
                    })
                elif status == 'inactive' and previous_status == 'active':
                    self.logger.warning(f"Service stopped: {service_name}")
                    self.event_logger.log_event("service_stopped", {
                        "service": service_name,
                        "previous_status": previous_status
                    })
                elif status == 'active' and previous_status != 'active':
                    self.logger.info(f"Service started: {service_name}")
                    self.event_logger.log_event("service_started", {
                        "service": service_name,
                        "previous_status": previous_status
                    })
            
            self.last_states[state_key] = status
        
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Timeout checking service: {service_name}")
        except Exception as e:
            self.logger.error(f"Error checking service {service_name}: {e}")
    
    def _check_service_pattern(self, pattern: str):
        """Check services matching a wildcard pattern"""
        try:
            # List all user services
            result = subprocess.run(
                ['systemctl', '--user', 'list-units', '--type=service', '--all', '--no-pager'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parse output and find matches
            import re
            pattern_regex = pattern.replace('*', '.*').replace('-', r'\-')
            
            for line in result.stdout.split('\n'):
                match = re.search(r'^\s*(\S+\.service)', line)
                if match:
                    service_name = match.group(1).replace('.service', '')
                    if re.match(pattern_regex, service_name):
                        self._check_single_service(service_name)
        
        except Exception as e:
            self.logger.error(f"Error checking service pattern {pattern}: {e}")
    
    def _cleanup(self):
        """Cleanup resources on shutdown"""
        self.logger.info("Shutting down monitor...")
        
        if self.event_logger:
            EventLoggerFactory.close_logger()
        
        self.logger.info("Monitor stopped")


def main():
    """Main entry point"""
    # Get config path
    config_path = os.environ.get(
        'MONITOR_CONFIG',
        '/opt/mythos/graph_logging/config/monitoring_config.yaml'
    )
    
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        return 1
    
    # Start monitor
    monitor = SystemMonitor(config_path)
    return monitor.start()


if __name__ == '__main__':
    sys.exit(main())
