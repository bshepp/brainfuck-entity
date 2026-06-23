# Foundation — Design Spec

**Date:** 2026-06-22
**Sub-project:** 1 of 3 (Foundation → Library → Tutorials & Challenges)
**Status:** Approved for planning

## Context

The brainfuck-entity toolchain (interpreter, optimizer, validator, profiler) is
clean and fully tested (59/59 passing). The user asked to "continue development"
across four directions: expand the program library, build tutorials & challenges,
harden the toolchain, and a polish pass. These are independent sub-projects and
are being sequenced as **Foundation → Library → Tutorials & Challenges**, each
with its own spec → plan → implementation cycle.

**Foundation** is the first cycle. It folds the *polish* and *harden* directions
together: small, well-bounded changes to the existing toolchain and repo, with
no new content directories. Its purpose is to strengthen the base so later
sub-projects (new programs, tutorials) are written and tested against a safer,
correctly-documented toolchain.

Scope was deliberately narrowed during brainstorming:
- **Harden = safety only.** The single concrete gap is the missing infinite-loop
  guard in the main interpreter. Optimizer/validator feature work is explicitly
  deferred to a future cycle.
- **Guard default = generous cap.** The default run should abort cleanly on
  runaway loops rather than preserving today's hang-forever behavior.

## Goals

1. The main interpreter must not hang forever on an infinite loop in either
   batch (`execute`) or REPL (`execute_repl`) mode.
2. A runaway program aborts with a clear, actionable message and any output
   produced before the abort.
3. The default `python bf_interpreter.py prog.bf` invocation is protected by a
   high step cap; users can raise it or disable it.
4. Documented commands actually work; environmental gotchas are documented.
5. No regression: all existing programs and tests continue to pass unchanged.

## Non-Goals (out of scope for Foundation)

- Optimizer or validator feature improvements.
- Removing/fixing the validator's dead comment-detection block (`bf_validator.py`
  lines ~100–115).
- Refactoring the profiler's duplicated execute loop into shared code.
- Any new `programs/`, `tutorials/`, or `challenges/` content (later cycles).

## Design

### A. Interpreter step guard (harden)

**Current state**
- `BrainfuckInterpreter.execute()` (`interpreters/bf_interpreter.py:78`) has no
  step cap — e.g. `+[]` runs forever.
- `BrainfuckInterpreter.execute_repl()` (`:167`) likewise has no cap.
- `ProfilingInterpreter.execute()` (`tools/bf_profiler.py:18`) already caps at
  `max_steps=10_000_000` and raises a bare `RuntimeError`.
- The byte→string decode logic is duplicated three times (`execute`,
  `execute_repl`, and the profiler).

**Changes**
1. Define `class BFStepLimitExceeded(RuntimeError)` in `bf_interpreter.py`.
   Subclassing `RuntimeError` keeps it catchable specifically while remaining
   compatible with existing `except RuntimeError` handlers and the profiler's
   `test_step_limit` (which asserts `RuntimeError`).
2. Add `max_steps: int = 10_000_000` parameter to `execute()` and
   `execute_repl()`. Semantics:
   - `max_steps > 0`: raise `BFStepLimitExceeded` once the steps taken **in this
     call** exceed `max_steps`.
   - `max_steps == 0`: unlimited (no cap).
   The check goes inside the main dispatch loop, after the step counter is
   incremented. Implementation note on the counter:
   - `execute()` calls `self.reset()` first, so `self.instruction_count` starts
     at 0 and equals the steps taken this run — check `instruction_count > max_steps`.
   - `execute_repl()` deliberately preserves `self.instruction_count` across
     calls (it is only cleared by `reset()`), so the guard must measure a
     **per-call delta**: capture `start = self.instruction_count` before the
     loop and check `self.instruction_count - start > max_steps`. This prevents
     a tiny command from aborting late in a long REPL session.
3. Extract a `_decode_output(self) -> str` helper holding the existing
   try/except decode logic, and call it from `execute()` and `execute_repl()`.
   This removes duplication and — critically — lets the CLI emit partial output
   when a run aborts mid-stream.
4. Repoint the profiler's existing cap to raise `BFStepLimitExceeded` instead of
   a bare `RuntimeError` (one line). Behavior is unchanged; the existing
   profiler tests still pass because the new type *is* a `RuntimeError`. The
   profiler's separate execute loop is otherwise left intact (refactor is a
   non-goal).

### B. CLI flag handling (`main()`)

