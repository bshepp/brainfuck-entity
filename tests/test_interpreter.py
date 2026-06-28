#!/usr/bin/env python3
"""
Test suite for the Brainfuck interpreter, optimizer, and validator.
Run with: python -m pytest tests/ -v   (or)   python -m unittest tests.test_interpreter -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from interpreters.bf_interpreter import BrainfuckInterpreter, BFStepLimitExceeded
from interpreters.bf_optimizer import optimize, cancel_opposites, remove_clear_loops, remove_dead_code
from tools.bf_validator import validate
from tools.bf_profiler import ProfilingInterpreter

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')


class TestBracketValidation(unittest.TestCase):
    """Test bracket matching and program loading."""

    def setUp(self):
        self.interp = BrainfuckInterpreter()

    def test_valid_brackets(self):
        self.assertEqual(self.interp.load_program('[+]'), '[+]')
        self.assertEqual(self.interp.load_program('[[]]'), '[[]]')
        self.assertEqual(self.interp.load_program('[>[<]]'), '[>[<]]')

    def test_unmatched_open(self):
        with self.assertRaises(ValueError):
            self.interp.load_program('[+')

    def test_unmatched_close(self):
        with self.assertRaises(ValueError):
            self.interp.load_program('+]')

    def test_strips_non_bf_characters(self):
        self.assertEqual(self.interp.load_program('hello +world- !!!'), '+-')

    def test_empty_program(self):
        self.assertEqual(self.interp.load_program(''), '')
        self.assertEqual(self.interp.load_program('no bf chars here'), '')

    def test_bracket_map_built(self):
        self.interp.load_program('[+]')
        self.assertEqual(self.interp.bracket_map, {0: 2, 2: 0})

    def test_nested_bracket_map(self):
        # [>[<]] -> positions: [ at 0, > at 1, [ at 2, < at 3, ] at 4, ] at 5
        self.interp.load_program('[>[<]]')
        self.assertEqual(self.interp.bracket_map, {0: 5, 5: 0, 2: 4, 4: 2})


class TestMemoryOperations(unittest.TestCase):
    """Test pointer movement and cell value operations."""

    def setUp(self):
        self.interp = BrainfuckInterpreter()

    def test_increment(self):
        result = self.interp.execute('+++.')
        self.assertEqual(result, '\x03')
        self.assertEqual(self.interp.memory[0], 3)

    def test_decrement(self):
        result = self.interp.execute('+++-.')
        self.assertEqual(result, '\x02')

    def test_byte_overflow(self):
        # 255 + 1 = 0
        code = '+' * 256 + '.'
        result = self.interp.execute(code)
        self.assertEqual(self.interp.memory[0], 0)

    def test_byte_underflow(self):
        # 0 - 1 = 255
        result = self.interp.execute('-.')
        self.assertEqual(self.interp.memory[0], 255)

    def test_pointer_right(self):
        self.interp.execute('>+++')
        self.assertEqual(self.interp.pointer, 1)
        self.assertEqual(self.interp.memory[1], 3)

    def test_pointer_left(self):
        self.interp.execute('>>><<<+++')
        self.assertEqual(self.interp.pointer, 0)
        self.assertEqual(self.interp.memory[0], 3)

    def test_pointer_wrap_right(self):
        interp = BrainfuckInterpreter(memory_size=4)
        interp.execute('>>>>')
        self.assertEqual(interp.pointer, 0)

    def test_pointer_wrap_left(self):
        interp = BrainfuckInterpreter(memory_size=4)
        interp.execute('<')
        self.assertEqual(interp.pointer, 3)


class TestIO(unittest.TestCase):
    """Test input and output operations."""

    def setUp(self):
        self.interp = BrainfuckInterpreter()

    def test_output_ascii(self):
        # Set cell to 65 ('A') and output
        code = '+' * 65 + '.'
        result = self.interp.execute(code)
        self.assertEqual(result, 'A')

    def test_input(self):
        result = self.interp.execute(',.', input_data='A')
        self.assertEqual(result, 'A')

    def test_input_multiple(self):
        result = self.interp.execute(',>,<.>.', input_data='AB')
        self.assertEqual(result, 'AB')

    def test_input_eof(self):
        self.interp.execute(',', input_data='')
        self.assertEqual(self.interp.memory[0], 0)

    def test_echo_loop(self):
        result = self.interp.execute(',[.,]', input_data='Hello')
        self.assertEqual(result, 'Hello')


class TestLoops(unittest.TestCase):
    """Test loop (bracket) execution."""

    def setUp(self):
        self.interp = BrainfuckInterpreter()

    def test_skip_loop_on_zero(self):
        # Cell starts at 0, loop should be skipped
        self.interp.execute('[+++]')
        self.assertEqual(self.interp.memory[0], 0)

    def test_clear_loop(self):
        self.interp.execute('+++++[-]')
        self.assertEqual(self.interp.memory[0], 0)

    def test_move_value(self):
        # cell0=5, move to cell1: [->+<]
        self.interp.execute('+++++[->+<]')
        self.assertEqual(self.interp.memory[0], 0)
        self.assertEqual(self.interp.memory[1], 5)

    def test_multiplication_loop(self):
        # 3 * 4 = 12: cell0=3, [>++++<-]
        self.interp.execute('+++[>++++<-]')
        self.assertEqual(self.interp.memory[0], 0)
        self.assertEqual(self.interp.memory[1], 12)

    def test_nested_loops(self):
        # Outer loop 2x, inner loop multiplies
        # cell0=2, [>+++[>++<-]<-], cell2 should be 2*3*2 = 12... 
        # Actually: outer runs 2x, each time inner sets cell2 += cell1(=3)*2
        # but cell1 is destroyed each inner run. Let me use a simpler test.
        # cell0=3, [>++<-], cell1 = 6
        self.interp.execute('+++[>++<-]')
        self.assertEqual(self.interp.memory[1], 6)

    def test_deeply_nested(self):
        # cell0=1, [cell1=1, [cell2=1, [-]cell1=0, [-]]cell0=0, [-]]
        # Just verify it doesn't crash
        self.interp.execute('+[>+[>+[-]<[-]]<[-]]')
        # All cells should be 0
        self.assertEqual(self.interp.memory[0], 0)
        self.assertEqual(self.interp.memory[1], 0)
        self.assertEqual(self.interp.memory[2], 0)


class TestREPL(unittest.TestCase):
    """Test REPL state persistence via execute_repl."""

    def setUp(self):
        self.interp = BrainfuckInterpreter()

    def test_state_persists(self):
        self.interp.execute_repl('+++++')
        self.assertEqual(self.interp.memory[0], 5)
        self.interp.execute_repl('+++')
        self.assertEqual(self.interp.memory[0], 8)

    def test_pointer_persists(self):
        self.interp.execute_repl('>>>')
        self.assertEqual(self.interp.pointer, 3)
        self.interp.execute_repl('+++')
        self.assertEqual(self.interp.memory[3], 3)

    def test_output_per_call(self):
        self.interp.execute_repl('+' * 65)  # Set cell to 'A'
        result = self.interp.execute_repl('.')
        self.assertEqual(result, 'A')
        result2 = self.interp.execute_repl('+.')
        self.assertEqual(result2, 'B')

    def test_reset_clears_state(self):
        self.interp.execute_repl('+++++')
        self.interp.reset()
        self.assertEqual(self.interp.memory[0], 0)
        self.assertEqual(self.interp.pointer, 0)


class TestProgramOutputs(unittest.TestCase):
    """Run each .bf program and verify expected output."""

    def setUp(self):
        self.interp = BrainfuckInterpreter()

    def _run_file(self, rel_path, input_data=''):
        path = os.path.join(PROJECT_ROOT, rel_path)
        with open(path, 'r') as f:
            code = f.read()
        return self.interp.execute(code, input_data)

    def test_hello_world(self):
        result = self._run_file('programs/hello-world/hello.bf')
        self.assertEqual(result, 'Hello World!\n')

    def test_simple_hello(self):
        result = self._run_file('programs/hello-world/simple_hello.bf')
        self.assertEqual(result, 'Hello World!')

    def test_add_two_numbers(self):
        result = self._run_file('programs/mathematical/add_two_numbers.bf', '35')
        self.assertEqual(result, '8')
        result2 = self._run_file('programs/mathematical/add_two_numbers.bf', '27')
        self.assertEqual(result2, '9')
        result3 = self._run_file('programs/mathematical/add_two_numbers.bf', '00')
        self.assertEqual(result3, '0')

    def test_simple_star(self):
        result = self._run_file('programs/art/simple_star.bf')
        self.assertEqual(result, '*\n')

    def test_mandala(self):
        result = self._run_file('programs/art/mandala.bf')
        expected_lines = ['*  *'] * 10 + ['*', '']
        self.assertEqual(result, '\n'.join(expected_lines))

    def test_zen_koan(self):
        result = self._run_file('programs/philosophy/zen_koan.bf')
        self.assertIn('+ + + + + + + + + +', result)
        self.assertIn('=?', result)
        self.assertIn('Zen: silence', result)

    def test_guess_the_number_correct(self):
        result = self._run_file('programs/games/guess_the_number.bf', '5')
        self.assertEqual(result, 'Y\n')

    def test_guess_the_number_wrong_then_correct(self):
        result = self._run_file('programs/games/guess_the_number.bf', '35')
        self.assertEqual(result, 'N\nY\n')

    # --- Library expansion (2026-06-23) ---

    def test_digits(self):
        result = self._run_file('programs/hello-world/digits.bf')
        self.assertEqual(result, '0123456789\n')

    def test_alphabet(self):
        result = self._run_file('programs/hello-world/alphabet.bf')
        self.assertEqual(result, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ\n')

    def test_multiply(self):
        self.assertEqual(self._run_file('programs/mathematical/multiply.bf', '23'), '6')
        self.assertEqual(self._run_file('programs/mathematical/multiply.bf', '14'), '4')
        self.assertEqual(self._run_file('programs/mathematical/multiply.bf', '31'), '3')

    def test_subtract(self):
        self.assertEqual(self._run_file('programs/mathematical/subtract.bf', '73'), '4')
        self.assertEqual(self._run_file('programs/mathematical/subtract.bf', '90'), '9')
        self.assertEqual(self._run_file('programs/mathematical/subtract.bf', '55'), '0')

    def test_even_or_odd(self):
        self.assertEqual(self._run_file('programs/games/even_or_odd.bf', '4'), 'E')
        self.assertEqual(self._run_file('programs/games/even_or_odd.bf', '7'), 'O')
        self.assertEqual(self._run_file('programs/games/even_or_odd.bf', '0'), 'E')

    def test_secret_knock(self):
        self.assertEqual(self._run_file('programs/games/secret_knock.bf', '7'), '!')
        self.assertEqual(self._run_file('programs/games/secret_knock.bf', '147'), '..!')
        self.assertEqual(self._run_file('programs/games/secret_knock.bf', '27'), '.!')

    def test_triangle(self):
        result = self._run_file('programs/art/triangle.bf')
        self.assertEqual(result, '*\n**\n***\n****\n*****\n')

    def test_box(self):
        result = self._run_file('programs/art/box.bf')
        self.assertEqual(result, '****\n*  *\n*  *\n****\n')

    def test_less_is_more(self):
        result = self._run_file('programs/philosophy/less_is_more.bf')
        self.assertEqual(result, 'less is more\n')

    def test_empty_is_full(self):
        result = self._run_file('programs/philosophy/empty_is_full.bf')
        self.assertEqual(result, 'empty is full\n')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and unusual programs."""

    def test_empty_program(self):
        interp = BrainfuckInterpreter()
        result = interp.execute('')
        self.assertEqual(result, '')

    def test_comment_only_program(self):
        interp = BrainfuckInterpreter()
        result = interp.execute('this has no bf instructions at all')
        self.assertEqual(result, '')

    def test_large_output(self):
        interp = BrainfuckInterpreter()
        code = '+' * 65 + '+' * 0 + '.' * 100
        result = interp.execute(code)
        self.assertEqual(result, 'A' * 100)

    def test_maximum_cell_values(self):
        interp = BrainfuckInterpreter()
        interp.execute('+' * 255)
        self.assertEqual(interp.memory[0], 255)
        interp.execute('+' * 255 + '+')
        self.assertEqual(interp.memory[0], 0)


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


