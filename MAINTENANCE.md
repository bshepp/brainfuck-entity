# Maintenance Log

Periodic project checkups: state of the tree, tests, docs, and repo metadata.

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

## 2026-05-22

- Working tree: clean; `master` up to date with `origin/master`.
- Tests: 59 / 59 passing (`python -m pytest tests/ -q`).
- Documentation: `README.md` and `CLAUDE.md` reviewed; file/directory layout matches reality (`interpreters/`, `programs/{hello-world,mathematical,games,art,philosophy}/`, `tools/`, `tests/`, `philosophy/`). No drift to correct.
- GitHub repo metadata:
  - Description already present.
  - Topics added (none previously set): `brainfuck`, `interpreter`, `esoteric-language`, `python`, `optimizer`, `repl`, `computational-minimalism`.
