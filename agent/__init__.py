"""
agent/__init__.py
-----------------
PURPOSE: Makes `agent` a Python package and re-exports the primary class.
"""

from agent.runner import AgentRunner

__all__ = ["AgentRunner"]
