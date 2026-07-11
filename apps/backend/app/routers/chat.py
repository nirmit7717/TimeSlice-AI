from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from attention_kernel.agent_kernel import AgenticAttentionKernel
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter(prefix="/chat", tags=["chat"])
kernel = AgenticAttentionKernel()

class ChatMessagePayload(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessagePayload]] = None

@router.post("")
def chat_with_agent(payload: ChatRequest):
    """
    Invokes the multi-agent LangGraph attention kernel.
    """
    # Translate chat history to LangChain messages format
    history_messages = []
    if payload.history:
        for msg in payload.history:
            if msg.role == "user":
                history_messages.append(HumanMessage(content=msg.content))
            else:
                history_messages.append(AIMessage(content=msg.content))

    try:
        # Run graph
        res = kernel.invoke_chat(payload.message, history=history_messages)
        
        # Format response
        messages_out = []
        for m in res.get("messages", []):
            role = "user" if isinstance(m, HumanMessage) else "assistant"
            messages_out.append({"role": role, "content": m.content})
            
        return {
            "messages": messages_out,
            "currentProcess": res.get("current_process"),
            "suggestedPolicy": res.get("suggested_policy")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Kernel execution error: {str(e)}"
        )
