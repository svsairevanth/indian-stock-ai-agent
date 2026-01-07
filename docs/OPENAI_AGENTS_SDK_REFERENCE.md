# OpenAI Agents SDK - Complete Reference Guide

## Overview

The OpenAI Agents SDK is a lightweight, production-ready Python framework for building agentic AI applications. It's the official upgrade from OpenAI's experimental Swarm framework.

**Installation:**
```bash
pip install openai-agents
```

**Version:** 0.6.5 (as of January 2026)

---

## Core Primitives

### 1. Agents
LLMs configured with instructions and tools.

### 2. Handoffs
Allow agents to delegate tasks to other specialized agents.

### 3. Guardrails
Enable validation of agent inputs and outputs.

### 4. Sessions
Automatically maintain conversation history across agent runs.

---

## Basic Agent Setup

```python
from agents import Agent, Runner

# Simple agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant"
)

# Synchronous execution
result = Runner.run_sync(agent, "Hello, how can you help me?")
print(result.final_output)

# Asynchronous execution
import asyncio

async def main():
    result = await Runner.run(agent, "Hello!")
    print(result.final_output)

asyncio.run(main())
```

---

## Agent Configuration Options

```python
from agents import Agent, ModelSettings, function_tool

agent = Agent(
    name="MyAgent",                          # Required: Agent identifier
    instructions="System prompt here",        # Instructions/system prompt
    model="gpt-4o",                           # LLM model to use
    model_settings=ModelSettings(             # Model tuning parameters
        temperature=0.7,
        top_p=0.9,
    ),
    tools=[my_tool],                          # List of tools
    handoffs=[other_agent],                   # Agents to hand off to
    output_type=MyOutputModel,                # Structured output type (Pydantic)
    input_guardrails=[my_guardrail],          # Input validation
    output_guardrails=[my_guardrail],         # Output validation
)
```

---

## Function Tools (Most Important!)

### Basic Function Tool

```python
from agents import function_tool, Agent

@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a given city.

    Args:
        city: The name of the city to get weather for.
    """
    # Your implementation here
    return f"The weather in {city} is sunny"

agent = Agent(
    name="Weather Agent",
    instructions="Help users with weather information",
    tools=[get_weather]
)
```

### Function Tool with Context

```python
from dataclasses import dataclass
from agents import function_tool, RunContextWrapper, Agent, Runner

@dataclass
class UserContext:
    user_id: str
    user_name: str
    is_premium: bool

@function_tool
async def get_user_data(ctx: RunContextWrapper[UserContext]) -> str:
    """Fetch data for the current user."""
    return f"User {ctx.context.user_name} (ID: {ctx.context.user_id})"

agent = Agent[UserContext](
    name="User Agent",
    tools=[get_user_data]
)

# Run with context
async def main():
    context = UserContext(user_id="123", user_name="John", is_premium=True)
    result = await Runner.run(agent, "Get my data", context=context)
    print(result.final_output)
```

### Function Tool with Custom Name/Description

```python
@function_tool(
    name_override="fetch_stock_price",
    description_override="Fetch the current stock price for a given symbol"
)
def get_price(symbol: str) -> float:
    """Internal function to get stock price."""
    return 150.25
```

### Function Tool with Error Handling

```python
from agents import function_tool, RunContextWrapper
from typing import Any

def my_error_handler(context: RunContextWrapper[Any], error: Exception) -> str:
    """Custom error handler for tool failures."""
    print(f"Tool failed: {error}")
    return "Sorry, there was an error processing your request."

@function_tool(failure_error_function=my_error_handler)
def risky_operation(data: str) -> str:
    """A tool that might fail."""
    if not data:
        raise ValueError("Data cannot be empty")
    return f"Processed: {data}"
```

### Tool with Complex Types (Pydantic/TypedDict)

```python
from typing import TypedDict
from pydantic import BaseModel
from agents import function_tool

class Location(TypedDict):
    lat: float
    long: float

class StockQuery(BaseModel):
    symbol: str
    exchange: str = "NSE"
    include_history: bool = False

@function_tool
async def fetch_weather(location: Location) -> str:
    """Fetch weather for coordinates."""
    return f"Weather at {location['lat']}, {location['long']}: Sunny"

@function_tool
def get_stock_info(query: StockQuery) -> dict:
    """Get stock information based on query parameters."""
    return {
        "symbol": query.symbol,
        "exchange": query.exchange,
        "price": 150.0
    }
```

---

## Structured Outputs

```python
from pydantic import BaseModel, Field
from agents import Agent

class StockAnalysis(BaseModel):
    symbol: str = Field(description="Stock symbol")
    recommendation: str = Field(description="BUY, SELL, or HOLD")
    confidence: float = Field(description="Confidence score 0-1")
    reasoning: str = Field(description="Explanation for the recommendation")

agent = Agent(
    name="Stock Analyst",
    instructions="Analyze stocks and provide recommendations",
    output_type=StockAnalysis  # Forces structured output
)
```

