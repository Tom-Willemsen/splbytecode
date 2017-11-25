from java_class.constant_pool_entry import utf8, class_ref, name_and_type, method_ref, field_ref


class ConstantPool(object):
    """
    A java_class representing the constant pool in a .java_class file.
    """
    def __init__(self):
        self._pool = []

        self.this_index = None
        self.this_utf8_index = None
        self.super_index = None
        self.super_utf8_index = None

    def get_index(self, entry):
        """
        If the entry was already in the pool, return the 1-based index of the existing entry.

        If not, adds the entry to the pool and returns the (1-based) index at which it was inserted.

        This ensures that there aren't duplicated entries in the constant pool.
        """
        if entry in self._pool:
            return self._pool.index(entry) + 1

        self._pool.append(entry)
        return len(self._pool)

    def __iter__(self):
        return self._pool.__iter__()

    def __len__(self):
        return len(self._pool)

    def add_method_ref(self, defining_class, name, type):
        defining_class_index = self.get_index(class_ref(self.get_index(utf8(defining_class))))
        name_and_type_index = self.get_index(name_and_type(self.get_index(utf8(name)), self.get_index(utf8(type))))
        return self.get_index(method_ref(defining_class_index, name_and_type_index))

    def add_field_ref(self, defining_class, name, type):
        defining_class_index = self.get_index(class_ref(self.get_index(utf8(defining_class))))
        name_and_type_index = self.get_index(name_and_type(self.get_index(utf8(name)), self.get_index(utf8(type))))
        return self.get_index(field_ref(defining_class_index, name_and_type_index))

    @staticmethod
    def generate_default(this_class, super_class="java/lang/Object"):
        """
        A convenience method to quickly generate a skeletal constant pool, with "this" and "super" set.
        """
        pool = ConstantPool()
        pool.this_class = this_class
        pool.super_class = super_class

        pool.this_utf8_index = pool.get_index(utf8(this_class))
        pool.this_index = pool.get_index(class_ref(pool.this_utf8_index))

        pool.super_utf8_index = pool.get_index(utf8(super_class))
        pool.super_index = pool.get_index(class_ref(pool.super_utf8_index))

        return pool
