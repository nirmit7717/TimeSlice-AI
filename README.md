# TimeSlice AI 🧠⌚

> **Everything is a Process. Every Process deserves the Right Time Slice.**

TimeSlice AI is an AI-powered **Productivity Operating System** designed to optimize human attention. Unlike traditional task managers or calendar applications, TimeSlice AI models projects as operating system processes and allocates a user's finite attention using scheduling algorithms inspired by modern operating systems.

At the heart of the platform is the **Attention Kernel**, a multi-agent AI system (built using LangGraph) responsible for planning, scheduling, contextual reasoning, progress tracking, and adaptive learning.

---

## 🛠️ Monorepo Architecture

This project is organized as a domain-driven monorepo containing both the applications and the modular packages.

```
timeslice-ai/
├── apps/
│   ├── desktop/           # Tauri + React + TS (Desktop Client)
│   └── backend/           # FastAPI (Web APIs & Orchestration)
├── packages/
│   ├── shared/            # Shared interfaces, contracts, types, & schemas
│   ├── ui/                # Shared Design System UI components
│   ├── process-system/    # Process lifecycle services, health, & state
│   ├── scheduling-system/ # Pure deterministic scheduling engine
│   ├── execution-system/  # Time slices, checklist generator, progress tracker
│   ├── analytics-system/  # Attention debt, equity, & progress metrics
│   ├── context-vault/     # RAG context storage (SQLite & ChromaDB)
│   ├── adaptive-intelligence/ # Reward engines & Contextual Bandit profiles
│   ├── attention-kernel/  # Multi-agent LangGraph orchestration brain
│   └── integrations/      # Third-party adapters (Google/Apple Calendars, Telegram)
├── infrastructure/        # Terraform infrastructure & Nginx configs
├── docs/                  # Architectural documents & ADR records
│   └── design-bible/      # Original Product & Technical Design documents
├── scripts/               # Migration, seeding, & automation scripts
└── docker/                # Development & production Dockerfiles
```

---

## 🧭 Project Documents

- **Design Bible (Markdown):** [docs/design-bible/PRD.md](file:///w:/Projects%20Antigravity/TimeSlice%20AI/docs/design-bible/PRD.md)
- **Design Bible (Original Word):** [docs/design-bible/Product%20and%20Technical%20Design%20Bible.docx](file:///w:/Projects%20Antigravity/TimeSlice%20AI/docs/design-bible/Product%20and%20Technical%20Design%20Bible.docx)
- **Development Roadmap:** [development_roadmap.md](file:///w:/Projects%20Antigravity/TimeSlice%20AI/development_roadmap.md)

---

## 📐 Core Engineering Principles

Before contributing to TimeSlice AI, make sure you understand these architectural rules:

1. **Separation of Responsibilities:** Each package owns exactly one capability. For example, `packages/scheduling-system` owns scheduling logic and contains no database, API, or AI-specific code.
2. **The Attention Kernel Never Owns Business Logic:** The AI kernel is an orchestrator. It uses tools to interact with system APIs (`Kernel` ➔ `Create Process Tool` ➔ `Process System` ➔ `Database`). The AI should never bypass standard business rules.
3. **Independently Testable Subsystems:** You must be able to run scheduling tests or process CRUD functions without booting FastAPI, LangGraph, or database engines.
4. **Local-First, Cloud-Enhanced:** All personal databases, embeddings, and context memories remain local by default. Cloud layers are used strictly for sync, backup, and cross-device authentication.
