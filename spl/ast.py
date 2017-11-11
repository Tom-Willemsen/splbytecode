class Operators(object):
    MULTIPLY = "*"
    ADD = "+"


class AstNode(object):
    def get_children(self):
        return []


class Assign(AstNode):
    def __init__(self, var, expr_tree, dynamic=True):
        self.var = var
        self.expr_tree = expr_tree
        self.dynamic = dynamic

    def __str__(self):
        return "({} Assign '{}' to {})".format("Dynamic" if self.dynamic else "Static", self.var, self.expr_tree)

    def __repr__(self):
        return str(self)

    def get_children(self):
        return [self.expr_tree]


class BinaryOperator(AstNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return "({} {} {})".format(self.left, self.op, self.right)

    def get_children(self):
        return [self.left, self.right]


class Value(AstNode):
    def __init__(self, value):
        assert isinstance(value, int)
        self.value = value

    def __str__(self):
        return "({})".format(self.value)


class DynamicValue(AstNode):
    def __init__(self, field):
        assert isinstance(field, str)
        self.field = field

    def __str__(self):
        return "(field '{}')".format(self.field)


class PrintVariable(AstNode):
    def __init__(self, field, as_char=False):
        assert isinstance(field, str)
        self.field = field
        self.as_char = as_char

    def __str__(self):
        return "(print field '{}')".format(self.field)


class InputVariable(AstNode):
    def __init__(self, field, as_char=False):
        assert isinstance(field, str)
        self.field = field
        self.as_char = as_char

    def __str__(self):
        return "(input to field '{}')".format(self.field)


class Goto(AstNode):
    def __init__(self, act, scene):
        self.act = act
        self.scene = scene

    def __str__(self):
        return "(Goto act={} scene={})".format(self.act, self.scene)
