# splbytecode
Shakespeare programming language to Java bytecode compiler

To compile:
`python compiler.py hello.spl`

To run:
`java SplProgram`

Developed with Python 3.6 and Java 9. 

The resulting `.class` file reports it's version as Java 9 but I suspect if the version number was changed it would work on an older JRE.


Current deficiencies/TODOs:
- Does not support Gotos (yet)
- Each scene must have a well-defined set of characters on stage. All characters must leave at the end of a scene.
- Characters are single-valued, stacks have not been implemented.
- Arithmetic isn't supported yet (e.g. `You are the quotient of ... and ...`)
- Each character can only say one line at a time.
- Compiler always produces a "java 9" class. This should be configurable.
- Turn on/off variable initializers (The official spec says the text after a variable declaration is ignored, but other compilers try to interpret it as a value)
- Allow input (probably passed in as `String[] args`).

But seriously, if you're trying to compile SPL to Java bytecode, you have far bigger problems than the above...
