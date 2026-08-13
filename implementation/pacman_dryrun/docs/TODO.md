> **Anchor document** — pacman_dryrun: core + immersion features implemented and verified (Items 0–14 ✅, Item 16 ✅). Extension backlog remains (Items 15, 17 ⏳).
> Next: **Item 15** — high score persistence.
> Before touching code: read **Accumulated Active Constraints**.

## Resume (start here)

- From `implementation/pacman_dryrun/docs/TODO.md`: Continue **Item 15** — high score persistence

## Session start prompt

```
load the use-context skill, and from: implementation/pacman_dryrun/docs/TODO.md, continue
```

---

## Accumulated Active Constraints

- Maze encoding is authoritative in [maze.yaml](../config/maze.yaml): do not hardcode legend tokens in source.
- Only [renderer.py](../src/ai_pacman/renderer.py) may call `pygame.draw`; entity modules must not import pygame.
- Only [audio.py](../src/ai_pacman/audio.py) may call `pygame.mixer`.
- Gameplay tuning values (FPS, lives, speeds, scores, colours) live in YAML under `config/` — no domain constants in source.
- Module verification runs inside the module directory: `uv run --project . python -m pytest -q`.

---

## Items

### ✅ Item 0 — Create draft PRD from brief

**Brief:** slide 26 Pac-Man workshop prompt.

**Done:**
- `PRD.md` created — requirements translated from prompt, single-file approach explicitly rejected,
  architecture constraints applied, [TBD] items named, proposed module structure documented.
- `docs/TODO.md` (this file) created as the backlog anchor doc.
- `README.md` created.

**Constraints established:**
- Single-file god-script approach is rejected. Module-per-concern is non-negotiable.
- All tuneable values (colours, timing, lives, window size, maze layout) belong in YAML config, not source.

Checkpoint (completed)
- Done: PRD + anchor doc created and copied to `pacman_dryrun`
- Verification: N/A (docs-only)
- Gotchas: none

---

### ✅ Item 1 — Pre-implementation gate: research, extend backlog, strengthen PRD

Two parts: (A) internet research to discover what a well-featured Pac-Man clone looks like
beyond the brief, then use findings to populate the extension backlog items (Items 10–16);
(B) resolve all [TBD] items in `PRD.md` so implementation can begin.

Neither part is optional — extension items must be framed before core implementation
starts so the architecture accommodates them (e.g. the sound system shapes how `game.py`
is wired; difficulty shapes what goes in config).

**Still todo — Part A: research and extension backlog**

1. Use web search to research Pac-Man game design: original arcade mechanics, common clone
   implementations, sound design, difficulty progression, high score systems, start screens.
   Authoritative sources preferred (original game documentation, well-regarded open-source
   clones, game design references). Record findings as a short evidence summary with source
   URLs — do not paste raw content, distil into decision-relevant claims.
2. From research findings, review and refine Items 10–16 below:
   - Confirm or adjust scope, behaviour, and config keys for each item
   - Add any extension items the research surfaces that are not already listed
   - Remove any seeded item that research shows is out of scope or unworkable
3. Add `config/sounds.yaml` to the proposed module structure in `PRD.md` (maps sound event
   names to file paths — all sound wiring is config, no hardcoded paths in source)
4. Add `config/difficulty.yaml` to the proposed module structure (maps difficulty level names
   to numeric parameters — speed multipliers, frightened duration, ghost count, etc.)
5. Update PRD.md Requirements with any additions from research (new functional requirements
   for sound, start screen, difficulty, high scores)

**Still todo — Part B: resolve [TBD] items**

6. Resolve T1 — define the maze grid encoding format and commit a default maze pattern to `config/maze.yaml`
7. Resolve T2 — specify ghost frightened mode movement (random walk at reduced speed; confirm from research)
8. Resolve T3 — specify ghost respawn: immediate return to centre spawn cell on being eaten
9. Resolve T4 — revise scope: single looping level for core (Items 2–9); difficulty progression
   and multi-level are extension scope (Items 14–15)
10. Resolve T5 — finalise config YAML key names; confirm five-file split (game / visuals / maze / sounds / difficulty)
11. Resolve T6 — confirm module file list including sound and UI additions; write list into Accumulated Active Constraints
12. Update PRD.md status from 🟡 Draft to 🟢 Ready
13. Update this anchor doc: move Item 1 to ✅, set Item 2 as next, update Resume line

Checkpoint (completed)
- Done: [PRD.md](../PRD.md) strengthened (TBDs resolved; status 🟢 Ready); [RESEARCH.md](RESEARCH.md) added; default maze committed to [maze.yaml](../config/maze.yaml)
- Constraints / ground rules (active for all remaining items):
  - Maze legend + grid live in YAML and are the authoritative encoding contract.
  - Core scope is single-level; multi-level progression remains extension scope.
