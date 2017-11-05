from spl.ast import Operators
from spl.tokens import Token, TokenTypes


class Lexer(object):
    def __init__(self, text):
        self.text = text.lower()
        self.pos = 0

    def token_generator(self):
        while self.pos < len(self.text):
            token = self.get_next_token()
            if token.type is not TokenTypes.NoOp:
                yield token
        yield Token(TokenTypes.Eof)

    def get_next_token(self):

        # Act
        found, text = self.text_starts_with_item("act")
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Act)

        # Scene
        found, text = self.text_starts_with_item("scene")
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Scene)

        # Names
        found, text = self.text_starts_with_any_of(["romeo", "juliet", "the ghost"])
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Name, text)

        # Nouns
        found, text = self.text_starts_with_any_of(["man", "patience"])
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Noun, 1)

        found, text = self.text_starts_with_any_of(["pig"])
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Noun, -1)

        # Adjectives
        found, text = self.text_starts_with_any_of(["young", "remarkable"])
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Adj, 2)

        found, text = self.text_starts_with_any_of(["with", "and"])
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Add, value=Operators.ADD)

        if self.text_starts_with_item(".")[0]:
            self.pos += 1
            return Token(TokenTypes.FullStop)

        if self.text_starts_with_item(",")[0]:
            self.pos += 1
            return Token(TokenTypes.Comma)

        if self.text_starts_with_item("[")[0]:
            self.pos += 1
            return Token(TokenTypes.OpenSqBracket)

        if self.text_starts_with_item("]")[0]:
            self.pos += 1
            return Token(TokenTypes.CloseSqBracket)

        if self.text_starts_with_item(":")[0]:
            self.pos += 1
            return Token(TokenTypes.Colon)

        self.pos += 1
        return Token(TokenTypes.NoOp)

    def text_starts_with_any_of(self, ls):
        for item in ls:
            if self.text_starts_with_item(item)[0]:
                return True, self.text_starts_with_item(item)[1]
        return False, None

    def text_starts_with_item(self, item):
        if self.text[self.pos:].startswith(item):
            return True, item
        return False, None
