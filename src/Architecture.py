class Node:
    def __init__(self):
        self.next = None
        self.output = None
        self.inputs = []

    def add_input(self, ainput: Node):
        self.inputs.append(ainput)

    def set_next(self, anext: Node):
        self.next = anext

    def get_inputs(self):
        return [node.get_output() for node in self.inputs]

    def calc(self, inputs):
        raise NotImplementedError

    def get_output(self):
        if self.output == None:
            self.output = self.calc(self.get_inputs())
        return self.output

    def do(self):
        self.output = self.calc(self.get_inputs())
        self.next.do()