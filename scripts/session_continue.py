"""
session_continue.py — Session Management Skill for Claude Code
--------------------------------------------------------------
Persists project state across AI sessions using local JSON checkpoints.
Store at ~/.ai_memory/<project_name>_memory.json (append-only log).

Usage:
    sc = SessionContinue(project_name="MyProject")

    # Check context health before continuing heavy work
    sc.check_context(current_usage_pct=85)

    sc.update_checkpoint(
        notes="What I did this session.",
        skills=["Skill A", "Skill B"],
        files_to_cleanup=["temp_plot.png"]
    )

Nothing is ever lost:
    - Checkpoints are append-only; no entry is ever overwritten.
    - Only files explicitly passed to `files_to_cleanup` are deleted.
    - Full history accumulates indefinitely in ~/.ai_memory/<project>_memory.json
"""

import os
import json
from datetime import datetime

# Context window threshold — suggest checkpoint above this level
CONTEXT_WARN_THRESHOLD = 80  # percent


class SessionContinue:
    def __init__(self, project_name: str = "default_project"):
        """
        Initialize session manager for a named project.

        Args:
            project_name: Identifier for this project's memory file.
                          Use consistent names across sessions (e.g., "VarViz_Dev").
        """
        self.project_name = project_name
        self.memory_path = os.path.expanduser(
            f"~/.ai_memory/{project_name}_memory.json"
        )
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Creates the memory directory if it doesn't exist."""
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)

    def check_context(
        self,
        current_usage_pct: float,
        threshold: float = CONTEXT_WARN_THRESHOLD,
        auto_prompt: bool = True,
    ) -> str:
        """
        Check if context window usage is approaching the limit.
        Prints a warning and optionally suggests a pre-filled checkpoint call
        when usage is at or above the threshold (default: 80%).

        Args:
            current_usage_pct: Current context usage as a percentage (0–100).
            threshold:          Usage level that triggers the warning (default: 80).
            auto_prompt:        If True, print a ready-to-run checkpoint snippet.

        Returns:
            "ok" if below threshold, "warn" if at or above.

        Example:
            sc.check_context(current_usage_pct=85)
            # ⚠️  Context window at 85% (threshold: 80%)
            # Recommend saving a checkpoint now for smooth session continuity.
        """
        if current_usage_pct >= threshold:
            print(
                f"\n⚠️  Context window at {current_usage_pct:.0f}% "
                f"(threshold: {threshold:.0f}%)"
            )
            print(
                "Recommend saving a checkpoint now for smooth session continuity.\n"
                "Nothing will be lost — checkpoints are append-only.\n"
            )
            if auto_prompt:
                print("Run this to save your session:\n")
                print(
                    f'    sc = SessionContinue(project_name="{self.project_name}")\n'
                    f'    sc.update_checkpoint(\n'
                    f'        notes="<describe what you did this session>",\n'
                    f'        skills=["<skill or pattern learned>"],\n'
                    f'        files_to_cleanup=[]  # add temp files if any\n'
                    f'    )\n'
                )
            return "warn"

        remaining = threshold - current_usage_pct
        print(
            f"✓ Context at {current_usage_pct:.0f}% — "
            f"{remaining:.0f}% remaining before checkpoint is recommended."
        )
        return "ok"

    def update_checkpoint(
        self,
        notes: str,
        skills: list[str],
        files_to_cleanup: list[str] | None = None,
        extra: dict | None = None,
    ) -> str:
        """
        Save current session state and optionally clean up temp files.

        Args:
            notes:            Freeform summary of what was done this session.
            skills:           List of techniques/patterns/knowledge acquired.
            files_to_cleanup: Optional list of file paths to delete after saving.
            extra:            Optional dict of additional metadata to store.

        Returns:
            Confirmation string.
        """
        payload = {
            "timestamp": datetime.now().isoformat(),
            "notes": notes,
            "skills_acquired": skills,
            "project": self.project_name,
        }
        if extra:
            payload["extra"] = extra
        # Load existing history (or start fresh)
        history: list[dict] = []
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, "r") as f:
                    history = json.load(f)
            except (json.JSONDecodeError, IOError):
                history = []

        history.append(payload)

        with open(self.memory_path, "w") as f:
            json.dump(history, f, indent=4)

        if files_to_cleanup:
            self._purge_files(files_to_cleanup)

        return f"Memory synced ({len(history)} checkpoints). Session ready for restart."

    def _purge_files(self, file_list: list[str]) -> None:
        """Delete temp/session-specific files."""
        for file in file_list:
            if os.path.exists(file):
                os.remove(file)
                print(f"Removed artifact: {file}")
            else:
                print(f"Skipped (not found): {file}")

    def load_history(self, last_n: int | None = None) -> list[dict]:
        """
        Load checkpoint history for this project.

        Args:
            last_n: If set, return only the most recent N entries.

        Returns:
            List of checkpoint dicts, oldest first.
        """
        if not os.path.exists(self.memory_path):
            return []
        with open(self.memory_path, "r") as f:
            history = json.load(f)
        if last_n is not None:
            return history[-last_n:]
        return history

    def latest(self) -> dict | None:
        """Return the most recent checkpoint, or None if no history."""
        history = self.load_history()
        return history[-1] if history else None

    def summary(self, last_n: int = 5) -> str:
        """
        Return a human-readable summary of recent checkpoints.
        Useful for briefing Claude at the start of a new session.

        Args:
            last_n: Number of recent entries to include.

        Returns:
            Formatted string summary.
        """
        entries = self.load_history(last_n=last_n)
        if not entries:
            return f"No checkpoints found for project '{self.project_name}'."

        lines = [f"=== {self.project_name} — Last {len(entries)} checkpoint(s) ===\n"]
        for e in entries:
            ts = e.get("timestamp", "unknown time")
            notes = e.get("notes", "")
            skills = ", ".join(e.get("skills_acquired", []))
            lines.append(f"[{ts}]")
            lines.append(f"  Notes : {notes}")
            if skills:
                lines.append(f"  Skills: {skills}")
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI / quick-test entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sc = SessionContinue(project_name="VarViz_Dev")

    # Simulate checking context at 85% usage
    print("--- Context Check (85%) ---")
    sc.check_context(current_usage_pct=85)

    print("--- Context Check (60%) ---")
    sc.check_context(current_usage_pct=60)

    print("--- Saving Checkpoint ---")
    result = sc.update_checkpoint(
        notes="Optimized GWAS parser; added Flutter UI hooks.",
        skills=["Advanced R-squared filtering", "Flutter state management"],
        files_to_cleanup=["temp_plot_01.png"],
    )
    print(result)
    print()
    print(sc.summary())
