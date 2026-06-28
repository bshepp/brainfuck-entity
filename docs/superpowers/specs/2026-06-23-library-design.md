# Library — Design Spec

**Date:** 2026-06-23
**Sub-project:** 2 of 3 (Foundation ✅ → Library → Tutorials & Challenges)
**Status:** Approved for planning

## Context

Foundation (sub-project 1) is merged to `master`: the interpreter now has a
step guard, an argparse CLI with `--max-steps`, and 66 passing tests. The
program library is still small — 7 programs across five categories:

- `hello-world/`: `hello.bf`, `simple_hello.bf`
- `mathematical/`: `add_two_numbers.bf`
- `games/`: `guess_the_number.bf`
- `art/`: `simple_star.bf`, `mandala.bf`
- `philosophy/`: `zen_koan.bf`

Each program has an exact-output test in `tests/test_interpreter.py`
(`TestProgramOutputs`), run via the `_run_file(rel_path, input_data)` helper.

**Library** expands this with ~10 new programs, balanced ~2 per category, each
hand-crafted in the existing commented multiplication-loop style and verified by
an exact-output test (TDD). The programs are also intended to serve as worked
examples for the Tutorials & Challenges sub-project that follows.

## Goals

1. Add 10 new, byte-correct BF programs across the five existing categories.
2. Each program is deterministic and covered by an exact-output test (input-driven
   programs covered for fixed test inputs).
3. Programs follow the existing aesthetic: short, elegant, well-commented with the
   tape layout, biased toward loop/algorithmic structure over long fixed text.
4. No regressions; the full suite grows from 66 to 76 passing tests.

## Non-Goals (out of scope for Library)

- Optimizer or validator changes.
- Multi-digit number input/output (deliberately avoided — it is where byte-level
  bugs multiply; all numeric programs operate on single digits).
- Randomness or wall-clock-dependent behavior (not deterministically testable).
- New category directories (balance is across the five existing categories).
- Tutorials and challenges (sub-project 3).

## Authoring Approach

Hand-craft each program in the existing style, test-driven: write the
exact-output test first (it is the correctness gate), then construct the BF using
the project's established patterns (multiplication loops `[->+++<]`, clear loops
`[-]`, move/copy patterns) and iterate against the interpreter until the test
passes. Rejected alternatives: mechanically generating fixed-text programs (ugly,
off-brand, adds a generator tool) and curating public BF programs (provenance
concerns, against the project ethos).

## The Programs

All `.bf` files go in their existing category directory. Outputs are exact,
including trailing newlines where shown. Input-driven programs read ASCII digit
bytes via `,` (matching `add_two_numbers.bf` / `guess_the_number.bf`); after the
test input is consumed, their control flow must terminate without relying on
further input (a `,` at EOF yields 0 in non-interactive execution).

### hello-world/

1. **`alphabet.bf`** — print `A`–`Z` using a 26-iteration loop (a counter cell and
   a printable cell starting at `A`=65), then a newline.
   - Output: `ABCDEFGHIJKLMNOPQRSTUVWXYZ\n`

2. **`digits.bf`** — print `0`–`9` using a 10-iteration loop (printable cell
   starting at `0`=48), then a newline.
   - Output: `0123456789\n`

### mathematical/

3. **`multiply.bf`** — read two ASCII digit bytes, compute the product of their
   numeric values, print the product as one ASCII digit. Specified only for
   products ≤ 9; behavior for larger products is unspecified and not tested.
   - `"23"` → `6`; `"14"` → `4`; `"31"` → `3`

4. **`subtract.bf`** — read two ASCII digit bytes a, b (assume a ≥ b), print
   a − b as one ASCII digit. (The ASCII offsets cancel in the subtraction; add 48
   back for output.)
   - `"73"` → `4`; `"90"` → `9`; `"55"` → `0`

### games/

5. **`guess_higher_lower.bf`** — secret digit is `5`. Repeatedly read a guess
   digit; print `H` if the guess is below 5, `L` if above 5, `Y` if equal; stop
   after printing `Y`. No separators between letters.
   - `"5"` → `Y`; `"275"` → `HLY`

