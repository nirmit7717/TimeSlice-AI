# TimeSlice AI — File Mapper & Architecture Guide

This document maps out the domain-driven monorepo architecture of TimeSlice AI, explaining the purpose of each directory and key codebase file.

---

## 📂 Codebase Directory Overview

```
timeslice-ai/
├── apps/                  # Target interfaces (Desktop UI and Backend API)
│   ├── backend/           # FastAPI Web Application & API Routers
│   └── desktop/           # Tauri, React, and TypeScript Desktop Application
├── packages/              # Domain-specific python packages containing core logic
│   ├── database/          # SQLAlchemy connection, ORM models, Repositories, & Sync Engine
│   ├── scheduling-system/ # Scheduling Policies, Schedulers, & Metrics Calculations
│   ├── execution-system/  # Focus Session Lifecycle & Checklist Operations
│   ├── analytics-system/  # Analytical Rollups, Streaks, & Charts Calculations
│   ├── context-vault/     # Semantic Vector Storage & RAG Context Retrieval
│   ├── adaptive-intelligence/ # Contextual Bandit (LinUCB) & Reward Engine
│   ├── attention-kernel/  # Multi-Agent LangGraph Conversations & DB Tools
│   ├── notification-system/ # Desktop Alerts, Telegram Dispatcher, & Background Daemon
│   └── platform/          # Host OS Environment Configs
├── deployment/            # Production Containerization & Backup Scripts
├── docs/                  # System Architecture & Design Bible Documents
├── run.ps1                # PowerShell script for one-click startup
└── run.bat                # CMD script for one-click startup
```

---

## 🗺️ Core File Maps

### 1. Applications (`apps/`)

#### Backend (`apps/backend/`)
*   [main.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/apps/backend/main.py): Application entrypoint. Instantiates FastAPI, registers CORS policies, maps database lifespan hooks, and mounts core routers.
*   `app/dependencies.py`: Exposes dependency injections for DB Sessions (`get_db`), Repositories (`get_process_repo`, `get_slice_repo`), and singleton clients (ChromaDB `get_vector_store`).
*   [app/auth.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/apps/backend/app/auth.py): Handles local password hashing using `bcrypt` and encoding/decoding JWT credentials.
*   **Routers (`app/routers/`)**:
    *   [auth.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/apps/backend/app/routers/auth.py): Registration, login, token refresh, and profile fetching endpoints.
    *   [processes.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/apps/backend/app/routers/processes.py): Standard process CRUD. Automatically schedules recomputation upon updates.
    *   [slices.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/apps/backend/app/routers/slices.py): Focus session triggers (`/start`, `/complete`, `/abandon`) and checklist toggles.
    *   [scheduler.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/apps/backend/app/routers/scheduler.py): Exposes focus plans, policy simulations, and recommendations.
    *   [calendar.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/apps/backend/app/routers/calendar.py): Manual local calendar CRUD, focus time slice merges, and OAuth stubs.
    *   [notifications.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/apps/backend/app/routers/notifications.py): Notification log lookups and manual alert tests.
    *   [analytics.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/apps/backend/app/routers/analytics.py): Exposes focus streaks, time allocations, and weekly metrics.
    *   [sync.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/apps/backend/app/routers/sync.py): Exposes transaction pulls, conflict detection, and status reporting.
    *   [chat.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/apps/backend/app/routers/chat.py): Handles LangGraph conversation streams, passing database contexts on-the-fly.

#### Desktop Frontend (`apps/desktop/`)
*   `src/App.tsx`: Layout routing and JWT authentication checks.
*   `src/pages/`:
    *   `dashboard.tsx`: Main cockpit. Renders live insights, recommendations, and checklist updates.
    *   `calendar.tsx`: Displays the combined scheduled execution windows and manual appointments.
    *   `processes.tsx`: Detailed listing and addition of active/paused operational processes.
    *   `chat.tsx`: Multi-agent kernel chat interface.
    *   `vault.tsx`: Context vault search panel and conflict list resolution grid.
    *   `settings.tsx`: Configuration for integrations, themes, and LinUCB preferences.
*   `src/stores/`: Zustand state managers (`auth-store.ts`, `process-store.ts`, `calendar-store.ts`, `adaptive-store.ts`, `sync-store.ts`).
*   `src/components/shared/`: Layout units (`sidebar.tsx`, `timeline.tsx`, `insights.tsx`, `recommendation-card.tsx`, `sync-status.tsx`, `sync-conflict-panel.tsx`, `onboarding.tsx`).

---

### 2. Monorepo Shared Packages (`packages/`)

