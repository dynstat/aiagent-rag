"""
agent/runner.py
---------------
PURPOSE: Provides a clean, high-level interface for running the agent.
         Hides LangGraph internals (thread IDs, state management, streaming)
         from the caller (main.py).

         This is the "service layer" pattern — main.py asks the runner to
         process a query, and the runner handles all the LangGraph plumbing.
"""

import uuid
from typing import Optional

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from agent.graph import AgentState, build_agent_graph
from config import Config
from memory import ConversationMemory


class AgentRunner:
    """
    Wraps the LangGraph compiled graph and manages:
    - Thread IDs for LangGraph's built-in checkpointer memory
    - Short-term ConversationMemory for formatted history display
    - Streaming vs. batch invocation
    - Clean output extraction

    CONCEPT — Two layers of memory:
        1. LangGraph's MemorySaver (checkpointer): stores the FULL state
           graph including all tool calls, results, and messages.
           Used internally by LangGraph for multi-turn conversations.

        2. ConversationMemory (our class): a lightweight window of recent
           turns used for logging, display, and injecting into prompts
           when needed outside of LangGraph.
    """

    def __init__(self, thread_id: Optional[str] = None):
        """
        Args:
            thread_id: Unique identifier for this conversation session.
                       LangGraph uses this to isolate state between sessions.
                       If None, a random UUID is generated.
        """
        # Build the compiled LangGraph agent
        self.graph = build_agent_graph(temperature=0.0)

        # Each conversation needs a unique thread_id for the checkpointer
        self.thread_id = thread_id or str(uuid.uuid4())

        # Short-term memory for display and human-readable history logging
        self.memory = ConversationMemory(window_size=Config.MEMORY_WINDOW)

        # LangGraph config — passed on every invoke() call to route state
        self._config: RunnableConfig = {"configurable": {"thread_id": self.thread_id}}

        print(f"[AgentRunner] Session started | Thread ID: {self.thread_id}")

    def run(self, user_input: str, verbose: bool = True) -> str:
        """
        PURPOSE: Process a single user message and return the agent's response.

        Internally this may involve MULTIPLE LangGraph steps:
        - LLM decides to call tool(s)
        - Tool(s) execute
        - LLM reasons over results
        - LLM may call more tools
        - LLM finally produces a text response → END

        Args:
            user_input: The user's question or message.
            verbose: If True, print intermediate tool calls to stdout for
                     educational visibility into the agent's reasoning.

        Returns:
            The agent's final text response as a string.
        """
        # Record user message in our short-term memory
        self.memory.add_user_message(user_input)

        # Wrap user input in a LangChain HumanMessage
        input_state: AgentState = {"messages": [HumanMessage(content=user_input)]}

        if verbose:
            print(f"\n{'=' * 60}")
            print(f"[User]: {user_input}")
            print(f"{'=' * 60}")

        # ── Invoke the LangGraph agent ────────────────────────────────────────
        # stream_mode="values" returns the FULL state after each graph step.
        # This lets us see intermediate states (tool calls, tool results).
        final_state = None
        step_count = 0

        for state in self.graph.stream(
            input_state, config=self._config, stream_mode="values"
        ):
            step_count += 1
            last_message = state["messages"][-1]

            if verbose:
                # Show what happened at each step
                msg_type = type(last_message).__name__
                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    # LLM decided to call a tool
                    for tc in last_message.tool_calls:
                        print(f"\n[Step {step_count}] [Tool Call]: {tc['name']}")
                        print(f"   Args: {tc['args']}")
                elif msg_type == "ToolMessage":
                    # Tool returned a result
                    print(
                        f"\n[Step {step_count}] [Tool Result] ({last_message.name}):"
                    )
                    # Print first 300 chars to avoid flooding the terminal
                    content_preview = str(last_message.content)[:300]
                    print(
                        f"   {content_preview}{'...' if len(str(last_message.content)) > 300 else ''}"
                    )

            final_state = state

        # ── Extract the final AI response ─────────────────────────────────────
        # The last message in the final state is the AI's text response
        if final_state is None:
            return "I encountered an error processing your request."

        final_message = final_state["messages"][-1]
        response_text = final_message.content

        # Record AI response in short-term memory
        self.memory.add_ai_message(response_text)

        if verbose:
            print(f"\n[Agent Response] ({step_count} steps):")
            print(f"{response_text}")
            print(f"\n{'─' * 60}")

        return response_text

    def get_conversation_history(self) -> str:
        """
        PURPOSE: Returns formatted conversation history for display.
        Useful for debugging or showing the user what has been discussed.
        """
        return self.memory.get_formatted_history()

    def clear_memory(self) -> None:
        """
        PURPOSE: Clears short-term display memory.
        Note: LangGraph's checkpointer memory is thread-based and cannot
        be cleared without creating a new thread_id.
        """
        self.memory.clear()
        print("[AgentRunner] Short-term memory cleared.")

    def new_session(self) -> None:
        """
        PURPOSE: Start a completely fresh conversation session.
        Creates a new thread_id so LangGraph's checkpointer is also reset.
        """
        self.thread_id = str(uuid.uuid4())
        self._config = {"configurable": {"thread_id": self.thread_id}}
        self.memory.clear()
        print(f"[AgentRunner] New session started | Thread ID: {self.thread_id}")
