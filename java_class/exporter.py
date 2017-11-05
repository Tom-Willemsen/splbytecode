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
        stream.write(u2(len(self.output_class.pool_table) + 1))
        for entry in self.output_class.pool_table:
            stream.write(entry)

        # Access modifiers
        stream.write(u2(reduce(operator.xor, self.output_class.access_modifiers)))

        # "This" and "Super" classes
        stream.write(u2(self.output_class.pool_table.this_index))
        stream.write(u2(self.output_class.pool_table.super_index))

        # Interface table (not implemented)
        stream.write(u2(0))

        # Field table
        stream.write(u2(len(self.output_class.field_table)))
        for field in self.output_class.field_table:
            stream.write(u2(field.access_flags))
            stream.write(u2(field.name_index))
            stream.write(u2(field.descriptor_index))
            stream.write(u2(len(field.attributes)))

            # Attributes table within field table
            for _ in field.attributes:
                raise NotImplementedError("Writing fields with attributes is not supported.")

        # Methods table
        stream.write(u2(len(self.output_class.method_table)))
        for method in self.output_class.method_table:
            stream.write(u2(method.access_flags))
            stream.write(u2(method.name_index))
            stream.write(u2(method.descriptor_index))
            stream.write(u2(len(method.attributes)))

            # Attributes table within method table
            for attribute in method.attributes:
                stream.write(u2(attribute.code_attribute_index))
                stream.write(u4(12 + attribute.code_length))
                stream.write(u2(attribute.max_stack))
                stream.write(u2(attribute.max_locals))
                stream.write(u4(attribute.code_length))
                for instruction in attribute.instructions:
                    stream.write(instruction)
                stream.write(u2(attribute.exception_table_length))
                stream.write(u2(attribute.attributes_count))

        # Attributes table (not implemented)
        stream.write(u2(0))
