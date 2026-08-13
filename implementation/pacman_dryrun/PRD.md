# PRD: ai_game_pacman_dryrun

**Version:** 0.3  
**Status:** 🟢 Ready

---

## Problem

The workshop prompt produces a working game but demonstrates the failure mode: all logic,
rendering, configuration, and state in one file. A data engineer watching the demo learns
"Claude can write code" but not "Claude can produce well-structured code."

This implementation exists to show the alternative: the same outcome, the right structure.

---

## Solution

A playable, arcade-like Pac-Man clone built as a modular, config-driven Python package using Pygame.

The governed intent is twofold:

- Deliver a game that feels recognisably like Pac-Man (maze, ghosts, frightened mode, pacing, bonus fruit).
- Demonstrate agent-friendly engineering: modular boundaries, config purity, and a continuity backlog.

---

## Requirements

### Functional

| # | Requirement |
|---|-------------|
| F1 | Display a grid-based maze with walls, pellets, and power pellets |
| F2 | Pac-Man starts stationary and moves in four directions via keyboard input; stops at walls |
| F3 | Pac-Man animates a chomping mouth while moving |
| F4 | Start screen supports difficulty selection; a READY/GO countdown precedes play |
| F5 | Four named ghosts (Blinky, Pinky, Inky, Clyde) navigate the maze and pursue Pac-Man |
| F6 | Eating pellets increments score; eating power pellets triggers frightened mode for a configurable duration |
| F7 | In frightened mode, Pac-Man can eat ghosts for increasing chain scores (200/400/800/1600) within a single frightened window |
| F8 | When eaten, a ghost becomes “eyes”, routes back to the ghost house/spawn, regenerates briefly, then resumes chasing |
| F9 | Ghost collision in normal mode: lose 1 life, play a death beat, reset positions, then re-enter via countdown |
| F10 | 0 lives remaining: Game Over screen |
| F11 | Clearing all pellets advances to the next level (maze resets, level counter increments, difficulty escalates) |
| F12 | Bonus fruit appears twice per level at fixed dot-eaten thresholds, remains for a short time, and awards a level-dependent score when eaten |
| F13 | HUD displays score, lives, level, and “next fruit” information; pause/resume is supported |

### Non-Functional

| # | Requirement |
|---|-------------|
| N1 | Target 60 FPS (configurable) |
| N2 | All tuneable values in YAML config — no domain constants in source |
| N3 | One class per source file; no file exceeds ~300 lines |
| N4 | Renderer is decoupled from entity logic — no `pygame.draw` calls inside entity classes |
| N5 | Entry point `main()` is a thin wrapper over importable classes |
| N6 | No external image or sound assets — all rendering uses `pygame.draw` primitives and audio is synth-generated |

---

## Scope Boundaries

In scope:

- Classic-feeling maze with tunnel wrap-around and a ghost house concept.
- Frightened mode with visible feedback and clear eat/regenerate loop for ghosts.
- Multi-level loop with escalating difficulty (speed scaling).
- Bonus fruit schedule and a simple “what’s next” indicator.

Out of scope (by design):

- Perfect arcade timings, pattern-accurate ghost personalities, and full scatter/chase schedules.
- External sprite sheets, licensed sound, and pixel-perfect art fidelity.
- Persistent high-score tables (file or network).

---

## Architecture Constraints

These apply unconditionally (from PCO governance rules):

- **Config purity:** window size, FPS, lives count, pellet score, frightened duration,
  all colours, maze grid — in YAML. Not in source.
- **Modular entry points:** classes are independently importable. No procedural top-to-bottom scripts.
- **One responsibility per file:** entity logic, rendering, game state, and UI are separate files.
- **No god file:** the single-file approach from the original brief is a non-starter.

---

## Configuration Contract

The game’s behaviour is driven by YAML configuration split by concern:

- Game rules + timing + movement tuning
- Difficulty profiles (speed multipliers and frightened duration tuning)
- Visual palette (including fruit palette) and sizing
- Maze layout + legend (including spawn locations, tunnels, and ghost house metadata)
- Sound event mapping (synth specs; no external assets)

## Acceptance Criteria

- [x] Game is playable end-to-end: start → play → game over
- [x] Clearing all pellets advances to the next level (level counter increments, maze resets)
- [x] Bonus fruit appears at two dot-eaten thresholds and expires if not collected
- [x] Ghosts chase Pac-Man in normal mode and become edible in frightened mode, with eyes returning to regenerate
- [x] Difficulty selection changes numeric tuning without code changes
- [x] Changing colours/sizes/timing in YAML changes the game without touching source
- [x] Modular boundaries are preserved (renderer-only draw; audio-only mixer)
