# Tablut Game
This repository contains the implementation of a client for the Tablut game, including various utilities and algorithms to play the game.
## Features
-`Client`: Connects to a Tablut game server, sends moves, and receives game state updates.
-`State Management`: Manages the game state, including the board and player turns.
-`Move Generation`: Generates all possible moves for a given game state.
-`Heuristics`: Evaluates the game state to make strategic decisions.
-`Minimax Algorithm`: Implements the minimax algorithm with alpha-beta pruning for decision making.
## Usage
To start the client, run the seguent command in the `TablutClient` folder:
```
python ./Client.py -p <player> -t <timeout> -i <server_ip>
```
-`<player>`: Role of the player (white or black).
-`<timeout>`: Timeout in seconds.
-`<server_ip>`: IP address of the server.

## Project Structure
-`Client.py`: Main client implementation.
-`State.py`: Manages the game state and board.
-`Search.py`: Implements the minimax algorithm and heuristics.
-`ReadCSV.py`: Utility for reading and processing CSV files.
-`ParseFiles.py`: Parses game state files and generates CSV data.
-`test.ipynb`: Jupyter notebook for testing and experimenting with the code.
