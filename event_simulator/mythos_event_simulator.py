#!/usr/bin/env python3
"""
Mythos Event Simulator
Triggers test events and tracks results historically per-machine
"""

import os
import sys
import json
import uuid
import psutil
import socket
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# Add graph logging to path
sys.path.insert(0, '/opt/mythos/graph_logging/src')

try:
    from neo4j import GraphDatabase
except ImportError:
    print("Error: neo4j library not installed")
    sys.exit(1)


class EventSimulator:
    """Simulates system events and tracks test history"""
    
    def __init__(self):
        self.hostname = socket.gethostname()
        self.test_run_id = str(uuid.uuid4())
        self.results = []
        self.neo4j_driver = None
        self._connect_neo4j()
    
    def _connect_neo4j(self):
        """Connect to Neo4j"""
        uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
        user = os.environ.get('NEO4J_USER', 'neo4j')
        password = os.environ.get('NEO4J_PASSWORD')
        
        if not password:
            print("Warning: NEO4J_PASSWORD not set, history won't be saved")
            return
        
        try:
            self.neo4j_driver = GraphDatabase.driver(uri, auth=(user, password))
            # Test connection
            with self.neo4j_driver.session() as session:
                session.run("RETURN 1")
        except Exception as e:
            print(f"Warning: Could not connect to Neo4j: {e}")
            self.neo4j_driver = None
    
    def run_all_tests(self, duration: int = 90) -> Dict:
        """Run all event simulation tests"""
        print("=" * 60)
        print("Mythos Event Simulator")
        print("=" * 60)
        print(f"Machine: {self.hostname}")
        print(f"Test Run ID: {self.test_run_id}")
        print(f"Started: {datetime.now().isoformat()}")
        print("=" * 60)
        print()
        
        tests = [
            ("CPU Spike", self.test_cpu_spike, duration),
            ("Memory Pressure", self.test_memory_pressure, 30),
            ("Disk Fill", self.test_disk_fill, 10),
            ("Service Restart", self.test_service_restart, 5),
            ("Process Spawn", self.test_process_spawn, 20)
        ]
        
        for test_name, test_func, test_duration in tests:
            print(f"\n[TEST] {test_name}")
            print("-" * 60)
            result = test_func(test_duration)
            self.results.append(result)
            
            # Display result
            status = "✓ PASS" if result['success'] else "✗ FAIL"
            print(f"Status: {status}")
            print(f"Events triggered: {result.get('events_triggered', 0)}")
            if result.get('error'):
                print(f"Error: {result['error']}")
            print()
            
            # Wait for monitor to detect
            if result['success']:
                print("Waiting 65s for monitor to detect...")
                time.sleep(65)
        
        # Save results
        self._save_results()
        
        # Display summary
        self._display_summary()
        
        return {
            'test_run_id': self.test_run_id,
            'hostname': self.hostname,
            'timestamp': datetime.now().isoformat(),
            'results': self.results
        }
    
    def test_cpu_spike(self, duration: int) -> Dict:
        """Simulate high CPU usage"""
        result = {
            'test': 'cpu_spike',
            'started': datetime.now().isoformat(),
            'success': False,
            'events_triggered': 0,
            'duration': duration
        }
        
        try:
            print(f"Spawning CPU stress for {duration} seconds...")
            
            # Use Python CPU burner (more portable than stress-ng)
            processes = []
            cpu_count = psutil.cpu_count()
            
            # Spawn processes to consume CPU
            for i in range(cpu_count):
                proc = subprocess.Popen(
                    [sys.executable, '-c', 
                     'while True: pass'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                processes.append(proc)
            
            print(f"Spawned {len(processes)} CPU-burning processes")
            
            # Monitor for a bit
            time.sleep(min(duration, 10))
            
            # Check if CPU is high
            cpu_percent = psutil.cpu_percent(interval=2)
            print(f"Current CPU: {cpu_percent:.1f}%")
            
            if cpu_percent > 80:
                result['events_triggered'] = 1
                result['success'] = True
                result['cpu_percent'] = cpu_percent
            
            # Wait for full duration
            remaining = duration - 12
            if remaining > 0:
                time.sleep(remaining)
            
            # Kill processes
            for proc in processes:
                proc.terminate()
            
            # Wait for cleanup
            time.sleep(2)
            for proc in processes:
                try:
                    proc.kill()
                except:
                    pass
            
            result['completed'] = datetime.now().isoformat()
            
        except Exception as e:
            result['error'] = str(e)
            result['completed'] = datetime.now().isoformat()
        
        return result
    
    def test_memory_pressure(self, duration: int) -> Dict:
        """Simulate memory pressure"""
        result = {
            'test': 'memory_pressure',
            'started': datetime.now().isoformat(),
            'success': False,
            'events_triggered': 0,
            'duration': duration
        }
        
        try:
            print(f"Allocating memory for {duration} seconds...")
            
            # Get available memory
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024 ** 3)
            
            # Allocate 30% of available memory
            target_gb = available_gb * 0.3
            chunk_size = 100 * 1024 * 1024  # 100 MB chunks
            chunks = []
            
            print(f"Target allocation: {target_gb:.2f} GB")
            
            allocated = 0
            while allocated < target_gb * (1024 ** 3):
                chunks.append(bytearray(chunk_size))
                allocated += chunk_size
                
                if len(chunks) % 10 == 0:
                    allocated_gb = allocated / (1024 ** 3)
                    print(f"Allocated: {allocated_gb:.2f} GB")
            
            print(f"Total allocated: {allocated / (1024**3):.2f} GB")
            
            # Check memory usage
            mem = psutil.virtual_memory()
            print(f"Current memory: {mem.percent:.1f}%")
            
            if mem.percent > 80:
                result['events_triggered'] = 1
                result['success'] = True
                result['memory_percent'] = mem.percent
            
            # Hold memory
            time.sleep(duration)
            
            # Release
            chunks.clear()
            
            result['completed'] = datetime.now().isoformat()
            
        except Exception as e:
            result['error'] = str(e)
            result['completed'] = datetime.now().isoformat()
        
        return result
    
    def test_disk_fill(self, duration: int) -> Dict:
        """Simulate disk fill (safe - uses temp files)"""
        result = {
            'test': 'disk_fill',
            'started': datetime.now().isoformat(),
            'success': False,
            'events_triggered': 0,
            'duration': duration
        }
        
        try:
            print(f"Creating temporary large file for {duration} seconds...")
            
            temp_file = f"/tmp/mythos_test_{self.test_run_id}.tmp"
            
            # Create 1GB file
            size_gb = 1
            chunk_size = 10 * 1024 * 1024  # 10 MB
            chunks = int(size_gb * 1024 / 10)
            
            with open(temp_file, 'wb') as f:
                for i in range(chunks):
                    f.write(b'0' * chunk_size)
                    if i % 10 == 0:
                        print(f"Written: {(i * 10):.0f} MB")
            
            print(f"Created {size_gb}GB test file")
            
            # Check disk usage
            disk = psutil.disk_usage('/')
            print(f"Current disk: {disk.percent:.1f}%")
            
            # This won't trigger threshold unless disk was already close
            result['disk_percent'] = disk.percent
            result['success'] = True
            
            # Hold file
            time.sleep(duration)
            
            # Remove
            os.remove(temp_file)
            print("Removed test file")
            
            result['completed'] = datetime.now().isoformat()
            
        except Exception as e:
            result['error'] = str(e)
            result['completed'] = datetime.now().isoformat()
            # Cleanup
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        
        return result
    
    def test_service_restart(self, duration: int) -> Dict:
        """Test service restart (restarts arcturus-cleanup as safe test)"""
        result = {
            'test': 'service_restart',
            'started': datetime.now().isoformat(),
            'success': False,
            'events_triggered': 0,
            'duration': duration
        }
        
        try:
            print("Restarting arcturus-cleanup service (safe test service)...")
            
            # Stop the cleanup service
            subprocess.run(
                ['systemctl', '--user', 'stop', 'arcturus-cleanup.service'],
                check=False,
                capture_output=True
            )
            
            print("Service stopped")
            time.sleep(5)
            
            # Start it again
            subprocess.run(
                ['systemctl', '--user', 'start', 'arcturus-cleanup.service'],
                check=False,
                capture_output=True
            )
            
            print("Service started")
            
            result['events_triggered'] = 1
            result['success'] = True
            result['completed'] = datetime.now().isoformat()
            
        except Exception as e:
            result['error'] = str(e)
            result['completed'] = datetime.now().isoformat()
        
        return result
    
    def test_process_spawn(self, duration: int) -> Dict:
        """Spawn multiple processes to trigger monitoring"""
        result = {
            'test': 'process_spawn',
            'started': datetime.now().isoformat(),
            'success': False,
            'events_triggered': 0,
            'duration': duration
        }
        
        try:
            print(f"Spawning 20 test processes for {duration} seconds...")
            
            processes = []
            for i in range(20):
                proc = subprocess.Popen(
                    ['sleep', str(duration)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                processes.append(proc)
            
            print(f"Spawned {len(processes)} processes")
            
            # Wait
            time.sleep(duration)
            
            # Cleanup
            for proc in processes:
                try:
                    proc.terminate()
                except:
                    pass
            
            result['success'] = True
            result['processes_spawned'] = len(processes)
            result['completed'] = datetime.now().isoformat()
            
        except Exception as e:
            result['error'] = str(e)
            result['completed'] = datetime.now().isoformat()
        
        return result
    
    def _save_results(self):
        """Save test results to Neo4j"""
        if not self.neo4j_driver:
            print("\nWarning: Neo4j not connected, results not saved to database")
            return
        
        try:
            with self.neo4j_driver.session() as session:
                session.execute_write(
                    self._create_test_run_node,
                    self.test_run_id,
                    self.hostname,
                    self.results
                )
            print("\n✓ Results saved to Neo4j")
        except Exception as e:
            print(f"\nWarning: Could not save results to Neo4j: {e}")
    
    def _create_test_run_node(self, tx, test_run_id, hostname, results):
        """Transaction: Create test run node"""
        
        # Calculate summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r['success'])
        events_triggered = sum(r.get('events_triggered', 0) for r in results)
        
        # Create test run node
        tx.run("""
            MERGE (machine:TestMachine {hostname: $hostname})
            CREATE (run:TestRun {
                id: $test_run_id,
                hostname: $hostname,
                timestamp: datetime(),
                total_tests: $total_tests,
                passed_tests: $passed_tests,
                failed_tests: $failed_tests,
                events_triggered: $events_triggered,
                results: $results_json
            })
            CREATE (machine)-[:HAD_TEST_RUN]->(run)
            
            // Link to system
            MERGE (sys:System {name: 'localhost'})
            CREATE (sys)-[:TESTED_BY]->(run)
        """, test_run_id=test_run_id, hostname=hostname,
             total_tests=total_tests, passed_tests=passed_tests,
             failed_tests=total_tests - passed_tests,
             events_triggered=events_triggered,
             results_json=json.dumps(results))
    
    def _display_summary(self):
        """Display test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['success'])
        failed = total - passed
        events = sum(r.get('events_triggered', 0) for r in self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Events Triggered: {events}")
        print()
        
        print("Individual Results:")
        for r in self.results:
            status = "✓" if r['success'] else "✗"
            print(f"  {status} {r['test']}")
        
        print("\n" + "=" * 60)
        print("View results in Neo4j:")
        print(f"  MATCH (run:TestRun {{id: '{self.test_run_id}'}}) RETURN run")
        print("=" * 60)
    
    def show_history(self, limit: int = 10):
        """Show test history for this machine"""
        if not self.neo4j_driver:
            print("Error: Neo4j not connected")
            return
        
        print("=" * 60)
        print(f"Test History for {self.hostname}")
        print("=" * 60)
        print()
        
        try:
            with self.neo4j_driver.session() as session:
                result = session.run("""
                    MATCH (machine:TestMachine {hostname: $hostname})-[:HAD_TEST_RUN]->(run:TestRun)
                    RETURN run.timestamp AS timestamp,
                           run.total_tests AS total,
                           run.passed_tests AS passed,
                           run.failed_tests AS failed,
                           run.events_triggered AS events
                    ORDER BY run.timestamp DESC
                    LIMIT $limit
                """, hostname=self.hostname, limit=limit)
                
                runs = list(result)
                
                if not runs:
                    print("No test history found for this machine.")
                    return
                
                print(f"Last {len(runs)} test runs:\n")
                print(f"{'Date':<20} {'Total':<8} {'Passed':<8} {'Failed':<8} {'Events':<8}")
                print("-" * 60)
                
                for run in runs:
                    ts = run['timestamp']
                    print(f"{str(ts):<20} {run['total']:<8} {run['passed']:<8} {run['failed']:<8} {run['events']:<8}")
                
                # Calculate statistics
                total_runs = len(runs)
                avg_pass_rate = sum(r['passed'] / r['total'] * 100 for r in runs) / total_runs
                total_events = sum(r['events'] for r in runs)
                
                print()
                print("Statistics:")
                print(f"  Total runs: {total_runs}")
                print(f"  Average pass rate: {avg_pass_rate:.1f}%")
                print(f"  Total events triggered: {total_events}")
                
        except Exception as e:
            print(f"Error retrieving history: {e}")
    
    def show_common_failures(self):
        """Show common test failures across all runs"""
        if not self.neo4j_driver:
            print("Error: Neo4j not connected")
            return
        
        print("=" * 60)
        print(f"Common Failures for {self.hostname}")
        print("=" * 60)
        print()
        
        try:
            with self.neo4j_driver.session() as session:
                # Parse results JSON to find failures
                result = session.run("""
                    MATCH (machine:TestMachine {hostname: $hostname})-[:HAD_TEST_RUN]->(run:TestRun)
                    RETURN run.results AS results
                """, hostname=self.hostname)
                
                all_results = []
                for record in result:
                    results_json = record['results']
                    if results_json:
                        all_results.extend(json.loads(results_json))
                
                if not all_results:
                    print("No test data found.")
                    return
                
                # Count failures by test type
                from collections import Counter
                failures = Counter()
                
                for r in all_results:
                    if not r['success']:
                        failures[r['test']] += 1
                
                if not failures:
                    print("No failures found! All tests passing.")
                    return
                
                print("Most common failures:\n")
                for test, count in failures.most_common():
                    print(f"  {test}: {count} failures")
                
        except Exception as e:
            print(f"Error analyzing failures: {e}")
    
    def cleanup(self):
        """Cleanup connections"""
        if self.neo4j_driver:
            self.neo4j_driver.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Mythos Event Simulator - Trigger test events and track history',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--run', action='store_true', help='Run all tests')
    parser.add_argument('--history', action='store_true', help='Show test history')
    parser.add_argument('--failures', action='store_true', help='Show common failures')
    parser.add_argument('--duration', type=int, default=90, help='Test duration in seconds (default: 90)')
    parser.add_argument('--limit', type=int, default=10, help='History limit (default: 10)')
    
    args = parser.parse_args()
    
    # Load environment
    if os.path.exists(os.path.expanduser('~/.arcturus_development_env.sh')):
        # Can't source shell script directly, but env vars should be set
        pass
    
    simulator = EventSimulator()
    
    try:
        if args.history:
            simulator.show_history(limit=args.limit)
        elif args.failures:
            simulator.show_common_failures()
        elif args.run:
            simulator.run_all_tests(duration=args.duration)
        else:
            # Default: run tests
            simulator.run_all_tests(duration=args.duration)
    finally:
        simulator.cleanup()


if __name__ == '__main__':
    main()
