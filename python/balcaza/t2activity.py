__all__ = ('BeanshellActivity', 'InteractionActivity', 'NestedWorkflow', 
    'NestedWorkflowFile', 'RestActivity', 'TextConstant', 'RServer')

from t2util import alphanumeric

class Activity:

    activityGroup = 'net.sf.taverna.t2.activities'
    activityArtifact = 'stringconstant-activity'
    activityVersion = '1.4'
    activityClass = 'net.sf.taverna.t2.activities.stringconstant.StringConstantActivity'
    configEncoding = 'xstream'

    def __init__(self, inputs=None, outputs=None):
        if inputs is None:
            self.inputs = {}
        else:
            self.inputs = inputs
        if outputs is None:
            self.outputs = {}
        else:
            self.outputs = outputs

class BeanshellActivity(Activity):

    activityArtifact = 'beanshell-activity'
    activityVersion = '1.0.4'
    activityClass = 'net.sf.taverna.t2.activities.beanshell.BeanshellActivity'

    def __init__(self, script, localDependencies=(), **kw):
        Activity.__init__(self, **kw)
        self.script = script
        self.localDependencies = localDependencies

    def exportConfigurationXML(self, xml):
        with xml.namespace() as conf:
            with conf.net.sf.taverna.t2.activities.beanshell.BeanshellActivityConfigurationBean:
                with conf.inputs:
                    for name, type in self.inputs.items():
                        with conf.net.sf.taverna.t2.workflowmodel.processor.activity.config.ActivityInputPortDefinitionBean:
                            conf.name >> name
                            conf.depth >> type.getDepth()
                            with conf.mimeTypes:
                                conf.string >> 'text/plain'
                            conf.handledReferenceSchemes
                            conf.translatedElementType >> 'java.lang.String'
                            conf.allowsLiteralValues >> 'true'
                with conf.outputs:
                    for name, type in self.outputs.items():
                        with conf.net.sf.taverna.t2.workflowmodel.processor.activity.config.ActivityOutputPortDefinitionBean:
                            conf.name >> name
                            conf.depth >> type.getDepth()
                            conf.mimeTypes
                            conf.granularDepth >> type.getDepth()
                conf.classLoaderSharing >> 'workflow'
                with conf.localDependencies:
                    for dep in self.localDependencies:
                        conf.string >> dep
                conf.artifactDependencies
                conf.script >> self.script
                conf.dependencies

class NestedWorkflow(Activity):

    activityArtifact = 'dataflow-activity'
    activityClass = 'net.sf.taverna.t2.activities.dataflow.DataflowActivity'
    configEncoding = 'dataflow'

    def __init__(self, flow):
        Activity.__init__(self, inputs=flow.getInputs(), outputs=flow.getOutputs())
        self.flow = flow

    def exportConfigurationXML(self, xml):
        with xml.namespace('http://taverna.sf.net/2008/xml/t2flow') as tav:
            tav.dataflow(ref=self.flow.getId())

def NestedWorkflowFile(filename, flowname='flow'):
    with open(filename, 'r') as f:
        source = f.read()
    code = compile(source, filename, 'exec')
    module = {}
    exec(code, module)
    flow = module[flowname]
    return NestedWorkflow(flow)

class InteractionActivity(Activity):

    activityArtifact = 'interaction-activity'
    activityVersion = '1.0.4'
    activityClass = 'net.sf.taverna.t2.activities.interaction.InteractionActivity'

    def __init__(self, url, **kw):
        Activity.__init__(self, **kw)
        self.url = url

    def exportConfigurationXML(self, xml):
        with xml.namespace() as conf:
            with conf.net.sf.taverna.t2.activities.interaction.InteractionActivityConfigurationBean:
                with conf.inputs:
                    for name, type in self.inputs.items():
                        with conf.net.sf.taverna.t2.workflowmodel.processor.activity.config.ActivityInputPortDefinitionBean:
                            conf.name >> name
                            conf.depth >> type.getDepth()
                            with conf.mimeTypes:
                                conf.string >> 'text/plain'
                            conf.handledReferenceSchemes
                            conf.translatedElementType >> 'java.lang.String'
                            conf.allowsLiteralValues >> 'false'
                with conf.outputs:
                    for name, type in self.outputs.items():
                        with conf.net.sf.taverna.t2.workflowmodel.processor.activity.config.ActivityOutputPortDefinitionBean:
                            conf.name >> name
                            conf.depth >> type.getDepth()
                            conf.mimeTypes
                            conf.granularDepth >> type.getDepth()
                conf.presentationOrigin >> self.url
                conf.interactionActivityType >> 'LocallyPresentedHtml'
                conf.progressNotification >> 'false'


