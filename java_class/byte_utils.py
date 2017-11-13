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


def int_to_bytes(i, l, signed):
    """
    Converts an integer to bytes.
    :param i: The integer to convert
    :param l: The number of bytes to be used in the output.
    :param signed: Whether the output should be signed.
    :return: The integer as bytes with length l.
    """
    return int(i).to_bytes(l, 'big', signed=signed)


def u1(i):
    """
    1 byte unsigned int
    """
    return int_to_bytes(i, 1, False)


def u2(i):
    """
    2 byte unsigned int
    """
    return int_to_bytes(i, 2, False)


def u4(i):
    """
    4 byte unsigned int
    """
    return int_to_bytes(i, 4, False)


def s1(i):
    """
    1 byte signed int
    """
    return int_to_bytes(i, 1, True)


def s2(i):
    """
    2 byte signed int
    """
    return int_to_bytes(i, 2, True)


def s4(i):
    """
    4 byte signed int
    """
    return int_to_bytes(i, 4, True)
