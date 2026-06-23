#!/usr/bin/env python3
"""
Brainfuck Execution Profiler
Runs a BF program with full instrumentation and reports execution statistics.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from interpreters.bf_interpreter import BrainfuckInterpreter, BFStepLimitExceeded


class ProfilingInterpreter(BrainfuckInterpreter):
    """Extended interpreter that collects execution statistics."""

    def execute(self, code: str, input_data: str = "", debug: bool = False,
                max_steps: int = 10_000_000) -> str:
        self.reset()
        program = self.load_program(code)
        self.set_input(input_data)

        # Profiling state
        self.op_counts = {op: 0 for op in '><+-.,[]'}
        self.loop_iterations = {}  # bracket_pos -> iteration count
        self.max_pointer = 0
        self.cells_written = set()

        start_time = time.perf_counter()

        while self.instruction_pointer < len(program):
            command = program[self.instruction_pointer]
            self.instruction_count += 1
            self.op_counts[command] += 1

            if self.instruction_count > max_steps:
                self.elapsed = time.perf_counter() - start_time
                raise BFStepLimitExceeded(
                    f"Exceeded {max_steps:,} steps -- possible infinite loop"
                )

            if command == '>':
                self.pointer = (self.pointer + 1) % self.memory_size
            elif command == '<':
                self.pointer = (self.pointer - 1) % self.memory_size
            elif command == '+':
                self.memory[self.pointer] = (self.memory[self.pointer] + 1) % 256
                self.cells_written.add(self.pointer)
            elif command == '-':
                self.memory[self.pointer] = (self.memory[self.pointer] - 1) % 256
                self.cells_written.add(self.pointer)
            elif command == '.':
                self.output.append(self.memory[self.pointer])
            elif command == ',':
                if self.input_buffer:
                    self.memory[self.pointer] = self.input_buffer.pop(0)
                else:
                    self.memory[self.pointer] = 0
                self.cells_written.add(self.pointer)
            elif command == '[':
                if self.memory[self.pointer] == 0:
                    self.instruction_pointer = self.bracket_map[self.instruction_pointer]
                else:
                    loop_start = self.instruction_pointer
                    self.loop_iterations[loop_start] = self.loop_iterations.get(loop_start, 0) + 1
            elif command == ']':
                if self.memory[self.pointer] != 0:
                    target = self.bracket_map[self.instruction_pointer]
                    self.loop_iterations[target] = self.loop_iterations.get(target, 0) + 1
                    self.instruction_pointer = target

            self.max_pointer = max(self.max_pointer, self.pointer)
            self.instruction_pointer += 1

        self.elapsed = time.perf_counter() - start_time

        try:
            return bytes(self.output).decode('utf-8')
        except UnicodeDecodeError:
            return ''.join(
                chr(b) if 32 <= b <= 126 else f'\\x{b:02x}'
                for b in self.output
            )

    def report(self, program_code: str) -> str:
        """Generate a human-readable profiling report."""
        lines = []
        lines.append("=== Brainfuck Execution Profile ===")
        lines.append("")

        # Program size
        bf_chars = sum(1 for c in program_code if c in '><+-.,[]')
        lines.append(f"Program size:       {bf_chars} instructions")
        lines.append(f"Total steps:        {self.instruction_count:,}")
        lines.append(f"Execution time:     {self.elapsed * 1000:.2f} ms")
        if self.elapsed > 0:
            lines.append(f"Steps per second:   {self.instruction_count / self.elapsed:,.0f}")
        lines.append("")

        # Instruction frequency
        lines.append("Instruction frequency:")
        for op in '><+-.,[]':
            count = self.op_counts.get(op, 0)
            pct = (count / self.instruction_count * 100) if self.instruction_count else 0
            bar = '#' * int(pct / 2)
            lines.append(f"  {op}  {count:>10,}  ({pct:5.1f}%)  {bar}")
        lines.append("")

        # Memory usage
        lines.append(f"Memory cells used:  {len(self.cells_written)}")
        lines.append(f"Max pointer pos:    {self.max_pointer}")
        lines.append(f"Output length:      {len(self.output)} bytes")
        lines.append("")

        # Loop statistics
        if self.loop_iterations:
            lines.append("Loop iterations (top 10 hottest):")
            sorted_loops = sorted(
                self.loop_iterations.items(), key=lambda x: x[1], reverse=True
            )
            for pos, count in sorted_loops[:10]:
                match_pos = self.bracket_map.get(pos, '?')
                lines.append(f"  [{pos}..{match_pos}]  {count:>10,} iterations")
        else:
            lines.append("No loops executed.")

        lines.append("")
        lines.append("=== End Profile ===")
        return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python bf_profiler.py <program.bf> [input]")
        sys.exit(1)

    filename = sys.argv[1]
    positional = [a for a in sys.argv[2:] if not a.startswith('--')]
    input_data = positional[0] if positional else ""

    if not os.path.isfile(filename):
        print(f"Error: '{filename}' not found")
        sys.exit(1)

    with open(filename, 'r') as f:
        code = f.read()

    interp = ProfilingInterpreter()
    try:
        result = interp.execute(code, input_data)
        print(interp.report(code))
        if result:
            print(f"\nProgram output:\n{result}")
    except RuntimeError as e:
        print(f"ABORTED: {e}")
        print(interp.report(code))
        sys.exit(1)


if __name__ == "__main__":
    main()
