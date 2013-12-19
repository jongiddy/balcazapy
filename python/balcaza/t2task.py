from t2base import Namespace, OrderedMapIterator, Port, Ports, Source, Sink
from t2annotation import Annotation
from t2activity import Activity

class TaskPort(Port):

    def __init__(self, task, name, type):
        Port.__init__(self, name, type)
        self.task = task

class TaskInputPort(TaskPort, Sink):

    def __init__(self, flow, task, name):
        type = task.activity.getInputType(name)
        Sink.__init__(self, flow)
        TaskPort.__init__(self, task, name, type)

    def exportInputPortXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.port as port:
                port.name >> self.name
                port.depth >> self.getDepth()

    def exportSinkXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.sink(type="processor"):
                tav.processor >> self.task.name
                tav.port >> self.name

class TaskOutputPort(TaskPort, Source):

    def __init__(self, flow, task, name):
        type = task.activity.getOutputType(name)
        Source.__init__(self, flow)
        TaskPort.__init__(self, task, name, type)
        
    def exportOutputPortXML(self, xml):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.port as port:
                port.name >> self.name
                depth = self.getDepth()
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
        self.flow = flow
        if activity is not None:
            self.activity = activity
        self.annotations = {}
        self.input = TaskInputPorts(flow, self)
        self.output = TaskOutputPorts(flow, self)
        self.retryConfig = {
            'maxRetries': 0,
            'initialDelay': 1000,
            'maxDelay': 5000,
            'backoffFactor': 1.0
        }
        self.parallelizeConfig = {
            'maxJobs': 1
        }

    def extendUnusedPorts(self):
        self.extendUnusedInputs()
        self.extendUnusedOutputs()

    def extendUnusedInputs(self):
        for portName in self.activity.inputs.keys():
            if portName not in self.input:
                flowPort = self.flow.selectUniqueLabel(self.flow.input, portName)
                self.flow.input[flowPort] = self.input[portName]

    def extendUnusedOutputs(self):
        for portName in self.activity.outputs.keys():
            if portName not in self.output:
                flowPort = self.flow.selectUniqueLabel(self.flow.output, portName)
                self.flow.output[flowPort] = self.output[portName]

    def parallel(self, maxJobs):
        self.parallelizeConfig['maxJobs'] = maxJobs

    def retry(self, maxRetries=None, initialDelay=None, maxDelay=None, backoffFactor=None):
        if maxRetries is not None:
            self.retryConfig['maxRetries'] = maxRetries
        if initialDelay is not None:
            self.retryConfig['initialDelay'] = initialDelay
        if maxDelay is not None:
            self.retryConfig['maxDelay'] = maxDelay
        if backoffFactor is not None:
            self.retryConfig['backoffFactor'] = backoffFactor

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
                        port.exportInputPortXML(xml)
                with proc.outputPorts:
                    for port in self.output:
                        port.exportOutputPortXML(xml)
                with proc.annotations:
                    for annotationClass, annotation in self.annotations.items():
                        annotation.exportXML(xml, annotationClass)
                with proc.activities:
                    self.activity.exportActivityXML(xml, self.input, self.output)
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
                                    Parallelize.maxJobs >> self.parallelizeConfig['maxJobs']
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
                                    Retry.backoffFactor >> self.retryConfig['backoffFactor']
                                    Retry.initialDelay >> self.retryConfig['initialDelay']
                                    Retry.maxDelay >> self.retryConfig['maxDelay']
                                    Retry.maxRetries >> self.retryConfig['maxRetries']
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
                            if self.input:
                                with proc.cross:
                                    for port in self.input:
                                        tav.port(name=port.name, depth=port.getDepth())

class UnassignedTask:

    def __init__(self, ns, name):
        self._ = ns
        self.name = name

    def __lshift__(self, activity):
        if not isinstance(activity, Activity):
            raise TypeError('cannot assign non-Activity %s to task "%s"' % (repr(activity), self.name))
        task = WorkflowTask(self._.flow, self.name, activity)
        self._.tasks[self.name] = task
        self._.order.append(self.name)
        return task

class WorkflowTasks(object):

    def __init__(self, flow):
        super(WorkflowTasks, self).__setattr__('_', Namespace())
        self._.flow = flow
        self._.tasks = {}
        self._.order = []

    def __iter__(self):
        return OrderedMapIterator(self._.tasks, self._.order)

    def __contains__(self, name):
        return self._.tasks.has_key(name)

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, activity):
        return self.__setattr__(name, activity)

    def __getattr__(self, name):
        if self._.tasks.has_key(name):
            return self._.tasks[name]
        else:
            return UnassignedTask(self._, name)
