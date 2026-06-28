# Tutorials & Challenges — Design Spec

**Date:** 2026-06-23
**Sub-project:** 3 of 3 (Foundation ✅ → Library ✅ → Tutorials & Challenges)
**Status:** Built autonomously for review — NOT user-approved before implementation

## Important: autonomous build

The user authorized continuing through the planned sequence unattended ("continue
as long as you can ... we can reverse things if necessary"), but was asleep and
did not review a design for this sub-project. To respect the normal
brainstorm→approve gate, this sub-project is built on the `tutorials` branch and
**pushed for review, not merged to master**. All design decisions below were made
autonomously and are open to revision. Every embedded BF snippet is verified
against the interpreter; the rest is markdown content (low risk, fully reversible).

## Context

The README's "Planned / Future Work" lists `tutorials/` (progressive learning
materials) and `challenges/` (code-golf / optimization challenges). Foundation
hardened the interpreter (`--max-steps`) and Library added 10 tested programs.
This sub-project delivers both planned directories, teaching from the now-verified
program library and exercising the existing toolchain (interpreter, validator,
profiler, optimizer).

## Goals

1. `tutorials/`: a progressive, self-contained lesson series taking a reader from
   the tape model to writing their own loops/IO/art, each lesson grounded in real
   programs already in `programs/`.
2. `challenges/`: a set of self-directed exercises with clear specs, exact
   expected outputs, and golf/▶profiling guidance — problem statements only
   (no solutions committed), so they remain exercises.
3. No code changes; the test suite stays at 76 passing. Any BF shown is verified.

## Non-Goals

- No interpreter/optimizer/validator/program changes.
- No automated grading harness for challenges (out of scope; challenges reference
  the existing tools for self-checking).
- No solutions committed for challenges.

## Design

### `tutorials/` (markdown lessons + index)

- `tutorials/README.md` — index, how to run examples, learning path.
- `tutorials/01-the-tape.md` — the tape, the pointer, the 8 commands; `>`/`<`.
- `tutorials/02-output.md` — `+`/`-`/`.`, ASCII, building one character; refs
  `programs/hello-world/simple_hello.bf`.
- `tutorials/03-loops.md` — `[`/`]`, the clear loop `[-]`, the multiplication
  loop `[->+++<]`; refs `digits.bf`, `alphabet.bf`, `hello.bf`.
- `tutorials/04-input.md` — `,`, the echo loop `,[.,]`, single-digit ASCII math;
  refs `add_two_numbers.bf`, `multiply.bf`, `subtract.bf`.
- `tutorials/05-conditionals.md` — loops as if/branch, flags and the if/else
  pattern; refs `even_or_odd.bf`, `secret_knock.bf`, `guess_the_number.bf`.
- `tutorials/06-art-and-zen.md` — nested loops and ASCII art, fixed-text via a
  base-build loop; refs `triangle.bf`, `box.bf`, `mandala.bf`, `less_is_more.bf`.

Each lesson: short concept explanation, a tiny verified snippet or a reference to
a real program with a walk-through, a "try it" command using the interpreter, and
a one-line pointer to the next lesson. Tutorial prose must avoid stray BF
characters only inside fenced ```text``` blocks that are meant to be run; ordinary
markdown prose may use punctuation freely (it is never fed to the interpreter).

### `challenges/` (markdown prompts + index)

- `challenges/README.md` — rules: solve in BF, validate with
  `tools/bf_validator.py`, measure with `tools/bf_profiler.py`, golf for fewer
  instructions; how to self-check against the stated expected output.
- `challenges/01-initials.md` — print two uppercase initials + newline.
- `challenges/02-sum-of-three.md` — read three digits, print their sum (sum ≤ 9).
- `challenges/03-countdown.md` — print `9` down to `0` then a newline.
- `challenges/04-shout.md` — read lowercase letters, echo them uppercased (offset
  by 32) until EOF.
- `challenges/05-rectangle.md` — print a 3×5 rectangle of `#` (art / nested loops).

Each challenge: title, difficulty, problem statement, input/output contract with
an exact example, constraints (single-digit where relevant), and self-check +
golf hints. No solutions committed.

## Verification

- Any BF snippet shown as runnable is verified against the interpreter before
  inclusion (scratchpad harness).
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q` stays at 76 passing
  (no code touched).
- README "Planned / Future Work" and CLAUDE.md structure updated to reflect that
  `tutorials/` and `challenges/` now exist.

## Files Touched

| File | Change |
|---|---|
| `tutorials/README.md` + 6 lesson files | new |
| `challenges/README.md` + 5 challenge files | new |
| `README.md`, `CLAUDE.md` | reflect new dirs; move tutorials/challenges out of "Planned" |
| `MAINTENANCE.md` | 2026-06-23 entry for sub-project 3 (review status) |
| `docs/superpowers/specs/2026-06-23-tutorials-design.md` | this spec |

## Risks & Mitigations

- **Risk:** a tutorial shows incorrect BF.
  **Mitigation:** every runnable snippet is interpreter-verified; lessons prefer
  referencing already-tested programs.
- **Risk:** design not user-approved.
  **Mitigation:** delivered on a branch, pushed for review, not merged; trivially
  reversible.