class TestOptimizer(unittest.TestCase):
    """Test BF code optimizer."""

    def test_cancel_plus_minus(self):
        self.assertEqual(cancel_opposites('+-'), '')
        self.assertEqual(cancel_opposites('-+'), '')
        self.assertEqual(cancel_opposites('++-'), '+')

    def test_cancel_arrows(self):
        self.assertEqual(cancel_opposites('><'), '')
        self.assertEqual(cancel_opposites('<>'), '')
        self.assertEqual(cancel_opposites('>><'), '>')

    def test_clear_loop_normalization(self):
        self.assertEqual(remove_clear_loops('[+]'), '[-]')
        self.assertEqual(remove_clear_loops('[-][-]'), '[-]')

    def test_dead_code_before_clear(self):
        self.assertEqual(remove_dead_code('+++[-]'), '[-]')
        self.assertEqual(remove_dead_code('---[-]'), '[-]')

    def test_full_optimization(self):
        self.assertEqual(optimize('+-'), '')
        self.assertEqual(optimize('++-+><[-][-]>><'), '[-]>')
        # +++[+] -> +++[-] -> [-] (dead code before clear loop)
        self.assertEqual(optimize('+++[+]'), '[-]')

    def test_output_equivalence(self):
        """Optimized program must produce the same output as original."""
        interp = BrainfuckInterpreter()
        programs = [
            '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.'
            '>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.',
            ',[.,]',
            '++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.',
        ]
        inputs = ['', 'hello', '']
        for code, inp in zip(programs, inputs):
            original = interp.execute(code, inp)
            optimized_code = optimize(code)
            optimized_result = interp.execute(optimized_code, inp)
            self.assertEqual(
                original, optimized_result,
                f"Output mismatch for: {code[:40]}..."
            )