- Verification: `grep -n "\[TBD\]" PRD.md` (must return no matches)
- Gotchas: anchor doc originally referenced `pacman_demo` paths; updated to `pacman_dryrun`

---

### ✅ Item 2 — Scaffold: structure, pyproject.toml, config stubs

Create the directory skeleton and empty config files. No source logic yet.

**Still todo:**
1. Create `pyproject.toml` with `pygame` dependency (uv)
2. Create `config/game.yaml` with all keys from PRD N2 (no hardcoded defaults in source)
3. Create `config/visuals.yaml` with all colour keys (walls, background, pellets, power pellets, pacman, each ghost)
4. Create `config/maze.yaml` with default maze grid (resolved in Item 1)
5. Create empty `src/ai_pacman/__init__.py` and stub files for each module
6. Confirm `uv run python -m ai_pacman.game` is the entry point

Checkpoint (completed)
- Done: module scaffold created: [pyproject.toml](../pyproject.toml), `src/ai_pacman/`, `config/` stubs, `tests/`
- Verification: `uv sync --project .` (creates `.venv` and installs deps)
- Gotchas: running `pytest` from repo root collects other modules; run from this module directory

---

### ✅ Item 3 — Maze module

Implement `maze.py`: load grid from `config/maze.yaml`, expose wall collision queries, pellet map.

Checkpoint (completed)
- Done: [maze.py](../src/ai_pacman/maze.py) implemented + tests
- Constraints / ground rules (active for all remaining items):
  - Maze is immutable; `eat_pellet()` returns a new Maze to keep state updates explicit.
- Verification: `uv run --project . python -m pytest -q tests/test_maze.py`
- Gotchas: none

---

### ✅ Item 4 — Pac-Man entity

Implement `pacman.py`: position, queued direction, movement per tick, wall collision via Maze,
chomping animation state.

Checkpoint (completed)
- Done: [pacman.py](../src/ai_pacman/pacman.py) implemented + tests
- Constraints / ground rules (active for all remaining items):
  - Pac-Man movement is grid-step (tile-based) with an accumulator; dt spikes can create multi-tile steps.
- Verification: `uv run --project . python -m pytest -q tests/test_pacman.py`
- Gotchas: unit tests should use small `dt_s` values to avoid multi-tile movement in a single update

---

### ✅ Item 5 — Ghost entity + AI

Implement `ghost.py`: position, AI mode (normal / frightened / eaten), movement with random
turns at intersections, frightened mode timer sourced from `config/game.yaml`.

Checkpoint (completed)
- Done: [ghost.py](../src/ai_pacman/ghost.py) implemented + tests
- Constraints / ground rules (active for all remaining items):
  - Frightened start reverses ghost direction; frightened movement is random-walk at intersections.
- Verification: `uv run --project . python -m pytest -q tests/test_ghost.py`
- Gotchas: none

---

### ✅ Item 6 — Renderer

Implement `renderer.py`: all `pygame.draw` calls, reads colours exclusively from `config/visuals.yaml`.
No entity class imports pygame directly.

Checkpoint (completed)
- Done: [renderer.py](../src/ai_pacman/renderer.py) implemented (all `pygame.draw` calls here)
- Constraints / ground rules (active for all remaining items):
  - Renderer reads only values passed from config; entities remain pygame-free.
- Verification: manual (run game; change `config/visuals.yaml` colours and observe)
- Gotchas: none

---

### ✅ Item 7 — Game state + loop

Implement `state.py` (GameState dataclass) and `game.py` (main loop: event handling, update,
collision detection, render, FPS cap from config).

Checkpoint (completed)
- Done: [state.py](../src/ai_pacman/state.py) + [game.py](../src/ai_pacman/game.py) implemented
- Verification: `uv run --project . python -c \"from ai_pacman.game import main; print('import ok')\"`
- Gotchas: interactive run requires quitting the Pygame window (Esc) to return control

---

### ✅ Item 8 — UI

Implement `ui.py`: HUD (score + lives), Game Over overlay, Victory overlay.

Checkpoint (completed)
- Done: [ui.py](../src/ai_pacman/ui.py) implemented (HUD + overlays)
- Verification: manual (play to game-over/victory)
- Gotchas: none

---

### ✅ Item 9 — Integration pass

End-to-end playable run. Verify all acceptance criteria in `PRD.md` are met.
Update PRD.md acceptance criteria checkboxes.

