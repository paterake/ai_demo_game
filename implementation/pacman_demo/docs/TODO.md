> **Anchor document** — pacman_demo: PRD drafted (v0.1), not yet strengthened. Extension backlog seeded (Items 10–16).
> Next: **Item 1** — research + pre-implementation gate. Parts A and B both required before any code.
> Read `PRD.md` before starting Item 1.

## Resume (start here)

- From `implementation/pacman_demo/docs/TODO.md`: Continue **Item 1** — Part A (research, refine extension items) then Part B (resolve all [TBD] items in PRD.md)

## Session start prompt

```
load the use-context skill, and from: implementation/pacman_demo/docs/TODO.md, continue
```

## Workshop prompt (bounded research → PRD → start build)

Use this when a breakout team wants the agent to do the research and PRD strengthening quickly, then proceed to scaffolding.

```
Load the use-context skill.

From implementation/pacman_demo/docs/TODO.md, complete Item 1 with these constraints:
- Timebox web research to 10 minutes and at most 5 sources.
- Every behaviour-changing claim must include a source URL; otherwise mark it as a design choice.
- Convert research into explicit decisions in PRD.md (no open questions remain).
- Create docs/RESEARCH.md with a short evidence summary (claims → decisions + URLs).

Then stop after updating the anchor doc to mark Item 1 ✅ and set Item 2 as next.
```

---

## Accumulated Active Constraints

_None yet — grows as items complete. Every completed item must forward its invariants here._

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

---

### ⏳ Item 1 — Pre-implementation gate: research, extend backlog, strengthen PRD

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

**Verification:**
- `PRD.md` has no remaining `[TBD]` markers and status is 🟢 Ready
- Items 10–16 each have a confirmed scope and at least one verification command
- Research evidence summary is recorded in `docs/RESEARCH.md`

---

### ⏳ Item 2 — Scaffold: structure, pyproject.toml, config stubs

Create the directory skeleton and empty config files. No source logic yet.

**Still todo:**
1. Create `pyproject.toml` with `pygame` dependency (uv)
2. Create `config/game.yaml` with all keys from PRD N2 (no hardcoded defaults in source)
3. Create `config/visuals.yaml` with all colour keys (walls, background, pellets, power pellets, pacman, each ghost)
4. Create `config/maze.yaml` with default maze grid (resolved in Item 1)
5. Create empty `src/ai_pacman/__init__.py` and stub files for each module
6. Confirm `uv run python -m ai_pacman.game` is the entry point

**Verification:** `uv run python -m ai_pacman.game` exits cleanly (no game yet, just no import errors).

---

### ⏳ Item 3 — Maze module

Implement `maze.py`: load grid from `config/maze.yaml`, expose wall collision queries, pellet map.

**Verification:** unit test — given a grid, `maze.is_wall(x, y)` and `maze.has_pellet(x, y)` return correct values without pygame.

---

### ⏳ Item 4 — Pac-Man entity

Implement `pacman.py`: position, queued direction, movement per tick, wall collision via Maze,
chomping animation state.

**Verification:** unit test — PacMan moves in open cells, stops at walls, animation state cycles on movement.

---

### ⏳ Item 5 — Ghost entity + AI

Implement `ghost.py`: position, AI mode (normal / frightened / eaten), movement with random
turns at intersections, frightened mode timer sourced from `config/game.yaml`.

**Verification:** unit test — ghost turns at intersections, frightened mode activates and expires on timer.

---

### ⏳ Item 6 — Renderer

Implement `renderer.py`: all `pygame.draw` calls, reads colours exclusively from `config/visuals.yaml`.
No entity class imports pygame directly.

**Verification:** changing a colour in `visuals.yaml` changes the rendered output without touching source.

---

### ⏳ Item 7 — Game state + loop

Implement `state.py` (GameState dataclass) and `game.py` (main loop: event handling, update,
collision detection, render, FPS cap from config).

