# ai_game_pacman_dryrun

Showcase of the Claude Code workflow: brief → PRD → backlog continuity → implementation.

**Source brief:** the Pac-Man prompt from the AI Assisted Development workshop (slide 26).

**What this demonstrates:**
- Turning a naive single-file prompt into a governed PRD
- Using a backlog continuity anchor doc to implement across multiple sessions without losing context
- Config purity: colours, timing, and game rules live in YAML, not source code
- Modular structure: one class per file, renderer decoupled from game logic

## Run

```bash
cd implementation/ai_game_pacman_dryrun
uv sync --project .
uv run --project . python -m ai_pacman.game
```

## CLI

```bash
cd implementation/ai_game_pacman_dryrun
uv run --project . python -m ai_pacman.game
```

## Test

```bash
cd implementation/ai_game_pacman_dryrun
uv run --project . python -m pytest -q
```

**Start here:** [PRD.md](PRD.md), then [docs/RESEARCH.md](docs/RESEARCH.md), then [docs/TODO.md](docs/TODO.md).