Checkpoint (completed)
- Done: core game is playable; tests added; acceptance criteria updated in PRD
- Constraints / ground rules (active for all remaining items):
  - Keep the “no pygame in entities” boundary intact when adding sound/difficulty/high-score features.
- Verification: `uv run --project . python -m pytest -q`
- Gotchas: none

---

## Extension Items

_Seeded from the brief and refined by research in Item 1. Scope and verification for each
item must be confirmed before that item is picked up. Research may add, remove, or reshape
these items — treat them as provisional until Item 1 is complete._

---

### ✅ Item 10 — Sound system foundation

Introduce the audio subsystem and sound event mapping. The YAML maps named sound events
to specs, and all `pygame.mixer` calls are contained inside the audio module.

Checkpoint (completed)
- Done: audio subsystem added; game loop starts/stops music and plays event SFX; no mixer calls outside audio module.

**Verification:** changing a sound file path in `sounds.yaml` changes what plays without touching source.

---

### ✅ Item 11 — Theme music

Implement looping background music that plays during gameplay and stops on game over.
Music is config-driven and started/stopped from game state transitions.

Checkpoint (completed)
- Done: synth-generated theme plays during gameplay and is stopped on game-over.

**Verification:** theme plays on game start, stops on game over/victory, resuming a new game restarts it.

---

### ✅ Item 12 — Sound effects

Implement event-triggered sound effects for pellets, power pellets, ghost eat, death, game over, and level clear.
All mapped in `config/sounds.yaml`.

Checkpoint (completed)
- Done: synth-generated SFX implemented and wired to gameplay events.

**Verification:** each game event triggers its configured sound; swapping a file in `sounds.yaml` changes the sound.

---

### ✅ Item 13 — Start screen

Implement a start screen shown before the first game. It includes game title, controls, and difficulty selection.

Checkpoint (completed)
- Done: start screen implemented with difficulty selection and a READY/GO countdown before play.

**Verification:** game opens to start screen; pressing start key transitions to gameplay; high score is shown.

---

### ✅ Item 14 — Multiple difficulty levels

Add `config/difficulty.yaml` mapping named levels (`easy`, `normal`, `hard`) to numeric parameters.
Player selects difficulty on the start screen; active difficulty affects speed and frightened duration.

Checkpoint (completed)
- Done: difficulty profiles implemented and applied to gameplay tuning.

**Verification:** switching difficulty in `difficulty.yaml` or on the start screen changes ghost speed and frightened duration in gameplay.

---

### ⏳ Item 15 — High score persistence

Persist the top N scores (name, score, difficulty, date) to a local JSON file. Path
is config-driven (`config/game.yaml: high_score_file`). Load on start, save on game
over if score qualifies. Display on start screen and game over screen.

Research should confirm: standard high score table size (typically 5–10 entries);
whether initials entry (3-char) or full name is more appropriate for this context.

**Verification:** scoring above the current high score updates the persisted file; score survives process restart; high score file path is configurable.

---

### ✅ Item 16 — Level progression

After all pellets are eaten, advance to the next level.
Level number increments; maze resets with pellets; ghost speed scales per level (with difficulty profile multipliers).

Checkpoint (completed)
- Done: level progression implemented (multi-level loop with escalating difficulty).

**Verification:** completing a level resets the maze and increments the level counter; parameters scale correctly; final level triggers Victory.

---

### ⏳ Item 17 — Save and resume game progression

Persist the full game state to disk so a player can quit mid-game and continue from the
same position. Saved state includes: current level, score, lives remaining, pellet map
(which pellets have been eaten), Pac-Man position, ghost positions and modes, active
difficulty, and timestamp. Save file path is config-driven (`config/game.yaml: save_file`).

Save is triggered explicitly (e.g. Escape key → pause menu with Save & Quit option) —
not on every tick. Load is offered on the start screen when a save file exists. A
corrupted or incompatible save file is discarded silently with a logged warning, not a crash.

Research should confirm: which fields constitute the minimal recoverable state; whether
pygame has any native save support or whether JSON serialisation of `GameState` is sufficient.

**Verification:** save mid-level, quit, relaunch — game resumes at the correct level,
score, lives, and pellet state. Deleting the save file returns to a clean start screen.

---

## Gotchas

- **`uv` must be installed before Item 2.** The `pyproject.toml` and `pygame` dependency are created in Item 2 via `uv add pygame`. If `uv` is not installed on the machine, that step stalls. Install with `curl -LsSf https://astral.sh/uv/install.sh | sh` (Mac/Linux) or `winget install astral-sh.uv` (Windows) before the workshop.
- **Claude Code must be installed and authenticated before the workshop.** `npm install -g @anthropic-ai/claude-code` then `claude` to authenticate.
