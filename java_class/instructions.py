from java_class.byte_utils import u1, u2, u4, s4, s1


def voidreturn():
    return u1(0xB1)


def getstatic(field_index):
    return u1(0xB2) + u2(field_index)


def ldc(const_index):
    return u1(0x12) + u1(const_index)


def invokevirtual(method):
    return u1(0xB6) + u2(method)


def bipush(value):
    if value == -1:
        return u1(0x2)  # iconst_m1
    elif value == 0:
        return u1(0x3)  # iconst_0
    elif value == 1:
        return u1(0x4)  # iconst_1
    elif value == 2:
        return u1(0x5)  # iconst_2
    else:
        return u1(0x10) + s1(value)


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
    if idx == 0:
        return u1(0x2A)  # aload_0
    elif idx == 1:
        return u1(0x2B)  # aload_1
    elif idx == 2:
        return u1(0x2C)  # aload_2
    elif idx == 3:
        return u1(0x2D)  # aload_3
    else:
        return u1(0x19) + u1(idx)


def aaload():
    return u1(0x32)


def invokestatic(ref):
    return u1(0xB8) + u2(ref)


def goto_w(offset):
    return u1(0xC8) + s4(offset)


def nop():
    return u1(0)
