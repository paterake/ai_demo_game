# ai_demo_game — Coding-Agent Workshop Demos

Fun, interactive Pygame demos built as a showcase for coding-agent-driven
development. Two complete, modular, config-driven games:

| Demo | What it is | Package |
|---|---|---|
| **Pac-Man Dry Run** | Modular, config-driven Pac-Man with maze/ghost/AI scaffolding | `implementation/pacman_dryrun/` |
| **Space Invaders Dry Run** | Modular, config-driven Space Invaders with bunker/UFO/attract mode | `implementation/space_invader_dryrun/` |
| **Pac-Man Demo** | Design notes and product narrative for the workshop | `implementation/pacman_demo/` |

## Why this is a standalone repo

These demos were originally built as a quick, fun workshop exercise to
showcase how coding agents iterate on a game loop. They have **no runtime,
governance, or code overlap** with the governed context-engineering and
inference platform. Keeping them isolated avoids cross-repo noise: pytest
collection failures, PRD-drift false positives, and a product-mix that
blurred the boundary between a governed inference platform and a workshop
demo sandbox.

Split rule: anything that depends on `ai-agent-core` or the governed
context-assembly / trust-gate / eval substrate lives in the governed
platform repo; anything that is pure Pygame + workshop narrative lives here.

## Quick start

```bash
# Pac-Man
uv sync --package ai-pacman-dryrun
uv run --package ai-pacman-dryrun ai-pacman

# Space Invaders
uv sync --package ai-space-invader-dryrun
uv run --package ai-space-invader-dryrun ai-space-invader
```

## Repo layout

```
ai_demo_game/
├── implementation/
│   ├── pacman_demo/            # Design docs & product narrative
│   ├── pacman_dryrun/          # Run: ai-pacman
│   │   ├── config/             # Difficulty, maze, visuals, sounds
│   │   ├── src/ai_pacman/
│   │   ├── tests/
│   │   └── docs/
│   └── space_invader_dryrun/   # Run: ai-space-invader
│       ├── config/             # Difficulty, formation, visuals, sounds
│       ├── src/ai_space_invader/
│       ├── tests/
│       └── docs/
├── pyproject.toml              # uv workspace root
└── README.md
```
