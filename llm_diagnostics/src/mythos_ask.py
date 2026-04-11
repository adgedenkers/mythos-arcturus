#!/usr/bin/env python3
"""
Mythos Ask - CLI interface for LLM diagnostics
Usage: mythos-ask "your question about the system"
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import Optional

# Add to path
sys.path.insert(0, '/opt/mythos/graph_logging/src')
sys.path.insert(0, '/opt/mythos/llm_diagnostics/src')

try:
    import ollama
except ImportError:
    print("Error: Ollama Python library not installed")
    print("Run: pip install ollama")
    sys.exit(1)

from conversation_logger import log_conversation


class MythosAsk:
    """Interface for asking the LLM about system state"""
    
    def __init__(self, model: str = "llama3.2:3b"):
        self.model = model
        self.client = ollama.Client()
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load the system prompt for diagnostics"""
        return """You are a system diagnostics assistant for the Mythos infrastructure.

You have access to tools that query the system's Neo4j graph database for:
- System health metrics
- Service statuses  
- Recent events and errors
- Process resource usage
- Failure causality chains
- Predictive failure analysis

When answering questions:
1. Use the diagnostic tools to get current, accurate information
2. Be concise and direct (R2-D2 style - efficient, not verbose)
3. Focus on actionable information
4. When tracing failures, explain the causal chain clearly
5. Provide specific numbers and timestamps when relevant

You are read-only - you cannot make changes to the system, only diagnose and explain.

Current system: arcturus (localhost)
Monitoring: CPU, memory, disk, processes, services
Event retention: 10 days
"""
    
    def ask(self, question: str, conversation_id: Optional[str] = None) -> str:
        """
        Ask a question about the system
        
        Args:
            question: The question to ask
            conversation_id: Optional conversation ID for context
        
        Returns:
            LLM response
        """
        try:
            # Call Ollama with tools
            response = self.client.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': question}
                ],
                tools=[
                    {
                        'type': 'function',
                        'function': {
                            'name': 'get_system_health',
                            'description': 'Get current system health status',
                            'parameters': {'type': 'object', 'properties': {}}
                        }
                    },
                    {
                        'type': 'function',
                        'function': {
                            'name': 'trace_failure',
                            'description': 'Trace root cause of service failure',
                            'parameters': {
                                'type': 'object',
                                'properties': {
                                    'service_name': {
                                        'type': 'string',
                                        'description': 'Name of the failed service'
                                    }
                                },
                                'required': ['service_name']
                            }
                        }
                    },
                    {
                        'type': 'function',
                        'function': {
                            'name': 'get_recent_events',
                            'description': 'Get recent system events',
                            'parameters': {
                                'type': 'object',
                                'properties': {
                                    'minutes': {
                                        'type': 'integer',
                                        'description': 'Look back this many minutes',
                                        'default': 60
                                    },
                                    'event_types': {
                                        'type': 'string',
                                        'description': 'Comma-separated event types to filter'
                                    }
                                }
                            }
                        }
                    },
                    {
                        'type': 'function',
                        'function': {
                            'name': 'get_service_status',
                            'description': 'Get systemd service status',
                            'parameters': {
                                'type': 'object',
                                'properties': {
                                    'service_name': {
                                        'type': 'string',
                                        'description': 'Service name (optional, returns all if not provided)'
                                    }
                                }
                            }
                        }
                    },
                    {
                        'type': 'function',
                        'function': {
                            'name': 'get_high_resource_processes',
                            'description': 'Get processes using high CPU or memory',
                            'parameters': {
                                'type': 'object',
                                'properties': {
                                    'memory_threshold': {
                                        'type': 'number',
                                        'description': 'Memory percent threshold',
                                        'default': 10.0
                                    },
                                    'cpu_threshold': {
                                        'type': 'number',
                                        'description': 'CPU percent threshold',
                                        'default': 50.0
                                    }
                                }
                            }
                        }
                    }
                ]
            )
            
            # Extract response
            message = response['message']
            
            # Handle tool calls
            if message.get('tool_calls'):
                # Process tool calls
                tool_results = []
                for tool_call in message['tool_calls']:
                    result = self._execute_tool(tool_call)
                    tool_results.append(result)
                
                # Get final response with tool results
                messages = [
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': question},
                    message,
                    {'role': 'tool', 'content': json.dumps(tool_results)}
                ]
                
                final_response = self.client.chat(model=self.model, messages=messages)
                answer = final_response['message']['content']
                
                # Log conversation with tool usage
                log_conversation(
                    question=question,
                    answer=answer,
                    tools_used=[tc['function']['name'] for tc in message['tool_calls']],
                    conversation_id=conversation_id
                )
                
                return answer
            else:
                # Direct response without tools
                answer = message['content']
                
                # Log conversation
                log_conversation(
                    question=question,
                    answer=answer,
                    tools_used=[],
                    conversation_id=conversation_id
                )
                
                return answer
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg
    
    def _execute_tool(self, tool_call: dict) -> dict:
        """Execute a diagnostic tool"""
        from diagnostics import Diagnostics
        import json
        
        tool_name = tool_call['function']['name']
        arguments = tool_call['function'].get('arguments', {})
        
        diag = Diagnostics()
        
        try:
            if tool_name == 'get_system_health':
                result = diag.get_system_health()
            elif tool_name == 'trace_failure':
                result = diag.trace_failure(service_name=arguments['service_name'])
            elif tool_name == 'get_recent_events':
                result = diag.get_recent_events(
                    minutes=arguments.get('minutes', 60),
                    event_types=arguments.get('event_types', '').split(',') if arguments.get('event_types') else None
                )
            elif tool_name == 'get_service_status':
                result = diag.get_service_status(service_name=arguments.get('service_name'))
            elif tool_name == 'get_high_resource_processes':
                result = diag.get_high_resource_processes(
                    memory_threshold=arguments.get('memory_threshold', 10.0),
                    cpu_threshold=arguments.get('cpu_threshold', 50.0)
                )
            else:
                result = {'error': f'Unknown tool: {tool_name}'}
            
            # Convert to JSON string and back to handle DateTime objects
            result_str = json.dumps(result, default=str)
            result_clean = json.loads(result_str)
            
            return {
                'tool': tool_name,
                'result': result_clean
            }
        except Exception as e:
            return {
                'tool': tool_name,
                'error': str(e)
            }
        finally:
            diag.close()

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Ask questions about your system',
        epilog='Examples:\n'
               '  mythos-ask "how is the system?"\n'
               '  mythos-ask "why did neo4j backup fail?"\n'
               '  mythos-ask "what\'s using memory?"',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('question', nargs='+', help='Question to ask')
    parser.add_argument('--model', default='llama3.2:3b', help='Ollama model to use')
    parser.add_argument('--conversation-id', help='Conversation ID for context')
    
    args = parser.parse_args()
    
    question = ' '.join(args.question)
    
    # Initialize and ask
    asker = MythosAsk(model=args.model)
    answer = asker.ask(question, conversation_id=args.conversation_id)
    
    print(answer)


if __name__ == '__main__':
    main()