class RestActivity(Activity):

    activityArtifact = 'rest-activity'
    activityClass = 'net.sf.taverna.t2.activities.rest.RESTActivity'

    def __init__(self, httpMethod, urlTemplate, **kw):
        assert httpMethod in ('GET', 'POST', 'PUT', 'DELETE'), httpMethod
        Activity.__init__(self, **kw)
        self.httpMethod = httpMethod
        self.urlTemplate = urlTemplate

    def exportConfigurationXML(self, xml):
        with xml.namespace() as conf:
            with conf.net.sf.taverna.t2.activities.rest.RESTActivityConfigurationBean:
                conf.httpMethod >> self.httpMethod
                conf.urlTemplate >> self.urlTemplate
                conf.acceptsHeaderValue >> 'application/xml'
                conf.contentTypeForUpdates >> 'application/xml'
                conf.outgoingDataFormat >> 'String'
                conf.sendHTTPExpectRequestHeader >> 'false'
                conf.showRedirectionOutputPort >> 'false'
                conf.showActualUrlPort >> 'false'
                conf.showResponseHeadersPort >> 'false'
                conf.escapeParameters >> 'true'
                conf.otherHTTPHeaders
                with conf.activityInputs:
                    with conf.entry:
                      conf.string >> 'id'
                      conf['java-class'] >> 'java.lang.String'


class TextConstant(Activity):

    activityArtifact = 'stringconstant-activity'
    activityClass = 'net.sf.taverna.t2.activities.stringconstant.StringConstantActivity'

    def __init__(self, text):
        from t2types import String
        Activity.__init__(self, outputs=dict(value=String))
        self.text = str(text)

    def getLabel(self):
        parts = self.text.split()
        label = '__'
        candidate = ['_']
        while parts and (len(candidate) < 30):
            candidate += [ch for ch in parts[0] if ch in alphanumeric]
            del parts[0]
            candidate.append('_')
            if len(candidate) > 30:
                break
            label = ''.join(candidate)
        return label

    def exportConfigurationXML(self, xml):
        with xml.namespace() as conf:
            with conf.net.sf.taverna.t2.activities.stringconstant.StringConstantConfigurationBean:
                conf.value >> self.text

class RServerActivity(Activity):

    activityArtifact = 'rshell-activity'
    activityClass = 'net.sf.taverna.t2.activities.rshell.RshellActivity'

    def __init__(self, rserve, script, **kw):
        Activity.__init__(self, **kw)
        self.rserve = rserve
        self.script = script
        if not script.endswith('\n'):
            # Taverna 2.4 adds lines to the to the end of a script to 
            # access output values, but does not add a newline to separate
            # the last line of our script from the first line added by
            # Taverna. So, we ensure the script ends with a newline.
            self.script += '\n'

    def exportConfigurationXML(self, xml):
        with xml.namespace() as config:
            with config.net.sf.taverna.t2.activities.rshell.RshellActivityConfigurationBean:
                with config.inputs:
                    for name, type_ in self.inputs.items():
                        with config.net.sf.taverna.t2.workflowmodel.processor.activity.config.ActivityInputPortDefinitionBean as inputPort:
                            inputPort.name >> name
                            inputPort.depth >> type_.getDepth()
                            inputPort.allowsLiteralValues >> 'false'
                with config.outputs:
                    for name, type_ in self.outputs.items():
                        with config.net.sf.taverna.t2.workflowmodel.processor.activity.config.ActivityOutputPortDefinitionBean as outputPort:
                            outputPort.name >> name
                            outputPort.depth >> type_.getDepth()
                            outputPort.mimeTypes
                            outputPort.granularDepth >> type_.getDepth()
                config.rVersion >> 'false'
                config.script >> self.script
                with config.connectionSettings as conn:
                    self.rserve.exportXML(xml)
                    conn.keepSessionAlive >> 'false'
                    conn.newRVersion >> 'false'
                with config.inputSymanticTypes:
                    for name, type_ in self.inputs.items():
                        with config.net.sf.taverna.t2.activities.rshell.RShellPortSymanticTypeBean:
                            config.name >> name
                            config.symanticType >> type_.symanticType()
                with config.outputSymanticTypes:
                    for name, type_ in self.outputs.items():
                        with config.net.sf.taverna.t2.activities.rshell.RShellPortSymanticTypeBean:
                            config.name >> name
                            config.symanticType >> type_.symanticType()

class RServer:

    def __init__(self, host='localhost', port=6311):
        self.host = host
        self.port = port

    def exportXML(self, xml):
        with xml.namespace() as conn:
            conn.host >> self.host
            conn.port >> self.port

    def Activity(self, script, **kw):
        return RServerActivity(self, script, **kw)

    def runScript(self, script, **kw):
        return RServerActivity(self, script, **kw)

    def runFile(self, filename, encoding='utf-8', **kw):
        import codecs
        with codecs.open(filename, encoding=encoding) as f:
            return RServerActivity(self, f.read(), **kw)
