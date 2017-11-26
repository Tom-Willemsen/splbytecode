import unittest

from java_class import access_modifiers
from java_class.constant_pool_entry import utf8
from java_class.java_class import JavaClass, InvalidClassError


class JavaClassTests(unittest.TestCase):
    def test_GIVEN_a_default_java_class_WHEN_checking_validity_THEN_error(self):
        klass = JavaClass("Hello")

        with self.assertRaises(InvalidClassError):
            klass.check_valid()

    def test_GIVEN_a_default_java_class_with_a_method_and_version_added_WHEN_checking_validity_THEN_valid(self):
        klass = JavaClass("Hello")

        klass.add_method("main", "abc", access_modifiers.PUBLIC, [])
        klass.set_version(1, 1)

        try:
            klass.check_valid()
        except InvalidClassError as e:
            self.fail("Class should not have been invalid: {}".format(e))

    def test_GIVEN_a_method_is_added_to_a_class_THEN_it_has_the_relevant_attributes_and_constant_pool_entries(self):

        klass = JavaClass("Hello")

        name = "main"
        descriptor = "abc"
        access = access_modifiers.PUBLIC
        code = []
        klass.add_method(name, descriptor, access, code)

        self.assertEqual(len(klass.methods), 1)

        name_index, descriptor_index, access_flags, attributes = klass.methods[0]

        self.assertIn(utf8(name), klass.pool)
        self.assertIn(utf8(descriptor), klass.pool)
        self.assertEqual(access_flags, access)
        self.assertIn(utf8("Code"), klass.pool)
        self.assertEqual(attributes[0]["instructions"], code)
        self.assertEqual(attributes[0]["code_length"], sum(len(c) for c in code))

    def test_GIVEN_a_field_is_added_to_a_class_THEN_it_has_the_relevant_constant_pool_entries(self):

        klass = JavaClass("Hello")

        name = "field_name"
        descriptor = "ok"
        access = access_modifiers.PUBLIC

        klass.add_field(name, descriptor, access)

        self.assertEqual(len(klass.fields), 1)

        self.assertIn(utf8(name), klass.pool)
        self.assertIn(utf8(descriptor), klass.pool)

    def test_GIVEN_two_identical_fields_added_to_a_class_THEN_the_class_only_contains_the_field_once(self):

        klass = JavaClass("Hello")

        name = "field_name"
        descriptor = "ok"
        access = access_modifiers.PUBLIC

        klass.add_field(name, descriptor, access)
        klass.add_field(name, descriptor, access)

        self.assertEqual(len(klass.fields), 1)