---

## Running Agents

### Three Ways to Run

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="Be helpful")

# 1. Async run (recommended for production)
async def async_example():
    result = await Runner.run(agent, "Hello")
    return result.final_output

# 2. Sync run (convenience method)
result = Runner.run_sync(agent, "Hello")

# 3. Streaming run
async def streaming_example():
    result = await Runner.run_streamed(agent, "Hello")
    async for event in result.stream_events():
        print(event)
    print(result.final_output)
```

### Run Configuration

```python
from agents import Runner, RunConfig

result = await Runner.run(
    agent,
    "Hello",
    run_config=RunConfig(
        model="gpt-4o",                    # Override model
        model_settings=ModelSettings(      # Override settings
            temperature=0.5
        ),
        tracing_disabled=False,            # Enable/disable tracing
        workflow_name="my_workflow",       # For tracing
    ),
    max_turns=10,                          # Maximum conversation turns
)
```

---

## Multi-Agent Patterns

### Pattern 1: Agents as Tools (Orchestrator Pattern)

```python
from agents import Agent

# Specialized agents
data_agent = Agent(
    name="Data Agent",
    instructions="You fetch and process stock data"
)

analysis_agent = Agent(
    name="Analysis Agent",
    instructions="You perform technical analysis"
)

# Orchestrator that uses other agents as tools
orchestrator = Agent(
    name="Stock Orchestrator",
    instructions="You coordinate stock analysis tasks",
    tools=[
        data_agent.as_tool(
            tool_name="fetch_stock_data",
            tool_description="Fetch stock data for analysis"
        ),
        analysis_agent.as_tool(
            tool_name="analyze_stock",
            tool_description="Perform technical analysis on stock data"
        )
    ]
)
```

### Pattern 2: Handoffs (Delegation Pattern)

```python
from agents import Agent, handoff

# Specialized agents
fundamental_agent = Agent(
    name="Fundamental Analyst",
    instructions="You analyze company fundamentals"
)

technical_agent = Agent(
    name="Technical Analyst",
    instructions="You analyze charts and technical indicators"
)

# Triage agent that hands off to specialists
triage_agent = Agent(
    name="Triage Agent",
    instructions="""
    You are a stock analysis triage agent.
    - For fundamental analysis questions, hand off to Fundamental Analyst
    - For technical/chart analysis, hand off to Technical Analyst
    """,
    handoffs=[fundamental_agent, technical_agent]
)
```

### Handoff with Custom Configuration

```python
from agents import handoff, RunContextWrapper
from pydantic import BaseModel

class HandoffData(BaseModel):
    reason: str
    priority: str

async def on_handoff(ctx: RunContextWrapper, data: HandoffData):
    print(f"Handoff triggered: {data.reason} (Priority: {data.priority})")

custom_handoff = handoff(
    agent=specialist_agent,
    tool_name_override="escalate_to_specialist",
    tool_description_override="Escalate complex issues to specialist",
    on_handoff=on_handoff,
    input_type=HandoffData
)
```

---

## Context Management

### Local Context (Dependencies & State)

```python
from dataclasses import dataclass
from agents import Agent, Runner, RunContextWrapper, function_tool

@dataclass
class AppContext:
    user_id: str
    api_key: str
    db_connection: any  # Your database connection

    def log(self, message: str):
        print(f"[{self.user_id}] {message}")

@function_tool
def fetch_portfolio(ctx: RunContextWrapper[AppContext]) -> str:
    """Fetch user's portfolio."""
    ctx.context.log("Fetching portfolio")
    # Use ctx.context.db_connection to fetch data
    return "Portfolio data here"

agent = Agent[AppContext](
    name="Portfolio Agent",
    tools=[fetch_portfolio]
)

# Usage
context = AppContext(
    user_id="user123",
    api_key="xxx",
    db_connection=my_db
)
result = await Runner.run(agent, "Show my portfolio", context=context)
```

### Dynamic Instructions

```python
from agents import Agent, RunContextWrapper

def dynamic_instructions(
    ctx: RunContextWrapper[AppContext],
    agent: Agent
) -> str:
    return f"""
    You are helping user {ctx.context.user_id}.
    Today's date is {datetime.now().strftime('%Y-%m-%d')}.
    Provide personalized stock recommendations.
    """

agent = Agent[AppContext](
    name="Personalized Agent",
    instructions=dynamic_instructions  # Function instead of string
)
```

---

## Guardrails

### Input Guardrail

```python
from pydantic import BaseModel
from agents import (
    Agent, Runner, GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered, input_guardrail,
    RunContextWrapper, TResponseInputItem
)

class SafetyCheck(BaseModel):
    is_safe: bool
    reason: str

