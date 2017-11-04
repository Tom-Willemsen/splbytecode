class Assign(object):
    def __init__(self, var, value):
        self.var = var
        self.value = value

    def __str__(self):
        return "(Assign {} = {})".format(self.var, self.value)

    def __repr__(self):
        return str(self)
