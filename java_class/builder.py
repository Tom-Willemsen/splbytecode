from java_class import access_modifiers, instructions
from java_class.java_class import JavaClass
from spl.ast import BinaryOperator, Operators, Value, Assign, DynamicValue, AstNode, PrintVariable, InputVariable


class CompilationError(Exception):
    pass


class Builder(object):
    """
    Builder class for a .class file. Contains methods for performing abstracted operations
    (reading/writing from fields, invoking methods, etc).
    """

    # Variable used to keep track of how many inputs have been "used up" from 'String[] args'
    INPUT_INDEX = "$input_index"

    # Access modifier for all fields that this builder generates.
    FIELD_ACCESS_MODIFIERS = access_modifiers.PUBLIC | access_modifiers.STATIC

    # Access modifier for the main method that this builder generates
    MAIN_METHOD_ACCESS_MODIFIERS = access_modifiers.PUBLIC | access_modifiers.STATIC

    def __init__(self, name):
        """
        This generates the stub of a valid java class file.
        """
        self.name = name
        self.output_class = JavaClass(name)
        self.main_method_instructions = []

        self.set_field(Builder.INPUT_INDEX, 0)

    def build(self):
        """
        This methods performs final transformations before export.
        """
        self.main_method_instructions.append(instructions.voidreturn())
        self.output_class.add_method("main", "([Ljava/lang/String;)V", Builder.MAIN_METHOD_ACCESS_MODIFIERS,
                                     self.main_method_instructions)

        valid, message = self.output_class.check_valid()
        if not valid:
            raise CompilationError("Can't build class: {}".format(message))

        return self.output_class

    def set_field(self, name, value):
        """
        Sets a field with a constant value.
        """
        self.main_method_instructions.append(instructions.bipush(value))
        self.set_field_with_value_from_top_of_stack(name)
        return self

    def set_field_with_value_from_top_of_stack(self, name):
        """
        Sets a field to have the value at the top of the stack.
        """
        self.output_class.add_field(name, "I", Builder.FIELD_ACCESS_MODIFIERS)
        field_ref = self.output_class.pool.add_field_ref(self.name, name, "I")

        self.main_method_instructions.extend([
            instructions.putstatic(field_ref),
        ])
        return self

    def integer_at_top_of_stack_to_sysout(self, as_char):
        """
        The integer at the top of the stack is popped and printed to standard out.

        Formats as a character if as_char is True, otherwise formats as an integer.
        """
        printstream = self.output_class.pool.add_field_ref("java/lang/System", "out", "Ljava/io/PrintStream;")
        sysout = self.output_class.pool.add_method_ref("java/io/PrintStream", "println", "(C)V" if as_char else "(I)V")

        self.main_method_instructions.extend([
            instructions.getstatic(printstream),
            instructions.swap(),
        ])

        if as_char:
            self.main_method_instructions.append(instructions.i2c())

        self.main_method_instructions.append(instructions.invokevirtual(sysout))
        return self

    def multiply_integer_at_top_of_stack_by_two(self):
        self.main_method_instructions.extend([
            instructions.bipush(2),
            instructions.imul(),
        ])
        return self

    def push_field_value_onto_stack(self, name):
        # Ensures the field exists otherwise getting it will cause a runtime error.
        self.output_class.add_field(name, "I", Builder.FIELD_ACCESS_MODIFIERS)

        field_ref = self.output_class.pool.add_field_ref(self.name, name, "I")
        self.main_method_instructions.append(instructions.getstatic(field_ref))
        return self

    def print_field(self, name, as_char):
        self.push_field_value_onto_stack(name)
        self.integer_at_top_of_stack_to_sysout(as_char)

    def input_to_field(self, name, as_char):
        self.main_method_instructions.append(instructions.aload(0))
        self.push_field_value_onto_stack(Builder.INPUT_INDEX)

        self.main_method_instructions.append(instructions.aaload())

        if as_char:
            self.main_method_instructions.append(instructions.bipush(0))
            char_at = self.output_class.pool.add_method_ref("java/lang/String", "charAt", "(I)C")
            self.main_method_instructions.append(instructions.invokevirtual(char_at))
        else:
            parse_int = self.output_class.pool.add_method_ref("java/lang/Integer", "parseInt", "(Ljava/lang/String;)I")
            self.main_method_instructions.append(instructions.invokestatic(parse_int))

        self.set_field_with_value_from_top_of_stack(name)
        self.increment_field(Builder.INPUT_INDEX)
        return self

    def increment_field(self, name):
        self.push_field_value_onto_stack(name)
        self.main_method_instructions.extend([
            instructions.bipush(1),
            instructions.iadd(),
        ])
        self.set_field_with_value_from_top_of_stack(name)
        return self

    def ast_dump(self, tree):
        for node in tree.get_children():
            self.ast_dump(node)

        assert isinstance(tree, AstNode)

        if isinstance(tree, BinaryOperator):
            operator_mapping = {
                Operators.ADD: instructions.iadd(),
                Operators.MULTIPLY: instructions.imul(),
            }
            try:
                self.main_method_instructions.append(operator_mapping[tree.op])
            except KeyError:
                raise CompilationError("No instruction specified to map {}".format(tree.op))
        elif isinstance(tree, Value):
            self.main_method_instructions.append(instructions.bipush(tree.value))
        elif isinstance(tree, DynamicValue):
            self.push_field_value_onto_stack(tree.field)
        elif isinstance(tree, Assign):
            self.set_field_with_value_from_top_of_stack(tree.var)
        elif isinstance(tree, PrintVariable):
            self.print_field(tree.field, tree.as_char)
        elif isinstance(tree, InputVariable):
            self.input_to_field(tree.field, tree.as_char)
        else:
            raise CompilationError("Unknown type of AST node {}".format(tree))

        return self
