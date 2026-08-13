# Research Evidence — Pac-Man Mechanics (bounded)

This document records the minimal external research used to shape requirements and tuning for this Pac-Man clone. It distils claims into decision-relevant guidance and includes source URLs for auditability.

## Evidence Summary (claims → decisions)

### Maze geometry, tunnels, and what “classic” looks like

- Claim: A “classic-feeling” Pac-Man clone typically uses the standard maze proportions (commonly represented as a 28×31 tile grid in many implementations), with a central ghost house and a side tunnel wrap-around row.  
  Sources: https://github.com/bborbe/pacman/ , https://github.com/andymccall/pac-man/wiki/Arcade-fidelity
- Decision: Treat maze layout as first-class config (grid + legend) and prefer a 28-column grid so it can be upgraded to a closer-to-arcade layout without code changes. If arcade fidelity is desired, implement explicit tunnel wrap-around rather than relying on “open edges”.

### “READY!” / intro pacing is part of the feel

- Claim: Arcade-faithful implementations explicitly model a state machine that includes a READY banner / pre-play pause before gameplay begins.  
  Source: https://github.com/andymccall/pac-man/wiki/Arcade-fidelity
- Decision: Include a start screen and a short countdown before transitioning into gameplay (workshop-friendly version of READY pacing).

### Frightened mode: ghosts turn blue, become edible, then “regenerate”

- Claim: When a power pellet (energizer) is eaten, ghosts enter a frightened state where Pac-Man can eat them for points; eaten ghosts return to a “pen/house” to regenerate, then resume chasing.  
  Sources: https://en.wikipedia.org/wiki/Pac-Man , https://www.tumblr.com/lullatome/126395552734/understanding-pac-man-ghost-behavior , https://github.com/andymccall/pac-man/wiki/Arcade-fidelity
- Decision: Use a global frightened timer (config-driven). When eaten, a ghost becomes “eyes”, routes back to the ghost house/spawn area, then regenerates briefly before returning to normal pursuit.

### Maze, dots, and energizers as fixed elements of play

- Claim: The canonical game loop is “eat all dots in the maze while avoiding four ghosts”; energizers are larger pellets that trigger frightened mode.  
  Sources: https://en.wikipedia.org/wiki/Pac-Man
- Decision: Maze encoding includes distinct pellet types (`.` pellet, `o` power pellet). Victory condition is “no pellets remain”.

### Ghost movement complexity in the original is high; clones commonly simplify

- Claim: The original ghost AI includes multiple modes (scatter/chase), mode timers, and direction reversals on mode transitions; frightened mode typically affects speed and decision behaviour.  
  Sources: https://github.com/andymccall/pac-man/wiki/Ghost-AI , https://github.com/andymccall/pac-man/wiki/Arcade-fidelity , https://www.tumblr.com/lullatome/126395552734/understanding-pac-man-ghost-behavior
- Decision: Prioritise clarity over perfect fidelity: use deterministic, maze-aware pursuit (shortest-path-style decisions at intersections) in normal mode, and random-walk decisions in frightened mode. Scatter/chase schedules remain out of scope for this workshop demo.

### Bonus fruit (symbols) timing and value

- Claim: In the original Pac-Man, bonus symbols (“fruit”) appear twice per level: once after 70 dots and again after 170 dots, typically below the ghost pen. They remain on screen for ~9–10 seconds (variable), and the symbol/value depends on the current level.  
  Source: https://pacmanmuseum.com/history/pacman-scoring.php
- Decision: Implement two per-level fruit spawns at dot thresholds (70 and 170), with a configurable TTL range (9–10 seconds). Use a level-indexed fruit schedule (cherry → strawberry → orange → apple → pineapple → galaxian → bell → key).

### Implementation references (Pygame-specific)

- Claim: A full Pac-Man build in Pygame commonly evolves through stages: grid + movement → node-restricted movement → ghosts + AI → UI polish → sprites/animation → title page + buttons + music/SFX.  
  Source: https://pacmancode.com/
- Claim: A larger Pac-Man Pygame project describes reading mazes from external text files and using more sophisticated ghost pathfinding (A* variant), with multiple mazes and richer gameplay elements.  
  Sources: https://www.pygame.org/project-Pacman-426-4585.html , https://github.com/greyblue9/pacman-python
- Decision: For this workshop demo, prefer a config-driven maze, explicit game states, and synth audio (no external assets). Prioritise recognisable feel and extensibility over arcade-perfect reproduction.

## Notes on source quality

- Wikipedia is used for high-level gameplay facts, not timing-perfect mechanics.
- The andymccall “pac-man” wiki is treated as a high-signal engineering reference for what arcade fidelity entails, but the workshop scope may deliberately simplify it.
- Community guides and clones are used only to triangulate “what feels classic” (maze proportions, READY pacing), not as authoritative sources for the original arcade timings.
