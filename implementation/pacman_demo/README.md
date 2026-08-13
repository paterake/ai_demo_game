# ai_game_pacman_demo

Showcase of the Claude Code workflow: brief → PRD → backlog continuity → implementation.

**Source brief:** the Pac-Man prompt from the AI Assisted Development workshop (slide 26).

This folder is intentionally **docs-first**. In the workshop, breakout teams will build the runnable scaffold and the game directly in this folder by driving the agent from the anchor backlog.

**What this demonstrates:**
- Turning a naive single-file prompt into a governed PRD
- Using a backlog continuity anchor doc to implement across multiple sessions without losing context
- Config purity: colours, timing, and game rules live in YAML, not source code
- Modular structure: one class per file, renderer decoupled from game logic

**Start here:** [PRD.md](PRD.md) then [docs/TODO.md](docs/TODO.md).
