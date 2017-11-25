from __future__ import absolute_import

from intermediate import ast, operators
from java_class import access_modifiers, instructions
from java_class.java_class import JavaClass, InvalidClassError
from java_class.instructions import goto_w, ifeq


class CompilationError(Exception):
    pass


class Builder(object):
    """
    Builder class for a .class file. Contains methods for performing abstracted operations
    (reading/writing from fields, invoking methods, etc).
    """

    # Variable used to keep track of how many inputs have been "used up" from 'String[] args'.
    INPUT_INDEX = "$input_index"

    # Variable used to keep track of the result of the last conditional statement.
    CONDITIONAL = "$conditional"

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

        self._set_field(Builder.INPUT_INDEX, 0)
        self._set_field(Builder.CONDITIONAL, 0)

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

        try:
            self.output_class.check_valid()
        except InvalidClassError as e:
            raise CompilationError("Can't build class: {}".format(e))

        return self.output_class

    @staticmethod
    def _compute_gotos(code):

        def length_of_code_up_to_instruction(num):
            return sum(len(i) for i in code[0:num])

        labels = {}

        for instruction in code:
            if isinstance(instruction, Label):
                idx = code.index(instruction)
                labels[instruction.name] = length_of_code_up_to_instruction(idx)
                code[idx] = instructions.nop()

        for instruction in code:
            if isinstance(instruction, Goto):
                idx = code.index(instruction)
                offset = labels[instruction.name] - length_of_code_up_to_instruction(idx)
                code[idx] = ifeq(offset) if instruction.conditional else goto_w(offset)

        return code

    def _set_field(self, name, value):
        """
        Sets a field with a constant value.
        """
        self.code.append(instructions.bipush(value))
        self._set_field_with_value_from_top_of_stack(name)

    def _set_field_with_value_from_top_of_stack(self, name):
        """
        Sets a field to have the value at the top of the stack.
        """
        self.output_class.add_field(name, "I", Builder.FIELD_ACCESS_MODIFIERS)
        field_ref = self.output_class.pool.add_field_ref(self.name, name, "I")

        self.code.append(instructions.putstatic(field_ref))

    def _integer_at_top_of_stack_to_sysout(self, as_char):
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

    def _multiply_integer_at_top_of_stack_by_two(self):
        self.code.extend([
            instructions.bipush(2),
            instructions.imul(),
        ])

    def _push_field_value_onto_stack(self, name):
        # Ensures the field exists otherwise getting it will cause a runtime error.
        self.output_class.add_field(name, "I", Builder.FIELD_ACCESS_MODIFIERS)

        field_ref = self.output_class.pool.add_field_ref(self.name, name, "I")
        self.code.append(instructions.getstatic(field_ref))

    def _print_field(self, name, as_char):
        self._push_field_value_onto_stack(name)
        self._integer_at_top_of_stack_to_sysout(as_char)

    def _input_to_field(self, name, as_char):
        self.code.append(instructions.aload(0))
        self._push_field_value_onto_stack(Builder.INPUT_INDEX)

        self.code.append(instructions.aaload())

        if as_char:
            self.code.append(instructions.bipush(0))
            char_at = self.output_class.pool.add_method_ref("java/lang/String", "charAt", "(I)C")
            self.code.append(instructions.invokevirtual(char_at))
        else:
            parse_int = self.output_class.pool.add_method_ref("java/lang/Integer", "parseInt", "(Ljava/lang/String;)I")
            self.code.append(instructions.invokestatic(parse_int))

        self._set_field_with_value_from_top_of_stack(name)
        self._increment_field(Builder.INPUT_INDEX)

    def _increment_field(self, name):
        self._push_field_value_onto_stack(name)
        self.code.extend([
            instructions.bipush(1),
            instructions.iadd(),
        ])
        self._set_field_with_value_from_top_of_stack(name)

    def _add_operator_instruction_from_node(self, node):
        operator_mapping = {
            operators.Operators.ADD: instructions.iadd(),
            operators.Operators.MULTIPLY: instructions.imul(),
        }
        try:
            self.code.append(operator_mapping[node.op])
        except KeyError:
            raise CompilationError("No instruction specified to map {}".format(node.op))

    def _compare(self, field1, field2):
        self._push_field_value_onto_stack(field1)
        self.code.append(instructions.i2l())
        self._push_field_value_onto_stack(field2)
        self.code.append(instructions.i2l())
        self.code.append(instructions.lcmp())
        self._set_field_with_value_from_top_of_stack(Builder.CONDITIONAL)

    def _add_conditional_goto(self, name):
        self._push_field_value_onto_stack(Builder.CONDITIONAL)
        self.code.append(Goto(name, True))

    def asl_dump(self, asl):

        mapping = {
            ast.Goto: lambda: self.code.append(Goto(item.name)),
            ast.ConditionalGoto: lambda: self._add_conditional_goto(item.name),
            ast.Label: lambda: self.code.append(Label(item.name)),
            ast.BinaryOperator: lambda: self._add_operator_instruction_from_node(item),
            ast.Value: lambda: self.code.append(instructions.bipush(item.value)),
            ast.DynamicValue: lambda: self._push_field_value_onto_stack(item.field),
            ast.Assign: lambda: self._set_field_with_value_from_top_of_stack(item.var),
            ast.PrintVariable: lambda: self._print_field(item.field, item.as_char),
            ast.InputVariable: lambda: self._input_to_field(item.field, item.as_char),
            ast.NoOp: lambda: None,
            ast.Compare: lambda: self._compare(item.var1, item.var2),
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
    """
    Placeholder instruction for GOTOs until they are computed.
    """
    def __init__(self, name, conditional=False):
        self.name = name
        self.conditional = conditional

    def __len__(self):
        return len(instructions.ifeq(0) if self.conditional else instructions.goto_w(0))


class Label(object):
    """
    Placeholder instruction for GOTO jump points until they are computed and replaced with NOOPs.
    """
    def __init__(self, name):
        self.name = name

    def __len__(self):
        return len(instructions.nop())

    def __eq__(self, other):
        if not isinstance(other, Label):
            return False
        return self.name == other.name
