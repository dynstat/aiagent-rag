"""
memory/conversation_memory.py
------------------------------
PURPOSE: Manages conversation memory for the AI agent.

         There are TWO kinds of memory in this project:

         1. SHORT-TERM (in-process) memory — the recent conversation turns
            kept in a Python list inside this module.  Fast, zero cost, but
            lost when the process exits.

         2. LONG-TERM (LangGraph checkpointer) memory — LangGraph can
            automatically save/restore the entire agent state (including
            message history) using a checkpointer.  This is wired up in
            agent/graph.py.

         This module handles short-term memory and provides utilities for
         formatting history into prompt-ready strings.

CONCEPT — Why does an agent need memory?
         Without memory each question is answered as if it's the first.
         The user would need to repeat context on every turn.
         With memory, the agent can refer to earlier parts of the conversation
         e.g. "What did I say about the sales rep earlier?" still works.
"""

from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from config import Config


class ConversationMemory:
    """
    A simple sliding-window conversation store.

    Attributes:
        _history: Ordered list of LangChain message objects.
                  We use LangChain message types (HumanMessage, AIMessage)
                  so they slot directly into LangChain/LangGraph chains.
    """

    def __init__(self, window_size: int = Config.MEMORY_WINDOW):
        """
        Args:
            window_size: Maximum number of (human + ai) message PAIRS to keep.
                         Older messages are dropped to stay within LLM context.
        """
        self._history: List[BaseMessage] = []
        # window_size pairs = window_size * 2 individual messages
        self._max_messages: int = window_size * 2

    # ─────────────────────────────────────────────────────────────────────────
    # Write
    # ─────────────────────────────────────────────────────────────────────────

    def add_user_message(self, text: str) -> None:
        """
        PURPOSE: Record a message from the human user.
        Called BEFORE the agent processes the turn.
        """
        self._history.append(HumanMessage(content=text))
        self._trim()

    def add_ai_message(self, text: str) -> None:
        """
        PURPOSE: Record the agent's response.
        Called AFTER the agent finishes its turn.
        """
        self._history.append(AIMessage(content=text))
        self._trim()

    def _trim(self) -> None:
        """
        PURPOSE: Enforce the sliding window.
        If history exceeds the limit, drop oldest messages (from the front).
        We always drop in pairs (human + ai) to keep the conversation balanced.
        """
        while len(self._history) > self._max_messages:
            # Remove the oldest message pair (index 0 and 1)
            self._history.pop(0)

    # ─────────────────────────────────────────────────────────────────────────
    # Read
    # ─────────────────────────────────────────────────────────────────────────

    def get_messages(self) -> List[BaseMessage]:
        """
        PURPOSE: Return the full history as LangChain message objects.
        These can be passed directly to a ChatModel or LangGraph state.
        """
        return list(self._history)

    def get_formatted_history(self) -> str:
        """
        PURPOSE: Return history as a human-readable string for injecting
                 into prompt templates that expect plain text context.

        Format:
            Human: <text>
            Assistant: <text>
        """
        lines = []
        for msg in self._history:
            role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
            lines.append(f"{role}: {msg.content}")
        return "\n".join(lines)

    def clear(self) -> None:
        """PURPOSE: Wipe history — useful for starting a fresh conversation."""
        self._history.clear()

    def __len__(self) -> int:
        """Returns number of individual messages (not pairs) in memory."""
        return len(self._history)
