# Maintenance Log

Periodic project checkups: state of the tree, tests, docs, and repo metadata.

## 2026-06-23

- Library sub-project (2 of 3): added 10 new BF programs, ~2 per category, each
  with an exact-output test. Tests: 76 / 76 passing (66 prior + 10 new). Run with
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -q`.
  - hello-world: `digits.bf`, `alphabet.bf`
  - mathematical: `multiply.bf`, `subtract.bf` (single-digit I/O)
  - games: `even_or_odd.bf`, `secret_knock.bf`
  - art: `triangle.bf`, `box.bf`
  - philosophy: `less_is_more.bf`, `empty_is_full.bf`
- Substitution from the spec: `secret_knock.bf` replaced the planned
  `guess_higher_lower.bf` (a correct three-way higher/lower comparison in raw BF
  was too brittle to verify unattended). Same category and testable shape; like
  the existing `guess_the_number.bf`, it loops until the secret digit is entered.
- All BF authored and verified against the interpreter before commit; spec and
  plan under `docs/superpowers/`. Foundation step guard backstops the interactive
  programs against runaway input.
- Tutorials & Challenges (sub-project 3 of 3): added `tutorials/` (six progressive
  lessons + index) and `challenges/` (five exercises + index), teaching from the
  verified program library and exercising the existing tools. Every runnable BF
  snippet was interpreter-verified; no code changed (suite stays at 76). Built
  unattended on branch `tutorials` and pushed for review — NOT merged to master,
  because the design was not user-approved first (see
  `docs/superpowers/specs/2026-06-23-tutorials-design.md`). Reversible.

## 2026-06-22

- Working tree: clean before work; Foundation sub-project implemented on branch `foundation`, then merged to `master` (fast-forward) and the branch deleted.
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

## 2026-05-22

- Working tree: clean; `master` up to date with `origin/master`.
- Tests: 59 / 59 passing (`python -m pytest tests/ -q`).
- Documentation: `README.md` and `CLAUDE.md` reviewed; file/directory layout matches reality (`interpreters/`, `programs/{hello-world,mathematical,games,art,philosophy}/`, `tools/`, `tests/`, `philosophy/`). No drift to correct.
- GitHub repo metadata:
  - Description already present.
  - Topics added (none previously set): `brainfuck`, `interpreter`, `esoteric-language`, `python`, `optimizer`, `repl`, `computational-minimalism`.
