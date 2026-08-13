# Architecture

`ai_game_space_invader_dryrun` keeps the classic arcade loop modular: deterministic gameplay
objects model the world, `renderer.py` draws it, `audio.py` emits sound, `attract.py`
provides the demo steering helper, and the thin entry point in `game.py` orchestrates
state transitions.

## Flow

```text
config/*.yaml
    |
    v
config_loader.py -> game.py -> build_world()
                        |            |
                        |            +-> player.py
                        |            +-> formation.py + alien.py
                        |            +-> bunker.py
                        |            +-> ufo.py
                        |
                        +-> state.py
                        +-> attract.py
                        +-> high_scores.py -> local JSON file
                        +-> renderer.py
                        +-> ui.py
                        +-> audio.py
```

## Deterministic Boundaries

- Gameplay remains deterministic: player movement, alien marching, bunker erosion,
  projectile motion, extra life awarding, and UFO score cycling are fixed rules.
- Rendering stays in `renderer.py`; gameplay objects do not import `pygame`.
- Audio stays in `audio.py`; mixer access is isolated there.
- High score persistence is a runtime JSON artefact controlled by `config/game.yaml`;
  the storage path and table size are configuration, not hardcoded policy in source.
- Attract mode reuses the gameplay systems through a separate demo session, so attract
  runs never reuse the player's live RNG or write leaderboard rows.

## Components

| File | Responsibility |
|------|----------------|
| `game.py` | Main loop, state transitions, input handling, and orchestration |
| `attract.py` | Deterministic idle-time trigger and demo steering decisions |
| `config_loader.py` | Loads YAML config files from the module root |
| `state.py` | Session state and the world container dataclasses |
| `world.py` | Builds a new wave from config and resets the player after a hit |
| `player.py` | Horizontal movement, cooldown, and shot spawn point |
| `projectile.py` | Shared projectile motion and overlap helpers |
| `formation.py` | Fleet marching, edge reversal, descent, acceleration, and shooter choice |
| `alien.py` | Alien row data and score values |
| `bunker.py` | Grid-based bunker erosion |
| `ufo.py` | Timed fly-by behaviour and deterministic score cycle |
| `renderer.py` | All primitive drawing for the arena, entities, and HUD backdrop |
| `ui.py` | HUD text, start/countdown/end overlays, and leaderboard presentation |
| `audio.py` | Config-driven synth event playback and theme control |
| `high_scores.py` | Load, rank, trim, and save the top N score table as JSON |

## Design Decisions

- JSON is used for persisted scores because it is a runtime data artefact, not authored
  configuration. YAML remains the source of gameplay tuning.
- The leaderboard saves exactly once per ended run (`game_over` or `victory`) so the
  event loop does not rewrite the file every frame.
- The start screen and end overlay read the same in-memory leaderboard list, which keeps
  the presentation consistent before and after a run.
- Attract mode starts from a fresh world/session with its own deterministic RNG seed, and
  exiting the demo rebuilds the normal start-screen session before the player can begin.
