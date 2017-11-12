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


def compute_gotos(code):

    def length_of_code_up_to_instruction(num):
        return sum(len(i) for i in code[0:num])

    labels = {}

    for instruction in code:
        if isinstance(instruction, Goto) and instruction.destination:
            idx = code.index(Goto(instruction.name, True))
            labels[instruction.name] = length_of_code_up_to_instruction(idx)
            code[idx] = instructions.nop()

    for instruction in code:
        if isinstance(instruction, Goto) and not instruction.destination:
            idx = code.index(instruction)
            code[idx] = goto_w(labels[instruction.name] - length_of_code_up_to_instruction(idx))

    return code
