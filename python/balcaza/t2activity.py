__all__ = ('BeanshellCode', 'BeanshellFile', 'InteractionPage',
    'NestedWorkflow', 'NestedZapyFile', 'HTTP', 'XPath', 'TextConstant', 
    'RServer')

import re
from t2types import *
from t2util import alphanumeric, getAbsolutePathRelativeToCaller

class Activity(object):

    activityGroup = 'net.sf.taverna.t2.activities'
    activityArtifact = 'stringconstant-activity'
    activityVersion = '1.4'
    activityClass = 'net.sf.taverna.t2.activities.stringconstant.StringConstantActivity'
    configEncoding = 'xstream'

    def __init__(self, name=None, description=None, inputs=None, outputs=None,
        defaultInput=None, defaultOutput=None, parameters=None):
        self.name = name
        self.description = description
        if inputs is None:
            self.inputs = {}
        else:
            self.inputs = inputs
        if outputs is None:
            self.outputs = {}
        else:
            self.outputs = outputs
        self.defaultIn = defaultInput
        self.defaultOut = defaultOutput
        self.parameters = {}
        if parameters is not None:
            self.updateParameters(parameters)

    def __call__(self, **kw):
        import copy
        obj = copy.copy(self)
        obj.parameters = self.parameters.copy()
        obj.updateParameters(parameters)
        return obj

    def updateParameters(self, parameters):
        for name, value in parameters.items():
            if self.inputs.has_key(name):
                self.parameters[name] = value
            else:
                raise RuntimeError('non-existent parameter')

    def getInputType(self, name):
        return self.inputs[name]

    def getOutputType(self, name):
        return self.outputs[name]

    def defaultInput(self):
        if self.defaultIn:
            return self.defaultIn
        elif len(self.inputs) == 1:
            return self.inputs.keys()[0]
        return None

    def defaultOutput(self):
        if self.defaultOut:
            return self.defaultOut
        elif len(self.outputs) == 1:
            return self.outputs.keys()[0]
        return None

    def exportActivityXML(self, xml, connectedInputs, connectedOutputs):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav.activity:
                with tav.raven as raven:
                    raven.group >> self.activityGroup
                    raven.artifact >> self.activityArtifact
                    raven.version >> self.activityVersion
                tav['class'] >> self.activityClass
                with tav.inputMap:
                    for port in connectedInputs:
                        tav.map({'from': port.name}, to=port.name)
                with tav.outputMap:
                    for port in connectedOutputs:
                        tav.map({'from': port.name}, to=port.name)
                with tav.configBean(encoding=self.configEncoding):
                    self.exportConfigurationXML(xml, connectedInputs, connectedOutputs)
                tav.annotations

class BeanshellCode(Activity):

    activityArtifact = 'beanshell-activity'
    activityVersion = '1.0.4'
    activityClass = 'net.sf.taverna.t2.activities.beanshell.BeanshellActivity'

    def __init__(self, script, localDependencies=(), **kw):
        Activity.__init__(self, **kw)
        self.script = script
        self.localDependencies = localDependencies

    def exportConfigurationXML(self, xml, connectedInputs, connectedOutputs):
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

def BeanshellFile(filename, localDependencies=(), **kw):
    with open(getAbsolutePathRelativeToCaller(filename), 'r') as f:
        script = f.read()
    return BeanshellCode(script, localDependencies, **kw)

class NestedWorkflow(Activity):

    activityArtifact = 'dataflow-activity'
    activityClass = 'net.sf.taverna.t2.activities.dataflow.DataflowActivity'
    configEncoding = 'dataflow'

    def __init__(self, flow, **kw):
        Activity.__init__(self, inputs=flow.getInputs(), outputs=flow.getOutputs(), **kw)
        self.flow = flow

    def exportConfigurationXML(self, xml, connectedInputs, connectedOutputs):
        with xml.namespace('http://taverna.sf.net/2008/xml/t2flow') as tav:
            tav.dataflow(ref=self.flow.getId())

def NestedZapyFile(filename, flowname='flow'):
    with open(getAbsolutePathRelativeToCaller(filename), 'r') as f:
        source = f.read()
    code = compile(source, filename, 'exec')
    module = {}
    exec(code, module)
    flow = module[flowname]
    return NestedWorkflow(flow)

