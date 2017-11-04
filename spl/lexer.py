from spl import tokens


class Lexer(object):
    def __init__(self, text):
        self.text = text.lower()
        self.pos = 0

    def token_generator(self):
        while self.pos < len(self.text):
            token = self.get_next_token()
            if not isinstance(token, tokens.Noop):
                yield token
        yield tokens.Eof()

    def get_next_token(self):

        # Act
        found, text = self.text_starts_with_item("act")
        if found:
            self.pos += len(text)
            return tokens.Act()

        # Act
        found, text = self.text_starts_with_item("scene")
        if found:
            self.pos += len(text)
            return tokens.Scene()


        # Names
        found, text = self.text_starts_with_any_of(["romeo", "juliet", "the ghost"])
        if found:
            self.pos += len(text)
            return tokens.Name(text)

        # Nouns
        found, text = self.text_starts_with_any_of(["man", "patience"])
        if found:
            self.pos += len(text)
            return tokens.NiceNoun()

        found, text = self.text_starts_with_any_of(["pig"])
        if found:
            self.pos += len(text)
            return tokens.BadNoun()

        # Adjectives
        found, text = self.text_starts_with_any_of(["young", "remarkable"])
        if found:
            self.pos += len(text)
            return tokens.Adj()

        found, text = self.text_starts_with_any_of(["with", "and"])
        if found:
            self.pos += len(text)
            return tokens.Add()

        if self.text_starts_with_item(".")[0]:
            self.pos += 1
            return tokens.FullStop()

        if self.text_starts_with_item(",")[0]:
            self.pos += 1
            return tokens.Comma()

        self.pos += 1
        return tokens.Noop()

    def text_starts_with_any_of(self, ls):
        for item in ls:
            if self.text_starts_with_item(item)[0]:
                return True, self.text_starts_with_item(item)[1]
        return False, None

    def text_starts_with_item(self, item):
        if self.text[self.pos:].startswith(item):
            return True, item
        return False, None


if __name__ == "__main__":
    token_generator = list(Lexer(open("expr.spl").read()).token_generator())

    current_token_value = None

    for token in token_generator:

        if isinstance(token, tokens.Noop):
            continue

        print(token)