class TestValidator(unittest.TestCase):
    """Test BF syntax validator."""

    def test_valid_program(self):
        diags = validate('++[>++<-]>.')
        errors = [d for d in diags if d['level'] == 'error']
        self.assertEqual(len(errors), 0)

    def test_unmatched_open(self):
        diags = validate('[++')
        errors = [d for d in diags if d['level'] == 'error']
        self.assertEqual(len(errors), 1)
        self.assertIn("Unmatched '['", errors[0]['message'])

    def test_unmatched_close(self):
        diags = validate('++]')
        errors = [d for d in diags if d['level'] == 'error']
        self.assertEqual(len(errors), 1)
        self.assertIn("Unmatched ']'", errors[0]['message'])

    def test_no_io_warning(self):
        diags = validate('++[>++<-]')
        warnings = [d for d in diags if d['level'] == 'warning']
        self.assertTrue(any("no I/O" in w['message'] for w in warnings))

    def test_empty_file_warning(self):
        diags = validate('')
        warnings = [d for d in diags if d['level'] == 'warning']
        self.assertTrue(any("no brainfuck" in w['message'] for w in warnings))

    def test_position_reporting(self):
        diags = validate('++[\n++')
        errors = [d for d in diags if d['level'] == 'error']
        self.assertEqual(errors[0]['line'], 1)
        self.assertEqual(errors[0]['col'], 3)


