# Contract: `chess_plus.Puzzle` public API

`from chess_plus import Puzzle` — the only export.

## Construction

| Call | Returns | Raises |
|------|---------|--------|
| `Puzzle.from_csv_row(line: str)` | `Puzzle` | `ValueError("<Field>: <reason>")` |
| `Puzzle.from_dict(row: Mapping[str, str])` | `Puzzle` | `ValueError("<Field>: <reason>")` |

`from_csv_row` expects exactly 11 fields; otherwise `ValueError` naming the row. `from_dict`
requires all 11 header keys; missing key → `ValueError` naming it.

## Data (read-only)

`puzzle_id`, `fen`, `moves`, `rating`, `rating_deviation`, `popularity`, `nb_plays`, `themes`,
`game_url`, `opening_tags`, `daily_date`, `solver_color`, `san_moves` — types in
[data-model.md](../data-model.md).

## Navigation

| Member | Type | Behavior |
|--------|------|----------|
| `step` | `int` property | current index, 0..N |
| `board` | `chess.Board` property | copy of position at `step` |
| `next_move` | `chess.Move \| None` property | move `forward()` would play |
| `previous_move` | `chess.Move \| None` property | move `back()` would undo |
| `forward()` | `-> bool` | play one move; `False` at end, no change |
| `back()` | `-> bool` | undo one move; `False` at start, no change |
| `go_to(step: int)` | `-> None` | jump; `ValueError` if outside 0..N |
| `go_to_start()` / `go_to_solver_start()` / `go_to_end()` | `-> None` | `go_to(0)` / `go_to(1)` / `go_to(N)` |
