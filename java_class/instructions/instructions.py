from java_class.byte_utils import u1, u2


class AbstractInstruction(object):
    def get_bytes(self):
        raise NotImplementedError


class Return(AbstractInstruction):
    def __init__(self):
        pass

    def get_bytes(self):
        return u1(0xB1)

    def __len__(self):
        return 1


class GetStatic(AbstractInstruction):
    def __init__(self, field_index):
        self.field_index = field_index

    def get_bytes(self):
        return u1(0xB2) \
               + u2(self.field_index)

    def __len__(self):
        return 3


class Ldc(AbstractInstruction):
    def __init__(self, const_index):
        self.const_index = const_index

    def get_bytes(self):
        return u1(0x12) \
               + u1(self.const_index)

    def __len__(self):
        return 2


class InvokeVirtual(AbstractInstruction):
    def __init__(self, method):
        self.method = method

    def get_bytes(self):
        return u1(0xB6) \
               + u2(self.method)

    def __len__(self):
        return 3


class Bipush(AbstractInstruction):
    def __init__(self, value):
        self.value = value

    def get_bytes(self):
        return u1(0x10) \
                + u1(self.value, signed=True)

    def __len__(self):
        return 2


class Swap(AbstractInstruction):
    def get_bytes(self):
        return u1(0x5F)

    def __len__(self):
        return 1


class Iadd(AbstractInstruction):
    def get_bytes(self):
        return u1(0x60)

    def __len__(self):
        return 1


class Imul(AbstractInstruction):
    def get_bytes(self):
        return u1(0x68)

    def __len__(self):
        return 1


class PutField(AbstractInstruction):
    def __init__(self, ref):
        self.ref = ref

    def get_bytes(self):
        return u1(0xB5) \
                + u2(self.ref)

    def __len__(self):
        return 3


class PutStatic(AbstractInstruction):
    def __init__(self, ref):
        self.ref = ref

    def get_bytes(self):
        return u1(0xB3) \
                + u2(self.ref)

    def __len__(self):
        return 3


class GetField(AbstractInstruction):
    def __init__(self, ref):
        self.ref = ref

    def get_bytes(self):
        return u1(0xB4) \
                + u2(self.ref)

    def __len__(self):
        return 3
