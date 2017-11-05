from spl.ast import Assign, Operators, BinaryOperator, Value, DynamicValue, PrintVariable
from spl.lexer import Lexer
from spl.tokens import TokenTypes


class SPLSyntaxError(Exception):
    pass


class Parser(object):
    def __init__(self, filepath):
        self.tokens = Lexer(open(filepath).read()).token_generator()
        self.current_token = None
        self.next_token()

        self.vars_table = []  # List of variable names declared.
        self.statements = []  # List of statements to be executed

        self.onstage = []  # List of characters currently on stage (for figuring out who "you" is...)
        self.speaking = None  # Character currently speaking

    def get_character_being_spoken_to(self):
        if len(self.onstage) != 2:
            raise SPLSyntaxError("There must be exactly 2 characters on stage to speak to someone")
        assert self.speaking is not None
        char = list(c for c in self.onstage if c != self.speaking)
        assert len(char) == 1
        return char[0]

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
        if self.current_token.type == TokenTypes.Adj:
            return BinaryOperator(Value(self.eat(TokenTypes.Adj)), Operators.MULTIPLY, self.term())
        elif self.current_token.type == TokenTypes.Name:
            return DynamicValue(self.eat(TokenTypes.Name))
        elif self.current_token.type == TokenTypes.SecondPronoun:
            self.eat(TokenTypes.SecondPronoun)
            return DynamicValue(self.get_character_being_spoken_to())
        elif self.current_token.type == TokenTypes.FirstPronoun:
            self.eat(TokenTypes.FirstPronoun)
            return DynamicValue(self.get_character_being_spoken_to())
        else:
            return Value(self.eat(TokenTypes.Noun))

    def expr(self):
        left = self.term()
        if self.current_token.type == TokenTypes.Add:
            return BinaryOperator(left, self.eat(TokenTypes.Add), self.expr())
        elif self.current_token.type == TokenTypes.Adj:
            return BinaryOperator(left, Operators.ADD, self.expr())
        elif self.current_token.type == TokenTypes.EndLine:
            self.eat(TokenTypes.EndLine)
            return left
        else:
            op = BinaryOperator(left, Operators.ADD, self.expr())
            return op

    def var_assignment(self):
        name = self.eat(TokenTypes.Name)
        self.eat(TokenTypes.Comma)
        value = self.expr()

        if name in self.vars_table:
            raise SPLSyntaxError("Redeclaring variables is not allowed ('{}').".format(name))
        self.vars_table.append(name)
        self.statements.append(Assign(name, value, dynamic=False))

    def act(self):
        self.eat(TokenTypes.Act)
        while self.current_token.type != TokenTypes.EndLine:
            self.next_token()
        self.eat(TokenTypes.EndLine)

        self.scene()
        while self.current_token.type != TokenTypes.Eof and self.current_token.type != TokenTypes.Act:
            self.scene()

    def scene(self):
        self.eat(TokenTypes.Scene)
        while self.current_token.type != TokenTypes.EndLine:
            self.next_token()
        self.eat(TokenTypes.EndLine)

        while self.current_token.type != TokenTypes.Eof \
                and self.current_token.type != TokenTypes.Act\
                and self.current_token.type != TokenTypes.Scene:
            self.statement()

        if len(self.onstage) != 0:
            raise SPLSyntaxError("Cannot have characters left on stage at the end of a scene")

    def statement(self):
        if self.current_token.type == TokenTypes.OpenSqBracket:
            self.stagecontrol()
        else:
            self.speech()

    def stagecontrol(self):
        self.eat(TokenTypes.OpenSqBracket)
        if self.current_token.type == TokenTypes.Enter:
            self.enter()
        elif self.current_token.type == TokenTypes.Exit:
            self.exit()
        else:
            self.exeunt()
        self.eat(TokenTypes.CloseSqBracket)

    def enter(self):
        self.eat(TokenTypes.Enter)
        self.onstage.append(self.eat(TokenTypes.Name))
        while self.current_token.type == TokenTypes.Add:
            self.eat(TokenTypes.Add)
            self.onstage.append(self.eat(TokenTypes.Name))

    def exit(self):
        def leave(name):
            if name not in self.onstage:
                raise SPLSyntaxError("Character '{}' cannot leave if they are not on stage.".format(name))
            self.onstage.remove(name)

        self.eat(TokenTypes.Exit)
        leave(self.eat(TokenTypes.Name))
        while self.current_token.type == TokenTypes.Add:
            self.eat(TokenTypes.Add)
            leave(self.eat(TokenTypes.Name))

    def exeunt(self):
        self.eat(TokenTypes.Exeunt)
        self.onstage = []

    def speech(self):
        name = self.eat(TokenTypes.Name)
        if name not in self.vars_table:
            raise SPLSyntaxError("Cannot reference an undeclared character ('{}')".format(name))
        if name not in self.onstage:
            raise SPLSyntaxError("Character {} cannot speak since they are not on stage.".format(name))
        self.speaking = name

        self.eat(TokenTypes.Colon)

        if self.current_token.type != TokenTypes.Print:
            statement = self.assignment()
        else:
            as_char = self.eat(TokenTypes.Print)
            statement = PrintVariable(self.get_character_being_spoken_to(), as_char)
            self.eat(TokenTypes.EndLine)

        self.statements.append(statement)
        self.speaking = None

    def assignment(self):
        if self.current_token.type == TokenTypes.FirstPronoun:
            spoken_to = self.speaking
            self.eat(TokenTypes.FirstPronoun)
        elif self.current_token.type == TokenTypes.SecondPronoun:
            spoken_to = self.get_character_being_spoken_to()
            self.eat(TokenTypes.SecondPronoun)
        else:
            spoken_to = self.eat(TokenTypes.Name)

        if spoken_to not in self.vars_table:
            raise SPLSyntaxError("Cannot reference an undeclared character ('{}')".format(self.speaking))

        expr_tree = self.expr()
        return Assign(spoken_to, expr_tree)

    def play(self):
        # Ignore everything up to and including the first full stop.
        while self.current_token.type != TokenTypes.EndLine:
            self.next_token()
        self.next_token()

        while self.current_token.type != TokenTypes.Act:
            self.var_assignment()

        self.act()

        while self.current_token.type != TokenTypes.Eof:
            self.act()

        return self.vars_table, self.statements
