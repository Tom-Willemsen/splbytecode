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

Requires Python 3.6 and a JRE >= 5 (versions before 5 may work if you don't use any characters with spaces in their names). No need for a JDK.

Note: A Java 9 class is produced by default. This can be configured using the `--cls-maj-version` compiler option. See [list of valid version numbers](https://stackoverflow.com/questions/9170832/list-of-java-class-file-format-major-version-numbers).

If you're running the `goto.spl` example you'll need to launch the JVM with the `-Xverify:none` option because newer java bytecode verifiers don't like `GOTO` instructions pointing at arbitrary locations. If you don't do this you will get a nasty-looking `java.lang.VerifyError`.


Current deficiencies/TODOs:
- Each scene must have a well-defined set of characters on stage. All characters must leave at the end of a scene.
- Characters are single-valued, stacks have not been implemented.
- Arithmetic isn't supported yet (e.g. `You are the quotient of ... and ...`)
- Each character can only say one line at a time.
- Turn on/off variable initializers (The official spec says the text after a variable declaration is ignored, but other compilers try to interpret it as a value)
