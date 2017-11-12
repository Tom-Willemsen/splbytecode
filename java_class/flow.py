from java_class import instructions
from java_class.instructions import goto_w


class Goto(object):
    def __init__(self, name, destination):
        self.name = name
        self.destination = destination

    def __len__(self):
        return len(instructions.nop() if self.destination else instructions.goto_w(0))

    def __eq__(self, other):
        if not isinstance(other, Goto):
            return False
        return self.name == other.name and self.destination == other.destination

    @staticmethod
    def compute_gotos(code):

        labels = {}

        print(code)

        for instruction in code:
            if isinstance(instruction, Goto) and instruction.destination:

                print("Found a label")

                idx = code.index(Goto(instruction.name, True))

                labels[instruction.name] = sum(len(i) for i in code[0:idx])

        print(labels)

        for instruction in code:
            if isinstance(instruction, Goto) and not instruction.destination:

                print("Found a goto")

                idx = code.index(instruction)
                code[idx] = goto_w(idx - labels[instruction.name]-1)

        for instruction in code:
            if isinstance(instruction, Goto):
                code[code.index(instruction)] = instructions.nop()

        return code
