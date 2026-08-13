# Configuration

This module is configuration-driven. YAML controls gameplay tuning, visuals, audio wiring,
and the persistent high score table. JSON is reserved for the runtime leaderboard file.

## `config/game.yaml`

| Key | Meaning | Why this default exists |
|-----|---------|-------------------------|
| `window.width_px`, `window.height_px` | Screen size in pixels | `800 x 720` leaves space for a readable HUD, full fleet width, four bunkers, and end-screen overlays without making the dry run feel cramped |
| `timing.fps` | Target frame rate | `60` matches the expected feel for a simple arcade loop and keeps movement smooth |
| `timing.start_countdown_s` | Delay before play starts | `2.0` gives the player a clear READY/GO beat after leaving the start screen |
| `timing.respawn_countdown_s` | Delay after losing a life | `1.6` is long enough to reset orientation without stalling the game |
| `timing.wave_clear_delay_s` | Delay before the next wave | `1.8` gives a short reward pause before rebuilding the fleet |
| `rules.starting_lives` | Lives at the start of a run | `3` matches the classic expectation and keeps the loop forgiving enough for a workshop demo |
| `rules.extra_life_score` | Score threshold for the bonus life | `1500` makes the reward achievable without trivialising life pressure |
| `rules.max_level` | Last playable level before victory | `6` gives escalation without turning the dry run into an endless session |
| `player.width_px`, `player.height_px` | Cannon dimensions | Sized to stay readable against the fleet and bunker scale |
| `player.speed_px_per_s` | Base horizontal speed | `320` keeps the cannon responsive while still punishable |
| `player.shot_cooldown_s` | Minimum delay between player shots | `0.35` preserves one-shot discipline without making the game feel sluggish |
| `projectiles.player_speed_px_per_s` | Upward player shot speed | `-520` keeps shots fast enough for the fleet rhythm |
| `projectiles.enemy_speed_px_per_s` | Downward enemy shot speed | `260` gives the player time to react while allowing pressure to build |
| `projectiles.width_px`, `projectiles.height_px` | Shared projectile dimensions | Narrow, readable bullets that work with primitive rendering |
| `ufo.enabled` | Turns the UFO system on or off | `true` keeps classic scoring variety enabled by default |
| `ufo.spawn_interval_s`, `ufo.respawn_delay_s` | UFO timing | Spaced out so the UFO feels like an event, not constant clutter |
| `ufo.speed_px_per_s`, `ufo.width_px`, `ufo.height_px`, `ufo.y_px` | UFO movement and size | Tuned to stay visible above the fleet without colliding with the HUD |
| `ufo.score_cycle` | Deterministic UFO score sequence | Lives in config so the classic scoring pattern is visible and editable without code changes |
| `progression.formation_interval_decay_per_level` | Per-level fleet speed-up | `0.08` creates noticeable escalation between waves |
| `progression.min_formation_interval_multiplier` | Lower bound on fleet interval scaling | Prevents later levels becoming unreadably fast |
| `progression.enemy_fire_interval_decay_per_level` | Per-level enemy fire acceleration | Tightens pressure each level without changing firing code |
| `attract_mode.enabled` | Turns the idle demo loop on or off | `true` makes the start screen feel cabinet-like by default while still allowing operators to disable the feature without code changes |
| `attract_mode.idle_timeout_s` | Idle time before the start screen enters the demo loop | `8.0` is long enough for a player to read the screen and choose difficulty before the demo takes over |
| `attract_mode.restart_delay_s` | Delay before a finished demo restarts itself | `2.2` gives the attract loop a brief GAME OVER / VICTORY beat instead of snapping back instantly |
| `attract_mode.fire_tolerance_px` | Horizontal aiming tolerance for the deterministic demo cannon | `10` keeps the autoplayer readable and imperfect without introducing randomness |
| `high_scores.file` | Relative or absolute JSON file path for persisted scores | Defaults to `.ignore/high_scores.json` so runtime data stays local and out of source control |
| `high_scores.max_entries` | Number of leaderboard rows kept | `5` keeps the table readable on both the start and end screens |
| `high_scores.default_name` | Stored player name for new qualifying scores | `PLAYER` gives every saved row a valid label without adding a text-entry flow to this item |
| `ui.hud_height_px` | Reserved HUD band height | Leaves room for score, lives, level, and difficulty |
| `ui.arena_top_px` | Top edge of the gameplay arena | Keeps the fleet below the HUD text |
| `ui.arena_bottom_margin_px` | Bottom buffer above the player baseline | Prevents the cannon hugging the window edge |
| `ui.invade_line_margin_px` | Distance from the bottom for the invasion loss line | Makes the lose condition visible but still threatening |
| `ui.font_size_px` | Base UI font size | `22` stays legible while fitting the leaderboard and overlays |

