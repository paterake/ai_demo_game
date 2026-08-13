from ai_pacman.maze import Maze


def test_maze_load_and_pellet_eat() -> None:
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
            "#P.1#",
            "#.o.#",
            "#2.3#",
            "##4##",
        ],
    }

    maze = Maze.from_config(config)
    assert maze.rows == 5
    assert maze.cols == 5
    assert maze.pacman_spawn == (1, 1)
    assert maze.ghost_spawns["blinky"] == (1, 3)
    assert maze.pellet_kind(1, 2) == "normal"
    assert maze.pellet_kind(2, 2) == "power"

    maze2, kind = maze.eat_pellet(1, 2)
    assert kind == "normal"
    assert not maze2.has_pellet(1, 2)

    maze3, kind = maze2.eat_pellet(2, 2)
    assert kind == "power"
    assert not maze3.has_pellet(2, 2)


def test_maze_tunnel_wrap() -> None:
    config = {
        "legend": {
            "wall": "#",
            "pellet": ".",
            "power_pellet": "o",
            "empty": " ",
            "pacman_spawn": "P",
            "ghost_spawns": {"blinky": "1", "pinky": "2", "inky": "3", "clyde": "4"},
        },
        "tunnels": {"wrap_rows": [1]},
        "grid": [
            "#####",
            " P.1 ",
            "##2##",
            "##3##",
            "##4##",
        ],
    }
    maze = Maze.from_config(config)
    assert maze.next_position(1, 0, "left") == (1, 4)
    assert maze.next_position(1, 4, "right") == (1, 0)
