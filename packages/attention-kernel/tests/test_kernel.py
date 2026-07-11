import pytest
from attention_kernel.agent_kernel import AgenticAttentionKernel

def test_agent_kernel_routing_and_execution():
    # Instantiates with default mock-key (no LLM, mock mode enabled)
    kernel = AgenticAttentionKernel()
    
    # 1. Test Process Intent Routing
    res_proc = kernel.invoke_chat("Please create a new project process for coding.")
    assert "messages" in res_proc
    # The last message should be from the process agent mock
    last_msg = res_proc["messages"][-1].content
    assert "Process Agent" in last_msg
    assert res_proc["current_process"] is not None
    assert res_proc["current_process"]["name"] == "Extracted Process Task"

    # 2. Test Scheduling Intent Routing
    res_sched = kernel.invoke_chat("Please run a scheduling optimization plan.")
    assert "messages" in res_sched
    last_msg = res_sched["messages"][-1].content
    assert "Scheduling Agent" in last_msg
    assert res_sched["suggested_policy"] == "Priority"

    # 3. Test Calendar Intent Routing
    res_cal = kernel.invoke_chat("Check my calendar for blockages tomorrow.")
    assert "messages" in res_cal
    last_msg = res_cal["messages"][-1].content
    assert "Calendar Agent" in last_msg
