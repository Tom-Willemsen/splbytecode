def str_to_byte(text):
    """
    Converts a string to it's byte representation (1 byte per character)
    :param text: The input string
    :return: The string converted to bytes
    """
    result = bytes()
    for char in text:
        b = ord(char)

        # See https://docs.oracle.com/javase/specs/jvms/se7/html/jvms-4.html#jvms-4.4.7
        # These characters are allowed in principle but have some special handling which has not been implemented.
        if b == 0 or 0xF0 <= b <= 0xFF:
            raise ValueError("The character with code {} is not allowed".format(b))

        result += u1(b)
    return result


def u1(i, signed=False):
    """
    Java java_class file u1 type
    """
    return int(i).to_bytes(1, 'big', signed=signed)


def u2(i, signed=False):
    """
    Java java_class file u2 type
    """
    return int(i).to_bytes(2, 'big', signed=signed)


def u4(i, signed=False):
    """
    Java java_class file u4 type
    """
    return int(i).to_bytes(4, 'big', signed=signed)
