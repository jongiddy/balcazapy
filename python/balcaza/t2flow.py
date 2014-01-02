__all__ = ("Workflow",)

import uuid

from t2base import Port, Ports, Pipeline, Source, Sink, DepthChange
from t2types import T2FlowType, List
from t2annotation import Annotation
from t2activity import Activity, NestedWorkflow, TextConstant
from t2task import WorkflowTasks
from t2util import alphanumeric

def getUUID():
    return uuid.uuid4()


class WorkflowPort(Port):

    def __init__(self, name, type):
        Port.__init__(self, name, type)
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

    def asSourcePort(self):
        return self

    def link(self, other):
        assert isinstance(other, Sink), other
        self.flow.linkData(self, other)

    def exportInputPortXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.port as port:
                port.name >> self.name
                depth = self.getDepth()
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

    def asSinkPort(self):
        return self

    def link(self, other):
        assert isinstance(other, Source), other
        self.flow.linkData(other, self)

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

class WorkflowPorts(Ports):

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, type):
        return self.__setattr__(name, type)

    def __setattr__(self, name, type):
        # flow.input.name = type
        if self._.ports.has_key(name):
            raise RuntimeError('port "%s" redefined' % name)
        if isinstance(type, Port):
            other = type
            type = other.type
        elif isinstance(type, T2FlowType):
            other = None
        else:
            raise TypeError('port "%s" must be assigned a type' % name)
        port = self._.ports[name] = self._.PortClass(self._.flow, name, type)
        self._.order.append(name)
        if other is not None:
            port.link(other)

    def __getattr__(self, name):
        if self._.ports.has_key(name):
            return self._.ports[name] # return an existing typed port
        return self(name) # return a new untyped port

class UntypedInputPort:

    def __init__(self, flow, name):
        self.flow = flow
        self.name = name

    def __or__(self, sink):
        return self.flow.linkData(self, sink)

class WorkflowInputPorts(WorkflowPorts):

    def __init__(self, flow):
        WorkflowPorts.__init__(self, flow)
        self._.PortClass = WorkflowInputPort

    def __call__(self, name):
        # this should be called untypedPort(), but that would pollute the
        # namespace that this class represents, so we use __call__ as a hack
        return UntypedInputPort(self._.flow, name)

class UntypedOutputPort:

    def __init__(self, flow, name):
        self.flow = flow
        self.name = name

    def __ror__(self, source):
        return self.flow.linkData(source, self)

