from java_class import access_modifiers
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
            self.version = (50, 0)  # JDK 9 by default

    def set_version(self, major, minor=0):
        self.version = (major, minor)

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

        field = Field(name_index, descriptor_index, access_flags)
        if field in self.fields:
            return

        self.fields.append(field)

    def check_valid(self):
        """
        Checks that the class is in a valid state for export.
        :return: None
        :raises: InvalidClassError if the class was not valid.
        """
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
    def __init__(self, name_index, descriptor_index, access_flags):
        self.name_index = name_index
        self.descriptor_index = descriptor_index
        self.access_flags = access_flags

    def __eq__(self, other):
        return self.name_index == other.name_index and self.descriptor_index == other.descriptor_index
