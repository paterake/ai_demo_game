# PRD: ai_game_pacman_demo

**Version:** 0.1 — draft  
**Status:** 🟡 Draft — [TBD] items must be resolved before implementation begins (see Item 1 in docs/TODO.md)

---

## Source Brief

The original brief is the Pac-Man workshop prompt (slide 26). The full text and all
extracted constraints are in **[docs/CORE_MECHANICS.md](docs/CORE_MECHANICS.md)** —
that document is the authoritative source for core gameplay constraints. This PRD
extends and governs those constraints; it does not replace them.

One deliberate departure from the brief: **the single-file approach is rejected**. A
single file of this complexity becomes a god file — it cannot be tested in parts, reviewed
meaningfully, or extended without touching everything. The governed implementation uses a
module-per-concern structure with config-driven tuneable values. All other constraints in
`CORE_MECHANICS.md` are carried forward unchanged.

---

## Problem

The workshop prompt produces a working game but demonstrates the failure mode: all logic,
rendering, configuration, and state in one file. A data engineer watching the demo learns
"Claude can write code" but not "Claude can produce well-structured code."

This implementation exists to show the alternative: the same outcome, the right structure.

---

## Solution

A playable Pac-Man clone built as a modular, config-driven Python package using Pygame.
Each concern lives in its own file. Every tuneable value lives in YAML config. The entry
point is a thin wrapper.

---

## Requirements

### Functional

| # | Requirement |
|---|-------------|
| F1 | Display a grid-based maze with walls, pellets, and power pellets |
| F2 | Pac-Man moves in four directions via arrow keys; stops at walls |
| F3 | Pac-Man animates a chomping mouth as it moves |
| F4 | Four named ghosts (Blinky, Pinky, Inky, Clyde) move through the maze |
| F5 | Ghosts use basic AI: navigate corridors, turn randomly at intersections |
| F6 | Pac-Man eating a pellet increments the score |
| F7 | Eating a power pellet triggers frightened mode on all ghosts for a configurable duration |
| F8 | In frightened mode, Pac-Man can eat ghosts; eaten ghost returns to spawn |
| F9 | Ghost collision in normal mode: lose 1 life, reset Pac-Man and ghost positions |
| F10 | 0 lives remaining: Game Over screen |
| F11 | All pellets eaten: Victory screen |
| F12 | HUD displays current score and remaining lives at all times |

### Non-Functional

| # | Requirement |
|---|-------------|
| N1 | Target 60 FPS (configurable) |
| N2 | All tuneable values in YAML config — no domain constants in source |
| N3 | One class per source file; no file exceeds ~300 lines |
| N4 | Renderer is decoupled from entity logic — no `pygame.draw` calls inside entity classes |
| N5 | Entry point `main()` is a thin wrapper over importable classes |
| N6 | No external image assets — all rendering uses `pygame.draw` primitives |

### [TBD] — must be resolved in Item 1 (pre-implementation gate)

| # | Open question |
|---|---------------|
| T1 | Exact maze layout — wall/path grid encoding format and default maze pattern |
| T2 | Ghost frightened mode movement — random walk, speed reduction, reversal behaviour |
| T3 | Ghost respawn after being eaten — immediate return or timed delay, exact spawn point |
| T4 | Level progression — single looping level or multi-level with escalating difficulty |
| T5 | Final config YAML split and key naming conventions |
| T6 | Module file list and class boundary decisions |

---

## Architecture Constraints

These apply unconditionally (from PCO governance rules):

- **Config purity:** window size, FPS, lives count, pellet score, power pellet duration,
  all colours, maze grid — in YAML. Not in source.
- **Modular entry points:** classes are independently importable. No procedural top-to-bottom scripts.
- **One responsibility per file:** entity logic, rendering, game state, and UI are separate files.
- **No god file:** the single-file approach from the original brief is a non-starter.

---

## Proposed Module Structure

Subject to confirmation in Item 1.

A single package of single-responsibility components:

- **Entry point** — thin main loop wiring the components together
- **Maze** — wall layout, pellet map, collision queries
- **PacMan** — position, direction, animation state, movement
- **Ghost** — position, AI mode, movement
- **Renderer** — all draw calls, decoupled from entity logic
- **Game state** — score, lives, mode, pellet count
- **UI** — HUD, game over / victory overlays

Configuration (YAML, no values in source):

- `game.yaml` — fps, lives, power_pellet_duration_s, window_size, pellet_score
- `visuals.yaml` — colours: walls, background, pellets, power pellets, pacman, ghosts (per name)
- `maze.yaml` — grid: list of row strings encoding walls (#) and open cells ( )

---

## Acceptance Criteria

- [ ] Game is playable end-to-end: start → play → game over or victory
- [ ] Changing a colour in `visuals.yaml` changes the rendered colour without touching source
- [ ] Changing `fps`, `lives`, or `power_pellet_duration_s` in `game.yaml` changes behaviour
- [ ] No source file exceeds ~300 lines
- [ ] the Maze, PacMan, Ghost, and Renderer components are importable independently
- [ ] All [TBD] items resolved before any source file is written
