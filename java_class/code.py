from java_class.constant_pool_entry import utf8


class CodeAttribute(object):
    """
    Class specifying how a CodeAttribute object is outputted to the final .java_class file.
    """
    def __init__(self, constant_pool, code_specification):
        self.code_attribute_index = constant_pool.get_index(utf8("Code"))
        self.max_stack = code_specification.max_stack
        self.max_locals = code_specification.max_locals
        self.instructions = code_specification.instructions
        self.code_length = sum(len(instruction) for instruction in self.instructions)
        self.exception_table_length = 0
        self.attributes_count = 0


class CodeSpecification(object):
    """
    Code specification, free from .java_class file implementation details.
    """
    def __init__(self, instructions, max_stack, max_locals):
        self.instructions = instructions
        self.max_stack = max_stack
        self.max_locals = max_locals