class InteractionPage(Activity):

    activityArtifact = 'interaction-activity'
    activityVersion = '1.0.4'
    activityClass = 'net.sf.taverna.t2.activities.interaction.InteractionActivity'

    def __init__(self, url, **kw):
        Activity.__init__(self, **kw)
        self.url = url

    def exportConfigurationXML(self, xml, connectedInputs, connectedOutputs):
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


class HTTP_Activity(Activity):

    activityArtifact = 'rest-activity'
    activityClass = 'net.sf.taverna.t2.activities.rest.RESTActivity'

    def __init__(self, httpMethod, urlTemplate, inputContentType=None,
        inputBinary=False, outputContentType='application/xml', headers=None, 
        sendExpectHeader=False, escapeParameters=True, defaultInput=None):
        assert httpMethod in ('GET', 'POST', 'PUT', 'DELETE'), httpMethod
        inputs = {}
        variables = re.findall(r'\{([^}]+)\}', urlTemplate)
        for variable in variables:
            inputs[variable] = String
        if inputContentType:
            inputs['inputBody'] = String(description="Input for HTTP request in MIME %s format" % inputContentType)
            if defaultInput is None:
                defaultInput = 'inputBody'
        Activity.__init__(self, inputs=inputs, outputs=dict(
            responseBody = String,
            status = Integer[100,...,599]
            ),
            defaultInput = defaultInput,
            defaultOutput = 'responseBody'
        )
        self.httpMethod = httpMethod
        self.urlTemplate = urlTemplate
        self.inputContentType = inputContentType
        self.inputBinary = inputBinary
        self.outputContentType = outputContentType
        self.sendExpectHeader = sendExpectHeader
        self.escapeParameters = escapeParameters
        self.headers = headers

    def getOutputType(self, name):
        if name in ('redirection', 'actualUrl'):
            return String
        elif name == 'responseHeaders':
            return List[String]
        else:
            return Activity.getOutputType(self, name)

    def exportConfigurationXML(self, xml, connectedInputs, connectedOutputs):
        with xml.namespace() as conf:
            with conf.net.sf.taverna.t2.activities.rest.RESTActivityConfigurationBean:
                conf.httpMethod >> self.httpMethod
                conf.urlSignature >> self.urlTemplate
                conf.acceptsHeaderValue >> self.outputContentType
                conf.contentTypeForUpdates >> (self.inputContentType if self.inputContentType else 'application/xml')
                conf.outgoingDataFormat >> ('Binary' if self.inputBinary else 'String')
                conf.sendHTTPExpectRequestHeader >> ('true' if self.sendExpectHeader else 'false')
                conf.showRedirectionOutputPort >> ('true' if 'redirection' in connectedOutputs else 'false')
                conf.showActualUrlPort >> ('true' if 'actualUrl' in connectedOutputs else 'false')
                conf.showResponseHeadersPort >> ('true' if 'responseHeaders' in connectedOutputs else 'false')
                conf.escapeParameters >> ('true' if self.escapeParameters else 'false')
                with conf.otherHTTPHeaders:
                    if self.headers is not None:
                        for name, value in self.headers.items():
                            with conf.list:
                                conf.string >> name
                                conf.string >> value
                with conf.activityInputs:
                    for name in self.inputs.keys():
                        with conf.entry:
                            conf.string >> name
                            conf['java-class'] >> 'java.lang.String'

class HTTP_Factory:

    def GET(self, urlTemplate, outputContentType='application/xml', 
        headers=None, escapeParameters=True):
        return HTTP_Activity('GET', urlTemplate, headers=headers, 
            outputContentType=outputContentType, 
            escapeParameters=escapeParameters)

    def DELETE(self, urlTemplate, outputContentType='application/xml', 
        headers=None, escapeParameters=True):
        return HTTP_Activity('DELETE', urlTemplate, headers=headers,
            outputContentType=outputContentType,
            escapeParameters=escapeParameters)

    def POST(self, urlTemplate, inputContentType='application/xml',
        inputBinary=False, outputContentType='application/xml', 
        headers=None, sendExpectHeader=False, escapeParameters=True):
        return HTTP_Activity('POST', urlTemplate,
            inputContentType=inputContentType, inputBinary=inputBinary,
            outputContentType=outputContentType, 
            headers=headers, sendExpectHeader=sendExpectHeader, 
            escapeParameters=escapeParameters)

    def PUT(self, urlTemplate, inputContentType='application/xml',
        inputBinary=False, outputContentType='application/xml', 
        headers=None, sendExpectHeader=False, escapeParameters=True):
        return HTTP_Activity('PUT', urlTemplate,
            inputContentType=inputContentType, inputBinary=inputBinary,
            outputContentType=outputContentType, 
            headers=headers, sendExpectHeader=sendExpectHeader, 
            escapeParameters=escapeParameters)

