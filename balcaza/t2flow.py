__all__ = ("Workflow",)

import uuid

from t2base import alphanumeric, Namespace, Port, Source, Sink
from t2types import T2FlowType
from t2annotation import Annotation
from t2activity import DataflowActivity, TextConstant
from t2task import WorkflowTasks

def getUUID():
    return uuid.uuid4()


class WorkflowPort(Port):

    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.annotations = {}
        dict = type.dict
        for name in ('description', 'example'):
            if dict.has_key(name):
                setattr(self, name, dict[name])

    @property
    def description(self):
        try:
            return self.annotations['net.sf.taverna.t2.annotation.annotationbeans.FreeTextDescription']
        except KeyError:
            raise AttributeError('description')

    @description.setter
    def description(self, value):
        if not isinstance(value, Annotation):
            value = Annotation(value)
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.FreeTextDescription'] = value
        
    @property
    def example(self):
        try:
            return self.annotations['net.sf.taverna.t2.annotation.annotationbeans.ExampleValue']
        except KeyError:
            raise AttributeError('example')

    @example.setter
    def example(self, value):
        if not isinstance(value, Annotation):
            value = Annotation(value)
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.ExampleValue'] = value


class WorkflowInputPort(WorkflowPort, Source):

    def __init__(self, flow, name, type):
        Source.__init__(self, flow)
        WorkflowPort.__init__(self, name, type)

    def exportInputPortXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.port as port:
                port.name >> self.name
                depth = self.type.getDepth()
                port.depth >> depth
                port.granularDepth >> depth
                with port.annotations:
                    for annotationClass, annotation in self.annotations.items():
                        annotation.exportXML(xml, annotationClass)

    def exportSourceXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.source(type="dataflow"):
                tav.port >> self.name

class WorkflowOutputPort(WorkflowPort, Sink):

    def __init__(self, flow, name, type):
        Sink.__init__(self, flow)
        WorkflowPort.__init__(self, name, type)

    def exportOutputPortXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.port as port:
                port.name >> self.name
                with port.annotations:
                    for annotationClass, annotation in self.annotations.items():
                        annotation.exportXML(xml, annotationClass)

    def exportSinkXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.sink(type="dataflow"):
                tav.port >> self.name

class WorkflowPorts(object):

    def __init__(self, flow):
        super(WorkflowPorts, self).__setattr__('_', Namespace())
        self._.flow = flow
        self._.ports = {}
        self._.order = []

    def __getitem__(self, index):
        return self._.ports[self._.order[index]]

    def __setattr__(self, name, type):
        # flow.input.name = type
        if self._.ports.has_key(name):
            raise RuntimeError('port "%s" redefined' % name)
        if not isinstance(type, T2FlowType):
            raise TypeError('port "%s" must be assigned a type' % name)
        self._.ports[name] = self._.PortClass(self._.flow, name, type)
        self._.order.append(name)

    def __getattr__(self, name):
        if self._.ports.has_key(name):
            return self._.ports[name]
        raise AttributeError(name)

class WorkflowInputPorts(WorkflowPorts):

    def __init__(self, flow):
        WorkflowPorts.__init__(self, flow)
        self._.PortClass = WorkflowInputPort

class WorkflowOutputPorts(WorkflowPorts):

    def __init__(self, flow):
        WorkflowPorts.__init__(self, flow)
        self._.PortClass = WorkflowOutputPort

class DataLink:

    def __init__(self, source, sink):
        self.source = source
        self.sink = sink

    def exportXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.datalink:
                self.source.exportSourceXML(xml)
                self.sink.exportSinkXML(xml)

def tavernaName(title):
    # Taverna creates the workflow name from the title annotation's first 20 characters,
    # with non-alphanumeric characters replaced by underscore
    name = []
    for ch in title[:20]:
        if ch in alphanumeric:
            name.append(ch)
        else:
            name.append('_')
    return ''.join(name)

class Workflow(object):

    def __init__(self, title="Workflow", author=None, description=None):
        self.id = getUUID()
        self.annotations = {}
        self.dataLinks = []
        self.input = WorkflowInputPorts(self)
        self.output = WorkflowOutputPorts(self)
        self.task = WorkflowTasks(self)
        self.title = title
        self.name = tavernaName(title)
        if author is not None:
            self.author = author
        if description is not None:
            self.description = description

    def getId(self):
        return self.id

    def getInputs(self):
        inputs = {}
        for port in self.input:
            inputs[port.name] = port.type
        return inputs

    def getOutputs(self):
        outputs = {}
        for port in self.output:
            outputs[port.name] = port.type
        return outputs

    @property
    def title(self):
        try:
            return self.annotations['net.sf.taverna.t2.annotation.annotationbeans.DescriptiveTitle']
        except KeyError:
            raise AttributeError('title')

    @title.setter
    def title(self, value):
        if not isinstance(value, Annotation):
            value = Annotation(value)
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.DescriptiveTitle'] = value
        self.name = tavernaName(value.text)
        
    @property
    def author(self):
        try:
            return self.annotations['net.sf.taverna.t2.annotation.annotationbeans.Author']
        except KeyError:
            raise AttributeError('author')

    @author.setter
    def author(self, value):
        if not isinstance(value, Annotation):
            value = Annotation(value)
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.Author'] = value
        
    @property
    def description(self):
        try:
            return self.annotations['net.sf.taverna.t2.annotation.annotationbeans.FreeTextDescription']
        except KeyError:
            raise AttributeError('description')

    @description.setter
    def description(self, value):
        if not isinstance(value, Annotation):
            value = Annotation(value)
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.FreeTextDescription'] = value

    def linkData(self, source, sink):
        if not isinstance(source, Source):
            textConstant = TextConstant(source)
            label = candidate = textConstant.getLabel()
            i = 1
            while hasattr(self.task, label):
                i += 1
                label = candidate + str(i)
            setattr(self.task, label, textConstant)
            source = getattr(self.task, label).output.value
        if not isinstance(sink, Sink):
            raise TypeError("link sink must be a Sink")
        source.connect()
        sink.connect()
        self.dataLinks.append(DataLink(source, sink))

    def allDescendants(self, descendants=None):
        # Create a list of all nested workflows and their nested workflows, ad infinitum
        if descendants is None:
            descendants = []
        for task in self.task:
            if isinstance(task.activity, DataflowActivity): 
                flow = task.activity.flow
                descendants.append(flow)
                flow.allDescendants(descendants)
        return descendants

    def exportXML(self, xml):
        # The uuidCache ensures that if a nested workflow is referenced more than once,
        # it is only added to the file once.
        uuidCache = set()
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.workflow(version=1, producedBy="pyt2flow"):
                self.exportXMLDataflow(xml, 'top')
                for flow in self.allDescendants():
                    if flow.id not in uuidCache:
                        uuidCache.add(flow.id)
                        flow.exportXMLDataflow(xml, 'nested')

    def exportXMLDataflow(self, xml, role):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.dataflow(id=self.id, role=role):
                tav.name >> self.name
                with tav.inputPorts:
                    for port in self.input:
                        port.exportInputPortXML(xml)
                with tav.outputPorts:
                    for port in self.output:
                        port.exportOutputPortXML(xml)
                with tav.processors:
                    for processor in self.task:
                        processor.exportXML(xml)                    
                tav.conditions
                with tav.datalinks:
                    for link in self.dataLinks:
                        link.exportXML(xml)
                with tav.annotations:
                    for annotationClass, annotation in self.annotations.items():
                        annotation.exportXML(xml, annotationClass)