**Verification:** game runs, Pac-Man moves, ghosts move, pellets disappear on contact.

---

### ⏳ Item 8 — UI

Implement `ui.py`: HUD (score + lives), Game Over overlay, Victory overlay.

**Verification:** 0 lives shows Game Over; all pellets eaten shows Victory; score increments on screen.

---

### ⏳ Item 9 — Integration pass

End-to-end playable run. Verify all acceptance criteria in `PRD.md` are met.
Update PRD.md acceptance criteria checkboxes.

**Verification:** all acceptance criteria checked; no source file over ~300 lines; no hardcoded colours or timing values in source.

---

## Extension Items

_Seeded from the brief and refined by research in Item 1. Scope and verification for each
item must be confirmed before that item is picked up. Research may add, remove, or reshape
these items — treat them as provisional until Item 1 is complete._

---

### ⏳ Item 10 — Sound system foundation

Introduce `audio.py` and `config/sounds.yaml`. The YAML maps named sound events
(`pellet_eat`, `power_pellet`, `ghost_eat`, `pacman_death`, `game_over`, `victory`,
`theme_music`) to file paths. `audio.py` loads and plays sounds by event name.
No hardcoded paths or pygame mixer calls outside `audio.py`.

Research should confirm: file format (WAV vs OGG for pygame compatibility), volume
control approach, looping vs one-shot distinction in config.

**Verification:** changing a sound file path in `sounds.yaml` changes what plays without touching source.

---

### ⏳ Item 11 — Theme music

Implement looping background music that plays during gameplay and stops on Game Over
or Victory. Music track is config-driven (`sounds.yaml: theme_music`). Start/stop
wired through `audio.py`, called from game loop state transitions.

Research should confirm: classic Pac-Man intro jingle is well-documented and freely
available in compatible formats; identify a suitable source or generate a MIDI-to-WAV
equivalent. Document source URL in `docs/RESEARCH.md`.

**Verification:** theme plays on game start, stops on game over/victory, resuming a new game restarts it.

---

### ⏳ Item 12 — Sound effects

Implement event-triggered sound effects for: pellet eat (short blip), power pellet
(distinct blip), ghost eat (ascending tone), Pac-Man death (descending sequence),
game over, victory fanfare. All mapped in `config/sounds.yaml`.

Research should confirm: original arcade sound timings and whether open-licensed
recreations exist; document sources in `docs/RESEARCH.md`.

**Verification:** each game event triggers its configured sound; swapping a file in `sounds.yaml` changes the sound.

---

### ⏳ Item 13 — Start screen

Implement a start screen shown before the first game and after Game Over / Victory.
Displays: game title, high score, controls (arrow keys = move), prompt to start.
Start screen is a state in `state.py` (`GameMode.START`), rendered by `ui.py`.
No separate file needed — extend existing UI module.

Research should confirm: what a standard Pac-Man attract/start screen shows; whether
difficulty selection appears on the start screen or a separate screen.

**Verification:** game opens to start screen; pressing start key transitions to gameplay; high score is shown.

---

### ⏳ Item 14 — Multiple difficulty levels

Add `config/difficulty.yaml` mapping named levels (`easy`, `normal`, `hard`) to
parameters: ghost speed multiplier, frightened duration (seconds), ghost count active,
pellet score multiplier. Player selects difficulty on the start screen.
`GameState` holds the active difficulty; all modules read parameters from it, not from
raw config values.

Research should confirm: standard difficulty parameters in well-regarded Pac-Man clones;
what makes ghost AI harder (speed vs count vs smarter pathfinding).

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

### ⏳ Item 16 — Level progression

After all pellets are eaten, advance to the next level rather than showing Victory.
Level number increments; maze resets with pellets; ghost speed and count scale per
level using parameters from `config/difficulty.yaml`. A configurable final level
triggers the Victory screen.

Research should confirm: classic Pac-Man level progression curve (speed increases,
frightened duration decreases); appropriate final level for a demo clone.

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
