# test_seraphe_prompt.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 122

---

### File: `test_seraphe_prompt.py`

#### Purpose
This file is a test script for the Seraphe's Cosmology Assistant prompt, which interacts with the Ollama API to generate responses based on user input. It loads a predefined system prompt and maintains a conversation history to provide context for each response.

#### Architecture
The file consists of:
- **Imports and Environment Setup**: It imports necessary modules and loads environment variables.
- **System Prompt**: A detailed system prompt is defined as a string, containing instructions for the AI assistant.
- **Main Loop**: A loop that reads user input, constructs a full prompt with the system prompt and conversation history, generates a response from the Ollama API, and prints the response.

#### Patterns
- **Singleton**: The Ollama client is initialized once and reused throughout the script.
- **Stateful Interaction**: The script maintains a state (conversation history) to provide context for each response.

#### Dependencies
- **Imports**: `os`, `load_dotenv` from `dotenv`, `Client` from `ollama`.
- **Environment Variables**: `OLLAMA_HOST`, `OLLAMA_MODEL`.

#### Interfaces
- **User Input**: The script reads user input from the command line.
- **Output**: The script prints the generated response to the command line.

#### Database
- **References**: The script references the `ollama`, `dotenv`, and `birth` tables in PostgreSQL, though it does not directly interact with them in the provided code.

#### Configuration
- **Environment Variables**: The script loads environment variables from `/opt/mythos/.env`, specifically `OLLAMA_HOST` and `OLLAMA_MODEL`.

#### Key Logic
- **Prompt Construction**: The script constructs a full prompt by combining the system prompt with the conversation history.
- **Response Generation**: It uses the Ollama API to generate responses based on the full prompt.
- **Conversation History**: It maintains a list of the last few exchanges to provide context for the AI assistant.

#### Integration Points
- **Ollama API**: The script integrates with the Ollama API to generate responses.
- **Environment Configuration**: It relies on environment variables for configuration and connects to the Ollama service.

### Detailed Breakdown

#### Imports and Environment Setup
```python
from ollama import Client
import os
from dotenv import load_dotenv
```
- **Imports**: `Client` from `ollama` for API interaction, `os` for environment variable access, and `load_dotenv` from `dotenv` to load environment variables from a file.
- **Environment Setup**: Loads environment variables from `/opt/mythos/.env` and initializes the Ollama client.

#### System Prompt
```python
SERAPHE_PROMPT = """You are Seraphe's cosmology assistant, helping her map soul architecture through numerology, tarot, astrology, and sacred geometry.
...
"""
```
- **System Prompt**: A detailed string containing instructions for the AI assistant, including roles, core knowledge, response guidelines, and tone.

#### Main Loop
```python
while True:
    user_input = input("Seraphe> ").strip()
    
    if user_input.lower() in ['exit', 'quit', 'q']:
        print("\n👋 Exiting test session")
        break
    
    if not user_input:
        continue
    
    full_prompt = SERAPHE_PROMPT + "\n\n"
    
    for msg in conversation_history[-6:]:  # Last 3 exchanges
        full_prompt += f"{msg['role']}: {msg['content']}\n\n"
    
    full_prompt += f"Seraphe: {user_input}\n\nAssistant:"
    
    print("\nAssistant: ", end="", flush=True)
    
    response_text = ""
    for chunk in ollama.generate(model=model, prompt=full_prompt, stream=True):
        text = chunk['response']
        print(text, end="", flush=True)
        response_text += text
    
    print("\n")
    
    conversation_history.append({"role": "Seraphe", "content": user_input})
    conversation_history.append({"role": "Assistant", "content": response_text})
```
- **User Input**: Reads user input and checks for exit commands.
- **Prompt Construction**: Combines the system prompt with the last few exchanges in the conversation history.
- **Response Generation**: Uses the Ollama API to generate responses and prints them to the command line.
- **Conversation History**: Stores user input and generated responses in a list to maintain context.

### Summary
This script serves as a local test interface for the Seraphe's Cosmology Assistant, leveraging the Ollama API to generate responses based on a detailed system prompt and conversation history. It integrates with environment variables for configuration and maintains stateful interaction through a conversation history.
