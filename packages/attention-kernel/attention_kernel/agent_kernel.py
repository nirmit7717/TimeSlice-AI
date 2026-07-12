import os
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from attention_kernel.tools import ToolRegistry

class AgentState(TypedDict):
    """
    Tracks conversational history and parsed domain contexts across LangGraph nodes.
    """
    messages: List[BaseMessage]
    current_process: Optional[Dict[str, Any]]
    action_plan: Optional[Dict[str, Any]]
    suggested_policy: Optional[str]

class AgenticAttentionKernel:
    """
    LangGraph orchestrator connecting multi-agent nodes to local tools via Nvidia NIM endpoints.
    """
    def __init__(self, api_key: Optional[str] = None, db_session: Optional[Any] = None):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY", "mock-key")
        self.db_session = db_session
        self.registry = ToolRegistry(db_session) if db_session else None
        
        # NIM is fully OpenAI-compatible. Default model routes to Nemotron/Llama
        if self.api_key == "mock-key":
            self.llm = None
        else:
            self.llm = ChatOpenAI(
                api_key=self.api_key,
                base_url="https://integrate.api.nvidia.com/v1",
                model="meta/llama-3.1-70b-instruct",
                temperature=0.2
            )
            
        self.graph = self._build_graph()


    def _build_graph(self) -> StateGraph:
        builder = StateGraph(AgentState)
        
        # 1. Add Nodes
        builder.add_node("router", self.router_node)
        builder.add_node("process_agent", self.process_agent_node)
        builder.add_node("scheduling_agent", self.scheduling_agent_node)
        builder.add_node("calendar_agent", self.calendar_agent_node)
        builder.add_node("chat_agent", self.chat_agent_node)
        
        # 2. Add Edges
        builder.add_edge(START, "router")
        
        # Conditional routing from router
        builder.add_conditional_edges(
            "router",
            self.route_decision,
            {
                "process": "process_agent",
                "schedule": "scheduling_agent",
                "calendar": "calendar_agent",
                "chat": "chat_agent"
            }
        )
        
        builder.add_edge("process_agent", END)
        builder.add_edge("scheduling_agent", END)
        builder.add_edge("calendar_agent", END)
        builder.add_edge("chat_agent", END)
        
        return builder.compile()

    def router_node(self, state: AgentState) -> Dict[str, Any]:
        """Analyzes request to identify primary intent."""
        return {}

    def route_decision(self, state: AgentState) -> str:
        """Determines which agent node should process the message."""
        if not state["messages"]:
            return "chat"
            
        last_msg = state["messages"][-1].content.lower()
        if any(w in last_msg for w in ["process", "task", "project", "create"]):
            return "process"
        elif any(w in last_msg for w in ["schedule", "plan", "optimize", "policy"]):
            return "schedule"
        elif any(w in last_msg for w in ["calendar", "meeting", "busy", "block"]):
            return "calendar"
        return "chat"

    def process_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Extracts process metadata from user inputs."""
        last_msg = state["messages"][-1].content
        
        # Mock LLM response if running test suite offline
        if self.llm is None:
            mock_proc = {
                "name": "Extracted Process Task",
                "priority": 4,
                "estimatedEffortHours": 10.0,
                "goal": "Verify Nvidia NIM extraction"
            }
            return {
                "current_process": mock_proc,
                "messages": [AIMessage(content="AI Process Agent: I have extracted a process project model from your prompt.")]
            }

        # Prompt engineering
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Process Agent. Extract name, priority, and estimated hours from prompt into JSON format."),
            ("human", "{input}")
        ])
        
        chain = prompt | self.llm
        res = chain.invoke({"input": last_msg})
        return {
            "messages": [AIMessage(content=res.content)]
        }

    def scheduling_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Assembles policy and planning requests."""
        # Mock LLM response if running test suite offline
        if self.llm is None:
            return {
                "suggested_policy": "Priority",
                "messages": [AIMessage(content="AI Scheduling Agent: Evaluated workloads. Recommend running Priority policy.")]
            }
            
        last_msg = state["messages"][-1].content
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Scheduling Agent. Suggest the best policy (Round Robin, Priority, SJF, EDF) based on input."),
            ("human", "{input}")
        ])
        chain = prompt | self.llm
        res = chain.invoke({"input": last_msg})
        return {
            "messages": [AIMessage(content=res.content)]
        }

    def calendar_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Handles calendar events and conflicts."""
        # Mock LLM response if running test suite offline
        if self.llm is None:
            return {
                "messages": [AIMessage(content="AI Calendar Agent: Evaluated calendar overlaps. 0 conflicts identified.")]
            }
            
        last_msg = state["messages"][-1].content
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Calendar Agent. Help the user check constraints or blocked events."),
            ("human", "{input}")
        ])
        chain = prompt | self.llm
        res = chain.invoke({"input": last_msg})
        return {
            "messages": [AIMessage(content=res.content)]
        }

    def chat_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Generates generic chat responses or offline help guide."""
        if self.llm is None:
            help_msg = (
                "I am the TimeSlice Attention Kernel. I can help you with:\n\n"
                "- **Process Management**: Create and track tasks (e.g., 'create a process for writing unit tests').\n"
                "- **Scheduling Optimization**: Suggest policies (e.g., 'suggest an optimal scheduling policy').\n"
                "- **Calendar Operations**: Scan for blocked focus slots (e.g., 'check my calendar blocks')."
            )
            return {
                "messages": [AIMessage(content=help_msg)]
            }
        
        last_msg = state["messages"][-1].content
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the generic Chat Agent of TimeSlice AI. Help the user understand how they can use the scheduler, process creator, and calendar tools."),
            ("human", "{input}")
        ])
        chain = prompt | self.llm
        res = chain.invoke({"input": last_msg})
        return {
            "messages": [AIMessage(content=res.content)]
        }

    def invoke_chat(self, user_prompt: str, history: List[BaseMessage] = None) -> Dict[str, Any]:
        """
        Public entry point invoking the LangGraph workflow.
        """
        messages = list(history or [])
        messages.append(HumanMessage(content=user_prompt))
        
        initial_state = {
            "messages": messages,
            "current_process": None,
            "action_plan": None,
            "suggested_policy": None
        }
        
        return self.graph.invoke(initial_state)
