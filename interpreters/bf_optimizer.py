#!/usr/bin/env python3
"""
Brainfuck Code Optimizer
Applies peephole optimizations to BF source code, producing equivalent but
more efficient programs.
"""

import sys
import os
import re


BF_CHARS = set('><+-.,[]')


def extract_bf(code: str) -> str:
    """Strip non-BF characters from source."""
    return ''.join(c for c in code if c in BF_CHARS)


def cancel_opposites(code: str) -> str:
    """Remove adjacent opposing instructions: +- -+ >< <>."""
    prev = None
    while prev != code:
        prev = code
        code = code.replace('+-', '')
        code = code.replace('-+', '')
        code = code.replace('><', '')
        code = code.replace('<>', '')
    return code


def collapse_runs(code: str) -> str:
    """
    Collapse consecutive identical instructions into a compact notation.
    Returns a list of (instruction, count) tuples for internal use,
    but for BF output we just return the canceled code since BF has no
    multi-increment syntax. This function is used for analysis only.
    """
    if not code:
        return []
    runs = []
    current = code[0]
    count = 1
    for ch in code[1:]:
        if ch == current:
            count += 1
        else:
            runs.append((current, count))
            current = ch
            count = 1
    runs.append((current, count))
    return runs


def remove_clear_loops(code: str) -> str:
    """Replace [-] and [+] with a single zero-cell operation.
    Since BF has no native 'set zero' instruction, we keep [-] as the
    canonical form but eliminate redundant patterns like [-][-]."""
    code = re.sub(r'\[\+\]', '[-]', code)
    # Remove consecutive clear loops
    prev = None
    while prev != code:
        prev = code
        code = code.replace('[-][-]', '[-]')
    return code


def remove_dead_code(code: str) -> str:
    """Remove provably dead code patterns."""
    # Remove operations before a clear loop when we know the cell will be zeroed
    # Pattern: any sequence of + and - immediately before [-] is dead
    code = re.sub(r'[+\-]+(\[-\])', r'\1', code)

    # Remove empty loops []
    code = code.replace('[]', '')

    return code


def optimize(code: str) -> str:
    """
    Apply all optimizations to BF source code.
    Returns optimized BF code string.
    """
    result = extract_bf(code)
    prev = None
    while prev != result:
        prev = result
        result = cancel_opposites(result)
        result = remove_clear_loops(result)
        result = remove_dead_code(result)
    return result


def format_output(code: str, line_width: int = 70) -> str:
    """Format optimized BF code with line breaks for readability."""
    lines = []
    i = 0
    while i < len(code):
        chunk = code[i:i + line_width]
        # Try to break at a loop boundary if possible
        if len(chunk) == line_width and i + line_width < len(code):
            last_bracket = max(chunk.rfind(']'), chunk.rfind('['))
            if last_bracket > line_width // 2:
                chunk = code[i:i + last_bracket + 1]
        lines.append(chunk)
        i += len(chunk)
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python bf_optimizer.py <program.bf> [--output file.bf] [--stats]")
        sys.exit(1)

    filename = sys.argv[1]
    output_file = None
    show_stats = '--stats' in sys.argv

    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    if not os.path.isfile(filename):
        print(f"Error: '{filename}' not found")
        sys.exit(1)

    with open(filename, 'r') as f:
        raw = f.read()

    original = extract_bf(raw)
    optimized = optimize(raw)

    if show_stats or not output_file:
        orig_len = len(original)
        opt_len = len(optimized)
        reduction = orig_len - opt_len
        pct = (reduction / orig_len * 100) if orig_len else 0
        print(f"Original:  {orig_len} instructions")
        print(f"Optimized: {opt_len} instructions")
        print(f"Reduction: {reduction} instructions ({pct:.1f}%)")

        orig_runs = collapse_runs(original)
        opt_runs = collapse_runs(optimized)
        print(f"Original run count:  {len(orig_runs)}")
        print(f"Optimized run count: {len(opt_runs)}")

    if output_file:
        formatted = format_output(optimized)
        with open(output_file, 'w') as f:
            f.write(formatted + '\n')
        print(f"Optimized code written to {output_file}")
    elif not show_stats:
        print()
        print(format_output(optimized))


if __name__ == "__main__":
    main()
