import uuid

from t2types import *
from t2activity import *

def getUUID():
    return uuid.uuid4()


class Annotation:

    def __init__(self, text):
        self.text = text
        self.chain = 'annotation_chain'
        self.label = 'text'

    def exportXML(self, xml, annotationClass):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav[self.chain](encoding="xstream"):
                with xml.namespace() as annotation:
                    with annotation.net.sf.taverna.t2.annotation.AnnotationChainImpl:
                        with annotation.annotationAssertions:
                            with annotation.net.sf.taverna.t2.annotation.AnnotationAssertionImpl:
                                with annotation.annotationBean({'class': annotationClass}):
                                    annotation[self.label] >> self.text
                                annotation.date >> '2013-11-27 14:27:50.10 UTC'
                                annotation.creators
                                annotation.curationEventList

class Annotation_2_2(Annotation):

    def __init__(self, text):
        Annotation.__init__(self, text)
        self.chain = 'annotation_chain_2_2'
        self.label = 'identification'

class Source:
    pass

class Sink:
    pass

class InputPort(Source):

    def __init__(self, name, t2type):
        self.name = name
        self.depth = t2type.getDepth()
        self.annotations = {}

    def setDescription(self, annotation):
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.FreeTextDescription'] = annotation

    def setExampleValue(self, annotation):
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.ExampleValue'] = annotation
    
    def exportXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.port as port:
                port.name >> self.name
                port.depth >> self.depth
                port.granularDepth >> self.depth
                with port.annotations:
                    for annotationClass, annotation in self.annotations.items():
                        annotation.exportXML(xml, annotationClass)

    def exportSourceXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.source(type="dataflow"):
                tav.port >> self.name

class OutputPort(Sink):

    def __init__(self, name, t2type):
        self.name = name
        self.annotations = {}

    def setDescription(self, annotation):
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.FreeTextDescription'] = annotation

    def setExampleValue(self, annotation):
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.ExampleValue'] = annotation
    
    def exportXML(self, xml):
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

class ProcessorInput(Sink):

    def __init__(self, processor, name):
        self.processor = processor
        self.name = name

    def exportSinkXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.sink(type="processor"):
                tav.processor >> self.processor.name
                tav.port >> self.name

class ProcessorInputs:

    def __init__(self, processor):
        self.processor = processor

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, name):
        self.processor.enableInputPort(name)
        return ProcessorInput(self.processor, name)

class ProcessorOutput(Source):

    def __init__(self, processor, name):
        self.processor = processor
        self.name = name

    def exportSourceXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.source(type="processor"):
                tav.processor >> self.processor.name
                tav.port >> self.name

class ProcessorOutputs:

    def __init__(self, processor):
        self.processor = processor

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, name):
        self.processor.enableOutputPort(name)
        return ProcessorOutput(self.processor, name)

class Processor:

    def __init__(self, name):
        self.name = name
        self.annotations = {}
        self.activities = []
        self.input = ProcessorInputs(self)
        self.output = ProcessorOutputs(self)
        self.inputMap = []
        self.outputMap = []

    def setDescription(self, annotation):
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.FreeTextDescription'] = annotation
    
    def addActivity(self, task):
        self.activities.append(task)

    def enableInputPort(self, name):
        if name in self.activities[0].inputs:
            self.inputMap.append((name, name, self.activities[0].inputs[name].getDepth()))
        else:
            raise RuntimeError('input port %s not found' % name)

    def enableOutputPort(self, name):
        if name in self.activities[0].outputs:
            self.outputMap.append((name, name, self.activities[0].outputs[name].getDepth()))
        else:
            raise RuntimeError('output port %s not found' % name)

    def exportXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.processor as proc:
                proc.name >> self.name
                with proc.inputPorts:
                    for (source, sink, depth) in self.inputMap:
                        with proc.port:
                            proc.name >> source
                            proc.depth >> depth
                with proc.outputPorts:
                    for (source, sink, depth) in self.outputMap:
                        with proc.port:
                            proc.name >> source
                            proc.depth >> depth
                            proc.granularDepth >> depth
                with proc.annotations:
                    for annotationClass, annotation in self.annotations.items():
                        annotation.exportXML(xml, annotationClass)
                with proc.activities:
                    for activity in self.activities:
                        activity.exportXML(xml) 
                with proc.dispatchStack:
                    with proc.dispatchLayer:
                        with proc.raven as raven:
                            raven.group >> 'net.sf.taverna.t2.core'
                            raven.artifact >> 'workflowmodel-impl'
                            raven.version >> '1.4'
                        proc['class'] >> 'net.sf.taverna.t2.workflowmodel.processor.dispatch.layers.Parallelize'
                        with proc.configBean(encoding="xstream"):
                            with xml.namespace() as Parallelize:
                                with Parallelize.net.sf.taverna.t2.workflowmodel.processor.dispatch.layers.ParallelizeConfig:
                                    Parallelize.maxJobs >> 1
                    with proc.dispatchLayer:
                        with proc.raven as raven:
                            raven.group >> 'net.sf.taverna.t2.core'
                            raven.artifact >> 'workflowmodel-impl'
                            raven.version >> '1.4'
                        proc['class'] >> 'net.sf.taverna.t2.workflowmodel.processor.dispatch.layers.ErrorBounce'
                        with proc.configBean(encoding="xstream"):
                            with xml.namespace() as ErrorBounce:
                                ErrorBounce.null
                    with proc.dispatchLayer:
                        with proc.raven as raven:
                            raven.group >> 'net.sf.taverna.t2.core'
                            raven.artifact >> 'workflowmodel-impl'
                            raven.version >> '1.4'
                        proc['class'] >> 'net.sf.taverna.t2.workflowmodel.processor.dispatch.layers.Failover'
                        with proc.configBean(encoding="xstream"):
                            with xml.namespace() as Failover:
                                Failover.null
                    with proc.dispatchLayer:
                        with proc.raven as raven:
                            raven.group >> 'net.sf.taverna.t2.core'
                            raven.artifact >> 'workflowmodel-impl'
                            raven.version >> '1.4'
                        proc['class'] >> 'net.sf.taverna.t2.workflowmodel.processor.dispatch.layers.Retry'
                        with proc.configBean(encoding="xstream"):
                            with xml.namespace() as Retry:
                                with Retry.net.sf.taverna.t2.workflowmodel.processor.dispatch.layers.RetryConfig:
                                    Retry.backoffFactor >> '1.0'
                                    Retry.initialDelay >> '1000'
                                    Retry.maxDelay >> '5000'
                                    Retry.maxRetries >> '0'
                    with proc.dispatchLayer:
                        with proc.raven as raven:
                            raven.group >> 'net.sf.taverna.t2.core'
                            raven.artifact >> 'workflowmodel-impl'
                            raven.version >> '1.4'
                        proc['class'] >> 'net.sf.taverna.t2.workflowmodel.processor.dispatch.layers.Invoke'
                        with proc.configBean(encoding="xstream"):
                            with xml.namespace() as Invoke:
                                Invoke.null
                with proc.iterationStrategyStack:
                    with proc.iteration:
                        proc.strategy

