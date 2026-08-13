# Research Evidence - Space Invaders Mechanics (bounded)

This document records the minimal external research used to shape requirements and tuning
for this Space Invaders clone. It distils claims into decision-relevant guidance and keeps
the source URLs for auditability.

## Evidence Summary (claims -> decisions)

### Formation shape, movement, and one-shot discipline define the feel

- Claim: A classic wave is an 11 x 5 grid of invaders that moves horizontally, reverses at screen edges, drops downward on each edge hit, and speeds up as invaders are removed. The player cannon moves horizontally only and usually has just one shot on screen.
  Sources: https://www.shmups.wiki/library/Space_Invaders , https://en.wikipedia.org/wiki/Space_Invaders
- Decision: Use an 11 x 5 configurable fleet, enforce one active player projectile, and implement fleet motion as discrete side-steps plus downward drops rather than freeform enemy movement.

### Shields are not decoration; they are part of the tactical loop

- Claim: Each wave includes four destructible shields that block both player and enemy fire, and damaged shields meaningfully change safe shooting lanes.
  Sources: https://www.shmups.wiki/library/Space_Invaders , https://www.brentradio.com/SpaceInvaders2.htm
- Decision: Model bunkers as destructible cell grids in config so erosion is a gameplay system, not a painted background element.

### Score values are row-based and UFO scoring is special

- Claim: Bottom invaders score 10, middle rows 20, top row 30; the UFO awards a value from a deterministic shot-count cycle rather than true randomness in the arcade game.
  Sources: https://www.shmups.wiki/library/Space_Invaders , https://www.brentradio.com/SpaceInvaders2.htm
- Decision: Keep row scoring explicit in config and implement the UFO using a deterministic score cycle tied to the player shot count.

### Pressure comes from acceleration and return fire, not from free movement

- Claim: The classic difficulty curve comes from the fleet accelerating as it thins and from invader fire arriving through surviving columns. Game over occurs when all lives are lost or invaders reach the player area.
  Sources: https://www.shmups.wiki/library/Space_Invaders , https://en.wikipedia.org/wiki/Space_Invaders
- Decision: Scale formation step interval down as alive count drops, let surviving columns fire back, and use an invasion line near the player as a second loss condition.

### Extra life and escalating waves are part of the recognisable arcade contract

- Claim: The player starts with three lives and can earn a fourth at 1500 points; additional waves continue with rising pressure.
  Sources: https://www.shmups.wiki/library/Space_Invaders
- Decision: Start with three lives, award one extra life at a configurable threshold defaulting to 1500, and reset a fresh wave on clear while tightening timing across levels.

### How it should be built in Pygame

- Claim: Common Pygame implementations organise the game around a fixed update loop, explicit game states, separate player/enemy/projectile systems, and dedicated rendering/collision responsibilities. Public examples often collapse everything into one large file.
  Sources: https://github.com/leerob/space-invaders/blob/master/spaceinvaders.py , https://code.stanford.edu/jon.b.green/ai-arcade-demo/-/blob/main/todo/012-space-invaders-game.md
- Decision: Reuse the Pac-Man dry-run principles instead of the common single-file pattern: one responsibility per file, YAML-driven tuning, dedicated renderer/audio modules, and tests for fleet, bunker, player-shot, and UFO logic.

## Notes on source quality

- Wikipedia is used for high-level gameplay facts, not frame-perfect arcade timing.
- Shmups Wiki is treated as the highest-signal gameplay reference in this bounded research pass because it captures concrete mechanical details used by players and arcade enthusiasts.
- Community strategy references are used only to confirm mechanics that matter to the clone feel (UFO scoring, shield role, fleet acceleration), not to justify exact emulation.
