"""
SDK Imports Helper - Handles the import conflict between local agents/ directory
and the OpenAI Agents SDK's agents module.

This module provides a clean way to import from the SDK without naming conflicts.
"""

import sys
import importlib

# Store reference to local agents module before SDK import
_local_agents_path = None
for path in sys.path:
    if 'Stock Agent' in path:
        _local_agents_path = path
        break


def get_sdk_components():
    """
    Import and return the OpenAI Agents SDK components.

    Returns:
        tuple: (Agent, Runner, ModelSettings, function_tool)
    """
    # Temporarily modify path to prefer SDK
    import agents as sdk_agents

    return (
        sdk_agents.Agent,
        sdk_agents.Runner,
        sdk_agents.ModelSettings,
        getattr(sdk_agents, 'function_tool', None),
    )


# Pre-import for convenience (will work once SDK is installed)
try:
    # Try direct import first
    from agents import Agent, Runner, ModelSettings, function_tool
    SDK_AVAILABLE = True
except ImportError:
    # SDK not installed - provide stubs for development
    SDK_AVAILABLE = False

    class Agent:
        """Stub Agent class for development without SDK installed."""
        def __init__(self, name, instructions, model=None, model_settings=None,
                     tools=None, handoffs=None, **kwargs):
            self.name = name
            self.instructions = instructions
            self.model = model
            self.model_settings = model_settings
            self.tools = tools or []
            self.handoffs = handoffs or []

    class Runner:
        """Stub Runner class for development without SDK installed."""
        @staticmethod
        async def run(agent, input_data, **kwargs):
            class Result:
                final_output = "SDK not installed. Install openai-agents to run."
                new_items = []
                def to_input_list(self):
                    return []
            return Result()

        @staticmethod
        def run_sync(agent, input_data, **kwargs):
            class Result:
                final_output = "SDK not installed. Install openai-agents to run."
            return Result()

    class ModelSettings:
        """Stub ModelSettings class."""
        def __init__(self, temperature=0.7, **kwargs):
            self.temperature = temperature

    def function_tool(func):
        """Stub function_tool decorator."""
        return func
