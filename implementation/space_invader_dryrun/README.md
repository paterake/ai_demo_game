# ai_game_space_invader_dryrun

Showcase of the Claude Code workflow: brief -> PRD -> backlog continuity -> implementation.

**Source brief:** create a classic Space Invaders arcade demo using the same governed approach as `ai_game_pacman_dryrun`.

**What this demonstrates:**
- Turning a naive arcade prompt into a governed PRD and research-backed backlog
- Using a backlog continuity anchor doc to preserve constraints across future sessions
- Config purity: fleet, bunker, UFO, timing, colours, and audio wiring live in YAML, not source
- Modular structure: fleet logic, bunker damage, attract mode, persistence, rendering, audio, and UI are decoupled

## Run

```bash
cd implementation/ai_game_space_invader_dryrun
uv sync --project .
uv run --project . python -m ai_space_invader.game
```

## CLI

```bash
cd implementation/ai_game_space_invader_dryrun
uv run --project . python -m ai_space_invader.game
```

## Test

```bash
cd implementation/ai_game_space_invader_dryrun
uv run --project . python -m pytest -q
```

## Docs

| File | Purpose |
|------|---------|
| [PRD.md](PRD.md) | Scope, requirements, and current evidence |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Runtime flow and module boundaries |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | YAML keys and why their defaults exist |
| [docs/RESEARCH.md](docs/RESEARCH.md) | Mechanics research behind the clone feel |
