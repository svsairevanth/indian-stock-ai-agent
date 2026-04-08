"""
OpenAI Agents SDK Wrapper - Handles the import conflict with local agents/ directory.
Import SDK components from this module instead of 'agents'.

This wrapper loads the SDK from site-packages by temporarily
manipulating sys.path to exclude the local directory.
"""

import sys
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

SDK_AVAILABLE = False
_import_error = None
_sdk = None
_sdk_modules_snapshot = {}

# Get current directory to exclude
_current_dir = os.path.dirname(os.path.abspath(__file__))
_stock_agent_dir = _current_dir  # This is the Stock Agent folder

# Save original state
_original_path = sys.path.copy()

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
        # Resolve entries like "" / "." to absolute paths so local project root is excluded reliably.
        try:
            resolved = os.path.abspath(p if p else os.getcwd())
        except Exception:
            resolved = p

        p_norm = os.path.normpath(resolved).lower()
        stock_norm = os.path.normpath(_stock_agent_dir).lower()

        if p_norm != stock_norm and not p_norm.startswith(stock_norm):
            clean_path.append(p)

    sys.path = clean_path

    # Now import the SDK
    import agents as _sdk
    _sdk_modules_snapshot = {
        key: value
        for key, value in sys.modules.items()
        if key == 'agents' or key.startswith('agents.')
    }

    # Get the components we need
    ModelSettings = _sdk.ModelSettings
    _sdk_function_tool = getattr(_sdk, 'function_tool', lambda x: x)
    handoff = getattr(_sdk, 'handoff', None)
    SDK_AVAILABLE = True

    # Configure custom OpenAI client for self-signed certificate endpoints
    _base_url = os.getenv("OPENAI_BASE_URL", "")
    if _base_url:
        import httpx
        from openai import AsyncOpenAI
        _async_http_client = httpx.AsyncClient(verify=False)
        _custom_client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            base_url=_base_url,
            http_client=_async_http_client,
        )
        _sdk.set_default_openai_client(_custom_client)
        _sdk.set_tracing_disabled(True)  # Disable tracing for custom endpoints

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

    # Restore local agents modules (if any were loaded before wrapper import)
    for key, value in _agents_modules_to_restore.items():
        sys.modules[key] = value


if SDK_AVAILABLE:
    @contextmanager
    def _sdk_namespace():
        """
        Temporarily map `agents.*` imports to the SDK package during runtime calls.
        This avoids collisions with the local `agents/` package.
        """
        local_snapshot = {
            key: value
            for key, value in sys.modules.items()
            if key == 'agents' or key.startswith('agents.')
        }
        try:
            for key in list(sys.modules.keys()):
                if key == 'agents' or key.startswith('agents.'):
                    del sys.modules[key]
            for key, value in _sdk_modules_snapshot.items():
                sys.modules[key] = value
            yield
        finally:
            for key in list(sys.modules.keys()):
                if key == 'agents' or key.startswith('agents.'):
                    del sys.modules[key]
            for key, value in local_snapshot.items():
                sys.modules[key] = value


    class Agent(_sdk.Agent):
        """SDK Agent with namespace collision guard."""

        def __init__(self, *args, **kwargs):
            with _sdk_namespace():
                super().__init__(*args, **kwargs)


    class Runner:
        """SDK Runner with namespace collision guard for every invocation."""

        @staticmethod
        async def run(*args, **kwargs):
            with _sdk_namespace():
                return await _sdk.Runner.run(*args, **kwargs)

        @staticmethod
        def run_sync(*args, **kwargs):
            with _sdk_namespace():
                return _sdk.Runner.run_sync(*args, **kwargs)

        @staticmethod
        async def run_streamed(*args, **kwargs):
            with _sdk_namespace():
                return await _sdk.Runner.run_streamed(*args, **kwargs)


    def function_tool(func=None, **kwargs):
        """SDK function_tool with namespace guard."""
        with _sdk_namespace():
            decorated = _sdk_function_tool(func, **kwargs) if func is not None else _sdk_function_tool(**kwargs)
        return decorated

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
