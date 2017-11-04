class Token(object):
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        result = repr(self.__class__.__name__)
        if self.value is not None:
            result += ": " + str(self.value)
        return result

    def __repr__(self):
        return str(self)


class Noun(Token):
    pass


class NiceNoun(Noun):
    def __init__(self):
        super().__init__(1)


class BadNoun(Noun):
    def __init__(self):
        super().__init__(-1)


class Noop(Token):
    pass


class Adj(Token):
    def __init__(self):
        super().__init__(2)


class FullStop(Token):
    pass


class Eof(Token):
    pass


class Add(Token):
    pass


class Comma(Token):
    pass


class Name(Token):
    pass


class Act(Token):
    pass


class Scene(Token):
    pass


class OpenSqBracket(Token):
    pass


class CloseSqBracket(Token):
    pass


class Colon(Token):
    pass

