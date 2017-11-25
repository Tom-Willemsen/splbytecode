import operator
import os
from functools import reduce

from java_class.byte_utils import u4, u2


class Exporter(object):
    """
    Exports the output of the Compiler java_class to disk, in the .java_class file format documented at
    https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-4.html
    """

    JAVA_FILE_HEADER = 0xCAFEBABE  # Constant header bytes

    def __init__(self, output_class):
        output_class.check_valid()
        self.output_class = output_class

    def export_as_file(self, output_dir):
        """
        Writes the contents of a .java_class file with the same name
        as the java_class in the order specified by the specification.
        """
        filename = os.path.join(output_dir, "{}.class".format(self.output_class.name))

        with open(filename, "w+b") as f:
            self._write(f)

    def _write(self, stream):
        # Java java_class file header (constant bytes + versions).
        stream.write(u4(Exporter.JAVA_FILE_HEADER))
        stream.write(u2(self.output_class.version[1]))
        stream.write(u2(self.output_class.version[0]))

        # Pool table
        stream.write(u2(len(self.output_class.pool) + 1))
        for entry in self.output_class.pool:
            stream.write(entry)

        # Access modifiers
        stream.write(u2(reduce(operator.xor, self.output_class.access_modifiers)))

        # "This" and "Super" classes
        stream.write(u2(self.output_class.pool.this_index))
        stream.write(u2(self.output_class.pool.super_index))

        # Interface table (not implemented)
        stream.write(u2(0))

        # Field table
        stream.write(u2(len(self.output_class.fields)))
        for field in self.output_class.fields:
            stream.write(u2(field.access_flags))
            stream.write(u2(field.name_index))
            stream.write(u2(field.descriptor_index))
            stream.write(u2(0))  # Writing fields with attributes has not been implemented.

        # Methods table
        stream.write(u2(len(self.output_class.methods)))
        for name_index, descriptor_index, access_flags, attributes in self.output_class.methods:
            stream.write(u2(access_flags))
            stream.write(u2(name_index))
            stream.write(u2(descriptor_index))
            stream.write(u2(len(attributes)))

            # Attributes table within method table (e.g. contains "Code" attribute)
            for attribute in attributes:
                stream.write(u2(attribute["code_attribute_index"]))
                stream.write(u4(12 + attribute["code_length"]))
                stream.write(u2(attribute["max_stack"]))
                stream.write(u2(attribute["max_locals"]))
                stream.write(u4(attribute["code_length"]))
                for instruction in attribute["instructions"]:
                    stream.write(instruction)
                stream.write(u2(0))  # Exception table not implemented
                stream.write(u2(0))  # Attributes of attributes not implemented

        # Attributes table (not implemented)
        stream.write(u2(0))
