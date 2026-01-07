"""
Specialized agents for multi-agent stock analysis system.
"""

# Import SDK components from the wrapper module
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai_sdk import Agent, Runner, ModelSettings, function_tool, SDK_AVAILABLE, handoff

# Now import local agent modules
from .fundamental_analyst import fundamental_analyst_agent
from .technical_analyst import technical_analyst_agent
from .sentiment_analyst import sentiment_analyst_agent
from .macro_analyst import macro_analyst_agent
from .document_analyst import document_analyst_agent
from .bull_agent import bull_agent
from .bear_agent import bear_agent
from .debate_judge import debate_judge_agent
from .risk_manager import risk_manager_agent
from .portfolio_analyst import portfolio_analyst_agent
from .orchestrator import stock_orchestrator_agent

# Set up handoffs back to orchestrator for all specialist agents
# This allows specialists to return control to the orchestrator after completing their analysis
_specialist_agents = [
    fundamental_analyst_agent,
    technical_analyst_agent,
    sentiment_analyst_agent,
    macro_analyst_agent,
    document_analyst_agent,
    bull_agent,
    bear_agent,
    debate_judge_agent,
    risk_manager_agent,
    portfolio_analyst_agent,
]

# Add handoff back to orchestrator for each specialist
for agent in _specialist_agents:
    if hasattr(agent, 'handoffs') and agent.handoffs is not None:
        # Check if orchestrator not already in handoffs
        if stock_orchestrator_agent not in agent.handoffs:
            agent.handoffs.append(stock_orchestrator_agent)
    else:
        agent.handoffs = [stock_orchestrator_agent]

__all__ = [
    "Agent", "Runner", "ModelSettings", "function_tool", "SDK_AVAILABLE", "handoff",
    "fundamental_analyst_agent", "technical_analyst_agent", "sentiment_analyst_agent",
    "macro_analyst_agent", "document_analyst_agent",
    "bull_agent", "bear_agent", "debate_judge_agent",
    "risk_manager_agent", "portfolio_analyst_agent",
    "stock_orchestrator_agent",
]
