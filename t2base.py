import t2types

class Source:

    def __init__(self, flow):
        self.flow = flow

    def __rshift__(self, sink):
        self.flow.linkData(self, sink)

class Sink:

    def __init__(self, flow):
        self.flow = flow

    def __rrshift__(self, text):
        self.flow.linkData(text, self)

class Port:

    def connect(self):
        pass

class Namespace:

    pass

