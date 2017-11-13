from intermediate import ast, operators
from java_class import access_modifiers, instructions
from java_class.java_class import JavaClass
from java_class.instructions import goto_w


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

        try:
            code = Builder._compute_gotos(self.code)
        except KeyError as e:
            raise CompilationError("Couldn't compute gotos because label '{}' was invalid.".format(e))

        self.output_class.add_method("main", "([Ljava/lang/String;)V", Builder.MAIN_METHOD_ACCESS_MODIFIERS, code)

        valid, message = self.output_class.check_valid()
        if not valid:
            raise CompilationError("Can't build class: {}".format(message))

        return self.output_class

    @staticmethod
    def _compute_gotos(code):

        def length_of_code_up_to_instruction(num):
            return sum(len(i) for i in code[0:num])

        labels = {}

        for instruction in code:
            if isinstance(instruction, Goto) and instruction.destination:
                idx = code.index(Goto(instruction.name, True))
                labels[instruction.name] = length_of_code_up_to_instruction(idx)
                code[idx] = instructions.nop()

        for instruction in code:
            if isinstance(instruction, Goto) and not instruction.destination:
                idx = code.index(instruction)
                code[idx] = goto_w(labels[instruction.name] - length_of_code_up_to_instruction(idx))

        return code

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

        self.code.append(instructions.putstatic(field_ref))
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
            operators.Operators.ADD: instructions.iadd(),
            operators.Operators.MULTIPLY: instructions.imul(),
        }
        try:
            self.code.append(operator_mapping[node.op])
        except KeyError:
            raise CompilationError("No instruction specified to map {}".format(node.op))

        return self

    def asl_dump(self, asl):

        mapping = {
            ast.Goto: lambda: self.code.append(Goto(item.name, False)),
            ast.Label: lambda: self.code.append(Goto(item.name, True)),
            ast.BinaryOperator: lambda: self.add_operator_instruction_from_node(item),
            ast.Value: lambda: self.code.append(instructions.bipush(item.value)),
            ast.DynamicValue: lambda: self.push_field_value_onto_stack(item.field),
            ast.Assign: lambda: self.set_field_with_value_from_top_of_stack(item.var),
            ast.PrintVariable: lambda: self.print_field(item.field, item.as_char),
            ast.InputVariable: lambda: self.input_to_field(item.field, item.as_char),
            ast.NoOp: lambda: None
        }

        for item in asl:
            for node_type in mapping.keys():
                if isinstance(item, node_type):
                    mapping[node_type]()
                    break
            else:
                raise CompilationError("No rule to map {}".format(item))

        return self


class Goto(object):
    def __init__(self, name, destination):
        self.name = name
        self.destination = destination

    def __len__(self):
        return len(instructions.nop() if self.destination else instructions.goto_w(0))

    def __eq__(self, other):
        if not isinstance(other, Goto):
            return False
        return self.name == other.name and self.destination == other.destination
