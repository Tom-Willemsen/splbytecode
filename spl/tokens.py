class Token(object):
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __str__(self):
        result = "{}".format(self.type)
        if self.value is not None:
            result += ": " + str(self.value)
        return result

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.type == other.type


class TokenTypes(object):
    Adj = "Adj"
    NoOp = "NoOp"
    Eof = "Eof"
    Scene = "Scene"
    Act = "Act"
    Name = "Name"
    Noun = "Noun"
    Add = "Add"
    FullStop = "."
    Comma = ","
    Colon = ":"
    OpenSqBracket = "["
    CloseSqBracket = "]"
