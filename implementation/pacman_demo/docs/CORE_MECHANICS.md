# Core Mechanics — Source Brief

This document records the original brief verbatim. It is the authoritative source for
core gameplay constraints. The PRD extends and governs these requirements — it does not
replace them. Any implementation item that touches core mechanics must be consistent
with this document.

---

## Original Brief (verbatim)

> Act as an expert Python game developer. Write a complete, single-file Python script to
> create a Pac-Man clone using the Pygame library. Ensure the code is production-ready,
> fully commented, and handles all errors.
>
> Implement the following core mechanics:
>
> **1. Window & Grid**
> A 600x600 window. Create a distinct grid layout with blue walls, a black background,
> yellow pellets, and larger power pellets.
>
> **2. Pac-Man**
> A yellow circle with an animated chomping mouth that changes direction based on arrow
> key inputs. Pac-Man must stop when colliding with walls.
>
> **3. Ghosts**
> Four distinct ghosts (Blinky, Pinky, Inky, Clyde) using red, pink, cyan, and orange
> colors. Implement basic AI where they navigate the maze and turn randomly at
> intersections.
>
> **4. Game Loop**
> Maintain 60 FPS. Handle events, update entity positions, check collisions, and render
> the screen.
>
> **5. Gameplay Logic**
> - Pac-Man eats pellets to increase the score.
> - Eating a power pellet turns ghosts blue (frightened mode) for 7 seconds, allowing
>   Pac-Man to eat them.
> - Normal ghost collision resets Pac-Man's position and loses 1 of 3 lives.
>
> **6. UI Text**
> Display current Score, Lives left, and a "Game Over" or "Victory" screen when
> conditions are met.
>
> Include a standard main execution block. Ensure all Pygame assets (like shapes) are
> drawn programmatically using pygame.draw so no external image files are required.

---

## Constraints Extracted

The following are hard constraints derived from the brief. They are non-negotiable
regardless of what extensions are added.

| # | Constraint | Source |
|---|------------|--------|
| C1 | Window size: 600×600 pixels (configurable default) | Window & Grid |
| C2 | Walls rendered in blue; background black | Window & Grid |
| C3 | Pellets yellow; power pellets larger and visually distinct | Window & Grid |
| C4 | Pac-Man is a yellow circle with an animated chomping mouth | Pac-Man |
| C5 | Pac-Man direction is controlled by arrow keys | Pac-Man |
| C6 | Pac-Man stops on wall collision — does not pass through | Pac-Man |
| C7 | Four ghosts: Blinky (red), Pinky (pink), Inky (cyan), Clyde (orange) | Ghosts |
| C8 | Ghost AI navigates corridors and turns randomly at intersections | Ghosts |
| C9 | Game loop targets 60 FPS | Game Loop |
| C10 | Loop handles: events → update positions → check collisions → render | Game Loop |
| C11 | Eating a pellet increments score | Gameplay Logic |
| C12 | Eating a power pellet triggers frightened mode on all ghosts for 7 seconds | Gameplay Logic |
| C13 | In frightened mode ghosts turn blue and can be eaten by Pac-Man | Gameplay Logic |
| C14 | Ghost collision in normal mode: lose 1 life, reset Pac-Man position | Gameplay Logic |
| C15 | Starting lives: 3 | Gameplay Logic |
| C16 | HUD displays current score and lives remaining | UI Text |
| C17 | Game Over screen shown when lives reach 0 | UI Text |
| C18 | Victory screen shown when all pellets are eaten | UI Text |
| C19 | All rendering uses pygame.draw — no external image files | pygame.draw |

---

## Governance Notes

The brief asks for a single-file script. That constraint is **overridden by governance**
(see `PRD.md` and `docs/AI_ENGAGEMENT.md`). All other constraints above are carried
forward unchanged into the implementation.

Values in C1, C12, and C15 (window size, frightened duration, starting lives) are
expressed as configurable defaults in `config/game.yaml` — the constraint is the
*default value*, not a hardcoded constant.

Colour values in C2, C3, C7, C13 are the *required defaults* in `config/visuals.yaml`.
They can be changed via config without touching source.
