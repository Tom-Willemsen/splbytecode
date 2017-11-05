import os

from java_class.access_modifiers import ACC_METHOD, ACC_FIELD
from java_class.attributes.code import CodeSpecification
from java_class.exporter import Exporter
from java_class.instructions import instructions
from java_class.methods.method_table import MethodSpecification
from java_class.java_class import JavaClass
from spl.ast import BinaryOperator, Operators, Value, Assign, DynamicValue, AstNode, PrintVariable


class CompilationError(Exception):
    pass


class Builder(object):
    """
    This java_class generates a valid java java_class file, ready for export.
    """
    def __init__(self, name):
        self.name = name
        self.output_class = JavaClass(name)
        self.pool_table = self.output_class.pool_table
        self.field_table = self.output_class.field_table
        self.code_specification = CodeSpecification([], 32768, 32768)

    def build(self):
        """
        This methods performs final transformations before export.
        """

        main_method = MethodSpecification("main", "([Ljava/lang/String;)V",
                                          ACC_METHOD.PUBLIC | ACC_METHOD.STATIC, self.code_specification)
        self.code_specification.instructions.append(instructions.Return())
        self.output_class.method_table.add_method(main_method)

        return self.output_class

    def set_field(self, name, value):
        """
        Sets a field with a constant value.
        """
        self.code_specification.instructions.extend([
            instructions.Bipush(value),
        ])
        self.set_field_with_value_from_top_of_stack(name)

    def set_field_with_value_from_top_of_stack(self, name):
        """
        Sets a field to have the value at the top of the stack.
        """
        self.field_table.add_field(name, "I", ACC_FIELD.PUBLIC | ACC_FIELD.STATIC)
        field_ref = self.pool_table.add_field_ref(self.name, name, "I")

        self.code_specification.instructions.extend([
            instructions.PutStatic(field_ref),
        ])

    def integer_at_top_of_stack_to_sysout(self):
        """
        The integer at the top of the stack is popped and printed to standard out.
        """
        printstream = self.pool_table.add_field_ref("java/lang/System", "out", "Ljava/io/PrintStream;")
        sysout_integer = self.pool_table.add_method_ref("java/io/PrintStream", "println", "(I)V")

        self.code_specification.instructions.extend([
            instructions.GetStatic(printstream),
            instructions.Swap(),
            instructions.InvokeVirtual(sysout_integer)
        ])

    def integer_at_top_of_stack_to_sysout_as_char(self):
        """
        The integer at the top of the stack is popped and printed to standard out.
        """
        printstream = self.pool_table.add_field_ref("java/lang/System", "out", "Ljava/io/PrintStream;")
        sysout_integer = self.pool_table.add_method_ref("java/io/PrintStream", "print", "(C)V")

        self.code_specification.instructions.extend([
            instructions.GetStatic(printstream),
            instructions.Swap(),
            instructions.I2c(),
            instructions.InvokeVirtual(sysout_integer)
        ])

    def multiply_integer_at_top_of_stack_by_two(self):
        self.code_specification.instructions.extend([
            instructions.Bipush(2),
            instructions.Imul(),
        ])

    def push_field_value_onto_stack(self, name):
        self.field_table.add_field(name, "I", ACC_FIELD.PUBLIC | ACC_FIELD.STATIC)
        field_ref = self.pool_table.add_field_ref(self.name, name, "I")

        self.code_specification.instructions.extend([
            instructions.GetStatic(field_ref),
        ])

    def print_field(self, name, as_char):
        self.push_field_value_onto_stack(name)
        if as_char:
            self.integer_at_top_of_stack_to_sysout_as_char()
        else:
            self.integer_at_top_of_stack_to_sysout()

    def ast_dump(self, tree):
        for node in tree.get_children():
            self.ast_dump(node)

        assert isinstance(tree, AstNode)

        if isinstance(tree, BinaryOperator):
            operator_mapping = {
                Operators.ADD: instructions.Iadd(),
                Operators.MULTIPLY: instructions.Imul(),
            }
            try:
                self.code_specification.instructions.append(operator_mapping[tree.op])
            except KeyError:
                raise CompilationError("No instruction specified to map {}".format(tree.op))
        elif isinstance(tree, Value):
            self.code_specification.instructions.append(instructions.Bipush(tree.value))
        elif isinstance(tree, DynamicValue):
            self.push_field_value_onto_stack(tree.field)
        elif isinstance(tree, Assign):
            self.set_field_with_value_from_top_of_stack(tree.var)
        elif isinstance(tree, PrintVariable):
            self.print_field(tree.field, tree.as_char)
        else:
            raise CompilationError("Unknown type of AST node {}".format(tree))
