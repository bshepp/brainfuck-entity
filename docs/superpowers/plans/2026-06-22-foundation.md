# Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the brainfuck interpreter an infinite-loop step guard, wire it through a robust CLI, and fix documented/test gaps — without touching program/tutorial content.

**Architecture:** Add a `BFStepLimitExceeded(RuntimeError)` exception and a `max_steps` budget to `BrainfuckInterpreter.execute()` and `execute_repl()`, extract the duplicated output-decode into a `_decode_output()` helper so aborts can emit partial output, point the profiler at the shared exception, replace the fragile hand-rolled CLI parser with `argparse`, and apply small polish fixes (package the tests dir, document the new flag and the pytest autoload workaround).

**Tech Stack:** Python 3.6+ standard library only (`argparse` is stdlib). Tests via `unittest` (run with `pytest`).

## Global Constraints

- Python `>=3.6`; standard library only — no third-party dependencies.
- Preserve existing code style: type hints on public methods, module/function docstrings, 4-space indent.
- Default step cap is exactly `10_000_000`; `max_steps=0` means unlimited. (Matches `tools/bf_profiler.py`.)
- The `--repl` CLI branch and the auto-interactive rule (`interactive = --interactive OR no input given`) must behave exactly as today.
- No new `programs/`, `tutorials/`, or `challenges/` content. No optimizer/validator feature changes.
- Branch: `foundation` (already created). Commit after each task.
- Full-suite verification command (the global pytest plugin autoload is broken on this machine):
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q`

---

### Task 1: Step guard + decode helper in `execute()`

**Files:**
- Modify: `interpreters/bf_interpreter.py` (add exception class near top; add `_decode_output` method; add `max_steps` param + guard to `execute()`; use helper for decode)
- Test: `tests/test_interpreter.py` (new `TestStepGuard` class)

**Interfaces:**
- Produces: `BFStepLimitExceeded(RuntimeError)`; `BrainfuckInterpreter._decode_output(self) -> str`; `BrainfuckInterpreter.execute(self, code, input_data="", debug=False, max_steps=10_000_000) -> str` raising `BFStepLimitExceeded` when the run exceeds `max_steps` (and `max_steps != 0`).

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_interpreter.py` (after the existing `TestEdgeCases` class, before `TestOptimizer`). Also update the import on line 12:

```python
from interpreters.bf_interpreter import BrainfuckInterpreter, BFStepLimitExceeded
```

```python
class TestStepGuard(unittest.TestCase):
    """Test the infinite-loop step guard on execute()."""

    def test_execute_step_limit_raises(self):
        interp = BrainfuckInterpreter()
        with self.assertRaises(BFStepLimitExceeded):
            interp.execute('+[]', max_steps=100)

    def test_step_limit_is_runtime_error(self):
        # Subclass of RuntimeError so existing `except RuntimeError` keeps working.
        self.assertTrue(issubclass(BFStepLimitExceeded, RuntimeError))

    def test_execute_unlimited_with_zero(self):
        # max_steps=0 disables the cap; a finite program still completes.
        interp = BrainfuckInterpreter()
        result = interp.execute('+' * 65 + '.', max_steps=0)
        self.assertEqual(result, 'A')

    def test_default_cap_does_not_break_normal_program(self):
        interp = BrainfuckInterpreter()
        result = interp.execute('+' * 66 + '.')  # 'B', far under 10M steps
        self.assertEqual(result, 'B')
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_interpreter.py::TestStepGuard -v`
Expected: ImportError / collection error — `cannot import name 'BFStepLimitExceeded'`.

- [ ] **Step 3: Add the exception class**

In `interpreters/bf_interpreter.py`, after the imports (after `from typing import List, Optional`, before `class BrainfuckInterpreter`):

```python


class BFStepLimitExceeded(RuntimeError):
    """Raised when a program exceeds its step budget (likely an infinite loop).

    Subclasses RuntimeError so callers using `except RuntimeError` still catch it.
    """
    pass
```

- [ ] **Step 4: Add the `_decode_output` helper**

In `interpreters/bf_interpreter.py`, add this method to `BrainfuckInterpreter` (place it just before `get_memory_dump`):

```python
    def _decode_output(self) -> str:
        """Decode collected output bytes to a string, with a printable-hex fallback."""
        try:
            return bytes(self.output).decode('utf-8')
        except UnicodeDecodeError:
            return ''.join(
                chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in self.output
            )
```

