# Challenge 4: Shout

**Difficulty:** intermediate
**Theme:** input loop + ASCII

## Problem

Read lowercase letters and echo them in uppercase, until input runs out.

## Contract

- Input: a run of lowercase letters, e.g. `abc`.
- Output: the same letters uppercased. For input `abc`, print `ABC`.

## Constraints

- Assume input is only lowercase letters `a` to `z`.
- Stop at end of input (this interpreter's `,` returns 0 when input is exhausted,
  which a loop can use to stop).

## Hints

- Lowercase and uppercase differ by exactly 32: `a` is 97, `A` is 65.
- The echo loop `,[.,]` (see [tutorials/04-input.md](../tutorials/04-input.md)) is
  the skeleton; the twist is adjusting each character by 32 before printing.
- Subtract 32 from the byte you read, print, then read the next.
- Check yourself:
  ```bash
  echo -n "hello" | python interpreters/bf_interpreter.py mine.bf
  python interpreters/bf_interpreter.py mine.bf "abc"   # expect ABC
  ```

## Stretch

Echo input unchanged except uppercase the vowels — or swap the case of every
letter (this needs a decision per character; see
[tutorials/05-conditionals.md](../tutorials/05-conditionals.md)).
