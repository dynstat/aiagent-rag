"""
agent/graph.py
--------------
PURPOSE: Defines the AI agent as a LangGraph StateGraph.

         This is the HEART of the project. LangGraph models the agent as a
         directed graph where:

         • NODES  = actions the agent can take (call LLM, execute a tool)
         • EDGES  = transitions between actions (fixed or conditional)
         • STATE  = shared data that flows through the graph on every step

         WHY LANGGRAPH instead of a simple LangChain chain?
         ─────────────────────────────────────────────────────
         A chain is linear: A → B → C (done).
         An agent needs CYCLES: it may call a tool, observe the result,
         decide to call ANOTHER tool, then finally answer.  LangGraph
         supports cycles (loops) natively.

         AGENT LOOP (React-style):
         ┌─────────────────────────────────────────────────────┐
         │  1. LLM node: Given the question + history + any    │
         │     previous tool results → decide what to do next  │
         │     (either call a tool OR produce a final answer)   │
         │                                                      │
         │  2. Condition: Did the LLM request a tool call?      │
         │     YES → route to ToolNode → back to LLM node       │
         │     NO  → route to END (return the final answer)     │
         └─────────────────────────────────────────────────────┘

         This loop can repeat many times (the agent keeps calling tools
         until it has enough information to answer confidently).
"""

from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from llm_factory import get_llm
from tools import ALL_TOOLS
from config import Config


# ─────────────────────────────────────────────────────────────────────────────
# STATE DEFINITION
# ─────────────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """
    PURPOSE: The shared state object that flows between all nodes in the graph.

    Every node receives a copy of this state, can read any field, and returns
    a PARTIAL update (only the fields it changed).  LangGraph merges the
    updates back into the full state automatically.

    Fields:
        messages: The conversation history as a list of LangChain messages.
                  `add_messages` is a reducer — when a node appends a new
                  message, LangGraph merges it into the list rather than
                  replacing the whole list.  This is how history accumulates.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an intelligent Sales Intelligence AI Assistant specializing
in Rep Context Analysis. Your primary job is to help users understand, evaluate,
and get insights about sales representatives using a combination of:

1. INTERNAL KNOWLEDGE BASE (via rag_search tool):
   - Documents, notes, and data that were loaded into the vector store
   - Use this for nuanced, descriptive context about reps or policies

2. CRM TOOLS (lookup_rep_profile, get_rep_deals, etc.):
   - Structured data directly from the CRM system
   - Use these for precise numbers, deal stages, and quota data

3. MEMORY:
   - You have access to the full conversation history
   - Reference earlier context when relevant (e.g., "As we discussed earlier...")
   - Don't repeat information you already provided unless asked

BEHAVIOR GUIDELINES:
- Always use tools to retrieve factual data; never hallucinate numbers
- Call tools multiple times if needed to build a complete picture
- After getting tool results, synthesize them into a clear, concise answer
- If a rep ID is unknown, use `list_all_reps` to find the right one
- Be direct and business-focused; avoid unnecessary filler text
"""


# ─────────────────────────────────────────────────────────────────────────────
# NODE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

def create_llm_node(llm_with_tools):
    """
    PURPOSE: Creates the 'llm' node function — the agent's reasoning step.

    The node receives the current state (all messages so far) and calls
    the LLM.  The LLM either:
      a) Generates a tool call  → LangGraph routes to ToolNode
      b) Generates a text reply → LangGraph routes to END

    We wrap this in a factory so the node closure captures `llm_with_tools`.

    Args:
        llm_with_tools: The LLM with tools bound to it (enables function calling).

    Returns:
        A node function compatible with LangGraph's StateGraph.
    """
    def llm_node(state: AgentState) -> dict:
        """
        The LLM reasoning node.

        Prepends the system prompt to every call so the LLM always has its
        role and guidelines, regardless of conversation length.
        """
        # Build the full message list: system prompt + conversation history
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(state["messages"])

        # Invoke the LLM — it will either respond or request a tool call
        response = llm_with_tools.invoke(messages)

        # Return only the NEW message (LangGraph merges it into state["messages"])
        return {"messages": [response]}

    return llm_node


# ─────────────────────────────────────────────────────────────────────────────
# GRAPH BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def build_agent_graph(temperature: float = 0.0):
    """
    PURPOSE: Assembles and compiles the full LangGraph agent.

    Steps:
    1. Create the LLM and bind tools to it (enables function/tool calling)
    2. Create the StateGraph and add nodes
    3. Define edges (transitions between nodes)
    4. Add a MemorySaver checkpointer for persistent conversation state
    5. Compile to a runnable graph

    Args:
        temperature: LLM temperature (0 = deterministic, good for tool use).

    Returns:
        A compiled LangGraph CompiledGraph ready to invoke.
    """

    # ── Step 1: LLM with tools bound ────────────────────────────────────────
    # bind_tools() tells the LLM about available tools (via function calling).
    # The LLM can now include ToolCall objects in its responses, not just text.
    llm = get_llm(temperature=temperature)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    # ── Step 2: Build the graph ──────────────────────────────────────────────
    # StateGraph(AgentState) declares what the shared state looks like
    graph = StateGraph(AgentState)

    # Add the LLM reasoning node
    # Every time the graph visits "llm", it calls the LLM and gets a response
    graph.add_node("llm", create_llm_node(llm_with_tools))

    # Add the ToolNode — a prebuilt LangGraph node that:
    # 1. Reads the tool calls from the last LLM message
    # 2. Calls each tool with the provided arguments
    # 3. Returns ToolMessage objects with the results
    graph.add_node("tools", ToolNode(ALL_TOOLS))

    # ── Step 3: Define edges ─────────────────────────────────────────────────

    # Start: always enter the graph at the "llm" node
    graph.set_entry_point("llm")

    # Conditional edge from "llm":
    # tools_condition() is a prebuilt function that checks whether the
    # LLM's last message contains tool calls.
    #   → If YES: route to "tools" node
    #   → If NO:  route to END (the LLM's message is the final answer)
    graph.add_conditional_edges("llm", tools_condition)

    # Fixed edge from "tools" back to "llm":
    # After tools execute, ALWAYS go back to the LLM so it can reason
    # about the tool results and decide its next action.
    # This creates the LOOP that allows multi-step reasoning.
    graph.add_edge("tools", "llm")

    # ── Step 4: Add checkpointer for persistent memory ───────────────────────
    # MemorySaver stores the full graph state (all messages) in memory.
    # Each conversation has a unique thread_id; state is isolated per thread.
    # In production, swap MemorySaver for SqliteSaver or PostgresSaver for
    # persistence across process restarts.
    checkpointer = MemorySaver()

    # ── Step 5: Compile ──────────────────────────────────────────────────────
    # compile() validates the graph structure and returns an executable object
    compiled_graph = graph.compile(checkpointer=checkpointer)

    return compiled_graph
