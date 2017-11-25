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

Requires Python 3.6 and a JRE >= 5. No need for a JDK.

A class file at version 50.0 (JRE 6) is produced by default. This can be configured using the `--cls-maj-version` and `--cls-min-version` compiler options. See [list of valid version numbers](https://stackoverflow.com/questions/9170832/list-of-java-class-file-format-major-version-numbers). 

# Troubleshooting

**`java.lang.VerifyError: Expecting a stackmap frame at branch target`**

This happens if you've chosen to use a class file version newer than 50 (JRE 6). Newer java bytecode verifiers don't like `GOTO` instructions pointing at arbitrary locations. A workaround is to disable the bytecode verifier with the `-Xverify:none` JVM option.

**`java.lang.ClassFormatError: Illegal field name [character name] in class`**

This happens if your character's names contain spaces and you have chosen to use a class file version older than 49 (JRE 5). As above, you can tell the JVM to ignore this error by using the `Xverify:none` JVM argument. Alternatively, you can choose characters that don't have spaces in their names.

**`java.lang.ClassFormatError: Truncated class file`**

This happens if you try to use a class file format earlier than `45.3` (JRE 1.1). Class file formats that old are not supported.

**`java.lang.UnsupportedClassVersionError`**

The produced class file version is not supported by your JRE. Upgrade your JRE or decrease the class file version.


# Current deficiencies/TODOs:
- Each scene must have a well-defined set of characters on stage. All characters must leave at the end of a scene.
- Characters are single-valued, stacks have not been implemented.
- Arithmetic isn't supported yet (e.g. `You are the quotient of ... and ...`)
- Each character can only say one line at a time.
- Turn on/off variable initializers (The official spec says the text after a variable declaration is ignored, but other compilers try to interpret it as a value)
