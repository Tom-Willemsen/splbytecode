from __future__ import absolute_import

from java_class.byte_utils import str_to_byte, u1, u2

"""
Constant pool entry types as given in the java class file documentation.
"""
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


def class_ref(name_index):
    return u1(id_Class) \
           + u2(name_index)


def method_ref(class_index, name_and_type_index):
    return u1(id_Methodref) \
           + u2(class_index) \
           + u2(name_and_type_index)


def field_ref(class_index, name_and_type_index):
    return u1(id_Fieldref) \
           + u2(class_index) \
           + u2(name_and_type_index)


def utf8(text):
    return u1(id_Utf8) \
           + u2(len(text)) \
           + str_to_byte(text)


def name_and_type(name_index, descriptor_index):
    return u1(id_NameAndType) \
           + u2(name_index) \
           + u2(descriptor_index)


def string(utf8str):
    return u1(id_String) \
           + u2(utf8str)
