# HackScript grammar

## Tokens
Keywords: `let`, `print`, `if`, `else`, `while`, `true`, `false`, `nil`, `and`, `or`

Symbols:
`(` `)` `{` `}` `,` `.` `;` `+` `-` `*` `/` `%` `!` `=` `<` `>`
(with combined operators `!=`, `==`, `<=`, `>=`)

Comments: line comments start with `//`

## EBNF-ish grammar

```ebnf
program        -> declaration* EOF ;

declaration    -> "let" IDENTIFIER "=" expression ";"
                | statement ;

statement      -> "print" expression ";"
                | "if" "(" expression ")" statement ( "else" statement )?
                | "while" "(" expression ")" statement
                | "{" declaration* "}"
                | expression ";" ;

expression     -> assignment ;
assignment     -> IDENTIFIER "=" assignment | logic_or ;
logic_or       -> logic_and ( "or" logic_and )* ;
logic_and      -> equality ( "and" equality )* ;
equality       -> comparison ( ("!=" | "==") comparison )* ;
comparison     -> term ( (">" | ">=" | "<" | "<=") term )* ;
term           -> factor ( ("+" | "-") factor )* ;
factor         -> unary ( ("*" | "/" | "%") unary )* ;
unary          -> ("!" | "-") unary | primary ;
primary        -> NUMBER | STRING | "true" | "false" | "nil"
                | IDENTIFIER | "(" expression ")" ;
```

## Semantics
- Variables are block-scoped.
- `+` does number addition or string concatenation.
- `nil` and `false` are falsey; everything else is truthy.
- Assignment updates existing variables; assigning to an undeclared name is an error.
