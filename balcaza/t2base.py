import string

alphanumeric = string.letters + string.digits

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

    def connect(self):
        pass

class Namespace:

    pass

