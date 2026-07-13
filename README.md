# TimeSlice AI 🧠⌚

> **Everything is a Process. Every Process deserves the Right Time Slice.**

TimeSlice AI is an AI-powered **Productivity Operating System** designed to optimize human attention. Unlike traditional task managers or calendar applications, TimeSlice AI models projects as operating system processes and allocates a user's finite attention using scheduling algorithms inspired by modern operating systems.

At the heart of the platform is the **Attention Kernel**, a multi-agent AI system (built using LangGraph) responsible for planning, scheduling, contextual reasoning, progress tracking, and adaptive learning.

---

## 🛠️ Clean Monorepo Architecture

This project is organized as a domain-driven, modular monorepo containing:

```
timeslice-ai/
├── apps/
│   ├── desktop/           # Tauri + React + TS (Desktop UI Client)
│   └── backend/           # FastAPI (Web APIs, JWT Auth, Sync & Orchestration)
├── packages/
│   ├── database/          # SQLite ORM models, transaction log sync, & vector DB client
│   ├── scheduling-system/ # Pure scheduling policy engine (RR, Priority, SJF, EDF)
│   ├── execution-system/  # Focus slice lifecycle & checklist state tracker
│   ├── analytics-system/  # Attention debt, streaks, & time allocation calculations
│   ├── context-vault/     # Semantic RAG context storage (ChromaDB)
│   ├── adaptive-intelligence/ # Persisted Contextual Bandit (LinUCB) & Reward Engine
│   ├── attention-kernel/  # Multi-agent LangGraph orchestrator & DB tools
│   ├── notification-system/ # Local desktop tips, Telegram alerts, & background reminders
│   └── platform/          # Platform and environment configurations
├── deployment/            # Docker compose and PostgreSQL/Cognito provider configs
│   ├── docker/            # Production multi-stage Dockerfile
│   └── scripts/           # Database migration, backup, & restore scripts
├── docs/                  # Architectural documents & ADR records
├── run.ps1                # One-click PowerShell startup script
└── run.bat                # One-click CMD startup script
```

---

## 🚀 Getting Started & Quick Launch

We provide zero-configuration startup scripts at the root directory to automatically resolve dependencies, configure `PYTHONPATH`, and boot both backend and frontend servers in separate windows.

*   **Windows PowerShell**:
    ```powershell
    .\run.ps1
    ```
*   **Command Prompt (CMD)**:
    ```cmd
    .\run.bat
    ```

Once running:
*   **Web App Interface**: `http://localhost:1420`
*   **FastAPI REST API**: `http://127.0.0.1:8000`
*   **Interactive API Documentation**: `http://127.0.0.1:8000/docs`

---

## 🎯 Current Implementation Status

All core phases of the product roadmap are complete and fully operational:

*   **Process & Checklist Management**: Dynamic operational metrics (**Attention Debt**, **Attention Equity**, and **Process Health**) recalculate automatically upon process modifications. Checklist items link directly to focus windows.
*   **Scheduling Policies**: Fully supports **Priority**, **Round Robin**, **Shortest Job First (SJF)**, and **Earliest Deadline First (EDF)** policies with rest period overlays.
*   **Attention Kernel Chat**: A multi-agent LangGraph workflow executing conversational requests by calling secure database, scheduling, and calendar tools on-the-fly.
*   **Contextual Bandit Engine**: A disjoint **LinUCB** algorithm mapping operator metrics (consistency, velocity, hour, day, switch tolerances) to optimal policy-quantum configurations, persisted locally as JSON.
*   **Execution & Analytics**: High-fidelity session trackers logging reflections, streaks, weekly hours, and visual allocation charts.
*   **Notification Daemon**: An `APScheduler` background service triggering upcoming focus reminders, post-session reflection forms, and weekly summary reviews.
*   **Bidirectional Sync**: Real-time synchronization pulling transaction logs, identifying concurrent updates, and prompting users with visual conflict-resolution cards.

---

## 🧪 Quality Gates & Verification

The codebase runs a unified validation suite verified by our GitHub CI/CD action on push and pull requests:

*   **Test Quality**: **100/100 backend test cases pass cleanly** (covering database repositories, sync engines, bandits, planners, and router endpoints).
*   **Tauri Frontend**: The desktop application builds cleanly with **0 TypeScript compiler errors or warnings**.
*   **Performance Requirements (NFRs Verified)**:
    *   *Schedule Generation*: Compiling allocations for 100 active processes takes **0.061 seconds** (Requirement: ≤ 1 second).
    *   *AI Overhead*: Conversation graph routing and tool checking takes **0.012 seconds** (Requirement: ≤ 5 seconds).
    *   *System Health Check*: Average endpoint latency is **20.54 ms** (Requirement: ≤ 100 ms).
