"""
Custom Tools
------------

Custom tool factory module for enterprise integrations.

Pattern for creating tools:
1. Define tool function with @tool decorator from agno.tools
2. Use factory pattern for dependency injection (DB, API clients, etc.)
3. Return tool function from factory
4. Add tool to agent's tools=[] list

All custom tools should:
- Have clear docstrings (the LLM reads these to decide when to use the tool)
- Handle errors gracefully (return error messages, don't raise)
- Log usage for tracking
"""
