import re
import os

from intermediate import operators
from spl.tokens import Token, TokenTypes


FIRST_PERSON_PRONOUNS = ["i ", "myself"]
SECOND_PERSON_PRONOUNS = ["you", "thyself"]

WORDS_DIRECTORY = os.path.join(os.path.dirname(__file__), "words")


def list_from_file(filename):
    result = []
    with open(os.path.join(WORDS_DIRECTORY, filename), "r") as f:
        for line in f.readlines():
            if line.strip() != "":
                result.append(line.strip().lower())
    return sorted(result)  # Ensure consistent order, at least.


def regex_from_words(words):
    return "({})".format("|".join(words))


class Lexer(object):
    def __init__(self, text):
        self.text = text.lower()
        self.pos = 0

        self.names = list_from_file("characters.txt")
        self.nouns = list_from_file("nouns.txt")
        self.negative_nouns = list_from_file("negative_nouns.txt")
        self.adjectives = list_from_file("adjectives.txt")

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
            regex_from_words(self.names):
                lambda: Token(TokenTypes.Name, text),
            regex_from_words(self.adjectives):
                lambda: Token(TokenTypes.Adj, 2),
            regex_from_words(self.nouns):
                lambda: Token(TokenTypes.Noun, 1),
            regex_from_words(self.negative_nouns):
                lambda: Token(TokenTypes.Noun, -1),
            regex_from_words(["with", "and"]):
                lambda: Token(TokenTypes.Add, operators.Operators.ADD),
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
            "(are|is|am) (?:{0}|{1}|{2}) ?(?:equal to) ?(?:{0}|{1}|{2})\?".format(
                regex_from_words(FIRST_PERSON_PRONOUNS),
                regex_from_words(SECOND_PERSON_PRONOUNS),
                regex_from_words(self.names)
                ):
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
        regex = "^{}".format(rx)
        match = re.search(regex, self.text[self.pos:])
        if match:
            try:
                return True, match.group(1)
            except IndexError:
                return False, None
        return False, None