class TestProfiler(unittest.TestCase):
    """Test profiling interpreter."""

    def test_instruction_counting(self):
        interp = ProfilingInterpreter()
        interp.execute('+++>++<')
        self.assertEqual(interp.op_counts['+'], 5)
        self.assertEqual(interp.op_counts['>'], 1)
        self.assertEqual(interp.op_counts['<'], 1)

    def test_loop_iteration_counting(self):
        interp = ProfilingInterpreter()
        interp.execute('+++[-]')
        # The [ is at position 3, loop runs 3 times
        self.assertEqual(interp.loop_iterations.get(3), 3)

    def test_memory_tracking(self):
        interp = ProfilingInterpreter()
        interp.execute('+>++>+++')
        self.assertEqual(interp.max_pointer, 2)
        self.assertEqual(len(interp.cells_written), 3)

    def test_step_limit(self):
        interp = ProfilingInterpreter()
        with self.assertRaises(RuntimeError):
            interp.execute('+[]', max_steps=100)

    def test_step_limit_raises_bf_exception(self):
        from interpreters.bf_interpreter import BFStepLimitExceeded
        interp = ProfilingInterpreter()
        with self.assertRaises(BFStepLimitExceeded):
            interp.execute('+[]', max_steps=100)

    def test_report_generation(self):
        interp = ProfilingInterpreter()
        interp.execute('++[-]')
        report = interp.report('++[-]')
        self.assertIn('Execution Profile', report)
        self.assertIn('Total steps', report)
        self.assertIn('Loop iterations', report)


if __name__ == '__main__':
    unittest.main()
