from java_class.byte_utils import u2


class Field(object):
    """
    Class representing a field in a .java_class file.
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