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

    def add_method(self, name, descriptor, access_flags, instructions):

        attributes = [{
            "code_attribute_index": self.pool.get_index(utf8("Code")),
            "instructions": instructions,
            "code_length": sum(len(instruction) for instruction in instructions),
            "max_locals": 32768,
            "max_stack": 32768,
        }]

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
        """
        Checks that the class is in a valid state for export.
        :return: Tuple of ((bool) is_valid, (str) reason).
        """
        if self.name is None:
            return False, "Name should be set."
        if self.pool is None:
            return False, "Pool table was not set."
        if self.methods is None:
            return False, "Method table was not set."
        if len(self.methods) == 0:
            return False, "Method table was empty."
        if self.fields is None:
            return False, "Field table was not set."
        if self.version is None or len(self.version) != 2:
            return False, "Version should be a tuple of two items (major, minor)."
        if self.access_modifiers is None:
            return False, "Access modifiers not set."
        return True, "OK"


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
