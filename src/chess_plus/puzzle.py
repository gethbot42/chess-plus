"""The Puzzle class: one Lichess puzzle row."""

from __future__ import annotations

import csv
import datetime
from collections.abc import Mapping

import chess

_HEADER: tuple[str, ...] = (
    "PuzzleId", "FEN", "Moves", "Rating", "RatingDeviation", "Popularity",
    "NbPlays", "Themes", "GameUrl", "OpeningTags", "DailyDate",
)


def _int(row: Mapping[str, str], key: str) -> int:
    value = row[key]
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{key}: expected an integer, got {value!r}") from None


class Puzzle:
    """One Lichess puzzle row with step-by-step navigation."""

    __slots__ = (
        "_puzzle_id", "_fen", "_moves", "_rating", "_rating_deviation", "_popularity",
        "_nb_plays", "_themes", "_game_url", "_opening_tags", "_daily_date",
        "_solver_color", "_san_moves",
    )

    _puzzle_id: str
    _fen: str
    _moves: tuple[chess.Move, ...]
    _rating: int
    _rating_deviation: int
    _popularity: int
    _nb_plays: int
    _themes: tuple[str, ...]
    _game_url: str
    _opening_tags: tuple[str, ...]
    _daily_date: datetime.date | None
    _solver_color: chess.Color
    _san_moves: tuple[str, ...]

    @classmethod
    def from_csv_row(cls, line: str) -> Puzzle:
        """Load a puzzle from one line of the Lichess puzzle CSV (no header).

        Raises ValueError("<Field>: <reason>") if the row is invalid.
        """
        fields = next(csv.reader([line]))
        if len(fields) != len(_HEADER):
            raise ValueError(f"row: expected {len(_HEADER)} fields, got {len(fields)}")
        return cls.from_dict(dict(zip(_HEADER, fields)))

    @classmethod
    def from_dict(cls, row: Mapping[str, str]) -> Puzzle:
        """Load a puzzle from a mapping keyed by the Lichess CSV header names.

        Raises ValueError("<Field>: <reason>") if a key is missing or a value is invalid.
        """
        for key in _HEADER:
            if key not in row:
                raise ValueError(f"{key}: missing")

        puzzle_id = row["PuzzleId"]
        if not puzzle_id:
            raise ValueError("PuzzleId: empty")

        fen = row["FEN"]
        try:
            board = chess.Board(fen)
        except ValueError as err:
            raise ValueError(f"FEN: {err}") from None
        solver_color = not board.turn

        ucis = row["Moves"].split()
        if len(ucis) < 2:
            raise ValueError(f"Moves: expected at least 2 moves, got {len(ucis)}")
        moves: list[chess.Move] = []
        san_moves: list[str] = []
        for uci in ucis:
            try:
                move = chess.Move.from_uci(uci)
            except ValueError:
                raise ValueError(f"Moves: {uci!r} is not a UCI move") from None
            if move not in board.legal_moves:
                raise ValueError(f"Moves: {uci!r} is illegal in {board.fen()!r}")
            san_moves.append(board.san(move))
            board.push(move)
            moves.append(move)

        rating = _int(row, "Rating")
        rating_deviation = _int(row, "RatingDeviation")
        popularity = _int(row, "Popularity")
        nb_plays = _int(row, "NbPlays")

        daily_date: datetime.date | None = None
        if row["DailyDate"].strip():
            try:
                daily_date = datetime.date.fromisoformat(row["DailyDate"].strip())
            except ValueError as err:
                raise ValueError(f"DailyDate: {err}") from None

        self = object.__new__(cls)
        self._puzzle_id = puzzle_id
        self._fen = fen
        self._moves = tuple(moves)
        self._rating = rating
        self._rating_deviation = rating_deviation
        self._popularity = popularity
        self._nb_plays = nb_plays
        self._themes = tuple(row["Themes"].split())
        self._game_url = row["GameUrl"]
        self._opening_tags = tuple(row["OpeningTags"].split())
        self._daily_date = daily_date
        self._solver_color = solver_color
        self._san_moves = tuple(san_moves)
        return self

    @property
    def puzzle_id(self) -> str:
        """Lichess puzzle ID."""
        return self._puzzle_id

    @property
    def fen(self) -> str:
        """Position before the first move (the opponent's setup move)."""
        return self._fen

    @property
    def moves(self) -> tuple[chess.Move, ...]:
        """All moves in order; the first is the opponent's setup move."""
        return self._moves

    @property
    def rating(self) -> int:
        """Puzzle rating."""
        return self._rating

    @property
    def rating_deviation(self) -> int:
        """Rating deviation."""
        return self._rating_deviation

    @property
    def popularity(self) -> int:
        """Popularity, -100..100 on Lichess (may be negative)."""
        return self._popularity

    @property
    def nb_plays(self) -> int:
        """Number of times the puzzle has been played."""
        return self._nb_plays

    @property
    def themes(self) -> tuple[str, ...]:
        """Theme tags."""
        return self._themes

    @property
    def game_url(self) -> str:
        """URL of the source game."""
        return self._game_url

    @property
    def opening_tags(self) -> tuple[str, ...]:
        """Opening tags; empty if the puzzle has none."""
        return self._opening_tags

    @property
    def daily_date(self) -> datetime.date | None:
        """Date this was the Lichess daily puzzle, or None."""
        return self._daily_date

    @property
    def solver_color(self) -> chess.Color:
        """Side the solver plays (the side not to move in `fen`)."""
        return self._solver_color

    @property
    def san_moves(self) -> tuple[str, ...]:
        """All moves in SAN, played from `fen`."""
        return self._san_moves
