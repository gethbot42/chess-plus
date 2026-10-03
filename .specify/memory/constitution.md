<!--
Sync Impact Report
- Version change: (template) → 1.0.0
- Modified principles: none (initial ratification)
- Added principles:
  I. Build on python-chess
  II. Test-First (NON-NEGOTIABLE)
  III. Simplicity / YAGNI
  IV. Stable, Typed Public API
- Added sections: Technical Constraints, Development Workflow, Governance
- Removed sections: Principle 5 slot (only four principles were adopted)
- Follow-up TODOs: none
-->

# chess-plus Constitution

## Core Principles

### I. Build on python-chess

chess-plus is a reusable Python library that extends python-chess (PyPI package `chess`).

- Board representation, move generation, legality checks, notation (SAN/UCI/FEN/PGN) and
  game-state detection MUST be delegated to python-chess.
- chess-plus MUST NOT re-implement functionality that python-chess already provides. If
  python-chess's behavior is insufficient, the gap MUST be documented in the plan before
  anything is wrapped or extended.
- chess-plus types SHOULD accept and return python-chess objects (`chess.Board`,
  `chess.Move`, etc.) rather than parallel types of its own.

Rationale: python-chess is mature and heavily tested. Duplicating it adds bugs and
maintenance work without adding value.

### II. Test-First (NON-NEGOTIABLE)

TDD applies to every change, without exception.

- Tests MUST be written first and MUST fail before any implementation code is written.
- Red → Green → Refactor MUST be followed: write a failing test, write the minimum code to
  pass it, then refactor while the tests stay green.
- Every bug fix MUST start with a test that reproduces the bug.
- A change MUST NOT be merged if the test suite fails or if it adds code that no test
  exercises.

Rationale: other projects depend on a library's correctness. Writing tests first proves
the behavior exists and keeps the API driven by how it is used.

### III. Simplicity / YAGNI

- Build only what a current spec requires. Speculative features, extension points and
  configuration options MUST NOT be added.
- Do not add abstractions (base classes, protocols, factories, plugin systems) until there
  are at least two real use cases for them.
- Prefer, in order: python-chess, then the Python standard library, then new code.
  New runtime dependencies MUST be justified in the plan's Complexity Tracking section.
- Any complexity that breaks these rules MUST be justified in writing in the plan.

Rationale: less code means a smaller surface area to test, document and keep stable.

### IV. Stable, Typed Public API

- The public API is whatever the package's top-level `__init__` exports and documents.
  Everything else MUST be private (named with a leading underscore or placed in a
  `_internal` module).
- Every public function, class and method MUST have type hints and a docstring.
- The package MUST follow Semantic Versioning. A breaking change to the public API requires
  a MAJOR version bump and a changelog entry.

Rationale: library users need a clear, predictable contract they can upgrade against
safely.

## Technical Constraints

- Language: Python. The minimum supported version MUST be declared in `pyproject.toml` and
  MUST NOT be older than the minimum that python-chess supports.
- Runtime dependencies: `chess` (python-chess) only, unless a dependency is justified under
  Principle III.
- Packaging: a standard `pyproject.toml`-based build. No `setup.py`.
- Testing: `pytest`. Type checking: a static type checker (for example `mypy`) MUST pass on
  the public API.
- The library MUST NOT do any I/O, networking or global state mutation that a caller did
  not explicitly request.

## Development Workflow

- Every feature follows the Spec Kit flow: specify → plan → tasks → implement.
- In tasks.md, each task that writes tests MUST come before the implementation task it
  covers.
- Before merging, every change MUST pass the full test suite, type checking and a review
  against this constitution.
- Plans MUST include a Constitution Check that confirms compliance with every principle, or
  records each deviation along with its justification.

## Governance

- This constitution supersedes all other practices and guidance in the project.
- Amendments are made through `/speckit-constitution`. Each amendment MUST state its
  rationale and its version bump.
- Constitution versioning follows SemVer:
  - MAJOR: a principle is removed or redefined in a backward-incompatible way.
  - MINOR: a principle or section is added, or guidance is materially expanded.
  - PATCH: clarifications and wording fixes.
- Every plan and every code review MUST verify compliance. Unjustified complexity is
  grounds for rejection.

**Version**: 1.0.0 | **Ratified**: 2026-10-03 | **Last Amended**: 2026-10-03