- [ ] **Step 5: Add `max_steps` to `execute()` and the in-loop guard**

Change the `execute` signature from:

```python
    def execute(self, code: str, input_data: str = "", debug: bool = False) -> str:
```

to:

```python
    def execute(self, code: str, input_data: str = "", debug: bool = False,
                max_steps: int = 10_000_000) -> str:
```

Then, inside the `while` loop, immediately after `self.instruction_count += 1`, insert the guard. The block currently reads:

```python
            command = program[self.instruction_pointer]
            self.instruction_count += 1
            
            if debug and self.instruction_count <= 100:  # Limit debug output
```

Change it to:

```python
            command = program[self.instruction_pointer]
            self.instruction_count += 1

            if max_steps and self.instruction_count > max_steps:
                raise BFStepLimitExceeded(
                    f"exceeded {max_steps:,} steps -- possible infinite loop"
                )

            if debug and self.instruction_count <= 100:  # Limit debug output
```

- [ ] **Step 6: Use the helper for `execute()`'s decode**

Replace the decode block near the end of `execute()`:

```python
        # Convert output to string
        try:
            result = bytes(self.output).decode('utf-8')
        except UnicodeDecodeError:
            # If decode fails, represent as byte values
            result = ''.join(chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in self.output)
```

with:

```python
        # Convert output to string
        result = self._decode_output()
```

- [ ] **Step 7: Run the tests to verify they pass**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_interpreter.py::TestStepGuard -v`
Expected: 4 passed.

- [ ] **Step 8: Run the full suite (no regression)**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q`
Expected: `63 passed` (59 existing + 4 new).

- [ ] **Step 9: Commit**

```bash
git add interpreters/bf_interpreter.py tests/test_interpreter.py
git commit -m "Add infinite-loop step guard to execute()

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Per-call step guard in `execute_repl()`

**Files:**
- Modify: `interpreters/bf_interpreter.py` (`execute_repl`: add `max_steps` param, per-call delta guard, use decode helper)
- Test: `tests/test_interpreter.py` (extend `TestStepGuard`)

**Interfaces:**
- Consumes: `BFStepLimitExceeded`, `_decode_output` (Task 1).
- Produces: `BrainfuckInterpreter.execute_repl(self, code, input_data="", max_steps=10_000_000) -> str`. The cap counts steps **for the current call only** (REPL preserves `instruction_count` across calls).

- [ ] **Step 1: Write the failing tests**

Add these two methods to the `TestStepGuard` class in `tests/test_interpreter.py`:

```python
    def test_repl_step_limit_raises(self):
        interp = BrainfuckInterpreter()
        with self.assertRaises(BFStepLimitExceeded):
            interp.execute_repl('+[]', max_steps=100)

    def test_repl_guard_is_per_call(self):
        # instruction_count accumulates across REPL calls; the cap must be
        # measured per-call, so a tiny command after a large one must not abort.
        interp = BrainfuckInterpreter()
        interp.execute_repl('+' * 100)            # ~100 cumulative steps
        result = interp.execute_repl('+.', max_steps=50)  # only 2 steps this call
        self.assertEqual(interp.memory[0], 101 % 256)
        self.assertEqual(result, chr(101))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest "tests/test_interpreter.py::TestStepGuard::test_repl_step_limit_raises" "tests/test_interpreter.py::TestStepGuard::test_repl_guard_is_per_call" -v`
Expected: `test_repl_step_limit_raises` hangs/fails (no guard yet) — if it hangs, that itself confirms the missing guard; Ctrl-C and proceed. `test_repl_guard_is_per_call` fails on the unexpected `max_steps` keyword.

(If the hang is inconvenient, temporarily skip Step 2 for the raises-test and rely on Step 5's full run; the per-call test still fails fast on the bad keyword.)

- [ ] **Step 3: Add `max_steps` + per-call guard to `execute_repl()`**

Change the `execute_repl` signature from:

```python
    def execute_repl(self, code: str, input_data: str = "") -> str:
```

to:

```python
    def execute_repl(self, code: str, input_data: str = "", max_steps: int = 10_000_000) -> str:
```

Just before its `while` loop — the lines currently read:

```python
        self.instruction_pointer = 0
        self.output = []
        
        while self.instruction_pointer < len(program):
            command = program[self.instruction_pointer]
            self.instruction_count += 1
