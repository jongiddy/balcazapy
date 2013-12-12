from t2base import Namespace, Port, Ports, Source, Sink
from t2annotation import Annotation
from t2activity import Activity

class TaskPort(Port):

    def __init__(self, task, name):
        Port.__init__(self, name)
        self.task = task
        self.activityPortName = name
        self.connected = False

    def __getitem__(self, name):
        self.activityPortName = name
        return self

    def getName(self):
        return self.name

    def getDepth(self):
        assert self.connected
        return self.type.getDepth()

    def connect(self):
        self.connected = True
        self.type = self.mapActivityPort()

    def isConnected(self):
        return self.connected

class TaskInputPort(TaskPort, Sink):

    def __init__(self, flow, task, name):
        Sink.__init__(self, flow)
        TaskPort.__init__(self, task, name)

    def mapActivityPort(self):
        return self.task.mapInput(self.name, self.activityPortName)

    def exportInputPortXML(self, xml):
        assert self.connected
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.port as port:
                port.name >> self.name
                port.depth >> self.type.getDepth()

    def exportSinkXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.sink(type="processor"):
                tav.processor >> self.task.name
                tav.port >> self.name

class TaskOutputPort(TaskPort, Source):

    def __init__(self, flow, task, name):
        Source.__init__(self, flow)
        TaskPort.__init__(self, task, name)
        
    def mapActivityPort(self):
        return self.task.mapOutput(self.name, self.activityPortName)

    def exportOutputPortXML(self, xml):
        assert self.connected
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.port as port:
                port.name >> self.name
                depth = self.type.getDepth()
                port.depth >> depth
                port.granularDepth >> depth

    def exportSourceXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.source(type="processor"):
                tav.processor >> self.task.name
                tav.port >> self.name

class TaskPorts(Ports):

    def __init__(self, flow, task):
        super(TaskPorts, self).__init__(flow)
        self._.task = task

    def __getattr__(self, name):
        if self._.ports.has_key(name):
            port = self._.ports[name]
        else:
            port = self._.ports[name] = self._.PortClass(self._.flow, self._.task, name)
            self._.order.append(name)
        return port

class TaskInputPorts(TaskPorts):

    def __init__(self, flow, task):
        TaskPorts.__init__(self, flow, task)
        self._.PortClass = TaskInputPort

class TaskOutputPorts(TaskPorts):

    def __init__(self, flow, task):
        TaskPorts.__init__(self, flow, task)
        self._.PortClass = TaskOutputPort


class WorkflowTask(object):

    def __init__(self, flow, name, activity=None):
        self.name = name
        if activity is not None:
            self.activity = activity
        self.annotations = {}
        self.input = TaskInputPorts(flow, self)
        self.output = TaskOutputPorts(flow, self)
        self.inputMap = {}
        self.outputMap = {}

    def mapInput(self, processorPort, activityPort):
        self.activity.inputs[activityPort]
        if self.inputMap.has_key(activityPort):
            raise RuntimeError('activity input "%s" already mapped' % activityPort)
        self.inputMap[activityPort] = processorPort
        return self.activity.inputs[activityPort]

    def mapOutput(self, processorPort, activityPort):
        self.activity.outputs[activityPort]
        if self.outputMap.has_key(activityPort):
            if self.outputMap[activityPort] != processorPort:
                raise RuntimeError('activity output "%s" already mapped' % activityPort)
            else:
                # OK to map activity port to same processor port multiple times.
                # This happens when an output is an input to multiple inputs
                pass
        else:
            self.outputMap[activityPort] = processorPort
        return self.activity.outputs[activityPort]

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
    
    def __setitem__(self, description, activity):
        self.description = description
        self.activity = activity

    def exportXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.processor as proc:
                proc.name >> self.name
                with proc.inputPorts:
                    for port in self.input:
                        if port.isConnected():
                            port.exportInputPortXML(xml)
                with proc.outputPorts:
                    for port in self.output:
                        if port.isConnected():
                            port.exportOutputPortXML(xml)
                with proc.annotations:
                    for annotationClass, annotation in self.annotations.items():
                        annotation.exportXML(xml, annotationClass)
                with proc.activities:
                    with proc.activity:
                        with proc.raven as raven:
                            raven.group >> self.activity.activityGroup
                            raven.artifact >> self.activity.activityArtifact
                            raven.version >> self.activity.activityVersion
                        proc['class'] >> self.activity.activityClass
                        with proc.inputMap:
                            for activityPort, processorPort in self.inputMap.items():
                                proc.map({'from': processorPort}, to=activityPort)
                        with proc.outputMap:
                            for activityPort, processorPort in self.outputMap.items():
                                proc.map({'from': activityPort}, to=processorPort)
                        with proc.configBean(encoding=self.activity.configEncoding):
                            self.activity.exportConfigurationXML(xml)
                        proc.annotations
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
                        with proc.strategy:
                            connected = [port for port in self.input if port.isConnected()]
                            if connected:
                                with proc.cross:
                                    for port in connected:
                                        tav.port(name=port.getName(), depth=port.getDepth())

class WorkflowTasks(object):

    def __init__(self, flow):
        super(WorkflowTasks, self).__setattr__('_', Namespace())
        self._.flow = flow
        self._.tasks = {}
        self._.order = []

    def __getitem__(self, index):
        return self._.tasks[self._.order[index]]

    def __setattr__(self, name, activity):
        from t2flow import Workflow
        # flow.input.name = type
        if self._.tasks.has_key(name):
            raise RuntimeError('task "%s" defined twice for workflow "%s"' % (name, self._.flow.name))
        if not isinstance(activity, Activity):
            raise TypeError('cannot assign non-Activity %s to task "%s"' % (`activity`, name))
        self._.tasks[name] = WorkflowTask(self._.flow, name, activity)
        self._.order.append(name)

    def __getattr__(self, name):
        if self._.tasks.has_key(name):
            return self._.tasks[name]
        raise AttributeError(name)
