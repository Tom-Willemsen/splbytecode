from java_class.access_modifiers import ACC_CLASS
from java_class.constant_pool.constant_pool import ConstantPool
from java_class.fields.field_table import FieldTable
from java_class.methods.method_table import MethodTable


class InvalidClassError(Exception):
    pass


class JavaClass(object):
    def __init__(self, name, use_defaults=True):
        self.name = name

        if use_defaults:
            self.pool_table = ConstantPool.generate_default(name)
            self.method_table = MethodTable(self.pool_table)
            self.field_table = FieldTable(self.pool_table)

            self.access_modifiers = [ACC_CLASS.PUBLIC, ACC_CLASS.SUPER]
            self.version = (0x35, 0)  # JDK 9 by default

    def check_valid(self):
        if self.name is None:
            raise InvalidClassError("Name should be set.")
        if self.pool_table is None:
            raise InvalidClassError("Pool table was not set.")
        if self.method_table is None:
            raise InvalidClassError("Method table was not set.")
        if self.field_table is None:
            raise InvalidClassError("Field table was not set.")
        if self.version is None or len(self.version) != 2:
            raise InvalidClassError("Version should be a tuple of two items (major, minor).")
        if self.access_modifiers is None:
            raise InvalidClassError("Access modifiers not set.")
