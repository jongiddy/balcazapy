class Source:

    def __init__(self, flow):
        self.flow = flow

    def __rshift__(self, sink):
        self.connect()
        sink.connect()
        self.flow.linkData(self, sink)

class Sink:

    def __init__(self, flow):
        self.flow = flow

    def __rrshift__(self, text):
        self.connect()
        self.flow.linkData(text, self)

class Port(object):

    def __init__(self, name):
        self.name = name

    def connect(self):
        pass

class Namespace:

    pass

