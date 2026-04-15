# 🧠 session-management — Claude Code Skill

> Never lose your AI session context again. Checkpoint your work, resume seamlessly, and get warned before your context window runs out.

A **Claude Code skill** that persists project state across sessions using local JSON checkpoints. Built for long-running projects — bioinformatics pipelines, app development, research workflows — where continuity between AI sessions matters.

> 💡 **Works standalone or alongside GSD** — see [comparison below](#-vs-gsd-get-shit-done).

---

## ✨ Features

| Feature | Description |
|---|---|
| 📌 Append-only checkpoints | Every save adds a new entry — nothing is ever overwritten |
| ⚠️ Context window monitor | Warns at 80% usage and suggests saving before cutoff |
| 🧹 Temp file cleanup | Optionally delete plots, exports, scratch files at checkpoint time |
| 📖 Session summary | Human-readable history to brief Claude when resuming |
| 🗂️ Per-project isolation | Separate memory file per project name |

---

## 📦 Install

**Option A — Clone directly into your Claude skills folder:**
```bash
git clone https://github.com/metviz/session-management-skill ~/.claude/skills/session_management
```

**Option B — Unzip from `.skill` file:**
```bash
mkdir -p ~/.claude/skills
unzip session_management.skill -d ~/.claude/skills/
```

Claude Code picks it up automatically on the next session — no config needed.

---

## 🚀 Usage

```python
from scripts.session_continue import SessionContinue

sc = SessionContinue(project_name="MyProject")

# 1. Check context window health
sc.check_context(current_usage_pct=85)
# ⚠️  Context window at 85% (threshold: 80%)
# Recommend saving a checkpoint now for smooth session continuity.

# 2. Save a checkpoint
sc.update_checkpoint(
    notes="Completed GWAS parser optimization; fixed edge case in VCF reader.",
    skills=["R-squared filtering", "Flutter state management"],
    files_to_cleanup=["temp_plot.png", "scratch_output.csv"]
)
# → Memory synced (3 checkpoints). Session ready for restart.

# 3. Resume — print summary to brief Claude
print(sc.summary())
```

---

## 💬 Claude Trigger Phrases

Claude Code activates this skill automatically when you say:

- `"save my session"` / `"checkpoint progress"`
- `"resume where I left off"` / `"don't lose my context"`
- `"sync memory"` / `"log what I've done"`
- Context window reaches **80%+**

---

## 📁 File Structure

```
~/.claude/skills/session_management/
├── SKILL.md                  # Skill definition + Claude instructions
├── README.md                 # This file
├── .gitignore
└── scripts/
    └── session_continue.py   # Core implementation
```

Checkpoints are stored at:
```
~/.ai_memory/<project_name>_memory.json
```

Each checkpoint entry looks like:
```json
{
    "timestamp": "2026-04-15T10:32:00.123456",
    "notes": "Optimized GWAS parser; added Flutter UI hooks.",
    "skills_acquired": ["R-squared filtering", "Flutter state management"],
    "project": "VarViz_Dev"
}
```

---

## 🔒 Nothing is Ever Lost

- Checkpoints are **append-only** — the file only grows
- Files are deleted **only** if explicitly passed to `files_to_cleanup`
- Saving at 80% context is a precaution, not a reset — you keep working after
- Think of it like `git commit` mid-feature: preserved, continuable

---

## 🛠️ API Reference

### `SessionContinue(project_name)`
Initialize for a named project. Creates `~/.ai_memory/<project>_memory.json`.

### `.check_context(current_usage_pct, threshold=80)`
Prints a warning and ready-to-run snippet if usage ≥ threshold.

### `.update_checkpoint(notes, skills, files_to_cleanup=None, extra=None)`
Appends a checkpoint entry. Optionally deletes temp files.

### `.summary(last_n=5)`
Returns a formatted string of the last N checkpoints — paste into Claude to resume.

### `.latest()`
Returns the most recent checkpoint dict, or `None`.

### `.load_history(last_n=None)`
Returns the full checkpoint list, optionally trimmed to last N entries.

---

## ⚔️ vs GSD (Get Shit Done)

[GSD](https://github.com/gsd-build/get-shit-done) is a popular full-scale spec-driven development system for Claude Code (53k ⭐). It also deals with context rot — but differently. Here's how they compare:

| | `session-management` (this) | GSD's `/clear` approach |
|---|---|---|
| **What it does** | Saves state to disk before context fills | Wipes context window completely |
| **After clearing** | `sc.summary()` reloads from `~/.ai_memory/` | `/gsd-resume-work` reloads from `.planning/` files |
| **State storage** | JSON checkpoint, lives outside project | `STATE.md`, `ROADMAP.md`, `HANDOFF.json` inside `.planning/` |
| **Requires GSD?** | ❌ Fully standalone | ✅ Needs full GSD install |
| **Tracks skills learned** | ✅ | ❌ |
| **Cross-project memory** | ✅ Isolated per project name | ❌ Per-project only |
| **Install size** | ~150 lines, Python stdlib only | Full npm package, 30+ commands |
| **Works with any project** | ✅ Drop in anywhere | ✅ But needs GSD workflow |

### How GSD handles context

GSD's own docs recommend: *"Clear your context window between major commands: `/clear` in Claude Code. GSD is designed around fresh contexts — every subagent gets a clean 200K window. If quality is dropping in the main session, clear and use `/gsd-resume-work` or `/gsd-progress` to restore state."*

The difference: `/clear` in GSD only works safely **because** GSD's planning files exist. Without them, clearing means starting from scratch.

### Using both together ✅

They're complementary, not competing. GSD even has **project skills awareness** — its agents automatically discover and load skills from your project. That means you can drop `session-management` into a GSD project and it gets picked up automatically.

**Recommended pattern with GSD:**
```bash
# Before running /clear between phases:
sc.update_checkpoint(
    notes="Finished phase 2 — auth flow complete.",
    skills=["JWT handling", "httpOnly cookies"]
)

# Now safely clear
/clear

# Resume with GSD
/gsd-resume-work
```

This gives you **two layers of recovery**: GSD's planning files + your own portable checkpoint that survives outside any specific project or tool.

---

## 📄 License

MIT — use freely, modify as needed.