class WorkflowOutputPorts(WorkflowPorts):

    def __init__(self, flow):
        WorkflowPorts.__init__(self, flow)
        self._.PortClass = WorkflowOutputPort

    def __call__(self, name):
        # this should be called untypedPort(), but that would pollute the
        # namespace that this class represents, so we use __call__ as a hack
        return UntypedOutputPort(self._.flow, name)

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
        self.ctrlLinks = []
        self.input = WorkflowInputPorts(self)
        self.output = WorkflowOutputPorts(self)
        self.task = WorkflowTasks(self)
        self.title = title
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
        return self.annotations.get('net.sf.taverna.t2.annotation.annotationbeans.DescriptiveTitle')

    @title.setter
    def title(self, value):
        if not isinstance(value, Annotation):
            value = Annotation(value)
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.DescriptiveTitle'] = value
        self.name = tavernaName(value.text)
        
    @property
    def author(self):
        return self.annotations.get('net.sf.taverna.t2.annotation.annotationbeans.Author')

    @author.setter
    def author(self, value):
        if not isinstance(value, Annotation):
            value = Annotation(value)
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.Author'] = value
        
    @property
    def description(self):
        return self.annotations.get('net.sf.taverna.t2.annotation.annotationbeans.FreeTextDescription')

    @description.setter
    def description(self, value):
        if not isinstance(value, Annotation):
            value = Annotation(value)
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.FreeTextDescription'] = value

    def isWorkbenchSafe(self):
        # If this is set to False, RServe activities will use direct mapping of 
        # dotted names. Taverna Engine is OK with this, but Workbench cannot
        # display the links or edit the component.
        # If it is True, the RServe activity will add lines to the start and
        # end of the script to map to Workbench-friendly names inside the script.
        return True

    def selectUniqueLabel(self, namespace, candidate):
        i = 1
        label = candidate
        while label in namespace:
            i += 1
            label = '%s_%d' % (candidate, i)
        return label

    def addActivity(self, activity, candidate=None):
        if candidate is None:
            if activity.name is None:
                candidate = activity.__class__.__name__
            else:
                candidate = activity.name
        label = self.selectUniqueLabel(self.task, candidate)
        task = self.task[label] << activity
        return task

    def linkData(self, source, sink):
        if isinstance(source, DepthChange):
            source = source.base
        if isinstance(sink, DepthChange):
            depthChange = sink.depthChange
            sink = sink.base
        else:
            depthChange = 0
        if isinstance(source, basestring):
            source = self.addActivity(TextConstant(source), sink.name)
        elif isinstance(source, Activity):
            source = self.addActivity(source)
        if isinstance(sink, Activity):
            sink = self.addActivity(sink)
        # need to sort activities out before untyped sinks, so that type
        # mapping will work
        if isinstance(source, UntypedInputPort):
            if isinstance(sink, UntypedOutputPort):
                raise RuntimeError('cannot pipe input port to output port without declaring type')
            type = sink.asSinkPort().type
            if depthChange < 0:
                for i in range(-depthChange):
                    type = List[type]
            self.input[source.name] = type
            source = self.input[source.name]
        if isinstance(sink, UntypedOutputPort):
            type = source.asSourcePort().type
            if depthChange > 0:
                for i in range(depthChange):
                    type = List[type]
            self.output[sink.name] = type
            sink = self.output[sink.name]
        pipe = Pipeline(self, source, sink)
        source = source.asSourcePort()
        sink = sink.asSinkPort()
        if source.type.getDepth() + depthChange != sink.type.getDepth():
            raise RuntimeError('%s | %s: depths %d - %d != %d expected difference' % (source, sink, source.type.getDepth(), sink.type.getDepth(), depthChange))
        validator = sink.type.validator(source.type)
        if validator is not None:
            task = self.addActivity(validator, 'Validate_' + source.name)
            self.dataLinks.append(DataLink(source, task.input.input))
            self.dataLinks.append(DataLink(task.output.output, sink))
        else:
            self.dataLinks.append(DataLink(source, sink))
        return pipe

    def sequenceTasks(self, task1, task2):
        self.ctrlLinks.append((task1, task2))

    def allDescendants(self, descendants=None):
        # Create a list of all nested workflows and their nested workflows, ad infinitum
        if descendants is None:
            descendants = []
        for task in self.task:
            for activity in task.activities:
                if isinstance(activity, NestedWorkflow): 
                    flow = activity.flow
                    descendants.append(flow)
                    flow.allDescendants(descendants)
        return descendants

    def exportXML(self, xml):
        # The uuidCache ensures that if a nested workflow is referenced more than once,
        # it is only added to the file once.
        uuidCache = set()
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.workflow(version=1, producedBy=getCreator()):
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
                with tav.conditions:
                    for task1, task2 in self.ctrlLinks:
                        tav.condition(control=task1.name, target=task2.name)
                with tav.datalinks:
                    for link in self.dataLinks:
                        link.exportXML(xml)
                with tav.annotations:
                    for annotationClass, annotation in self.annotations.items():
                        annotation.exportXML(xml, annotationClass)

def getCreator():
    from subprocess import check_output
    import os, traceback
    repo = "http://github.com/jongiddy/balcazapy"
    hash = " unknown version"
    modifications = ""
    try:
        balcazapy_home = os.environ['BALCAZAPY_HOME']
        output = check_output(["git", "config", "--get", "remote.origin.url"], cwd=balcazapy_home).strip()
        if output:
            repo = output
        words = check_output(["git", "show-ref", "--hash=10"], cwd=balcazapy_home).split()
        localHash = words[0]
        remoteHash = words[1]
        if remoteHash == localHash:
            hash = " " + localHash
        else:
            hash = " %s (remote %s)" % (localHash, remoteHash)
        if check_output(["git", "ls-files", "-m"], cwd=balcazapy_home).strip():
            modifications = ' with local modifications'
    except:
        traceback.print_exc()
    creator = "Balcazapy %s%s%s" % (repo, hash, modifications)
    return creator