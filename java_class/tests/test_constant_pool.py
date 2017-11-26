import unittest

from java_class.constant_pool import ConstantPool
from java_class.constant_pool_entry import utf8


class ConstantPoolTests(unittest.TestCase):

    def setUp(self):
        self.this_class = "ThisClass"
        self.super_class = "SuperClass"

    def test_GIVEN_a_default_constant_pool_THEN_it_contains_references_to_this_and_super(self):
        pool = ConstantPool.generate_default(self.this_class, self.super_class)
        
        self.assertIn(utf8(self.this_class), pool)
        self.assertIn(utf8(self.super_class), pool)

    def test_GIVEN_a_skeletal_pool_WHEN_getting_index_of_something_that_is_not_in_pool_THEN_index_is_returned(self):
        pool = ConstantPool.generate_default(self.this_class, self.super_class)

        item = utf8("Hello")
        self.assertNotIn(item, pool)
        length_of_pool_before_adding = len(pool)

        idx = pool.get_index(item)

        self.assertEqual(idx, length_of_pool_before_adding + 1)

    def test_WHEN_getting_index_of_something_already_in_pool_THEN_index_returned_and_length_of_pool_not_changed(self):
        pool = ConstantPool.generate_default(self.this_class, self.super_class)

        item = utf8("Hello")
        self.assertNotIn(item, pool)

        idx_before = pool.get_index(item)
        self.assertIn(item, pool)
        len_before = len(pool)

        idx_after = pool.get_index(item)
        self.assertIn(item, pool)
        len_after = len(pool)

        self.assertEqual(len_before, len_after)
        self.assertEqual(idx_after, idx_before)
