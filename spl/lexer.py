import re

from intermediate import operators
from spl.tokens import Token, TokenTypes


def list_from_file(filename):
    result = []
    with open(filename, "r") as f:
        for line in f.readlines():
            result.append(line.strip().lower())
    return result


FIRST_PERSON_PRONOUNS = ["i ", "myself"]
SECOND_PERSON_PRONOUNS = ["you", "thyself"]


class Lexer(object):
    def __init__(self, text):
        self.text = text.lower()
        self.pos = 0

        self.names = list_from_file("spl/words/characters.txt")
        self.nouns = list_from_file("spl/words/nouns.txt")
        self.negative_nouns = list_from_file("spl/words/negative_nouns.txt")
        self.adjectives = list_from_file("spl/words/adjectives.txt")

    def token_generator(self):
        while self.pos < len(self.text):
            token = self.get_next_token()
            if token.type is not TokenTypes.NoOp:
                yield token
        yield Token(TokenTypes.Eof)

    def get_next_token(self):

        mapping = {
            "(act)":
                lambda: Token(TokenTypes.Act),
            "(scene)":
                lambda: Token(TokenTypes.Scene),
            "(speak your mind)":
                lambda: Token(TokenTypes.Print, True),
            "(open your heart)":
                lambda: Token(TokenTypes.Print, False),
            "(open your mind)":
                lambda: Token(TokenTypes.Input, True),
            "(listen to your heart)":
                lambda: Token(TokenTypes.Input, False),
            "(let us proceed to |let us return to )":
                lambda: Token(TokenTypes.Goto, text),
            "({})".format("|".join(self.names)):
                lambda: Token(TokenTypes.Name, text),
            "({})".format("|".join(self.adjectives)):
                lambda: Token(TokenTypes.Adj, 2),
            "({})".format("|".join(self.nouns)):
                lambda: Token(TokenTypes.Noun, 1),
            "({})".format("|".join(self.negative_nouns)):
                lambda: Token(TokenTypes.Noun, -1),
            "(with|and)":
                lambda: Token(TokenTypes.Add, value=operators.Operators.ADD),
            "(\.|!)":
                lambda: Token(TokenTypes.EndLine),
            "(\?)":
                lambda: Token(TokenTypes.QuestionMark),
            "(,)":
                lambda: Token(TokenTypes.Comma),
            "(\[)":
                lambda: Token(TokenTypes.OpenSqBracket),
            "(\])":
                lambda: Token(TokenTypes.CloseSqBracket),
            "(:)":
                lambda: Token(TokenTypes.Colon),
            "({})".format("|".join(SECOND_PERSON_PRONOUNS)):
                lambda: Token(TokenTypes.SecondPronoun),
            "({})".format("|".join(FIRST_PERSON_PRONOUNS)):
                lambda: Token(TokenTypes.FirstPronoun),
            "(enter)":
                lambda: Token(TokenTypes.Enter),
            "(exit)":
                lambda: Token(TokenTypes.Exit),
            "(exeunt)":
                lambda: Token(TokenTypes.Exeunt),
            "(if so)":
                lambda: Token(TokenTypes.IfSo),
            " ([ivx]+)[.:]":
                lambda: Token(TokenTypes.Numeral, text),
            "(are|is|am) (?:{0}|{1}|{2}) ?(?:equal to) (?:{0}|{1}|{2})\?"
                .format("|".join(FIRST_PERSON_PRONOUNS), "|".join(SECOND_PERSON_PRONOUNS), "|".join(self.names)):
                lambda: Token(TokenTypes.QuestionStart),
        }

        for regexp in mapping:
            match, text = self.text_starts_with_regex(regexp)
            if match:
                self.pos += len(text)
                return mapping[regexp]()
        else:
            self.pos += 1
            return Token(TokenTypes.NoOp)

    def text_starts_with_regex(self, rx):
        match = re.search("^{}".format(rx), self.text[self.pos:])
        if match:
            try:
                return True, match.group(1)
            except IndexError:
                return False, None
        return False, None
