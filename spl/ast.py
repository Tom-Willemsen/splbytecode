class ConstAssign(object):
    def __init__(self, var, value):
        self.var = var
        self.value = value

    def __str__(self):
        return "(Assign {} = {})".format(self.var, self.value)

    def __repr__(self):
        return str(self)


class DynamicAssign(object):
    def __init__(self, var, expr_tree):
        self.var = var
        self.expr_tree = expr_tree