#### Database (`packages/database/`)
*   [database/connection.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/database/database/connection.py): Orchestrates SQLite connections. Enforces foreign key constraints at connection startup.
*   [database/models.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/database/database/models.py): Mapped SQLAlchemy schemas defining Database structures.
*   `database/repositories/`: Implements the repository pattern to encapsulate database writes and queries (e.g. `process_repo.py`, `slice_repo.py`).
*   [database/sync/sync_manager.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/database/database/sync/sync_manager.py): Implements bidirectional sync. Stores local changes in a transaction log and detects conflicts by comparing modification timestamps.
*   [database/vector/vector_store.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/database/database/vector/vector_store.py): Wrapper interface for local persistent ChromaDB semantic embedding collections.

#### Scheduling Engine (`packages/scheduling-system/`)
*   `scheduling_system/policy/`: Contains clean policy algorithms—[round_robin.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/scheduling-system/scheduling_system/policy/round_robin.py), [priority.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/scheduling-system/scheduling_system/policy/priority.py), [sjf.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/scheduling-system/scheduling_system/policy/sjf.py), and [edf.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/scheduling-system/scheduling_system/policy/edf.py).
*   `scheduling_system/metrics/`: Calculates completion velocity, deadline risk tiers, attention debt, and health scores.
*   [scheduling_system/planner/execution_planner.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/scheduling-system/scheduling_system/planner/execution_planner.py): Pure execution planner which loops over remaining process debts and structures time blocks, avoiding calendar overlaps.

#### Focus Execution (`packages/execution-system/`)
*   [execution_system/services/execution_service.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/execution-system/execution_system/services/execution_service.py): Manages focus cycles and tracks checkpoints. Fires learning feedback events when a slice is marked completed or abandoned.

#### Analytics (`packages/analytics-system/`)
*   [analytics_system/services/analytics_service.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/analytics-system/analytics_system/services/analytics_service.py): Gathers completed time slices, computing focus streaks, allocation statistics, and daily averages.

#### Context Vault (`packages/context-vault/`)
*   [context_vault/services/context_service.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/context-vault/context_vault/services/context_service.py): Wraps semantic text processing and RAG retrieval pipelines.

#### Adaptive Intelligence (`packages/adaptive-intelligence/`)
*   [adaptive_intelligence/contextual_bandits/bandit_engine.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/adaptive-intelligence/adaptive_intelligence/contextual_bandits/bandit_engine.py): Implements the Disjoint LinUCB algorithm. Maps a 6D operator feature vector to 20 potential settings arms (4 policies × 5 quantums).
*   [adaptive_intelligence/reward/reward_engine.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/adaptive-intelligence/adaptive_intelligence/reward/reward_engine.py): Computes composite reinforcement learning rewards based on session lengths, checklist completion ratios, and consistency bonuses.
*   [adaptive_intelligence/operator_model/operator_model.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/adaptive-intelligence/adaptive_intelligence/operator_model/operator_model.py): Houses the rolling average behavioral model representing operator velocity, consistency, focus length, and switch tolerances.
*   [adaptive_intelligence/learning_pipeline/learning_pipeline.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/adaptive-intelligence/adaptive_intelligence/learning_pipeline/learning_pipeline.py): Bridges focus events to the LinUCB bandit engine, updating matrix parameters and writing states back to the database.

#### Attention Kernel (`packages/attention-kernel/`)
*   [attention_kernel/agent_kernel.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/attention-kernel/attention_kernel/agent_kernel.py): Renders the multi-agent graph, directing execution flows through the router and individual planning agents.
*   [attention_kernel/tools.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/attention-kernel/attention_kernel/tools.py): Regroups operational tools, allowing agents to execute live commands (planning, database writes, searches) via dependencies.

#### Notifications (`packages/notification-system/`)
*   [notification_system/dispatcher.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/notification-system/notification_system/dispatcher.py): Triggers local balloon alerts and Telegram bot alerts.
*   [notification_system/scheduler/reminder_scheduler.py](file:///w:/Projects%20Antigravity/TimeSlice%20AI/packages/notification-system/notification_system/scheduler/reminder_scheduler.py): Background daemon checking upcoming focus intervals and reflection prompts.

---

### 3. Deployments & Infrastructure (`deployment/`)

*   `deployment/docker/production.Dockerfile`: Multi-stage Docker image packaging the FastAPI backend, embedding all 9 packages as python wheels.
*   `deployment/scripts/db_backup.py` / `db_restore.py`: Utility scripts for SQLite local exports and imports.
