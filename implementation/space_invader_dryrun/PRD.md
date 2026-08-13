# PRD: ai_game_space_invader_dryrun

**Version:** 0.4  
**Status:** 🟢 Ready

---

## Problem

The workshop-style arcade prompt can easily produce a single-file Space Invaders clone,
but that teaches the wrong lesson: that AI-generated code only needs to work, not to be
structured, configurable, and maintainable.

This module exists to show the governed alternative: the same recognisable outcome, built
with clean boundaries, config purity, testable game logic, and a continuity backlog that
another assistant can resume without prior conversation.

---

## Analogy

This game should feel like holding a defensive line against a marching phalanx. The player
is not free-roaming through space; they are managing a tightening corridor of risk where
every missed shot leaves the wall marching closer. The classic tension comes from rhythm:
one cannon, one shot, four bunkers, a fleet that accelerates as it thins.

---

## Solution

A playable, arcade-like Space Invaders clone built as a modular, config-driven Python
package using Pygame.

The governed intent is twofold:

- Deliver a game that feels recognisably like classic Space Invaders: horizontal cannon,
  one-shot discipline, descending fleet, destructible shields, return fire, UFO fly-by,
  lives, scoring, and escalating waves.
- Demonstrate agent-friendly engineering: modular boundaries, YAML-driven tuning, thin
  entry point, and backlog continuity for future extension work.

---

## Requirements

### Functional

| # | Requirement |
|---|-------------|
| F1 | Display a fixed-screen playfield with a player cannon, a five-row invader fleet, four destructible bunkers, and a top-lane UFO |
| F2 | The player cannon moves horizontally only and cannot leave the playfield |
| F3 | The player fires straight upward; only one player shot may exist on screen at a time |
| F4 | The alien fleet moves side-to-side, reverses on an edge hit, and steps downward after each edge reversal |
| F5 | The fleet movement interval accelerates as fewer invaders remain |
| F6 | Invaders fire back from surviving columns; enemy shots damage bunkers and the player |
| F7 | Bottom, middle, and top invader rows award distinct scores (10 / 20 / 30) |
| F8 | A UFO periodically crosses the top of the screen and awards score from a deterministic cycle when shot |
| F9 | The player starts with three lives; an extra life is awarded at a configurable score threshold |
| F10 | Losing a life resets the cannon and clears projectiles, but keeps the remaining wave intact |
| F11 | Clearing a wave advances to the next level and increases pressure through configurable timing multipliers |
| F12 | Game over occurs when lives reach zero or the fleet crosses the invasion line near the player |
| F13 | Start screen supports difficulty selection; countdown, pause/resume, wave-clear, and game-over states are explicit |
| F14 | HUD shows score, lives, level, and difficulty; controls remain keyboard-only |
| F15 | The game persists the top local high scores (name, score, difficulty, level reached, date) to a JSON file configured in YAML and shows the table on the start and end screens |
| F16 | The start screen can enter an optional, deterministic attract-mode demo after a configurable idle timeout; any key exits back to a fresh start screen without affecting the next playable run |

### Non-Functional

| # | Requirement |
|---|-------------|
| N1 | Target 60 FPS (configurable) |
| N2 | All tuneable values live in YAML config: timings, fleet geometry, bunker pattern, UFO cycle, colours, and sound event mapping |
| N3 | One responsibility per file; no gameplay object contains rendering code |
| N4 | Only the renderer may call `pygame.draw`; only the audio module may call `pygame.mixer` |
| N5 | The entry point `main()` is a thin orchestration wrapper over importable classes and helpers |
| N6 | No external sprite or audio assets are required; visuals use primitive drawing and audio is synth-generated |

---

## Scope Boundaries

In scope:

- Classic-feeling one-screen combat with a marching formation and bunker erosion.
- Deterministic UFO score cycling and extra-life threshold.
- Difficulty selection and multi-wave escalation.
- Local synth audio and clear state transitions.
- Local high score persistence backed by a config-driven JSON file.
- Optional attract-mode demo loop with deterministic control and clean reset semantics.

Out of scope (by design):

- Pixel-perfect arcade emulation, exact shot tables, or instruction-level fidelity.
- External artwork, cabinet shaders, CRT simulation, or licensed sounds.
- Alternating two-player support.

---

## Architecture Constraints

These apply unconditionally:

- **Config purity:** gameplay constants, movement intervals, colours, bunker patterns,
  UFO score tables, and difficulty multipliers live in YAML. Not in source.
- **Modular boundaries:** player, formation, bunker, projectile, UFO, state, renderer,
  UI, and audio are separate concerns.
- **Deterministic first:** fleet marching, bunker erosion, projectile motion, extra-life
  threshold, and UFO score cycle are deterministic systems. No probabilistic logic is used.
- **No god file:** a single-file arcade script is explicitly rejected.

---

## Configuration Contract

The game behaviour is driven by YAML configuration split by concern:

- `config/game.yaml` - window, timings, rules, projectile speeds, UFO schedule, UI bounds, progression
- `config/difficulty.yaml` - named difficulty profiles and gameplay multipliers
- `config/formation.yaml` - alien fleet geometry, step sizes, row scoring, bunker geometry
- `config/visuals.yaml` - palette and star-field styling
- `config/sounds.yaml` - synth sound event mapping and enable/disable toggle
- `config/game.yaml` `high_scores.*` - leaderboard file path, row limit, and stored player name

---

## Pillar Compliance

- **AI first:** the module exists as an AI implementation demo, but gameplay itself is deterministic rather than LLM-driven.
- **Config over code:** all domain-facing tuning lives in YAML; source code contains only reusable mechanics.
- **Deterministic first, AI last:** all gameplay rules are deterministic; there is no reason to introduce AI into the runtime.
- **LLMOps discipline:** not applicable at runtime because the module does not call an LLM; the governance value is in the documented build process.
- **Data engineering convergence:** game state transitions are explicit, testable, and bounded; configs and docs form the audit trail.

---

## Evidence Capture

**Capability intent:** demonstrate that the Pac-Man dry-run pattern can be reapplied to a second arcade game without falling back to a god-file implementation.

**What makes it credible:**
- Uses external research to distinguish classic behaviour from arbitrary clone behaviour.
- Preserves the same continuity-backlog pattern as `ai_game_pacman_dryrun`.
- Implements modular, testable gameplay logic instead of an opaque event-loop blob.

**Evidence checklist (from real runs):**
- [x] Research summary with decision-relevant mechanics and source URLs
- [x] Playable module with documented run command and focused automated tests
- [x] Config-driven difficulty, fleet, bunker, UFO, and audio behaviour
- [ ] Manual gameplay capture or publication-ready screenshots

---

## Acceptance Criteria

- [x] Game is playable end-to-end: start -> wave loop -> game over / victory
- [x] Player moves horizontally only and fires one shot at a time
- [x] Fleet reverses at screen edges, descends, and accelerates as invaders are destroyed
- [x] Bunkers absorb and erode under player and enemy fire
- [x] UFO fly-by and score cycle are implemented without hardcoded logic in the main loop
- [x] Difficulty selection changes timings without code edits
- [x] Rendering and audio boundaries remain separate from gameplay objects
- [x] Qualifying end-of-run scores persist locally and survive restart
- [x] Idle start-screen sessions can enter and exit attract mode without polluting the next playable run
