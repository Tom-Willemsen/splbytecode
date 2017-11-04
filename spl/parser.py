from spl import tokens
from spl.lexer import Lexer


class SPLSyntaxError(Exception):
    pass


class Parser(object):
    def __init__(self, filepath):
        self.tokens = Lexer(open(filepath).read()).token_generator()
        self.current_token = None
        self.next_token()

    def next_token(self):
        self.current_token = next(self.tokens, None)
        return self.current_token

    def eat(self, token_class):
        assert isinstance(self.current_token, tokens.Token)
        if isinstance(self.current_token, token_class):
            value = self.current_token.value
            self.next_token()
            return value
        else:
            raise SPLSyntaxError("Unexpected token {} (expected {})."
                                 .format(str(self.current_token), token_class.__name__))

    def noun(self):
        return self.eat(tokens.Noun)

    def adjective(self):
        return self.eat(tokens.Adj)

    def term(self):
        result = 1
        while isinstance(self.current_token, tokens.Adj):
            result *= self.adjective()
        result *= self.noun()
        return result

    def expr(self):
        result = self.term()

        while isinstance(self.current_token, tokens.Add):
            self.eat(tokens.Add)
            result += self.term()

        self.eat(tokens.FullStop)
        return result

    def var_assignment(self):
        name = self.eat(tokens.Name)
        self.eat(tokens.Comma)
        value = self.expr()
        return name, value

    def play(self):
        # Ignore everything up to and including the first full stop.
        while not isinstance(self.current_token, tokens.FullStop):
            self.next_token()
        self.next_token()

        var_initializations = []
        while not isinstance(self.current_token, tokens.Act):
            var_initializations.append(self.var_assignment())

        self.eat(tokens.Act)
        self.eat(tokens.Eof)

        return var_initializations