HTTP = HTTP_Factory()

class XPathActivity(Activity):

    activityArtifact = 'xpath-activity'
    activityClass = 'net.sf.taverna.t2.activities.xpath.XPathActivity'

    def __init__(self, xpath, xmlns=None):
        Activity.__init__(self, inputs={'xml_text': String}, outputs={
            'nodelist': List[String],
            'nodelistAsXML': List[String]
            },
            defaultInput='xml_text',
            defaultOutput='nodelist')
        self.xpath = xpath
        self.xmlns = xmlns

    def exportConfigurationXML(self, xml, connectedInputs, connectedOutputs):
        with xml.namespace() as conf:
            with conf.net.sf.taverna.t2.activities.xpath.XPathActivityConfigurationBean:
                # the xmlDocument is used solely for Workbench generation of
                # the XPath expression. It is not required for operation. But
                # if is empty, Workbench gives a validation warning. To prevent
                # the warning, we add a tiny XML document.
                conf.xmlDocument >> '<x/>'
                conf.xpathExpression >> self.xpath
                with conf.xpathNamespaceMap:
                    if self.xmlns is not None:
                        for abbr, url in self.xmlns.items():
                            with conf.entry:
                                conf.string >> abbr
                                conf.string >> url

XPath = XPathActivity

class TextConstant(Activity):

    activityArtifact = 'stringconstant-activity'
    activityClass = 'net.sf.taverna.t2.activities.stringconstant.StringConstantActivity'

    def __init__(self, text):
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

    def exportConfigurationXML(self, xml, connectedInputs, connectedOutputs):
        with xml.namespace() as conf:
            with conf.net.sf.taverna.t2.activities.stringconstant.StringConstantConfigurationBean:
                conf.value >> self.text

# The name of a special port for transferring the R workspace. This is the
# default port for Rserve activities. Although the code inserted by Balcazapy
# allows underscores in this name, the additional code inserted by Taverna 
# Engine does not. BioVeL JIRA bug [TAV-481]
RWorkspacePort = 'RWorkspace'

def checkPortTypesValidForR(ports):
    if ports is not None:
        if ports.has_key(RWorkspacePort):
            raise RuntimeError('Port name "%s" is reserved for R activity' % RWorkspacePort)
        for name, type in ports.items():
            if not hasattr(type, 'symanticType'):
                raise RuntimeError('Invalid R type "%s = %s"' % (name, type))

