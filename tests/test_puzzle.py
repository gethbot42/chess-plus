import chess
import csv
import datetime
import pytest

from chess_plus import Puzzle

SAMPLE_ROW = "00sO1,1k1r4/pp3pp1/2p1p3/4b3/P3n1P1/8/KPP2PN1/3rBR1R b - - 2 31,b8c7 e1a5 b7b6 f1d1,998,85,94,293,advantage discoveredAttack master middlegame short,https://lichess.org/vsfFkG0s/black#62,,"
SAMPLE_FEN = "1k1r4/pp3pp1/2p1p3/4b3/P3n1P1/8/KPP2PN1/3rBR1R b - - 2 31"
HEADER = "PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,OpeningTags,DailyDate"
TAGGED_ROW = SAMPLE_ROW[:-2] + ",Sicilian_Defense Sicilian_Defense_Najdorf,2024-01-15"


def row_with(**changes: str) -> str:
    """SAMPLE_ROW with the named columns replaced, e.g. row_with(Rating="abc")."""
    fields = dict(zip(HEADER.split(","), SAMPLE_ROW.split(",")))
    fields.update(changes)
    return ",".join(fields.values())


# --- US1: load ---


def test_load_sample_row_fields() -> None:
    p = Puzzle.from_csv_row(SAMPLE_ROW)
    assert p.puzzle_id == "00sO1"
    assert p.fen == SAMPLE_FEN
    assert p.moves == tuple(chess.Move.from_uci(m) for m in ["b8c7", "e1a5", "b7b6", "f1d1"])
    assert p.rating == 998
    assert p.rating_deviation == 85
    assert p.popularity == 94
    assert p.nb_plays == 293
    assert p.themes == ("advantage", "discoveredAttack", "master", "middlegame", "short")
    assert p.game_url == "https://lichess.org/vsfFkG0s/black#62"
    assert p.opening_tags == ()
    assert p.daily_date is None


def test_load_solver_color() -> None:
    assert Puzzle.from_csv_row(SAMPLE_ROW).solver_color == chess.WHITE


def test_load_tagged_row() -> None:
    p = Puzzle.from_csv_row(TAGGED_ROW)
    assert p.opening_tags == ("Sicilian_Defense", "Sicilian_Defense_Najdorf")
    assert p.daily_date == datetime.date(2024, 1, 15)


def test_load_from_dict() -> None:
    mapping = dict(zip(HEADER.split(","), next(csv.reader([SAMPLE_ROW]))))
    a, b = Puzzle.from_dict(mapping), Puzzle.from_csv_row(SAMPLE_ROW)
    for name in ("puzzle_id", "fen", "moves", "rating", "rating_deviation", "popularity", "nb_plays",
                 "themes", "game_url", "opening_tags", "daily_date", "solver_color", "san_moves"):
        assert getattr(a, name) == getattr(b, name), name
    del mapping["Rating"]
    with pytest.raises(ValueError, match="Rating"):
        Puzzle.from_dict(mapping)


def test_load_whitespace_tags() -> None:
    assert Puzzle.from_csv_row(row_with(Themes="  advantage   short ")).themes == ("advantage", "short")
    assert Puzzle.from_csv_row(row_with(Themes="")).themes == ()


@pytest.mark.parametrize(
    ("row", "field_name"),
    [
        (SAMPLE_ROW[:-1], "row"),
        (SAMPLE_ROW + ",", "row"),
        (row_with(PuzzleId=""), "PuzzleId"),
        (row_with(FEN="not a fen"), "FEN"),
        (row_with(Moves=""), "Moves"),
        (row_with(Moves="b8c7"), "Moves"),
        (row_with(Moves="b8c7 zzzz"), "Moves"),
        (row_with(Moves="b8c7 a1a8"), "Moves"),
        (row_with(Rating="abc"), "Rating"),
        (row_with(RatingDeviation="1.5"), "RatingDeviation"),
        (row_with(Popularity="x"), "Popularity"),
        (row_with(NbPlays=""), "NbPlays"),
        (row_with(DailyDate="2024-13-45"), "DailyDate"),
        (HEADER, r"^\w+: "),
    ],
    ids=["10-fields", "12-fields", "empty-id", "bad-fen", "no-moves", "one-move", "not-uci", "illegal",
         "rating", "deviation", "popularity", "nb-plays", "daily-date", "header"],
)
def test_load_invalid_rows(row: str, field_name: str) -> None:
    with pytest.raises(ValueError, match=field_name):
        Puzzle.from_csv_row(row)


def test_load_negative_popularity() -> None:
    assert Puzzle.from_csv_row(row_with(Popularity="-42")).popularity == -42