**Problem:** the current ad-hoc parser treats every non-`--` token as input data,
so a value-taking flag like `--max-steps 10000` would mis-read `10000` as the
program's input.

**Decision (Approach A — argparse for the file-run path):**
- Keep the `if sys.argv[1] == '--repl'` special-case branch as-is at the top of
  `main()`.
- Route the file-run branch through `argparse`:
  - positional `filename`
  - optional positional `input` (default `""`)
  - `--debug` (store_true)
  - `--interactive` (store_true)
  - `--max-steps N` (int, default `10_000_000`; `0` = unlimited)
- Preserve the existing auto-interactive behavior: interactive stdin is enabled
  when `--interactive` is passed **or** no `input` argument is given (matching
  current `interactive = '--interactive' in flags or not input_data`).
- On `BFStepLimitExceeded`: print any collected output first
  (`interpreter._decode_output()`), then a stderr message of the form
  `Error: exceeded 10,000,000 steps -- possible infinite loop (use --max-steps 0 for unlimited)`,
  and exit with code 1.
- The REPL needs no new handling: `execute_repl` gains the same `max_steps`
  default, and the REPL loop's existing `except Exception as e` already prints
  the error.

Rationale for argparse over hand-rolling: the new flag requires value-taking
support the current parser cannot cleanly provide, and argparse adds `--help`
and clearer errors. This is a targeted improvement to code directly in the path
of the change, not unrelated refactoring.

### C. Polish fixes

1. **Broken documented command.** `python -m unittest tests.test_interpreter`
   (in `README.md` and `CLAUDE.md`) fails because `tests/` is not a package.
   Fix: add an empty `tests/__init__.py`. Verify afterward that *both*
   `python -m unittest tests.test_interpreter` and pytest still pass.
2. **pytest plugin autoload crash.** Plain `python -m pytest` crashes during
   plugin collection due to a broken *global* `omegaconf`/`antlr4` plugin
   unrelated to this repo. This is environmental — no repo config workaround.
   Document the mitigation (`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest
   tests/ -q`) in the README test section and the MAINTENANCE.md entry.
3. **Document `--max-steps`.** Add the flag to the command lists in `README.md`
   and `CLAUDE.md`, written in BF's minimalist/zen voice.
4. **MAINTENANCE.md.** Add a `## 2026-06-22` checkup entry recording: working
   tree state, new test count, the autoload note, the doc fix, and the new
   step-guard feature.

## Files Touched

| File | Change |
|---|---|
| `interpreters/bf_interpreter.py` | `BFStepLimitExceeded`, `_decode_output()`, `max_steps` on `execute`/`execute_repl`, argparse file-run path, partial-output-on-abort |
| `interpreters/bf_profiler.py` | Raise shared `BFStepLimitExceeded` (one line) |
| `tests/test_interpreter.py` | New step-guard tests |
| `tests/__init__.py` | New empty file (makes `tests` a package) |
| `README.md` | Document `--max-steps`; add pytest autoload note |
| `CLAUDE.md` | Document `--max-steps` |
| `MAINTENANCE.md` | 2026-06-22 checkup entry |

## Testing Strategy

Test-driven for the guard — write failing tests first, then implement:

- `execute('+[]', max_steps=100)` raises `BFStepLimitExceeded`.
- `execute_repl('+[]', max_steps=100)` raises `BFStepLimitExceeded`.
- `BFStepLimitExceeded` is an instance of `RuntimeError`.
- `max_steps=0` runs a finite program to completion (no cap).
- A representative existing program runs unchanged under the default cap.

Verification commands (all must pass):
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q`
- `python -m unittest tests.test_interpreter`
- Manual: `python interpreters/bf_interpreter.py programs/hello-world/hello.bf`
  still prints `Hello World!` (default cap does not regress normal programs).

## Risks & Mitigations

- **Risk:** adding `tests/__init__.py` changes pytest import semantics.
  **Mitigation:** verify the full suite under pytest after adding it; the test
  file already manipulates `sys.path`, so package status is compatible.
- **Risk:** argparse changes the CLI usage/error text.
  **Mitigation:** preserve the `--repl` branch and the auto-interactive rule
  exactly; only the file-run branch changes. Manual smoke test of a normal run.
- **Risk:** default cap breaks a legitimately long program.
  **Mitigation:** cap is 10,000,000 steps (matches profiler); all bundled
  programs finish in well under that. `--max-steps 0` provides an escape hatch.
