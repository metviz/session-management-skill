---
name: session-management
description: >
  Persist and resume AI-assisted development sessions across restarts using structured JSON
  checkpoints. Use this skill whenever a user wants to save progress between Claude Code sessions,
  checkpoint a project state, resume work from a previous session, track skills or milestones
  acquired during development, clean up temp files after a session, or avoid losing context
  when switching tasks. Trigger on phrases like "save my session", "checkpoint progress",
  "resume where I left off", "don't lose my context", "sync memory", "log what I've done",
  or any mention of session continuity, project memory, or inter-session state.
---

# Session Management Skill

Saves and restores project-level context across Claude Code sessions using local JSON checkpoints.
Designed for long-running projects (bioinformatics pipelines, apps in development, research workflows)
where continuity between AI sessions matters.

---

## When to Use

- User is ending a session and wants to preserve state
- User is starting a new session and wants to resume from a checkpoint
- User wants to log milestones, notes, or newly acquired skills
- User wants to clean up temp files (plots, exports, scratch outputs) after a task
- User is working across multiple projects and needs isolated memory per project

---

## How It Works

Checkpoints are stored in `~/.ai_memory/<project_name>_memory.json` as an append-only JSON array.
Each entry captures a timestamp, freeform notes, and a list of skills or milestones acquired.
Optional temp file cleanup runs at checkpoint time.

---

## Core Script

The canonical implementation lives at `scripts/session_continue.py` in this skill folder.
Copy it into the user's project or run it directly.

```python
# Minimal usage
from session_continue import SessionContinue

sc = SessionContinue(project_name="MyProject")
sc.update_checkpoint(
    notes="Completed feature X; fixed edge case in parser.",
    skills=["Async I/O patterns", "Pandas groupby optimization"],
    files_to_cleanup=["temp_plot.png", "scratch_output.csv"]
)
```

---

## Workflow

### 1. Saving a Checkpoint

Call `update_checkpoint()` with:
- `notes` (str): Summary of what was accomplished this session
- `skills` (list[str]): New techniques, patterns, or knowledge gained
- `files_to_cleanup` (list[str], optional): Temp files to delete

Returns: `"Memory synced. Session ready for restart."`

### 2. Reading Previous Checkpoints

```python
import json, os

project = "MyProject"
path = os.path.expanduser(f"~/.ai_memory/{project}_memory.json")

with open(path) as f:
    history = json.load(f)

for entry in history[-3:]:  # last 3 sessions
    print(entry["timestamp"], "—", entry["notes"])
```

### 3. Resuming in a New Session

At the start of a session, load the latest checkpoint and paste it into your first message:

```python
sc = SessionContinue(project_name="MyProject")
# Read and print last entry to share with Claude
import json, os
path = os.path.expanduser("~/.ai_memory/MyProject_memory.json")
with open(path) as f:
    last = json.load(f)[-1]
print(last)
```

Then tell Claude: *"Here's my last checkpoint — pick up from here."*

---

## File Structure

```
~/.ai_memory/
└── <project_name>_memory.json   # Append-only checkpoint log
```

Each checkpoint entry:
```json
{
    "timestamp": "2025-04-15T10:32:00.123456",
    "notes": "Optimized GWAS parser; added Flutter UI hooks.",
    "skills_acquired": ["Advanced R-squared filtering", "Flutter state management"],
    "project": "VarViz_Dev"
}
```

---

## Context Window Monitoring

Claude Code exposes the current context usage as a percentage. When usage crosses **80%**, Claude should proactively suggest running a checkpoint before the session degrades or gets cut off.

### What Claude should do at ≥ 80%

When you notice context is at or above 80%, pause and say:

> ⚠️ **Context window is at [X]% — recommend saving a checkpoint now.**
> Run `sc.update_checkpoint(...)` to preserve your session state before continuing.
> This ensures smooth continuity if the session needs to restart.

Then offer to generate the checkpoint call with notes pre-filled from the current session.

### Nothing is lost — here's why

- Checkpoints are **append-only**: each save adds a new entry, nothing is ever overwritten
- The only files ever deleted are those you explicitly pass to `files_to_cleanup`
- Your full history accumulates in `~/.ai_memory/<project>_memory.json` indefinitely
- Saving a checkpoint early (at 80%) is a precaution, not a reset — you can keep working after

### Checking context usage in Claude Code

Claude Code surfaces context percentage in the UI. You can also ask Claude directly:
> *"What's your current context usage?"*

If it's above 80%, treat it as a nudge to checkpoint.

---

## Tips

- Use **descriptive project names** (`VarViz_Dev`, `BioSeq_Pipeline`) to isolate memory per project
- Call `update_checkpoint()` before every session end — treat it like a git commit message
- The `files_to_cleanup` param is ideal for matplotlib exports, test renders, or temp CSVs
- For long projects, periodically read back the full history to brief Claude on accumulated context
- You can store the script anywhere; it has no dependencies beyond Python stdlib

---

## Reference Script

See `scripts/session_continue.py` for the full implementation. Read it if you need to:
- Modify the storage schema
- Add new fields to the checkpoint payload
- Port to a different storage backend (SQLite, cloud, etc.)
