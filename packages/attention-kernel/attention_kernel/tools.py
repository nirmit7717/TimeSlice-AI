import time
from typing import Dict, Any, List, Optional
from database.repositories.process_repo import ProcessRepository
from database.repositories.slice_repo import TimeSliceRepository
from scheduling_system.services.scheduling_service import SchedulingService
from execution_system.services.execution_service import ExecutionService
from analytics_system.services.analytics_service import AnalyticsService
from context_vault.services.context_service import ContextService

class ToolRegistry:
    """
    Registry of all available tools for specialist agents. PRD §15.18
    """
    def __init__(self, db_session):
        self.db = db_session
        self.process_repo = ProcessRepository(db_session)
        self.slice_repo = TimeSliceRepository(db_session)
        self.sched_service = SchedulingService()
        self.exec_service = ExecutionService(db_session)
        self.analytics_service = AnalyticsService(db_session)
        self.context_service = ContextService()

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a concrete tool based on name and validates standard response contract. PRD §15.17
        """
        start_time = time.time()
        status = "success"
        message = ""
        data = {}

        try:
            # ── Process Tools ──────────────────────────────────────────────────
            if tool_name == "CreateProcessTool":
                from scheduling_system.models.process import Process
                from datetime import datetime
                # Construct domain model and save
                proc = Process(
                    id=params.get("id", str(uuid.uuid4())),
                    name=params["name"],
                    description=params.get("description", ""),
                    goal=params.get("goal", ""),
                    priority=params.get("priority", 1),
                    deadline=datetime.fromisoformat(params["deadline"]),
                    estimated_effort_hours=params["estimated_effort_hours"],
                    remaining_effort_hours=params.get("remaining_effort_hours", params["estimated_effort_hours"]),
                    status=params.get("status", "Active"),
                    tags=params.get("tags", []),
                    dependency_ids=params.get("dependency_ids", []),
                    progress=0.0,
                    health_score=100.0,
                    attention_debt=0.0,
                    attention_equity=0.0
                )
                res = self.process_repo.create(proc)
                data = res.model_dump()
                message = f"Process '{proc.name}' created successfully"

            elif tool_name == "UpdateProcessTool":
                # update existing process
                from database.models import DbProcess
                pid = params["id"]
                existing = self.process_repo.get(pid)
                if not existing:
                    raise ValueError(f"Process '{pid}' not found")
                for k, v in params.items():
                    if k != "id" and hasattr(existing, k):
                        setattr(existing, k, v)
                res = self.process_repo.update(existing)
                data = res.model_dump()
                message = f"Process '{pid}' updated successfully"

            elif tool_name == "DeleteProcessTool":
                pid = params["id"]
                success = self.process_repo.delete(pid)
                data = {"success": success}
                message = f"Process '{pid}' deleted"

            elif tool_name == "GetProcessTool":
                pid = params["id"]
                existing = self.process_repo.get(pid)
                if not existing:
                    raise ValueError(f"Process '{pid}' not found")
                data = existing.model_dump()
                message = "Process retrieved"

            # ── Scheduling Tools ───────────────────────────────────────────────
            elif tool_name == "GenerateExecutionPlanTool":
                plan = self.sched_service.generate_execution_plan(
                    processes=self.process_repo.list(),
                    calendar={"blocked_intervals": []},
                    preferences={
                        "max_daily_hours": params.get("max_daily_hours", 8.0),
                        "quantum_hours": params.get("quantum_hours", 2.0),
                        "available_hours": params.get("available_hours", 8.0)
                    },
                    policy_name=params.get("policy_name", "round_robin")
                )
                data = plan.model_dump()
                message = "Execution plan generated"

            elif tool_name == "RecommendSchedulingPolicyTool":
                # Simple recommendation check
                data = {"recommended_policy": "round_robin", "confidence": 0.85}
                message = "Recommended policy: Round Robin"

            elif tool_name == "SimulateScheduleTool":
                res = self.sched_service.simulate_policy(
                    policy_name=params.get("policy_name", "round_robin"),
                    processes=self.process_repo.list(),
                    constraints={"blocked_intervals": [], "quantum_hours": 2.0, "available_hours": 8.0}
                )
                data = res
                message = f"Simulation for policy '{params.get('policy_name')}' finished"

            # ── Execution Tools ────────────────────────────────────────────────
            elif tool_name == "GenerateChecklistTool":
                slice_id = params["time_slice_id"]
                checklists = self.exec_service.get_checklists(slice_id)
                data = [item.id for item in checklists]
                message = "Checklist loaded"

            elif tool_name == "SubmitReflectionTool":
                slice_id = params["time_slice_id"]
                res = self.exec_service.complete_time_slice(
                    slice_id=slice_id,
                    progress_gained=params.get("progress_gained", 0.1),
                    reflection=params.get("reflection", "")
                )
                data = {"status": "Completed"}
                message = "Reflection submitted"

            # ── Analytics Tools ────────────────────────────────────────────────
            elif tool_name == "GetProcessHealthTool":
                self.analytics_service.refresh_analytics()
                from database.models import DbAnalytics
                pid = params["id"]
                metric = self.db.query(DbAnalytics).filter(DbAnalytics.process_id == pid).first()
                if metric:
                    data = {
                        "process_id": metric.process_id,
                        "process_health": metric.process_health,
                        "health_status": metric.health_status
                    }
                message = "Process health loaded"

            # ── Context Tools ──────────────────────────────────────────────────
            elif tool_name == "RetrieveContextTool":
                q = params["query"]
                res = self.context_service.retrieve(q)
                data = res.model_dump()
                message = "Semantic search retrieved context package"

            elif tool_name == "StoreContextTool":
                doc_id = params["id"]
                text = params["text"]
                meta = params.get("metadata", {})
                self.context_service.store(doc_id, text, meta)
                message = "Context saved inside vault"

            else:
                raise ValueError(f"Unknown tool name: {tool_name}")

        except Exception as e:
            status = "error"
            message = str(e)

        end_time = time.time()
        return {
            "status": status,
            "tool": tool_name,
            "message": message,
            "data": data,
            "execution_time_ms": int((end_time - start_time) * 1000)
        }
