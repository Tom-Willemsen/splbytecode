from java_class.byte_utils import str_to_byte, u1, u2

id_Class = 7
id_Fieldref = 9
id_Methodref = 10
id_InterfaceMethodref = 11
id_String = 8
id_Integer = 3
id_Float = 4
id_Long = 5
id_Double = 6
id_NameAndType = 12
id_Utf8 = 1
id_MethodHandle = 15
id_MethodType = 16
id_InvokeDynamic = 18


class Entry(object):
    """
    Abstract constant pool entry. Not intended to be used directly.
    """
    def get_bytes(self):
        raise NotImplementedError


class EntryClass(Entry):
    """
    A constant pool entry referring to a java_class.
    """
    def __init__(self, name_index):
        self.name_index = name_index

    def get_bytes(self):
        return u1(id_Class) \
               + u2(self.name_index)


class EntryMethodRef(Entry):
    """
    A constant pool entry referring to a method.
    """
    def __init__(self, class_index, name_and_type_index):
        self.class_index = class_index
        self.name_and_type_index = name_and_type_index

    def get_bytes(self):
        return u1(id_Methodref) \
               + u2(self.class_index) \
               + u2(self.name_and_type_index)


class EntryFieldRef(Entry):
    """
    A constant pool entry referring to a field.
    """
    def __init__(self, class_index, name_and_type_index):
        self.class_index = class_index
        self.name_and_type_index = name_and_type_index

    def get_bytes(self):
        return u1(id_Fieldref) \
               + u2(self.class_index) \
               + u2(self.name_and_type_index)


class EntryUtf8(Entry):
    """
    A constant pool entry representing a utf-8 string.
    """
    def __init__(self, text):
        assert isinstance(text, str)
        self.text = text

    def get_bytes(self):
        return u1(id_Utf8) \
               + u2(len(self.text)) \
               + str_to_byte(self.text)


class EntryNameAndType(Entry):
    """
    A constant pool entry referring to a name-type pair.
    """
    def __init__(self, name_index, descriptor_index):
        self.name_index = name_index
        self.descriptor_index = descriptor_index

    def get_bytes(self):
        return u1(id_NameAndType) \
               + u2(self.name_index) \
               + u2(self.descriptor_index)


class EntryString(Entry):
    """
    A constant pool entry representing a string.
    """
    def __init__(self, utf8str):
        self.utf8str = utf8str

    def get_bytes(self):
        return u1(id_String) \
               + u2(self.utf8str)
