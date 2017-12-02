import operator
from functools import reduce
from zipfile import ZipFile
import os

import shutil

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

    def get_class_file_name(self):
        return "{}.class".format(self.output_class.name)

    def get_class_file_path(self, output_dir):
        return os.path.normpath(os.path.join(output_dir, self.get_class_file_name()))

    def export_as_file(self, output_dir):
        """
        Writes the contents of a .class file with the same name
        as the java_class in the order specified by the specification.
        """

        filepath = self.get_class_file_path(output_dir)

        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

        with open(filepath, "w+b") as f:
            self._write(f)

    def export_as_jar(self, output_dir):

        self.export_as_file(output_dir)

        manifest_dir = os.path.join(output_dir, "META-INF")
        manifest_path = os.path.join(manifest_dir, "MANIFEST.MF")

        os.mkdir(manifest_dir)

        with open(manifest_path, "w") as f:
            f.write('Manifest-Version: 1.0\nCreated-By: spl\nMain-Class: {}\n'.format(self.output_class.name))

        with ZipFile(os.path.join(output_dir, "{}.jar".format(self.output_class.name)), "w") as f:

            f.write(manifest_path, arcname=os.path.join("META-INF", "MANIFEST.MF"))

            f.write(self.get_class_file_path(output_dir), arcname=self.get_class_file_name())
            f.write(self.get_class_file_path(output_dir),
                    arcname=os.path.join(self.output_class.name.lower(), self.get_class_file_name()))

        os.remove(self.get_class_file_path(output_dir))
        shutil.rmtree(manifest_dir)

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
