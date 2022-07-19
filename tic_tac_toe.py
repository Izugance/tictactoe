"""An exploration of object-oriented modelling for Tic-Tac-Toe."""

from __future__ import annotations
from typing import Union, cast


class InvalidPosition(ValueError):
    pass


class GameOver(SystemExit):
    pass


class Win(SystemExit):
    pass


class UserExit(SystemExit):
    pass


class Forfeit(Exception):
    pass


Player = str
Players = tuple[Player, Player]
Position = tuple[int, int]


class Board:
    """Representation of a 3-by-3 Tic-Tac-Toe board."""

    _AXES = (
        {(0, 0), (0, 1), (0, 2)},  # Rows.
        {(1, 0), (1, 1), (1, 2)},
        {(2, 0), (2, 1), (2, 2)},
        {(0, 0), (1, 0), (2, 0)},  # Columns.
        {(0, 1), (1, 1), (2, 1)},
        {(0, 2), (1, 2), (2, 2)},
        {(0, 0), (1, 1), (2, 2)},  # Diagonals.
        {(2, 0), (1, 1), (0, 2)},
    )

    def __init__(self, players: Players) -> None:
        """Initialize a Tic-Tac-Toe board."""
        self._grid: list
        self._turn: int
        self._filled_squares: int
        self.reset_board()
        self._players: Players = players

    def _check_win(self, pos: Position) -> bool:
        """Check if a win has occurred.

        Return True if there's a win, else False.
        """
        relevant_axes = (axis for axis in Board._AXES if pos in axis)
        for axis in relevant_axes:
            vals = list(filter(lambda x: self._grid[x[0]][x[1]] != " ", axis))
            if len(vals) < 3:
                continue  # Row isn't filled.
            else:
                if len(set(self._grid[row][col] for row, col in vals)) > 1:
                    continue  # Row contains different values.
                return True

        return False

    def reset_board(self) -> None:
        """Clear the board and reset count statistics."""
        self._grid = [[" "] * 3 for i in range(3)]
        self._turn = 0
        self._filled_squares = 0

    def display_board(self) -> None:
        """Display the board with its values."""
        for i in range(3):
            print(
                self._grid[i][0], "|", self._grid[i][1], "|", self._grid[i][2], sep=""
            )
            if i < 2:
                print("-", "+", "-", "+", "-", sep="")
        print("\n")

    def move(self, pos: Position) -> None:
        """Update the board with a player's move at a position."""
        row, col = pos
        self._grid[row][col] = self._players[self._turn]
        self.display_board()
        self._filled_squares += 1
        # Check for wins only if the board has been filled
        # to a certain level.
        if self._filled_squares >= 5:
            win = self._check_win(pos)
            if win:
                # The player with the most recent turn wins.
                raise Win(f"Player {self._players[self._turn]!r} wins!")
        if self._filled_squares == 9:
            raise GameOver("Game Over!")
        self._turn = int(not self._turn)  # Easy here since we're using 1 or 0.


class TicTacToe:
    """3-by-3 grid tic-tac-toe game class."""

    ALLOWED_POSITIONS = {
        "1": (0, 0),
        "2": (0, 1),
        "3": (0, 2),
        "4": (1, 0),
        "5": (1, 1),
        "6": (1, 2),
        "7": (2, 0),
        "8": (2, 1),
        "9": (2, 2),
    }

    def __init__(self) -> None:
        """Create a TicTacToe instance."""
        self._board: Board

    def _display_exception(self, ex: BaseException) -> None:
        print(str(ex))
        print("\n")

    def _query_replay(self, rematch: bool = False) -> bool:
        query = "Play again? [y/n]: " if not rematch else "Rematch? [y/n]: "
        while True:
            play_again = input(query).lower().strip()
            if play_again == "y":
                print("\n")
                if rematch:
                    self._board.reset_board()
                return True
            elif play_again in ("n", "quit"):
                print("GOODBYE!")
                return False

    def _get_players(self) -> Players:
        """Get player marks and return a tuple of Player objects."""
        players = []
        i = 1
        while i <= 2:
            player = input(f"Enter mark (player {i}): ")
            if player == "quit":
                raise UserExit()
            if len(player) != 1:
                print("Enter a mark with one value\n")
                continue
            players.append(player)
            i += 1

        return cast(Players, tuple(players))

    def _get_player_move(self) -> Position:
        """Get a valid move from a player."""
        while True:
            try:
                print(f"Player {self._board._turn + 1}")
                in_ = input("Enter position: ").lower().strip()
                if in_ == "quit":
                    raise UserExit()
                elif in_ == "ff":
                    raise Forfeit()
                pos = self._validate_move(in_)
            except InvalidPosition as ex:
                self._display_exception(ex)
                continue
            else:
                return pos

    def _validate_move(self, pos: str) -> Position:
        """Validate a player's move."""
        if not pos in self.ALLOWED_POSITIONS:
            raise InvalidPosition("Position does not exist")

        row, col = self.ALLOWED_POSITIONS[pos]
        if self._board._grid[row][col] != " ":
            raise InvalidPosition("Position is occupied")

        return row, col

    def display_intro(self) -> None:
        """Display the game's layout and instructions."""
        layout = (
            "Welcome to Tic-tac-toe.\n"
            "Below is the board's layout, with the positions in the squares.\n"
            "1|2|3\n"
            "-+-+-\n"
            "4|5|6\n"
            "-+-+-\n"
            "7|8|9\n"
            "Enter a position as above, after setup to make a move.\n"
            "If there's no possibility of winning with a board's configuration, "
            "enter 'ff' to forfeit the round.\n"
            "Enter 'quit' at any point in the game to exit.\n"
        )
        print(layout)

    def main(self):
        """TicTacToe's main game loop."""
        self.display_intro()
        while True:
            players = self._get_players()
            self._board = Board(players)
            self._board.display_board()
            while True:
                try:
                    pos = self._get_player_move()
                    self._board.move(pos)
                except Forfeit:
                    rematch = self._query_replay(rematch=True)
                    if rematch:
                        self._board.display_board()
                        continue
                    else:
                        raise UserExit()
                except (Win, GameOver) as ex:
                    self._display_exception(ex)
                    play_again = self._query_replay()
                    if play_again:
                        break
                    else:
                        raise UserExit()


if __name__ == "__main__":
    TicTacToe().main()
