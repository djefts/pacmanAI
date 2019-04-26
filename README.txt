# Pac-Man Maze Search Comparison

This is a Python library for solving mazes using a plethora of search algorithms and paradigms.

## Installation

Unzip the `pacman_project.zip` file then `cd` into its directory. From there you can run any of the commands in `commands.txt` in the command line. For example:

```bash
python pacman.py -l tinyMaze -p SearchAgent
```

## Usage

```bash
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic
```

`pacman.py` is the main program file that parses the command line inputs and runs any other files that need to be run.

The `-l` flag followed by the name of a `.layout` file located in `layouts` determines the pre-made maze that will be used.

The `z` flag followed by a decimal number determines the size of the graphical interface output, we recommend `.5` for `mediumMaze` and `bigMaze` but the `-z` flag is never required.

`-p` determines the SearchAgent that will be used, however none are implemented except for `SearchAgent`.

`-a fn=` is used to set the search algorithm that will be used and can be one of the following:

```bash
dfs- Depth First Search
astar- A Star Search
gas- Genetic Algorithm Search
```

Following the `-a` flag is the optional `hueristic=` command to set a heuristic search option. It can only be used with the DFS and A-Star algorithms and is currently only implemented for the `manhatatenHeuristic`.

