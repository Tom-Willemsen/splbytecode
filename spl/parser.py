from spl import tokens
from spl.lexer import Lexer


class SPLSyntaxError(Exception):
    pass


class Parser(object):
    def __init__(self, filepath):
        self.tokens = Lexer(open(filepath).read()).token_generator()
        self.current_token = None
        self.next_token()

        self.vars_table = {}  # Dictionary of "variable_name": initial_value

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

        if name in self.vars_table:
            raise SPLSyntaxError("Redeclaring variables is not allowed ('{}').".format(name))
        self.vars_table[name] = value

    def act(self):
        self.eat(tokens.Act)
        while not isinstance(self.current_token, tokens.FullStop):
            self.next_token()
        self.eat(tokens.FullStop)

        self.scene()
        while not isinstance(self.current_token, tokens.Eof) and not isinstance(self.current_token, tokens.Act):
            self.scene()

    def scene(self):
        self.eat(tokens.Scene)
        while not isinstance(self.current_token, tokens.FullStop):
            self.next_token()
        self.eat(tokens.FullStop)

        while not isinstance(self.current_token, tokens.Eof) \
                and not isinstance(self.current_token, tokens.Act)\
                and not isinstance(self.current_token, tokens.Scene):
            self.statement()

    def statement(self):
        if isinstance(self.current_token, tokens.OpenSqBracket):
            self.stagecontrol()
        else:
            self.speech()

    def stagecontrol(self):
        self.eat(tokens.OpenSqBracket)
        self.eat(tokens.CloseSqBracket)

    def speech(self):
        name = self.eat(tokens.Name)
        self.eat(tokens.Colon)

        while not isinstance(self.current_token, tokens.FullStop):
            self.next_token()
        self.eat(tokens.FullStop)

    def play(self):
        # Ignore everything up to and including the first full stop.
        while not isinstance(self.current_token, tokens.FullStop):
            self.next_token()
        self.next_token()

        while not isinstance(self.current_token, tokens.Act):
            self.var_assignment()

        self.act()

        while not isinstance(self.current_token, tokens.Eof):
            self.act()

        return self.vars_table
