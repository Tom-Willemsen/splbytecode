from java_class.constant_pool.entry import EntryUtf8, EntryClass, EntryNameAndType, EntryMethodRef, EntryFieldRef


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

    def add_entry(self, entry):
        """
        Adds the entry to the pool. Returns the (1-based) index at which it was inserted.

        If the entry was already in the pool, return the index of the existing entry instead.
        This ensures that there aren't duplicated entries in the constant pool.
        """
        for e in self._pool:
            if e.get_bytes() == entry.get_bytes():
                return self._pool.index(e) + 1

        self._pool.append(entry)
        return len(self._pool)

    def __iter__(self):
        return self._pool.__iter__()

    def __len__(self):
        return len(self._pool)

    def add_method_ref(self, defining_class, name, type):
        defining_class_utf8_index = self.add_entry(EntryUtf8(defining_class))
        defining_class_index = self.add_entry(EntryClass(defining_class_utf8_index))
        name_index = self.add_entry(EntryUtf8(name))
        type_index = self.add_entry(EntryUtf8(type))
        name_and_type_index = self.add_entry(EntryNameAndType(name_index, type_index))

        return self.add_entry(EntryMethodRef(defining_class_index, name_and_type_index))

    def add_field_ref(self, defining_class, name, type):
        defining_class_utf8_index = self.add_entry(EntryUtf8(defining_class))
        defining_class_index = self.add_entry(EntryClass(defining_class_utf8_index))
        name_index = self.add_entry(EntryUtf8(name))
        type_index = self.add_entry(EntryUtf8(type))
        name_and_type_index = self.add_entry(EntryNameAndType(name_index, type_index))

        return self.add_entry(EntryFieldRef(defining_class_index, name_and_type_index))

    @staticmethod
    def generate_default(this_class="SplProg", super_class="java/lang/Object", add_default_constructor=True):
        """
        A convenience method to quickly add the necessary data to the constant pool for the .java_class file to be valid.
        """
        pool = ConstantPool()
        pool.this_class = this_class
        pool.super_class = super_class

        def add_this_and_super(pool):
            pool.this_utf8_index = pool.add_entry(EntryUtf8(this_class))
            pool.this_index = pool.add_entry(EntryClass(pool.this_utf8_index))

            pool.super_utf8_index = pool.add_entry(EntryUtf8(super_class))
            pool.super_index = pool.add_entry(EntryClass(pool.super_utf8_index))
            return pool

        add_this_and_super(pool)
        return pool
