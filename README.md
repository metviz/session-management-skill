# 🧠 session-management — Claude Code Skill

> Never lose your AI session context again.

A Claude Code skill that persists project state across sessions using local JSON checkpoints.

## Install

```bash
git clone https://github.com/metviz/session-management-skill ~/.claude/skills/session_management
```

## Usage

```python
from scripts.session_continue import SessionContinue

sc = SessionContinue(project_name="MyProject")
sc.check_context(current_usage_pct=85)
sc.update_checkpoint(
    notes="What I did this session.",
    skills=["Skill A", "Skill B"],
    files_to_cleanup=["temp_plot.png"]
)
print(sc.summary())
```
