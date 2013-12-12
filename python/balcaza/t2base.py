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

class OrderedMapIterator(object):

    def __init__(self, map, order):
        self.map = map
        self.order = order
        self.i = 0

    def __iter__(self):
        return self

    def next(self):
        if self.i >= len(self.order):
            raise StopIteration
        item = self.map[self.order[self.i]]
        self.i += 1
        return item

class Ports(object):

    def __init__(self, flow):
        Ports.__setattr__(self, '_', Namespace())
        self._.flow = flow
        self._.ports = {}
        self._.order = []

    def __len__(self):
        return len(self._.ports)

    def __iter__(self):
        return OrderedMapIterator(self._.ports, self._.order)

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, type):
        return self.__setattr__(name, type)


class Namespace:

    pass

