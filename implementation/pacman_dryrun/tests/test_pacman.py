from ai_pacman.maze import Maze
from ai_pacman.pacman import PacMan


def test_pacman_stops_at_wall_and_turns_when_possible() -> None:
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
            "#P..#",
            "###.#",
            "#1.2#",
            "#3.4#",
        ],
    }
    maze = Maze.from_config(config)
    pacman = PacMan(row=1, col=1, direction="right", queued_direction=None, speed_tiles_per_s=10.0)

    moved = pacman.update(0.2, maze, mouth_speed_hz=6.0)
    assert moved
    assert (pacman.row, pacman.col) == (1, 3)

    moved = pacman.update(0.2, maze, mouth_speed_hz=6.0)
    assert not moved
    assert (pacman.row, pacman.col) == (1, 3)

    pacman.queue_direction("down")
    moved = pacman.update(0.11, maze, mouth_speed_hz=6.0)
    assert moved
    assert (pacman.row, pacman.col) == (2, 3)