```

Change them to:

```python
        self.instruction_pointer = 0
        self.output = []
        start_count = self.instruction_count

        while self.instruction_pointer < len(program):
            command = program[self.instruction_pointer]
            self.instruction_count += 1

            if max_steps and self.instruction_count - start_count > max_steps:
                raise BFStepLimitExceeded(
                    f"exceeded {max_steps:,} steps -- possible infinite loop"
                )
```

- [ ] **Step 4: Use the helper for `execute_repl()`'s decode**

Replace the decode block at the end of `execute_repl()`:

```python
        try:
            return bytes(self.output).decode('utf-8')
        except UnicodeDecodeError:
            return ''.join(chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in self.output)
```

with:

```python
        return self._decode_output()
```

- [ ] **Step 5: Run the full suite**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q`
Expected: `65 passed` (63 + 2 new).

- [ ] **Step 6: Commit**

```bash
git add interpreters/bf_interpreter.py tests/test_interpreter.py
git commit -m "Add per-call step guard to execute_repl()

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Profiler adopts the shared exception

**Files:**
- Modify: `tools/bf_profiler.py` (import + raise `BFStepLimitExceeded` instead of bare `RuntimeError`)
- Test: `tests/test_interpreter.py` (extend `TestProfiler`)

**Interfaces:**
- Consumes: `BFStepLimitExceeded` (Task 1).
- Behavior unchanged: `ProfilingInterpreter.execute(..., max_steps=...)` raises on exceed; `main()` still catches it via its existing `except RuntimeError`.

- [ ] **Step 1: Write the failing test**

Add this method to the `TestProfiler` class in `tests/test_interpreter.py`:

```python
    def test_step_limit_raises_bf_exception(self):
        from interpreters.bf_interpreter import BFStepLimitExceeded
        interp = ProfilingInterpreter()
        with self.assertRaises(BFStepLimitExceeded):
            interp.execute('+[]', max_steps=100)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest "tests/test_interpreter.py::TestProfiler::test_step_limit_raises_bf_exception" -v`
Expected: FAIL — profiler raises bare `RuntimeError`, not `BFStepLimitExceeded`.

- [ ] **Step 3: Update the profiler import**

In `tools/bf_profiler.py`, change:

```python
from interpreters.bf_interpreter import BrainfuckInterpreter
```

to:

```python
from interpreters.bf_interpreter import BrainfuckInterpreter, BFStepLimitExceeded
```

- [ ] **Step 4: Raise the shared exception**

In `tools/bf_profiler.py`, the step-limit raise currently reads:

```python
            if self.instruction_count > max_steps:
                self.elapsed = time.perf_counter() - start_time
                raise RuntimeError(
                    f"Exceeded {max_steps:,} steps -- possible infinite loop"
                )
```

Change the `raise` to:

```python
            if self.instruction_count > max_steps:
                self.elapsed = time.perf_counter() - start_time
                raise BFStepLimitExceeded(
                    f"Exceeded {max_steps:,} steps -- possible infinite loop"
                )
```

(`main()`'s `except RuntimeError` on line ~155 still catches it, since `BFStepLimitExceeded` is a `RuntimeError`.)

- [ ] **Step 5: Run the full suite**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q`
Expected: `66 passed` (65 + 1 new). The existing `TestProfiler::test_step_limit` (which asserts `RuntimeError`) still passes.

- [ ] **Step 6: Commit**

```bash
git add tools/bf_profiler.py tests/test_interpreter.py
git commit -m "Profiler raises shared BFStepLimitExceeded

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: argparse CLI + `--max-steps` + partial output on abort

**Files:**
- Modify: `interpreters/bf_interpreter.py` (`import argparse`; rewrite the file-run branch of `main()`; update the no-args usage text)
- Verification: manual CLI runs (the test suite covers guard behavior at the class level; this task wires flags and the abort message).

**Interfaces:**
- Consumes: `execute(..., max_steps=...)`, `BFStepLimitExceeded`, `_decode_output` (Tasks 1).
- Produces: CLI flags `filename`, optional `input`, `--debug`, `--interactive`, `--max-steps N` (default `10_000_000`, `0` = unlimited). On abort: prints partial output to stdout, an `Error:` line to stderr, exits 1.

- [ ] **Step 1: Add the argparse import**

In `interpreters/bf_interpreter.py`, change the import block:

```python
import sys
from typing import List, Optional
```

to:

```python
import argparse
import sys
from typing import List, Optional
```

- [ ] **Step 2: Update the no-args usage text**

In `main()`, the top guard currently reads:

```python
    if len(sys.argv) < 2:
        print("Usage: python bf_interpreter.py <program.bf> [input] [--debug] [--interactive]")
        print("   or: python bf_interpreter.py --repl")
        sys.exit(1)
