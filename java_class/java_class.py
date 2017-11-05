from java_class import access_modifiers
from java_class.byte_utils import u2
from java_class.constant_pool import ConstantPool
from java_class.constant_pool_entry import utf8


class InvalidClassError(Exception):
    pass


class JavaClass(object):
    def __init__(self, name, use_defaults=True):
        self.name = name

        if use_defaults:
            self.pool = ConstantPool.generate_default(name)
            self.methods = []
            self.fields = []

            self.access_modifiers = [access_modifiers.PUBLIC, access_modifiers.SUPER]
            self.version = (0x35, 0)  # JDK 9 by default

    def add_method(self, name, descriptor, access_flags, attributes):

        name_index = self.pool.get_index(utf8(name))
        descriptor_index = self.pool.get_index(utf8(descriptor))
        self.methods.append((name_index, descriptor_index, access_flags, attributes))

    def add_field(self, name, descriptor, access_flags):
        """
        Adds a field reference to the table. If it already exists, do nothing.
        """
        name_index = self.pool.get_index(utf8(name))
        descriptor_index = self.pool.get_index(utf8(descriptor))

        field = Field(name_index, descriptor_index, access_flags, [])
        if field in self.fields:
            return

        self.fields.append(field)

    def check_valid(self):
        if self.name is None:
            raise InvalidClassError("Name should be set.")
        if self.pool is None:
            raise InvalidClassError("Pool table was not set.")
        if self.methods is None:
            raise InvalidClassError("Method table was not set.")
        if len(self.methods) == 0:
            raise InvalidClassError("Method table was empty.")
        if self.fields is None:
            raise InvalidClassError("Field table was not set.")
        if self.version is None or len(self.version) != 2:
            raise InvalidClassError("Version should be a tuple of two items (major, minor).")
        if self.access_modifiers is None:
            raise InvalidClassError("Access modifiers not set.")


class Field(object):
    """
    Class representing a field in a .class file.
    """
    def __init__(self, name_index, descriptor_index, access_flags, attributes):
        self.name_index = name_index
        self.descriptor_index = descriptor_index
        self.access_flags = access_flags
        self.attributes = attributes

    def get_bytes(self):
        result = u2(self.access_flags) \
               + u2(self.name_index) \
               + u2(self.descriptor_index) \
               + u2(len(self.attributes))

        for attribute in self.attributes:
            result += attribute.get_bytes()

        return result

    def __eq__(self, other):
        return self.name_index == other.name_index and self.descriptor_index == other.descriptor_index


class CodeAttribute(object):
    """
    Class specifying how a CodeAttribute object is outputted to the final .java_class file.
    """
    def __init__(self, constant_pool, instructions, max_stack=32768, max_locals=32768):
        self.code_attribute_index = constant_pool.get_index(utf8("Code"))
        self.max_stack = max_stack
        self.max_locals = max_locals
        self.instructions = instructions
        self.code_length = sum(len(instruction) for instruction in self.instructions)
        self.exception_table_length = 0
        self.attributes_count = 0

    def __len__(self):
        return self.code_length
