class Pipeline:

    def __init__(self, flow, first, last):
        self.flow = flow
        self.first = first
        self.last = last

    def __or__(self, sink):
        p = self.flow.linkData(self.last, sink)
        return Pipeline(self.flow, self.first, p.last)

    def __ror__(self, source):
        p = self.flow.linkData(source, self.first)
        return Pipeline(self.flow, p.first, self.last)

    @property
    def input(self):
        return self.first.input
    @input.setter
    def input(self, value):
        raise RuntimeError('cannot set pipeline input')

    @property
    def output(self):
        return self.last.output
    @output.setter
    def output(self, value):
        raise RuntimeError('cannot set pipeline output')
    
    def extendUnusedPorts(self):
        self.extendUnusedInputs()
        self.extendUnusedOutputs()

    def extendUnusedInputs(self):
        self.first.extendUnusedInputs()

    def extendUnusedOutputs(self):
        self.last.extendUnusedOutputs()

class Source:

    def __init__(self, flow):
        self.flow = flow

    def __or__(self, sink):
        return self.flow.linkData(self, sink)

    def __rshift__(self, sink):
        self.flow.linkData(self, sink)

class Sink:

    def __init__(self, flow):
        self.flow = flow

    def __ror__(self, source):
        return self.flow.linkData(source, self)

    def __rrshift__(self, text):
        self.flow.linkData(text, self)

class Port(object):

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def getDepth(self):
        return self.type.getDepth()

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

    def __contains__(self, name):
        return self._.ports.has_key(name)
        
    def __iter__(self):
        return OrderedMapIterator(self._.ports, self._.order)

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, type):
        return self.__setattr__(name, type)


class Namespace:

    pass

