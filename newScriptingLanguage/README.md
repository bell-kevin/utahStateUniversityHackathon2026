# HackScript

HackScript is a compact scripting language created for HackUSU 2026.

## Language highlights
- Variables: `let total = 10;`
- Printing: `print "hello";`
- Conditionals: `if (...) { ... } else { ... }`
- Loops: `while (...) { ... }`
- Expressions: arithmetic, comparisons, booleans, strings, and logical operators (`and`, `or`)
- Comments: `// comment`

## Quick start

Run a script:

```bash
python3 newScriptingLanguage/hackscript.py newScriptingLanguage/examples/hello.hk
```

Run interactive REPL:

```bash
python3 newScriptingLanguage/hackscript.py
```

## Example

```hackscript
let count = 1;
while (count <= 5) {
  print "count=" + count;
  count = count + 1;
}
```

## Files
- `hackscript.py`: lexer, parser, interpreter, CLI
- `spec/GRAMMAR.md`: grammar and semantics
- `examples/`: sample programs
- `tests.py`: quick automated tests
