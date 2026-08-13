import random

from ai_pacman.ghost import Ghost
from ai_pacman.maze import Maze


def test_ghost_turns_at_intersection() -> None:
    config = {
        "legend": {
            "wall": "#",
            "pellet": ".",
            "power_pellet": "o",
            "empty": " ",
            "pacman_spawn": "P",
            "ghost_spawns": {"blinky": "1", "pinky": "2", "inky": "3", "clyde": "4"},
        },
        "grid": [
            "#####",
            "#...#",
            "#.P.#",
            "#1.2#",
            "#3.4#",
        ],
    }
    maze = Maze.from_config(config)
    rng = random.Random(0)
    ghost = Ghost(
        name="blinky",
        row=2,
        col=2,
        direction="up",
        speed_tiles_per_s=10.0,
        spawn_row=3,
        spawn_col=1,
    )

    ghost.update(
        0.2,
        maze,
        now_s=0.0,
        pacman_row=1,
        pacman_col=1,
        frightened_active=False,
        frightened_remaining_s=0.0,
        frightened_speed_multiplier=0.6,
        rng=rng,
    )
    assert (ghost.row, ghost.col) != (2, 2)
    assert ghost.direction in {"left", "right", "up", "down"}


def test_ghost_reverses_on_fright_start() -> None:
    config = {
        "legend": {
            "wall": "#",
            "pellet": ".",
            "power_pellet": "o",
            "empty": " ",
            "pacman_spawn": "P",
            "ghost_spawns": {"blinky": "1", "pinky": "2", "inky": "3", "clyde": "4"},
        },
        "grid": [
            "#####",
            "#...#",
            "#.P.#",
            "#1.2#",
            "#3.4#",
        ],
    }
    maze = Maze.from_config(config)
    rng = random.Random(0)
    ghost = Ghost(
        name="blinky",
        row=2,
        col=2,
        direction="left",
        speed_tiles_per_s=0.0,
        spawn_row=3,
        spawn_col=1,
    )

    ghost.update(
        0.0,
        maze,
        now_s=0.0,
        pacman_row=1,
        pacman_col=1,
        frightened_active=True,
        frightened_remaining_s=6.0,
        frightened_speed_multiplier=0.6,
        rng=rng,
    )
    assert ghost.mode == "frightened"
    assert ghost.direction == "right"
