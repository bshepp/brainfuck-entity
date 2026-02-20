#!/usr/bin/env python3
"""
Brainfuck Syntax Validator
Checks BF programs for structural correctness and common issues.
"""

import sys
import os

BF_CHARS = set('><+-.,[]')


def validate(code: str, filename: str = "<stdin>") -> list:
    """
    Validate brainfuck source code and return a list of diagnostic messages.
    Each message is a dict with keys: level ("error" | "warning"), pos, line, message.
    """
    diagnostics = []

    # Map raw character positions to line numbers
    lines = code.split('\n')
    bf_positions = []
    for line_no, line in enumerate(lines, 1):
        for col, ch in enumerate(line):
            if ch in BF_CHARS:
                bf_positions.append((ch, line_no, col + 1))

    # Check bracket matching with position tracking
    stack = []
    for i, (ch, line_no, col) in enumerate(bf_positions):
        if ch == '[':
            stack.append((i, line_no, col))
        elif ch == ']':
            if not stack:
                diagnostics.append({
                    "level": "error",
                    "line": line_no,
                    "col": col,
                    "message": f"Unmatched ']' at line {line_no}, column {col}",
                })
            else:
                stack.pop()

    for _, line_no, col in stack:
        diagnostics.append({
            "level": "error",
            "line": line_no,
            "col": col,
            "message": f"Unmatched '[' at line {line_no}, column {col}",
        })

    bf_only = [ch for ch, _, _ in bf_positions]

    if not bf_only:
        diagnostics.append({
            "level": "warning",
            "line": 1,
            "col": 1,
            "message": "File contains no brainfuck instructions",
        })
        return diagnostics

    if '.' not in bf_only and ',' not in bf_only:
        diagnostics.append({
            "level": "warning",
            "line": 1,
            "col": 1,
            "message": "Program has no I/O instructions (no '.' or ',')",
        })

    # Detect long runs of the same instruction
    run_char = bf_only[0]
    run_start_line = bf_positions[0][1]
    run_len = 1
    for i in range(1, len(bf_only)):
        ch = bf_only[i]
        if ch == run_char and ch in '+-><':
            run_len += 1
        else:
            if run_len > 50:
                diagnostics.append({
                    "level": "warning",
                    "line": run_start_line,
                    "col": 1,
                    "message": f"Long run of '{run_char}' ({run_len} times) near line {run_start_line} "
                               f"-- consider using a multiplication loop",
                })
            run_char = ch
            run_start_line = bf_positions[i][1]
            run_len = 1
    if run_len > 50:
        diagnostics.append({
            "level": "warning",
            "line": run_start_line,
            "col": 1,
            "message": f"Long run of '{run_char}' ({run_len} times) near line {run_start_line} "
                       f"-- consider using a multiplication loop",
        })

    # Detect BF characters in comment text (common source of bugs)
    for line_no, line in enumerate(lines, 1):
        bf_in_line = [ch for ch in line if ch in BF_CHARS]
        non_bf_in_line = [ch for ch in line if ch not in BF_CHARS and not ch.isspace()]
        if non_bf_in_line and bf_in_line:
            # Line has both BF and non-BF characters (likely a comment with BF chars)
            text_portion = ''.join(ch for ch in line if ch not in BF_CHARS).strip()
            bf_in_text = [ch for ch in text_portion if ch in BF_CHARS]
            # Check if there are letter/digit characters mixed with BF chars
            has_alpha = any(c.isalpha() or c.isdigit() for c in line)
            if has_alpha and len(bf_in_line) < len(line.strip()) * 0.5:
                # Mostly text with some BF chars embedded -- likely intentional comment
                # Only warn if the BF chars in the text portion could cause issues
                stray = [ch for ch in line if ch in '+-' and line.index(ch) > 0]
                # This heuristic is imperfect; skip for now to avoid false positives
                pass

    return diagnostics


def main():
    if len(sys.argv) < 2:
        print("Usage: python bf_validator.py <program.bf> [program2.bf ...]")
        sys.exit(1)

    exit_code = 0
    for filename in sys.argv[1:]:
        if not os.path.isfile(filename):
            print(f"Error: '{filename}' not found")
            exit_code = 1
            continue

        with open(filename, 'r') as f:
            code = f.read()

        diagnostics = validate(code, filename)

        if not diagnostics:
            print(f"{filename}: OK")
        else:
            for d in diagnostics:
                prefix = "ERROR" if d["level"] == "error" else "WARNING"
                print(f"{filename}:{d['line']}: {prefix}: {d['message']}")
                if d["level"] == "error":
                    exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
