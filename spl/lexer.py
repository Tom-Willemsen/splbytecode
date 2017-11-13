import re

from intermediate.operators import Operators
from spl.tokens import Token, TokenTypes


class Lexer(object):
    def __init__(self, text):
        self.text = text.lower()
        self.pos = 0

        self.names = Lexer.list_from_file("spl/words/characters.txt")
        self.nouns = Lexer.list_from_file("spl/words/nouns.txt")
        self.negative_nouns = Lexer.list_from_file("spl/words/negative_nouns.txt")
        self.adjectives = Lexer.list_from_file("spl/words/adjectives.txt")

    @staticmethod
    def list_from_file(filename):
        result = []
        with open(filename, "r") as f:
            for line in f.readlines():
                result.append(line.strip().lower())
        return result

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

        found, text = self.text_starts_with_item("speak your mind")
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Print, True)

        found, text = self.text_starts_with_item("open your heart")
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Print, False)

        found, text = self.text_starts_with_item("open your mind")
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Input, True)

        found, text = self.text_starts_with_item("listen to your heart")
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Input, False)

        # goto
        found, text = self.text_starts_with_any_of(["let us proceed to ", "let us return to "])
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Goto)

        # Names
        found, text = self.text_starts_with_any_of(self.names)
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Name, text)

        # Adjectives
        found, text = self.text_starts_with_any_of(self.adjectives)
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Adj, 2)

        # Nouns
        found, text = self.text_starts_with_any_of(self.nouns)
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Noun, 1)

        found, text = self.text_starts_with_any_of(self.negative_nouns)
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Noun, -1)

        found, text = self.text_starts_with_any_of(["with", "and"])
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Add, value=Operators.ADD)

        found, text = self.text_starts_with_any_of([".", "!"])
        if found:
            self.pos += len(text)
            return Token(TokenTypes.EndLine)

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

        # Second person pronouns
        found, text = self.text_starts_with_any_of(["you", "thyself"])
        if found:
            self.pos += len(text)
            return Token(TokenTypes.SecondPronoun)

        # First person pronouns
        found, text = self.text_starts_with_any_of(["I ", "myself"])
        if found:
            self.pos += len(text)
            return Token(TokenTypes.FirstPronoun)

        # enter
        found, text = self.text_starts_with_item("enter")
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Enter)

        # exit
        found, text = self.text_starts_with_item("exit")
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Exit)

        # exeunt
        found, text = self.text_starts_with_item("exeunt")
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Exeunt)

        # numerals
        found, text = self.text_starts_with_regex(" ([ivx]+)[.:]")
        if found:
            self.pos += len(text)
            return Token(TokenTypes.Numeral, text)

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

    def text_starts_with_regex(self, rx):
        match = re.search("^{}".format(rx), self.text[self.pos:])
        if match:
            return True, match.group(1)
        return False, None
