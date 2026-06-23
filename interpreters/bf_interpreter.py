#!/usr/bin/env python3
"""
Pure Python Brainfuck Interpreter
A minimalist interpreter for the ultimate minimalist language
"""

import sys
from typing import List, Optional


class BFStepLimitExceeded(RuntimeError):
    """Raised when a program exceeds its step budget (likely an infinite loop).

    Subclasses RuntimeError so callers using `except RuntimeError` still catch it.
    """
    pass


class BrainfuckInterpreter:
    """
    Pure implementation of a brainfuck interpreter.
    
    Brainfuck operates on:
    - An array of 30,000 byte cells (initially zero)
    - A data pointer (initially points to leftmost cell) 
    - 8 simple commands that manipulate the array and pointer
    """
    
    def __init__(self, memory_size: int = 30000, interactive: bool = False):
        """
        Initialize the brainfuck machine.
        
        Args:
            memory_size: Size of memory tape (default 30,000 cells)
            interactive: Read from stdin when input buffer is exhausted
        """
        self.memory_size = memory_size
        self.interactive = interactive
        self.reset()
    
    def reset(self):
        """Reset the machine to initial state."""
        self.memory = [0] * self.memory_size
        self.pointer = 0
        self.instruction_pointer = 0
        self.bracket_map = {}
        self.output = []
        self.input_buffer = []
        self.instruction_count = 0
    
    def load_program(self, code: str) -> str:
        """
        Load and validate brainfuck program, building a bracket map for O(1) jumps.
        
        Args:
            code: Raw brainfuck code
            
        Returns:
            Cleaned code with only valid BF commands
        """
        valid_chars = set('><+-.,[]')
        cleaned = ''.join(c for c in code if c in valid_chars)
        
        # Build bracket map and validate in one pass
        stack = []
        self.bracket_map = {}
        for i, char in enumerate(cleaned):
            if char == '[':
                stack.append(i)
            elif char == ']':
                if not stack:
                    raise ValueError("Unmatched closing bracket ']'")
                j = stack.pop()
                self.bracket_map[j] = i
                self.bracket_map[i] = j
        
        if stack:
            raise ValueError("Unmatched opening bracket '['")
        
        return cleaned
    
    def set_input(self, input_data: str):
        """Set input for the program."""
        self.input_buffer = list(input_data.encode('utf-8'))
    
    def execute(self, code: str, input_data: str = "", debug: bool = False,
                max_steps: int = 10_000_000) -> str:
        """
        Execute a brainfuck program.

        Args:
            code: Brainfuck source code
            input_data: Input string for the program
            debug: Enable debug output
            max_steps: Maximum steps before raising BFStepLimitExceeded (0 = unlimited)

        Returns:
            Program output as string
        """
        self.reset()
        program = self.load_program(code)
        self.set_input(input_data)
        
        if debug:
            print(f"Executing program: {program}")
            print(f"Input: {repr(input_data)}")
        
        while self.instruction_pointer < len(program):
            command = program[self.instruction_pointer]
            self.instruction_count += 1

            if max_steps and self.instruction_count > max_steps:
                raise BFStepLimitExceeded(
                    f"exceeded {max_steps:,} steps -- possible infinite loop"
                )

            if debug and self.instruction_count <= 100:  # Limit debug output
                print(f"Step {self.instruction_count}: {command} | "
                      f"Ptr: {self.pointer} | "
                      f"Cell: {self.memory[self.pointer]} | "
                      f"IP: {self.instruction_pointer}")
            
            if command == '>':
                # Increment pointer
                self.pointer += 1
                if self.pointer >= self.memory_size:
                    self.pointer = 0  # Wrap around
                    
            elif command == '<':
                # Decrement pointer  
                self.pointer -= 1
                if self.pointer < 0:
                    self.pointer = self.memory_size - 1  # Wrap around
                    
            elif command == '+':
                # Increment byte at pointer
                self.memory[self.pointer] = (self.memory[self.pointer] + 1) % 256
                
            elif command == '-':
                # Decrement byte at pointer
                self.memory[self.pointer] = (self.memory[self.pointer] - 1) % 256
                
            elif command == '.':
                # Output byte at pointer
                byte_value = self.memory[self.pointer]
                self.output.append(byte_value)
                if debug:
                    print(f"Output: {chr(byte_value) if 32 <= byte_value <= 126 else f'\\x{byte_value:02x}'}")
                    
            elif command == ',':
                if self.input_buffer:
                    self.memory[self.pointer] = self.input_buffer.pop(0)
                elif self.interactive:
                    byte = sys.stdin.buffer.read(1)
                    self.memory[self.pointer] = byte[0] if byte else 0
                else:
                    self.memory[self.pointer] = 0
                    
            elif command == '[':
                if self.memory[self.pointer] == 0:
                    self.instruction_pointer = self.bracket_map[self.instruction_pointer]
                    
            elif command == ']':
                if self.memory[self.pointer] != 0:
                    self.instruction_pointer = self.bracket_map[self.instruction_pointer]
            
            self.instruction_pointer += 1
        
        # Convert output to string
        result = self._decode_output()

        if debug:
            print(f"Execution completed in {self.instruction_count} steps")
            print(f"Final output: {repr(result)}")
        
        return result
    
    def execute_repl(self, code: str, input_data: str = "") -> str:
        """
        Execute brainfuck code while preserving machine state between calls.
        Unlike execute(), memory, pointer position, and output persist.
        """
        program = self.load_program(code)
        if input_data:
            self.input_buffer.extend(list(input_data.encode('utf-8')))
        
        self.instruction_pointer = 0
        self.output = []
        
        while self.instruction_pointer < len(program):
            command = program[self.instruction_pointer]
            self.instruction_count += 1
            
            if command == '>':
                self.pointer = (self.pointer + 1) % self.memory_size
            elif command == '<':
                self.pointer = (self.pointer - 1) % self.memory_size
            elif command == '+':
                self.memory[self.pointer] = (self.memory[self.pointer] + 1) % 256
            elif command == '-':
                self.memory[self.pointer] = (self.memory[self.pointer] - 1) % 256
            elif command == '.':
                self.output.append(self.memory[self.pointer])
            elif command == ',':
                if self.input_buffer:
                    self.memory[self.pointer] = self.input_buffer.pop(0)
                elif self.interactive:
                    byte = sys.stdin.buffer.read(1)
                    self.memory[self.pointer] = byte[0] if byte else 0
                else:
                    self.memory[self.pointer] = 0
            elif command == '[':
                if self.memory[self.pointer] == 0:
                    self.instruction_pointer = self.bracket_map[self.instruction_pointer]
            elif command == ']':
                if self.memory[self.pointer] != 0:
                    self.instruction_pointer = self.bracket_map[self.instruction_pointer]
            
            self.instruction_pointer += 1
        
        try:
            return bytes(self.output).decode('utf-8')
        except UnicodeDecodeError:
            return ''.join(chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in self.output)

    def _decode_output(self) -> str:
        """Decode collected output bytes to a string, with a printable-hex fallback."""
        try:
            return bytes(self.output).decode('utf-8')
        except UnicodeDecodeError:
            return ''.join(
                chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in self.output
            )

    def get_memory_dump(self, start: int = 0, end: Optional[int] = None) -> List[int]:
        """
        Get a dump of memory contents.
        
        Args:
            start: Start index
            end: End index (None for all used memory)
            
        Returns:
            List of memory values
        """
        if end is None:
            # Find last non-zero cell
            end = len(self.memory)
            while end > 0 and self.memory[end-1] == 0:
                end -= 1
            end = max(end, self.pointer + 1)  # Include current pointer
        
        return self.memory[start:end]
    
    def visualize_memory(self, context: int = 10) -> str:
        """
        Create a visual representation of memory around the current pointer.
        
        Args:
            context: Number of cells to show on each side of pointer
            
        Returns:
            Formatted memory visualization
        """
        start = max(0, self.pointer - context)
        end = min(self.memory_size, self.pointer + context + 1)
        
        lines = []
        
        # Memory addresses
        addr_line = "Addr: "
        for i in range(start, end):
            addr_line += f"{i:>4} "
        lines.append(addr_line)
        
        # Memory values  
        val_line = "Val:  "
        for i in range(start, end):
            val_line += f"{self.memory[i]:>4} "
        lines.append(val_line)
        
        # Pointer indicator
        ptr_line = "Ptr:  "
        for i in range(start, end):
            if i == self.pointer:
                ptr_line += "  ^^ "
            else:
                ptr_line += "     "
        lines.append(ptr_line)
        
        # ASCII representation
        char_line = "Char: "
        for i in range(start, end):
            val = self.memory[i]
            if 32 <= val <= 126:
                char_line += f"  {chr(val)} "
            else:
                char_line += "  . "
        lines.append(char_line)
        
        return '\n'.join(lines)