class RserveServerActivity(Activity):

    activityArtifact = 'rshell-activity'
    activityClass = 'net.sf.taverna.t2.activities.rshell.RshellActivity'

    def __init__(self, rserve, script, inputs=None, inputMap=None, outputs=None,
        outputMap=None, **kw):
        checkPortTypesValidForR(inputs)
        checkPortTypesValidForR(outputs)
        Activity.__init__(self, inputs=inputs, outputs=outputs, **kw)
        self.rserve = rserve
        # Taverna 2.4 adds lines to the to the end of a script to access output
        # values, but does not add a newline to separate the last line of our
        # script from the first line added by Taverna. So, we ensure the script
        # ends with a newline.
        self.script = script.strip() + '\n'
        self.prefix = ''
        self.suffix = ''
        if inputMap is not None:
            for tName, rName in inputMap.items():
                if tName not in inputs:
                    raise RuntimeError('inputMap specifies "%s", but not in inputs' % tName)
                self.prefix += '%s <- %s\nrm(%s)\n' % (rName, tName, tName)
        if outputMap is not None:
            from t2types import TextFileType, BinaryFileType
            for tName, rName in outputMap.items():
                if tName not in outputs:
                    raise RuntimeError('outputMap specifies "%s", but not in outputs' % tName)
                if isinstance(outputs[tName], (TextFileType, BinaryFileType)):
                    # also needs to be set at beginning
                    self.prefix += '%s <- %s\nrm(%s)\n' % (rName, tName, tName)
                self.suffix += '%s <- %s\n' % (tName, rName)

    def defaultInput(self):
        if self.defaultIn is None:
            return RWorkspacePort
        return Activity.defaultInput(self)

    def defaultOutput(self):
        if self.defaultOut is None:
            return RWorkspacePort
        return Activity.defaultOutput(self)

    def getInputType(self, name):
        # If the variable has not been named as an input port for the RShell,
        # check (poorly) whether the variable appears in the script. If it
        # does, act as though the variable had been defined as an input port of
        # type RExpression.
        if name == RWorkspacePort:
            return BinaryFile
        try:
            return Activity.getInputType(self, name)
        except KeyError:
            if name in self.script:
                return RExpression

    def getOutputType(self, name):
        # If the variable has not been named as an output port for the RShell,
        # check (poorly) whether the variable appears in the script. If it
        # does, act as though the variable had been defined as an output port
        # of type RExpression.
        if name == RWorkspacePort:
            return BinaryFile
        try:
            return Activity.getOutputType(self, name)
        except KeyError:
            if name in self.script:
                return RExpression

    def exportConfigurationXML(self, xml, connectedInputs, connectedOutputs):
        # For inputs and outputs, first create a dictionary of connected ports,
        # all of type RExpression.  The overwrite these values with the ports
        # defined for the activity.  This leaves only the undefined ports
        # specified with type RExpression.
        prefix = self.prefix
        suffix = self.suffix
        inputs = {}
        for port in connectedInputs:
            inputs[port.name] = RExpression
        inputs.update(self.inputs)
        outputs = {}
        for port in connectedOutputs:
            outputs[port.name] = RExpression
        outputs.update(self.outputs)
        if inputs.has_key(RWorkspacePort) or outputs.has_key(RWorkspacePort):
            prefix += '.wsfile<-get("%s")\nrm("%s")\n' % (RWorkspacePort, RWorkspacePort)
            if inputs.has_key(RWorkspacePort):
                inputs[RWorkspacePort] = BinaryFile
                prefix += 'load(.wsfile)\n'
            if outputs.has_key(RWorkspacePort):
                outputs[RWorkspacePort] = BinaryFile
                suffix = 'save(list=ls(all.names=FALSE), file=.wsfile)\n"%s"<-.wsfile\n' % RWorkspacePort + suffix
        with xml.namespace() as config:
            with config.net.sf.taverna.t2.activities.rshell.RshellActivityConfigurationBean:
                with config.inputs:
                    for name, type in inputs.items():
                        with config.net.sf.taverna.t2.workflowmodel.processor.activity.config.ActivityInputPortDefinitionBean as inputPort:
                            inputPort.name >> name
                            inputPort.depth >> type.getDepth()
                            inputPort.allowsLiteralValues >> 'false'
                with config.outputs:
                    for name, type in outputs.items():
                        with config.net.sf.taverna.t2.workflowmodel.processor.activity.config.ActivityOutputPortDefinitionBean as outputPort:
                            outputPort.name >> name
                            outputPort.depth >> type.getDepth()
                            outputPort.mimeTypes
                            outputPort.granularDepth >> type.getDepth()
                config.rVersion >> 'false'
                config.script >> prefix >> self.script >> suffix
                with config.connectionSettings as conn:
                    self.rserve.exportXML(xml)
                    conn.keepSessionAlive >> 'false'
                    conn.newRVersion >> 'false'
                with config.inputSymanticTypes:
                    for name, type in inputs.items():
                        with config.net.sf.taverna.t2.activities.rshell.RShellPortSymanticTypeBean:
                            config.name >> name
                            config.symanticType >> type.symanticType()
                with config.outputSymanticTypes:
                    for name, type in outputs.items():
                        with config.net.sf.taverna.t2.activities.rshell.RShellPortSymanticTypeBean:
                            config.name >> name
                            config.symanticType >> type.symanticType()

class RServer:

    def __init__(self, host='localhost', port=6311):
        self.host = host
        self.port = port

    def exportXML(self, xml):
        with xml.namespace() as conn:
            conn.host >> self.host
            conn.port >> self.port

    def code(self, script, **kw):
        return RserveServerActivity(self, script, **kw)

    def file(self, filename, encoding='utf-8', **kw):
        import codecs
        with codecs.open(getAbsolutePathRelativeToCaller(filename), encoding=encoding) as f:            return RserveServerActivity(self, f.read(), **kw)