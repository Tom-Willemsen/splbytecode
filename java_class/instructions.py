from java_class.byte_utils import u1, u2


def voidreturn():
    return u1(0xB1)


def getstatic(field_index):
    return u1(0xB2) + u2(field_index)


def ldc(const_index):
    return u1(0x12) + u1(const_index)


def invokevirtual(method):
    return u1(0xB6) + u2(method)


def bipush(value):
    return u1(0x10) + u1(value, signed=True)


def swap():
    return u1(0x5F)


def iadd():
    return u1(0x60)


def imul():
    return u1(0x68)


def putfield(ref):
    return u1(0xB5) + u2(ref)


def putstatic(ref):
    return u1(0xB3) + u2(ref)


def getfield(ref):
    return u1(0xB4) + u2(ref)


def i2c():
    return u1(0x92)


def aload(idx):
    return u1(0x19) + u1(idx)


def aaload():
    return u1(0x32)


def invokestatic(ref):
    return u1(0xB8) + u2(ref)
