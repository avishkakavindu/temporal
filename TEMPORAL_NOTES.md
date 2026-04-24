# Temporal — Learning Notes

## What is Temporal?

A **workflow orchestration platform** that lets you write long-running, reliable processes in plain code — without manually handling failures, retries, or server crashes.

---

## The Big 3 Concepts

### 1. Activities — "the actual work"

```python
# activities.py
@activity.defn
async def say_hello(name: str) -> str:
    return f"Hello {name}, welcome to Temporal!"

@activity.defn
async def fetch_cat_images(limit: int) -> list:
    # makes real HTTP call to external API
    ...
```

- A plain Python function decorated with `@activity.defn`
- Where all **side effects** live: HTTP calls, DB writes, emails
- Can fail — Temporal will automatically retry them
- Do NOT need to be deterministic

---

### 2. Workflows — "the coordinator"

```python
# workflows.py
@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            say_hello, name, start_to_close_timeout=timedelta(seconds=5)
        )
```

- Orchestrates *what to do and in what order* by calling Activities
- `@workflow.defn` marks the class, `@workflow.run` marks the entry point
- **Must be deterministic** — no `datetime.now()`, no random, no direct HTTP calls
- All real work must go through Activities
- Temporal **replays** workflows from history to restore state after crashes

---

### 3. Worker — "the executor"

```python
# run_worker.py
client = await Client.connect("localhost:7233")
worker = Worker(
    client,
    task_queue="main-task-queue",
    workflows=[GreetingWorkflow, CatWorkflow],
    activities=[say_hello, fetch_cat_images],
)
await worker.run()
```

- Your Python process that connects to the Temporal server
- Registers which workflows and activities it handles
- Listens on a **task queue** for work
- The Temporal server never runs code directly — it tells workers what to run

---

## How it All Flows

```
You (CLI) ──► Temporal Server ──► Task Queue ──► Worker
                                                    │
                                              runs Workflow
                                                    │
                                          calls Activities
                                                    │
                                         (HTTP, DB, etc.)
                                                    │
                                         returns result ──► back to you
```

### Example trigger commands (from run_worker.py)

```bash
# Run GreetingWorkflow
temporal workflow execute --type GreetingWorkflow --task-queue main-task-queue --input '"Avishka"'

# Run CatWorkflow
temporal workflow execute --type CatWorkflow --task-queue main-task-queue --input 5
```

---

## The Durability Guarantee

If your server crashes mid-workflow:

1. Every step is recorded in an **event history** on the Temporal server
2. When the worker restarts, Temporal **replays the workflow** from history
3. Already-completed activities are skipped (results come from history)
4. The workflow picks up exactly where it left off

This is called **durable execution** — the workflow is effectively crash-proof.

---

## Timeouts

```python
# workflows.py
workflow.execute_activity(
    say_hello, name, start_to_close_timeout=timedelta(seconds=5)
)
```

| Timeout | Meaning |
|---|---|
| `start_to_close_timeout` | Max time from activity start to completion |
| `schedule_to_start_timeout` | Max time waiting in queue before a worker picks it up |
| `schedule_to_close_timeout` | Total time from scheduling to completion |
| `heartbeat_timeout` | For long-running activities that report progress |

---

## Project Structure

```
temporal-project/
├── activities.py    ← Functions that do real work (HTTP, DB, etc.)
├── workflows.py     ← Coordinators that call activities in order
└── run_worker.py    ← Connects to Temporal server and starts listening
```

> In production, workflow workers and activity workers are often separate processes so they can scale independently.

---

## Running the Project

```bash
# Terminal 1 — start Temporal server (dev mode)
temporal server start-dev

# Terminal 2 — start the worker
python run_worker.py

# Terminal 3 — trigger a workflow
temporal workflow execute --type GreetingWorkflow --task-queue main-task-queue --input '"Avishka"'
```

---

## Key Mental Model

| Concept | Role | Analogy |
|---|---|---|
| **Temporal Server** | Stores state, dispatches tasks | A very reliable task manager |
| **Workflow** | Orchestrates the steps | A recipe |
| **Activity** | Does actual work | Each cooking step |
| **Worker** | Executes workflows/activities | The chef |
| **Task Queue** | Routes work to the right worker | The order ticket rail |

**Core insight:** your code looks like normal sequential Python, but Temporal makes it survive crashes, retries, and distributed failures automatically.