class DataLink:

    def __init__(self, source, sink):
        self.source = source
        self.sink = sink

    def exportXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.datalink:
                self.source.exportSourceXML(xml)
                self.sink.exportSinkXML(xml)

class Workflow:

    def __init__(self, name):
        self.id = getUUID()
        self.name = name
        self.annotations = {}
        self.inputPorts = []
        self.inputs = {}
        self.outputPorts = []
        self.outputs = {}
        self.processors = {}
        self.dataLinks = []
        self.nested = []

    def setTitle(self, annotation):
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.DescriptiveTitle'] = annotation
    
    def setAuthors(self, annotation):
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.Author'] = annotation
    
    def setDescription(self, annotation):
        self.annotations['net.sf.taverna.t2.annotation.annotationbeans.FreeTextDescription'] = annotation
    
    def addInput(self, name, t2type, description=None, example=None):
        port = InputPort(name, t2type)
        if description is not None:
            port.setDescription(Annotation(description))
        if example is not None:
            port.setExampleValue(Annotation(example))
        self.inputPorts.append(port)
        self.inputs[name] = t2type
        return port

    def addOutput(self, name, t2type, description=None, example=None):
        port = OutputPort(name, t2type)
        if description is not None:
            port.setDescription(Annotation(description))
        if example is not None:
            port.setExampleValue(Annotation(example))
        self.outputPorts.append(port)
        self.outputs[name] = t2type
        return port

    def addTask(self, name, activity, description=None):
        assert isinstance(activity, Activity), activity
        processor = Processor(name)
        if description is not None:
            processor.setDescription(Annotation(description))
        processor.addActivity(activity)
        self.processors[name] = processor
        return processor

    def addFlow(self, name, flow, description=None):
        assert isinstance(flow, Workflow), flow
        self.nested.append(flow)
        return self.addTask(name, DataflowActivity(flow, inputs=self.inputs, outputs=self.outputs), description)

    def linkData(self, source, sink):
        if not isinstance(source, Source):
            text = str(source)
            import string
            parts = text.split()
            alnum = string.letters + string.digits
            candidate = ['_']
            while parts and len(candidate) < 25:
                candidate += [ch for ch in parts[0] if ch in alnum]
                del parts[0]
                candidate.append('_')
            i = 1
            oklabel = ''.join(candidate)
            label = oklabel
            while self.processors.has_key(label):
                i += 1
                label = oklabel + str(i)
            textConstant = self.addTask(label, TextConstant(text).output(value=String))
            source = textConstant.output.value
        if not isinstance(sink, Sink):
            raise TypeError("link sink must be a Sink")
        self.dataLinks.append(DataLink(source, sink))

    def allDescendants(self, descendants=None):
        # Create a list of all nested workflows and their nested workflows, ad infinitum
        if descendants is None:
            descendants = []
        for child in self.nested:
            descendants.append(child)
            child.allDescendants(descendants)
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
                    for port in self.inputPorts:
                        port.exportXML(xml)
                with tav.outputPorts:
                    for port in self.outputPorts:
                        port.exportXML(xml)
                with tav.processors:
                    for processor in self.processors.values():
                        processor.exportXML(xml)                    
                tav.conditions
                with tav.datalinks:
                    for link in self.dataLinks:
                        link.exportXML(xml)
                with tav.annotations:
                    for annotationClass, annotation in self.annotations.items():
                        annotation.exportXML(xml, annotationClass)

