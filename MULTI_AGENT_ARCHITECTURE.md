# Multi-Agent Architecture Guide

## Problem with Handoff-Based Orchestration

The original implementation relied on the LLM to correctly hand off to each agent sequentially. This is **unreliable** because:
- The LLM may skip agents
- The LLM may not follow the exact sequence
- Handoffs depend on model instruction-following

## Solution: Sequential Runner Pattern

Instead of relying on handoffs, we **explicitly call each agent** using `Runner.run()` and pass results between them.

```python
# BEST PRACTICE: Sequential Agent Execution
async def run_analysis_pipeline(stock_symbol: str):
    # Step 1: Fundamental Analysis
    result1 = await Runner.run(fundamental_agent, f"Analyze {stock_symbol}")
    fundamental_data = result1.final_output

    # Step 2: Technical Analysis (pass previous context)
    result2 = await Runner.run(
        technical_agent,
        result1.to_input_list() + [{"role": "user", "content": "Now do technical analysis"}]
    )
    technical_data = result2.final_output

    # Step 3: Sentiment Analysis
    result3 = await Runner.run(
        sentiment_agent,
        result2.to_input_list() + [{"role": "user", "content": "Now analyze sentiment"}]
    )
    # ... continue for all agents
```

## Alternative: Agents as Tools Pattern

Register specialist agents as tools so the orchestrator can call them deterministically:

```python
from agents import Agent

orchestrator = Agent(
    name="Orchestrator",
    instructions="Call each analysis tool in order...",
    tools=[
        fundamental_agent.as_tool(
            tool_name="run_fundamental_analysis",
            tool_description="Get fundamental analysis for a stock"
        ),
        technical_agent.as_tool(
            tool_name="run_technical_analysis",
            tool_description="Get technical analysis for a stock"
        ),
        # ... more agents as tools
    ]
)
```

## Our Implementation

We use the **Sequential Runner Pattern** for guaranteed execution:

### Pipeline Flow

```
User Query
    |
    v
[1] Fundamental Analyst --> fundamental_data
    |
    v
[2] Technical Analyst --> technical_data
    |
    v
[3] Sentiment Analyst --> sentiment_data
    |
    v
[4] Macro Analyst --> macro_data
    |
    v
[5] Document Analyst --> document_data
    |
    v
[6] Bull Advocate --> bull_case
    |
    v
[7] Bear Advocate --> bear_case
    |
    v
[8] Debate Judge --> verdict
    |
    v
[9] Risk Manager --> risk_assessment
    |
    v
[10] Orchestrator --> Final Report + PDF
```

### Key Benefits

1. **Guaranteed Execution**: Every agent runs in order
2. **Context Passing**: Each agent receives all previous analysis
3. **Deterministic**: No reliance on model decision-making for flow
4. **Debuggable**: Easy to see which agent ran and what it produced

## References

- [OpenAI Cookbook: Multi-Agent Portfolio Collaboration](https://cookbook.openai.com/examples/agents_sdk/multi-agent-portfolio-collaboration)
- [OpenAI Agents SDK: Orchestrating Agents](https://cookbook.openai.com/examples/orchestrating_agents)
- [Building Sequential Multi-Agent Systems](https://www.aidevmode.com/blog/sequential-multi-agent-systems)