```

Change the first `print` to include the new flag:

```python
    if len(sys.argv) < 2:
        print("Usage: python bf_interpreter.py <program.bf> [input] [--debug] [--interactive] [--max-steps N]")
        print("   or: python bf_interpreter.py --repl")
        sys.exit(1)
```

- [ ] **Step 3: Rewrite the file-run branch**

In `main()`, replace the entire `else:` branch (everything from `else:` through the final `sys.exit(1)` of the `except Exception` handler) with:

```python
    else:
        parser = argparse.ArgumentParser(
            prog='bf_interpreter.py',
            description='Run a brainfuck program.',
        )
        parser.add_argument('filename', help='path to the .bf source file')
        parser.add_argument('input', nargs='?', default='',
                            help='optional input string for the program')
        parser.add_argument('--debug', action='store_true',
                            help='print execution trace and final memory state')
        parser.add_argument('--interactive', action='store_true',
                            help='read stdin when the input buffer is exhausted')
        parser.add_argument('--max-steps', type=int, default=10_000_000, metavar='N',
                            help='abort after N steps (0 = unlimited); default 10,000,000')
        opts = parser.parse_args()

        # Auto-interactive when no input string is supplied (preserves prior behavior).
        interactive = opts.interactive or not opts.input
        interpreter = BrainfuckInterpreter(interactive=interactive)

        try:
            with open(opts.filename, 'r') as f:
                code = f.read()

            result = interpreter.execute(code, opts.input, debug=opts.debug,
                                         max_steps=opts.max_steps)

            if result:
                print(result, end='')

            if opts.debug:
                print(f"\nFinal memory state:")
                print(interpreter.visualize_memory())

        except FileNotFoundError:
            print(f"Error: File '{opts.filename}' not found")
            sys.exit(1)
        except BFStepLimitExceeded as e:
            # Emit whatever the program produced before the abort, then report.
            partial = interpreter._decode_output()
            if partial:
                print(partial, end='')
            print(f"\nError: {e} (use --max-steps 0 for unlimited)", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
```

- [ ] **Step 4: Verify the full suite still passes**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q`
Expected: `66 passed` (no test changes this task; confirms no syntax/import breakage).

- [ ] **Step 5: Manual CLI verification — normal run unchanged**

Run: `python interpreters/bf_interpreter.py programs/hello-world/hello.bf`
Expected: `Hello World!` followed by a newline.

- [ ] **Step 6: Manual CLI verification — abort path**

Run: `python interpreters/bf_interpreter.py programs/hello-world/hello.bf --max-steps 5 ; echo "exit=$?"`
Expected: no program output (the first `.` has not run within 5 steps), a stderr line like
`Error: exceeded 5 steps -- possible infinite loop (use --max-steps 0 for unlimited)`, then `exit=1`.

- [ ] **Step 7: Manual CLI verification — unlimited + help**

Run: `python interpreters/bf_interpreter.py programs/hello-world/hello.bf --max-steps 0`
Expected: `Hello World!` + newline (cap disabled).

Run: `python interpreters/bf_interpreter.py --help`
Expected: argparse help text listing `filename`, `input`, `--debug`, `--interactive`, `--max-steps`.

- [ ] **Step 8: Commit**

```bash
git add interpreters/bf_interpreter.py
git commit -m "Route interpreter CLI through argparse; add --max-steps

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Polish — package tests dir, document flag + autoload workaround, log checkup

**Files:**
- Create: `tests/__init__.py`
- Modify: `README.md` (test section + interpreter usage), `CLAUDE.md` (running programs), `MAINTENANCE.md` (new checkup entry)

**Interfaces:** none (docs + packaging only).

- [ ] **Step 1: Create `tests/__init__.py`**

Create `tests/__init__.py` with this single line:

```python
"""Test package for the brainfuck-entity toolchain."""
```

- [ ] **Step 2: Verify both runners now work**

Run: `python -m unittest tests.test_interpreter -v`
Expected: `Ran 66 tests` ... `OK` (the previously-broken documented command now works).

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q`
Expected: `66 passed` (packaging the dir does not change discovery).

- [ ] **Step 3: Update README — test section**

In `README.md`, the test section currently reads:

```markdown
### Run Tests
```bash
python -m pytest tests/ -v
```
```

Replace it with:

```markdown
### Run Tests
```bash
python -m pytest tests/ -v
# or, equivalently:
python -m unittest tests.test_interpreter -v
```

> If `pytest` aborts during plugin collection due to an unrelated global plugin
> on your machine, disable plugin autoload:
> `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q`
```

- [ ] **Step 4: Update README — interpreter usage**

In `README.md`, the "Running Your First Program" block currently ends with the interactive-stdin example. After that `python interpreters/bf_interpreter.py programs/games/guess_the_number.bf` line (still inside the same fenced ```bash block), add:

```bash
# Cap execution to guard against infinite loops (0 = unlimited; default 10,000,000)
python interpreters/bf_interpreter.py programs/hello-world/hello.bf --max-steps 100000
```

- [ ] **Step 5: Update CLAUDE.md — running programs**

In `CLAUDE.md`, the "Running Brainfuck Programs" fenced block currently ends with the `--repl` example. Before the closing ``` of that block, add:

```bash
# Limit steps to abort runaway/infinite programs (0 = unlimited)
python interpreters/bf_interpreter.py programs/hello-world/hello.bf --max-steps 100000
```

- [ ] **Step 6: Add the MAINTENANCE.md checkup entry**

In `MAINTENANCE.md`, insert this entry directly under the `Periodic project checkups...` intro line and above the existing `## 2026-05-22` heading:

```markdown
## 2026-06-22

- Working tree: clean before work; Foundation sub-project implemented on branch `foundation`.
- Tests: 66 / 66 passing (59 prior + 7 new step-guard tests). Run with
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q`.
- Hardening: added `BFStepLimitExceeded` and a `max_steps` budget (default
  10,000,000; `0` = unlimited) to `execute()` and `execute_repl()`; profiler now
  raises the shared exception. The interpreter CLI gained `--max-steps N` and was
  moved onto `argparse`; runaway programs now abort with partial output + a
  stderr error instead of hanging.
- Fixes: added `tests/__init__.py` so the documented
  `python -m unittest tests.test_interpreter` command works; documented the
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` workaround for the unrelated global pytest
  plugin crash on this machine.

```

(Confirm the test count in the entry matches the observed `pytest` output from Step 2; it should be 66.)

- [ ] **Step 7: Final full-suite verification**

Run: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q`
Expected: `66 passed`.

- [ ] **Step 8: Commit**

```bash
git add tests/__init__.py README.md CLAUDE.md MAINTENANCE.md
git commit -m "Polish: package tests dir, document --max-steps and pytest workaround

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**Spec coverage:**
- Step guard on `execute()` → Task 1. ✓
- Per-call guard on `execute_repl()` → Task 2. ✓
- `BFStepLimitExceeded(RuntimeError)` + `_decode_output()` helper → Task 1. ✓
- Profiler adopts shared exception → Task 3. ✓
- argparse CLI + `--max-steps` + partial-output-on-abort → Task 4. ✓
- `tests/__init__.py` (fix broken unittest command) → Task 5. ✓
- Document `--max-steps` (README + CLAUDE.md) → Task 5. ✓
- pytest autoload workaround documented → Task 5 (README) + MAINTENANCE.md. ✓
- MAINTENANCE.md 2026-06-22 entry → Task 5. ✓
- Default cap 10,000,000 / `0` = unlimited; `--repl` and auto-interactive unchanged → Tasks 1/2/4. ✓
- Non-goals (optimizer/validator features, profiler loop refactor, validator dead block) → not touched. ✓

**Placeholder scan:** No TBD/TODO/"handle edge cases"; every code step shows full code; every command has expected output. ✓

**Type consistency:** `BFStepLimitExceeded`, `_decode_output`, and the `max_steps` parameter name/default (`10_000_000`) are used identically across Tasks 1–4. Test counts chain consistently: 59 → 63 (Task 1, +4) → 65 (Task 2, +2) → 66 (Task 3, +1) → 66 (Tasks 4–5, +0). ✓