def main():
    """Command line interface for the brainfuck interpreter."""
    if len(sys.argv) < 2:
        print("Usage: python bf_interpreter.py <program.bf> [input] [--debug] [--interactive]")
        print("   or: python bf_interpreter.py --repl")
        sys.exit(1)
    
    if sys.argv[1] == '--repl':
        # Interactive REPL mode
        interpreter = BrainfuckInterpreter()
        print("Brainfuck REPL - Enter 'quit' to exit")
        print("Commands: .memory (show memory), .reset (reset machine)")
        
        while True:
            try:
                code = input("bf> ")
                if code.lower() in ['quit', 'exit']:
                    break
                elif code == '.memory':
                    print(interpreter.visualize_memory())
                elif code == '.reset':
                    interpreter.reset()
                    print("Machine reset")
                else:
                    result = interpreter.execute_repl(code)
                    if result:
                        print(f"Output: {repr(result)}")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        filename = sys.argv[1]
        flags = {a for a in sys.argv[2:] if a.startswith('--')}
        positional = [a for a in sys.argv[2:] if not a.startswith('--')]
        input_data = positional[0] if positional else ""
        debug = '--debug' in flags
        interactive = '--interactive' in flags or not input_data
        
        try:
            with open(filename, 'r') as f:
                code = f.read()
            
            interpreter = BrainfuckInterpreter(interactive=interactive)
            result = interpreter.execute(code, input_data, debug=debug)
            
            if result:
                print(result, end='')
            
            if debug:
                print(f"\nFinal memory state:")
                print(interpreter.visualize_memory())
                
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()