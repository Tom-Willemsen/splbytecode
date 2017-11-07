# splbytecode
Shakespeare programming language to Java bytecode compiler.

Hello, world:
```
> python compiler.py hello.spl
> java SplProgram
H
E
L
L
O
,

W
O
R
L
D
```

Incrementing user input:
```
> python compiler.py incrementor.spl
> java SplProgram 100
101
```

Requires Python 3.6 and a JRE >= 5 (versions before 5 did not allow spaces in field names). No need for a JDK.

Note: A Java 9 class is produced by default. This can be configured using the `--cls-maj-version` compiler option. See [list of valid version numbers](https://stackoverflow.com/questions/9170832/list-of-java-class-file-format-major-version-numbers).


Current deficiencies/TODOs:
- Does not support Gotos (yet)
- Each scene must have a well-defined set of characters on stage. All characters must leave at the end of a scene.
- Characters are single-valued, stacks have not been implemented.
- Arithmetic isn't supported yet (e.g. `You are the quotient of ... and ...`)
- Each character can only say one line at a time.
- Turn on/off variable initializers (The official spec says the text after a variable declaration is ignored, but other compilers try to interpret it as a value)

But seriously, if you're trying to compile SPL to Java bytecode, you have far bigger problems than the above...
