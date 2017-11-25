from intermediate import ast, operators
from spl.tokens import TokenTypes


class SPLSyntaxError(Exception):
    pass


class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.next_token()

        self.vars_table = []  # List of variable names declared.

        self.onstage = []  # List of characters currently on stage (for figuring out who thyself is...)
        self.speaking = None  # Character currently speaking
        self.current_act = None  # ID of current act. None = not in an act yet.

    def next_token(self):
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            raise SPLSyntaxError("Next token was requested, but none exists.")
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

    def character_name(self):
        if self.current_token.type == TokenTypes.Name:
            return self.eat(TokenTypes.Name)
        elif self.current_token.type == TokenTypes.SecondPronoun:
            self.eat(TokenTypes.SecondPronoun)
            return self.get_character_being_spoken_to()
        elif self.current_token.type == TokenTypes.FirstPronoun:
            self.eat(TokenTypes.FirstPronoun)
            return self.speaking
        else:
            raise SPLSyntaxError("Expected a character or pronoun.")

    def _is_current_token_character(self):
        return self.current_token.type in (TokenTypes.Name, TokenTypes.FirstPronoun, TokenTypes.SecondPronoun)

    def get_character_being_spoken_to(self):
        if len(self.onstage) != 2:
            raise SPLSyntaxError("There must be exactly 2 characters on stage to speak to someone")
        assert self.speaking is not None
        char = list(c for c in self.onstage if c != self.speaking)
        assert len(char) == 1
        return char[0]

    def term(self):
        if self.current_token.type == TokenTypes.Adj:
            return ast.BinaryOperator(ast.Value(self.eat(TokenTypes.Adj)), operators.Operators.MULTIPLY, self.term())
        elif self._is_current_token_character():
            return ast.DynamicValue(self.character_name())
        else:
            return ast.Value(self.eat(TokenTypes.Noun))

    def expr(self):
        left = self.term()
        if self.current_token.type == TokenTypes.Add:
            return ast.BinaryOperator(left, self.eat(TokenTypes.Add), self.expr())
        elif self.current_token.type == TokenTypes.Adj:
            return ast.BinaryOperator(left, operators.Operators.ADD, self.expr())
        elif self.current_token.type == TokenTypes.EndLine:
            self.eat(TokenTypes.EndLine)
            return left
        else:
            op = ast.BinaryOperator(left, operators.Operators.ADD, self.expr())
            return op

    def var_assignment(self):
        name = self.eat(TokenTypes.Name)
        self.eat(TokenTypes.Comma)
        value = self.expr()

        if name in self.vars_table:
            raise SPLSyntaxError("Redeclaring variables is not allowed ('{}').".format(name))
        self.vars_table.append(name)
        return ast.Assign(name, value, dynamic=False)

    def act(self):
        self.eat(TokenTypes.Act)
        id = self.eat(TokenTypes.Numeral)
        self.eat(TokenTypes.Colon)

        while self.current_token.type != TokenTypes.EndLine:
            self.eat(self.current_token.type)
        self.eat(TokenTypes.EndLine)

        self.current_act = id

        children = [self.scene()]

        while self.current_token.type != TokenTypes.Eof and self.current_token.type != TokenTypes.Act:
            children.append(self.scene())

        return ast.Label(name="act {}".format(id), children=children)

    def scene(self):
        self.eat(TokenTypes.Scene)
        id = self.eat(TokenTypes.Numeral)
        self.eat(TokenTypes.Colon)

        while self.current_token.type != TokenTypes.EndLine:
            self.eat(self.current_token.type)
        self.eat(TokenTypes.EndLine)

        children = []

        while self.current_token.type != TokenTypes.Eof \
                and self.current_token.type != TokenTypes.Act\
                and self.current_token.type != TokenTypes.Scene:
            children.append(self.statement())

        if len(self.onstage) != 0:
            raise SPLSyntaxError("Cannot have characters left on stage at the end of a scene")

        return ast.Label(name="act {} scene {}".format(self.current_act, id), children=children)

    def statement(self):
        if self.current_token.type == TokenTypes.OpenSqBracket:
            self.stagecontrol()
            return ast.NoOp()
        else:
            return self.speech()

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
        self.enter_single()
        while self.current_token.type == TokenTypes.Add:
            self.eat(TokenTypes.Add)
            self.enter_single()

    def enter_single(self):
        name = self.eat(TokenTypes.Name)
        if name in self.onstage:
            raise SPLSyntaxError("Character '{}' cannot enter as they are already on stage".format(name))
        self.onstage.append(name)

    def exit(self):
        self.eat(TokenTypes.Exit)
        self.exit_single()
        while self.current_token.type == TokenTypes.Add:
            self.eat(TokenTypes.Add)
            self.exit_single()

    def exit_single(self):
        name = self.eat(TokenTypes.Name)
        if name not in self.onstage:
            raise SPLSyntaxError("Character '{}' cannot leave if they are not on stage.".format(name))
        self.onstage.remove(name)

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

        if self.current_token.type == TokenTypes.Print:
            as_char = self.eat(TokenTypes.Print)
            statement = ast.PrintVariable(self.get_character_being_spoken_to(), as_char)
            self.eat(TokenTypes.EndLine)
        elif self.current_token.type == TokenTypes.Input:
            as_char = self.eat(TokenTypes.Input)
            statement = ast.InputVariable(self.get_character_being_spoken_to(), as_char)
            self.eat(TokenTypes.EndLine)
        elif self.current_token.type == TokenTypes.Goto:
            statement = self.goto()
            self.eat(TokenTypes.EndLine)
        elif self.current_token.type == TokenTypes.IfSo:
            statement = self.conditional_goto()
            self.eat(TokenTypes.EndLine)
        elif self.current_token.type == TokenTypes.QuestionStart:
            self.eat(TokenTypes.QuestionStart)
            statement = self.question()
            self.eat(TokenTypes.QuestionMark)
        else:
            statement = self.assignment()

        self.speaking = None
        return statement

    def question(self):
        person1 = self.character_name()
        person2 = self.character_name()
        if person1 not in self.vars_table or person2 not in self.vars_table:
            raise SPLSyntaxError("Cannot reference undeclared character.")
        return ast.Compare(person1, person2)

    def goto(self):
        self.eat(TokenTypes.Goto)
        if self.current_token.type == TokenTypes.Act:
            self.eat(TokenTypes.Act)
            id = self.eat(TokenTypes.Numeral)
            return ast.Goto(name="act {}".format(id))
        elif self.current_token.type == TokenTypes.Scene:
            self.eat(TokenTypes.Scene)
            id = self.eat(TokenTypes.Numeral)
            return ast.Goto(name="act {} scene {}".format(self.current_act, id))
        else:
            raise SPLSyntaxError("Expected act or scene, got {}".format(self.current_token.type))

    def conditional_goto(self):
        self.eat(TokenTypes.IfSo)
        self.eat(TokenTypes.Comma)
        self.eat(TokenTypes.Goto)
        if self.current_token.type == TokenTypes.Act:
            self.eat(TokenTypes.Act)
            id = self.eat(TokenTypes.Numeral)
            return ast.ConditionalGoto(name="act {}".format(id))
        elif self.current_token.type == TokenTypes.Scene:
            self.eat(TokenTypes.Scene)
            id = self.eat(TokenTypes.Numeral)
            return ast.ConditionalGoto(name="act {} scene {}".format(self.current_act, id))
        else:
            raise SPLSyntaxError("Expected act or scene, got {}".format(self.current_token.type))

    def assignment(self):
        spoken_to = self.character_name()

        if spoken_to not in self.vars_table:
            raise SPLSyntaxError("Cannot reference an undeclared character ('{}')".format(self.speaking))

        expr_tree = self.expr()
        return ast.Assign(spoken_to, expr_tree)

    def play(self):
        # Ignore everything up to and including the first full stop.
        while self.current_token.type != TokenTypes.EndLine:
            self.next_token()
        self.eat(TokenTypes.EndLine)

        children = []
        while self.current_token.type != TokenTypes.Act:
            children.append(self.var_assignment())

        children.append(self.act())
        while self.current_token.type != TokenTypes.Eof:
            children.append(self.act())

        return ast.Label(name="play", children=children)
