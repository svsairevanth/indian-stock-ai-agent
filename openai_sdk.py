"""
OpenAI Agents SDK Wrapper - Handles the import conflict with local agents/ directory.
Import SDK components from this module instead of 'agents'.

This wrapper loads the SDK from site-packages by temporarily
manipulating sys.path to exclude the local directory.
"""

import sys
import os

SDK_AVAILABLE = False
_import_error = None

# Get current directory to exclude
_current_dir = os.path.dirname(os.path.abspath(__file__))
_stock_agent_dir = _current_dir  # This is the Stock Agent folder

# Save original state
_original_path = sys.path.copy()
_cached_agents = sys.modules.get('agents')

# Clean all agents-related modules from cache
_agents_modules_to_restore = {}
for key in list(sys.modules.keys()):
    if key == 'agents' or key.startswith('agents.'):
        _agents_modules_to_restore[key] = sys.modules.pop(key)

try:
    # Create a new path excluding current directory
    # This ensures we get site-packages version
    clean_path = []
    for p in sys.path:
        # Normalize paths for comparison
        p_norm = os.path.normpath(p).lower()
        stock_norm = os.path.normpath(_stock_agent_dir).lower()

        if p_norm != stock_norm and not p_norm.startswith(stock_norm):
            clean_path.append(p)

    sys.path = clean_path

    # Now import the SDK
    import agents as _sdk

    # Get the components we need
    Agent = _sdk.Agent
    Runner = _sdk.Runner
    ModelSettings = _sdk.ModelSettings
    function_tool = getattr(_sdk, 'function_tool', lambda x: x)
    handoff = getattr(_sdk, 'handoff', None)
    SDK_AVAILABLE = True

except ImportError as e:
    import traceback
    _import_error = traceback.format_exc()

except Exception as e:
    import traceback
    _import_error = traceback.format_exc()

finally:
    # Restore original path
    sys.path = _original_path

    # Clear the SDK modules we just loaded so local agents/ can work
    for key in list(sys.modules.keys()):
        if key == 'agents' or key.startswith('agents.'):
            del sys.modules[key]

# Fallback stubs if SDK not available
if not SDK_AVAILABLE:
    class Agent:
        """Fallback Agent stub."""
        def __init__(self, name, instructions, model=None, model_settings=None,
                     tools=None, handoffs=None, **kwargs):
            self.name = name
            self.instructions = instructions
            self.model = model
            self.model_settings = model_settings
            self.tools = tools or []
            self.handoffs = handoffs or []

    class Runner:
        """Fallback Runner stub."""
        @staticmethod
        async def run(agent, input_data, **kwargs):
            raise NotImplementedError(f"OpenAI Agents SDK not available: {_import_error}")

        @staticmethod
        def run_sync(agent, input_data, **kwargs):
            raise NotImplementedError(f"OpenAI Agents SDK not available: {_import_error}")

        @staticmethod
        async def run_streamed(agent, input_data, **kwargs):
            raise NotImplementedError(f"OpenAI Agents SDK not available: {_import_error}")

    class ModelSettings:
        """Fallback ModelSettings stub."""
        def __init__(self, temperature=0.7, **kwargs):
            self.temperature = temperature

    def function_tool(func):
        """Fallback function_tool decorator."""
        return func

    def handoff(agent, **kwargs):
        """Fallback handoff function."""
        return agent

# Debug info
def get_import_error():
    return _import_error