safety_checker = Agent(
    name="Safety Checker",
    instructions="Check if input is safe and relevant to stock analysis",
    output_type=SafetyCheck
)

@input_guardrail
async def safety_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(safety_checker, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_safe
    )

main_agent = Agent(
    name="Stock Agent",
    instructions="Help with stock analysis",
    input_guardrails=[safety_guardrail]
)

# Usage with error handling
try:
    result = await Runner.run(main_agent, "Analyze RELIANCE.NS")
except InputGuardrailTripwireTriggered:
    print("Input was blocked by guardrail")
```

---

## Conversation Management

### Manual History Management

```python
async def chat_loop():
    agent = Agent(name="Assistant", instructions="Be helpful")
    conversation_history = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break

        # Add user message to history
        full_input = conversation_history + [{"role": "user", "content": user_input}]

        result = await Runner.run(agent, full_input)
        print(f"Agent: {result.final_output}")

        # Update history for next turn
        conversation_history = result.to_input_list()
```

### Using Sessions (Automatic)

```python
from agents import Agent, Runner, SQLiteSession

async def chat_with_session():
    agent = Agent(name="Assistant", instructions="Be helpful")
    session = SQLiteSession("user_123_conversation")

    # Session automatically manages history
    result1 = await Runner.run(agent, "My name is John", session=session)
    result2 = await Runner.run(agent, "What's my name?", session=session)
    # Agent will remember "John" from previous turn
```

---

## Results and Outputs

```python
from agents import Runner

result = await Runner.run(agent, "Analyze stock")

# Access results
print(result.final_output)          # The final response
print(result.last_agent)            # Last agent that ran
print(result.new_items)             # All items generated during run
print(result.input_guardrail_results)  # Guardrail results
print(result.raw_responses)         # Raw LLM responses

# Continue conversation
next_input = result.to_input_list() + [{"role": "user", "content": "Tell me more"}]
result2 = await Runner.run(agent, next_input)
```

---

## Best Practices

### 1. Tool Design
- Use clear, descriptive docstrings (they become tool descriptions)
- Use type hints for all parameters
- Return strings or Pydantic models
- Handle errors gracefully

### 2. Agent Design
- Keep instructions focused and specific
- Use structured outputs for predictable responses
- Separate concerns with multiple specialized agents

### 3. Context Management
- Use dataclasses or Pydantic models for context
- Include all dependencies (DB, APIs) in context
- Don't store secrets in context that goes to LLM

### 4. Error Handling
- Always wrap runs in try/except
- Handle guardrail exceptions appropriately
- Use custom error functions for tools

### 5. Production
- Enable tracing for debugging
- Use async methods for better performance
- Set appropriate max_turns limits
- Monitor token usage

---

## Complete Example: Stock Analysis Agent

```python
import asyncio
from dataclasses import dataclass
from pydantic import BaseModel, Field
from agents import Agent, Runner, RunContextWrapper, function_tool

# Context
@dataclass
class StockContext:
    user_id: str
    api_key: str

# Output type
class StockRecommendation(BaseModel):
    symbol: str
    action: str = Field(description="BUY, SELL, or HOLD")
    target_price: float
    stop_loss: float
    reasoning: str

# Tools
@function_tool
async def get_stock_price(symbol: str) -> dict:
    """Get current stock price and basic info.

    Args:
        symbol: Stock symbol (e.g., RELIANCE.NS)
    """
    # Your implementation
    return {"symbol": symbol, "price": 2500.0, "change": 1.5}

@function_tool
async def get_technical_indicators(symbol: str) -> dict:
    """Get technical indicators for a stock.

    Args:
        symbol: Stock symbol
    """
    return {"rsi": 55, "macd": "bullish", "sma_20": 2450}

# Agent
stock_agent = Agent[StockContext](
    name="Indian Stock Analyst",
    instructions="""
    You are an expert Indian stock market analyst.
    Analyze stocks using both fundamental and technical analysis.
    Always provide clear BUY/SELL/HOLD recommendations with reasoning.
    """,
    tools=[get_stock_price, get_technical_indicators],
    output_type=StockRecommendation
)

# Run
async def main():
    context = StockContext(user_id="user1", api_key="xxx")
    result = await Runner.run(
        stock_agent,
        "Should I buy RELIANCE.NS?",
        context=context
    )

    recommendation = result.final_output
    print(f"Recommendation: {recommendation.action}")
    print(f"Target: {recommendation.target_price}")
    print(f"Reasoning: {recommendation.reasoning}")

asyncio.run(main())
```

---

## Resources

- **Official Docs:** https://openai.github.io/openai-agents-python/
- **GitHub:** https://github.com/openai/openai-agents-python
- **PyPI:** https://pypi.org/project/openai-agents/
- **OpenAI Guide:** https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
