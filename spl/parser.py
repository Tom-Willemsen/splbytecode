from spl import tokens
from spl.lexer import Lexer
from spl.tokens import Token, TokenTypes


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

    def eat(self, token_type):
        if self.current_token.type == token_type:
            value = self.current_token.value
            self.next_token()
            return value
        else:
            raise SPLSyntaxError("Unexpected token {} (expected {})."
                                 .format(str(self.current_token), token_type))

    def noun(self):
        return self.eat(TokenTypes.Noun)

    def adjective(self):
        return self.eat(TokenTypes.Adj)

    def term(self):
        result = 1
        while self.current_token.type == TokenTypes.Adj:
            result *= self.adjective()
        result *= self.noun()
        return result

    def expr(self):
        result = self.term()

        while self.current_token.type == TokenTypes.Add:
            self.eat(TokenTypes.Add)
            result += self.term()

        self.eat(TokenTypes.FullStop)
        return result

    def var_assignment(self):
        name = self.eat(TokenTypes.Name)
        self.eat(TokenTypes.Comma)
        value = self.expr()

        if name in self.vars_table:
            raise SPLSyntaxError("Redeclaring variables is not allowed ('{}').".format(name))
        self.vars_table[name] = value

    def act(self):
        self.eat(TokenTypes.Act)
        while self.current_token.type != TokenTypes.FullStop:
            self.next_token()
        self.eat(TokenTypes.FullStop)

        self.scene()
        while self.current_token.type != TokenTypes.Eof and self.current_token.type != TokenTypes.Act:
            self.scene()

    def scene(self):
        self.eat(TokenTypes.Scene)
        while self.current_token.type != TokenTypes.FullStop:
            self.next_token()
        self.eat(TokenTypes.FullStop)

        while self.current_token.type != TokenTypes.Eof \
                and self.current_token.type != TokenTypes.Act\
                and self.current_token.type != TokenTypes.Scene:
            self.statement()

    def statement(self):
        if self.current_token.type == TokenTypes.OpenSqBracket:
            self.stagecontrol()
        else:
            self.speech()

    def stagecontrol(self):
        self.eat(TokenTypes.OpenSqBracket)
        self.eat(TokenTypes.CloseSqBracket)

    def speech(self):
        name = self.eat(TokenTypes.Name)
        self.eat(TokenTypes.Colon)

        while self.current_token.type != TokenTypes.FullStop:
            self.next_token()
        self.eat(TokenTypes.FullStop)

    def play(self):
        # Ignore everything up to and including the first full stop.
        while self.current_token.type != TokenTypes.FullStop:
            self.next_token()
        self.next_token()

        while self.current_token.type != TokenTypes.Act:
            self.var_assignment()

        self.act()

        while self.current_token.type != TokenTypes.Eof:
            self.act()

        return self.vars_table
