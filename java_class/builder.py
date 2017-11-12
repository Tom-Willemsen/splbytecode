from intermediate.ast import BinaryOperator, Operators, Value, Assign, DynamicValue, PrintVariable, \
    InputVariable, Goto, Label, NoOp
from java_class import access_modifiers, instructions, flow
from java_class.java_class import JavaClass


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
        self.code = []

        self.set_field(Builder.INPUT_INDEX, 0)

    def build(self):
        """
        This methods performs final transformations before export.
        """
        self.code.append(instructions.voidreturn())

        self.output_class.add_method("main", "([Ljava/lang/String;)V", Builder.MAIN_METHOD_ACCESS_MODIFIERS,
                                     flow.compute_gotos(self.code))

        valid, message = self.output_class.check_valid()
        if not valid:
            raise CompilationError("Can't build class: {}".format(message))

        return self.output_class

    def set_field(self, name, value):
        """
        Sets a field with a constant value.
        """
        self.code.append(instructions.bipush(value))
        self.set_field_with_value_from_top_of_stack(name)
        return self

    def set_field_with_value_from_top_of_stack(self, name):
        """
        Sets a field to have the value at the top of the stack.
        """
        self.output_class.add_field(name, "I", Builder.FIELD_ACCESS_MODIFIERS)
        field_ref = self.output_class.pool.add_field_ref(self.name, name, "I")

        self.code.extend([
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

        self.code.extend([
            instructions.getstatic(printstream),
            instructions.swap(),
        ])

        if as_char:
            self.code.append(instructions.i2c())

        self.code.append(instructions.invokevirtual(sysout))
        return self

    def multiply_integer_at_top_of_stack_by_two(self):
        self.code.extend([
            instructions.bipush(2),
            instructions.imul(),
        ])
        return self

    def push_field_value_onto_stack(self, name):
        # Ensures the field exists otherwise getting it will cause a runtime error.
        self.output_class.add_field(name, "I", Builder.FIELD_ACCESS_MODIFIERS)

        field_ref = self.output_class.pool.add_field_ref(self.name, name, "I")
        self.code.append(instructions.getstatic(field_ref))
        return self

    def print_field(self, name, as_char):
        self.push_field_value_onto_stack(name)
        self.integer_at_top_of_stack_to_sysout(as_char)

    def input_to_field(self, name, as_char):
        self.code.append(instructions.aload(0))
        self.push_field_value_onto_stack(Builder.INPUT_INDEX)

        self.code.append(instructions.aaload())

        if as_char:
            self.code.append(instructions.bipush(0))
            char_at = self.output_class.pool.add_method_ref("java/lang/String", "charAt", "(I)C")
            self.code.append(instructions.invokevirtual(char_at))
        else:
            parse_int = self.output_class.pool.add_method_ref("java/lang/Integer", "parseInt", "(Ljava/lang/String;)I")
            self.code.append(instructions.invokestatic(parse_int))

        self.set_field_with_value_from_top_of_stack(name)
        self.increment_field(Builder.INPUT_INDEX)
        return self

    def increment_field(self, name):
        self.push_field_value_onto_stack(name)
        self.code.extend([
            instructions.bipush(1),
            instructions.iadd(),
        ])
        self.set_field_with_value_from_top_of_stack(name)
        return self

    def add_operator_instruction_from_node(self, node):
        operator_mapping = {
            Operators.ADD: instructions.iadd(),
            Operators.MULTIPLY: instructions.imul(),
        }
        try:
            self.code.append(operator_mapping[node.op])
        except KeyError:
            raise CompilationError("No instruction specified to map {}".format(node.op))

    def asl_dump(self, asl):

        mapping = {
            Goto: lambda item: self.code.append(flow.Goto(item.name, False)),
            Label: lambda item: self.code.append(flow.Goto(item.name, True)),
            BinaryOperator: lambda item: self.add_operator_instruction_from_node(item),
            Value: lambda item: self.code.append(instructions.bipush(item.value)),
            DynamicValue: lambda item: self.push_field_value_onto_stack(item.field),
            Assign: lambda item: self.set_field_with_value_from_top_of_stack(item.var),
            PrintVariable: lambda item: self.print_field(item.field, item.as_char),
            InputVariable: lambda item: self.input_to_field(item.field, item.as_char),
            NoOp: lambda item: None
        }

        for item in asl:
            for node_type in mapping.keys():
                if isinstance(item, node_type):
                    mapping[node_type](item)
                    break
            else:
                raise CompilationError("No rule to map {}".format(item))

        return self