6. **`even_or_odd.bf`** — read one ASCII digit, print `E` if its numeric value is
   even, `O` if odd.
   - `"4"` → `E`; `"7"` → `O`; `"0"` → `E`

### art/

7. **`triangle.bf`** — print a 5-row left-aligned right triangle of `*`, newline
   after each row (nested loops: outer row counter, inner star counter).
   - Output: `*\n**\n***\n****\n*****\n`

8. **`box.bf`** — print a 4×4 bordered box (top/bottom solid, middle rows are
   star–space–space–star), newline after each row.
   - Output: `****\n*  *\n*  *\n****\n`

### philosophy/

9. **`less_is_more.bf`** — print a single koan line.
   - Output: `less is more\n`

10. **`empty_is_full.bf`** — print a single koan line.
    - Output: `empty is full\n`

## Testing

Extend `TestProgramOutputs` in `tests/test_interpreter.py` with one test method
per program, asserting exact output via `_run_file`. Input-driven programs assert
2–3 input/output cases within their single method. Expected new methods:

| Method | Program | Assertions |
|---|---|---|
| `test_alphabet` | `alphabet.bf` | `== 'ABCDEFGHIJKLMNOPQRSTUVWXYZ\n'` |
| `test_digits` | `digits.bf` | `== '0123456789\n'` |
| `test_multiply` | `multiply.bf` | `'23'→'6'`, `'14'→'4'`, `'31'→'3'` |
| `test_subtract` | `subtract.bf` | `'73'→'4'`, `'90'→'9'`, `'55'→'0'` |
| `test_guess_higher_lower` | `guess_higher_lower.bf` | `'5'→'Y'`, `'275'→'HLY'` |
| `test_even_or_odd` | `even_or_odd.bf` | `'4'→'E'`, `'7'→'O'`, `'0'→'E'` |
| `test_triangle` | `triangle.bf` | `== '*\n**\n***\n****\n*****\n'` |
| `test_box` | `box.bf` | `== '****\n*  *\n*  *\n****\n'` |
| `test_less_is_more` | `less_is_more.bf` | `== 'less is more\n'` |
| `test_empty_is_full` | `empty_is_full.bf` | `== 'empty is full\n'` |

Final suite: 66 → 76 passing (10 new test methods). Run with
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q`.

## Files Touched

| File | Change |
|---|---|
| `programs/hello-world/alphabet.bf`, `digits.bf` | new |
| `programs/mathematical/multiply.bf`, `subtract.bf` | new |
| `programs/games/guess_higher_lower.bf`, `even_or_odd.bf` | new |
| `programs/art/triangle.bf`, `box.bf` | new |
| `programs/philosophy/less_is_more.bf`, `empty_is_full.bf` | new |
| `tests/test_interpreter.py` | 10 new `TestProgramOutputs` methods |
| `README.md`, `CLAUDE.md` | update program-structure notes / example lists |
| `MAINTENANCE.md` | 2026-06-23 entry logging the expansion |

## Implementation Notes

- Subagent-driven, **one program per task**, TDD with the exact-output test as the
  gate. Construct the BF, run it through the interpreter, iterate until the test is
  green; commit per program.
- Keep each program small and commented with its tape layout, matching the
  existing files. Prefer loop/algorithmic structure over long literal text.
- Verify the whole suite under the autoload-disabled pytest command after each
  task and once at the end.

## Risks & Mitigations

- **Risk:** byte-level errors in hand-written BF.
  **Mitigation:** TDD — the exact-output test is written first and gates each
  program; per-program tasks keep failures isolated.
- **Risk:** input-driven programs hanging or mis-reading at EOF.
  **Mitigation:** control flow terminates on the program's own logic (e.g. the
  guess loop stops on a hit), not on EOF; test inputs are chosen to reach a stop
  state.
- **Risk:** `multiply.bf` misused with products > 9.
  **Mitigation:** specified and tested only for products ≤ 9; documented as a
  single-digit-result program in its comments.