## `config/difficulty.yaml`

| Key | Meaning | Why this default exists |
|-----|---------|-------------------------|
| `profiles.<name>.formation_interval_multiplier` | Multiplies fleet step timing | `easy` slows the march, `hard` quickens it, and `normal` stays neutral |
| `profiles.<name>.player_speed_multiplier` | Multiplies player movement speed | Slightly buffs the player on `easy` and trims responsiveness on `hard` |
| `profiles.<name>.enemy_fire_interval_s` | Base delay between enemy shots | Difficulty primarily changes pressure through how often the fleet fires |
| `profiles.<name>.enemy_shot_speed_multiplier` | Multiplies enemy shot velocity | `hard` shots fall faster to force cleaner bunker use |
| `profiles.<name>.max_enemy_projectiles` | Caps concurrent enemy bullets | Keeps `easy` less crowded while allowing `normal` and `hard` to sustain pressure |

## `config/formation.yaml`

| Key | Meaning | Why this default exists |
|-----|---------|-------------------------|
| `fleet.rows`, `fleet.cols` | Formation grid dimensions | `5 x 11` matches the recognisable classic fleet shape |
| `fleet.start_x_px`, `fleet.start_y_px` | Initial fleet origin | Centres the formation and keeps it below the HUD |
| `fleet.h_spacing_px`, `fleet.v_spacing_px` | Gaps between invaders | Preserves readability for primitive-drawn silhouettes |
| `fleet.alien_width_px`, `fleet.alien_height_px` | Invader size | Large enough to read row identity without sprite assets |
| `fleet.step_px`, `fleet.step_down_px` | Horizontal march step and descent depth | Produces the classic side-step then drop rhythm |
| `fleet.base_interval_s`, `fleet.min_interval_s` | Baseline and floor for fleet timing | Allows acceleration as aliens are removed while preventing impossible speeds |
| `fleet.row_types` | Row kind and score values | Keeps score bands data-driven rather than hidden in the event loop |
| `bunkers.top_y_px` | Bunker vertical placement | Leaves a defendable gap between shields and player |
| `bunkers.cell_size_px` | Grid cell size for bunker erosion | Balances visible damage against a compact config pattern |
| `bunkers.origins_x_px` | Horizontal bunker positions | Spreads four shields evenly across the arena |
| `bunkers.pattern` | ASCII bunker mask | Keeps shield geometry editable without touching code |

## `config/visuals.yaml`

| Key | Meaning | Why this default exists |
|-----|---------|-------------------------|
| `colours.*` | Hex colours for all rendered elements | Centralises palette tuning while keeping gameplay code colour-free |
| `stars.seed` | Random seed for the star field | `7` makes the background deterministic between runs |
| `stars.count` | Number of background stars | `64` gives atmosphere without distracting from projectiles |

## `config/sounds.yaml`

| Key | Meaning | Why this default exists |
|-----|---------|-------------------------|
| `enabled` | Enables or disables audio globally | `true` keeps the demo lively while still allowing silent mode |
| `events.<name>` | Maps gameplay events to synth sound names | Keeps sound selection in YAML so swapping event audio is a config change, not a code edit |
