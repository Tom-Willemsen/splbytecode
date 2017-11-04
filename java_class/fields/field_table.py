from java_class.constant_pool.entry import EntryUtf8
from java_class.fields.field import Field


class FieldTable(object):
    """
    A java_class representing the field table in a .java_class file.
    """
    def __init__(self, constant_pool):
        self.fields = []
        self.constant_pool = constant_pool

    def add_field(self, name, descriptor, access_flags):
        name_index = self.constant_pool.add_entry(EntryUtf8(name))
        descriptor_index = self.constant_pool.add_entry(EntryUtf8(descriptor))

        for field in self.fields:
            if field.name_index == name_index and descriptor_index == descriptor_index:
                return

        field = Field(name_index, descriptor_index, access_flags, [])
        self.fields.append(field)

    def __iter__(self):
        return self.fields.__iter__()

    def __len__(self):
        return len(self.fields)