from java_class.attributes.code import CodeAttribute
from java_class.constant_pool.entry import utf8


class MethodTable(object):
    """
    A java_class representing the method table in a .java_class file.
    """
    def __init__(self, constant_pool):
        self.methods = []
        self.constant_pool = constant_pool

    def add_method(self, method_specification):
        name_index = self.constant_pool.get_index(utf8(method_specification.name))
        descriptor_index = self.constant_pool.get_index(utf8(method_specification.descriptor))
        access_flags = method_specification.access_flags
        code_specification = method_specification.code_specification
        self.methods.append(Method(name_index,
                                   descriptor_index,
                                   access_flags,
                                   [CodeAttribute(self.constant_pool, code_specification)]))

    def __iter__(self):
        return self.methods.__iter__()

    def __len__(self):
        return len(self.methods)


class Method(object):
    """
    Class representing a method in a .java_class file.
    """
    def __init__(self, name_index, descriptor_index, access_flags, attributes):
        self.name_index = name_index
        self.descriptor_index = descriptor_index
        self.access_flags = access_flags
        self.attributes = attributes


class MethodSpecification(object):
    """
    A method specification free from the implementation details of a .java_class file.
    """
    def __init__(self, name, descriptor, access_flags, code_specification):
        self.access_flags = access_flags
        self.name = name
        self.descriptor = descriptor
        self.code_specification = code_specification
