# Quickstart: Lichess Puzzle

## Setup

```powershell
python -m venv .venv; .venv\Scripts\Activate.ps1
pip install -e . pytest mypy
```

## Validate

```powershell
pytest
mypy src
```

Both must pass.

## Manual check (SC-004: ≤ 5 lines)

```python
from chess_plus import Puzzle
p = Puzzle.from_csv_row("00sO1,1k1r4/pp3pp1/2p1p3/4b3/P3n1P1/8/KPP2PN1/3rBR1R b - - 2 31,b8c7 e1a5 b7b6 f1d1,998,85,94,293,advantage discoveredAttack master middlegame short,https://lichess.org/vsfFkG0s/black#62,,")
print(p.san_moves)      # ('Kc7', 'Ba5+', 'b6', 'Rxd1')
while p.forward(): print(p.board.fen())
```

## Scenarios the tests must cover

| Scenario | Expected | Spec ref |
|----------|----------|----------|
| Load sample row | all fields match row; `solver_color == chess.WHITE` | US1, SC-001 |
| Row with opening tags + date | tags tuple, `datetime.date` | US1-4 |
| Forward N then back N | `board.fen() == fen` | US2, SC-002 |
| Forward at end / back at start | returns `False`, board unchanged | US2-4/5 |
| `go_to(i)` vs stepping | same FEN; `go_to(-1)`/`go_to(N+1)` raise | US2-6, FR-010 |
| SAN at any step | `('Kc7','Ba5+','b6','Rxd1')` | US3, SC-003 |
| Invalid rows (field count, FEN, illegal move, non-int, <2 moves, header row) | `ValueError` naming the field | Edge Cases, SC-005 |

See [contracts/puzzle-api.md](contracts/puzzle-api.md) for the API.
