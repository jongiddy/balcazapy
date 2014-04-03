# Copyright (C) 2013 Cardiff University
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

__all__ = ('BeanshellCode', 'BeanshellFile', 'InteractionPage',
    'NestedWorkflow', 'NestedZapyFile', 'HTTP', 'XPath', 'ExternalTool',
    'TextConstant', 'RServer')

import re
from t2base import CollectDepthChange, SplayDepthChange, WrapDepthChange
from t2types import BinaryFileType, TextFileType, String, Integer, List, BinaryFile, RExpression
from t2util import alphanumeric, getAbsolutePathRelativeToCaller

# allow textual forms of booleans to be generated using t2Boolean[boolean expression]
T2Boolean = ('false', 'true')


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
        self.fixedParameters = {}
        if parameters is not None:
            self.updateParameters(parameters)

    def __call__(self, **kw):
        import copy
        obj = copy.copy(self)
        obj.fixedParameters = self.fixedParameters.copy()
        obj.updateParameters(kw)
        return obj

    def __pos__(self):
        return SplayDepthChange(self)

    def __neg__(self):
        return CollectDepthChange(self)

    def __invert__(self):
        return WrapDepthChange(self)

    def updateParameters(self, parameters):
        for name, value in parameters.items():
            if self.inputs.has_key(name):
                self.fixedParameters[name] = value
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
        if not kw.has_key('inputs'):
            kw['inputs'] = flow.getInputs()
        if not kw.has_key('outputs'):
            kw['outputs'] = flow.getOutputs()
        Activity.__init__(self, **kw)
        self.flow = flow

    def exportConfigurationXML(self, xml, connectedInputs, connectedOutputs):
        with xml.namespace('http://taverna.sf.net/2008/xml/t2flow') as tav:
            tav.dataflow(ref=self.flow.getId())

def NestedZapyFile(filename, flowname='flow', **kw):
    with open(getAbsolutePathRelativeToCaller(filename), 'r') as f:
        source = f.read()
    code = compile(source, filename, 'exec')
    module = {}
    exec(code, module)
    flow = module[flowname]
    if not kw.has_key('inputs'):
        kw['inputs'] = {}
    if not kw.has_key('outputs'):
        kw['outputs'] = {}
    for name, type in kw['inputs'].items():
        if name not in flow.input:
            raise RuntimeError('Nested workflow does not have input "%s"' % name)
        nestedDepth = flow.input[name].type.getDepth()
        if type.getDepth() != nestedDepth:
            raise RuntimeError('Input port "%s" depth is %d' % (name, nestedDepth))
    for name, type in kw['outputs'].items():
        if name not in flow.output:
            raise RuntimeError('Nested workflow does not have output "%s"' % name)
        nestedDepth = flow.output[name].type.getDepth()
        if type.getDepth() != nestedDepth:
            raise RuntimeError('Output port "%s" depth is %d' % (name, nestedDepth))
    return NestedWorkflow(flow, **kw)

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
                            conf.allowsLiteralValues >> T2Boolean[False]
                with conf.outputs:
                    for name, type in self.outputs.items():
                        with conf.net.sf.taverna.t2.workflowmodel.processor.activity.config.ActivityOutputPortDefinitionBean:
                            conf.name >> name
                            conf.depth >> type.getDepth()
                            conf.mimeTypes
                            conf.granularDepth >> type.getDepth()
                conf.presentationOrigin >> self.url
                conf.interactionActivityType >> 'LocallyPresentedHtml'
                conf.progressNotification >> T2Boolean[False]


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
                conf.contentTypeForUpdates >> ('application/xml', self.inputContentType)[self.inputContentType]
                conf.outgoingDataFormat >> ('String', 'Binary')[self.inputBinary]
                conf.sendHTTPExpectRequestHeader >> T2Boolean[self.sendExpectHeader]
                conf.showRedirectionOutputPort >> T2Boolean['redirection' in connectedOutputs]
                conf.showActualUrlPort >> T2Boolean['actualUrl' in connectedOutputs]
                conf.showResponseHeadersPort >> T2Boolean['responseHeaders' in connectedOutputs]
                conf.escapeParameters >> T2Boolean[self.escapeParameters]
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

import uuid
def getUUID():
   return uuid.uuid4()

class ExternalToolActivity(Activity):

    activityArtifact = 'external-tool-activity'
    activityVersion = '1.5-SNAPSHOT'
    activityClass = 'net.sf.taverna.t2.activities.externaltool.ExternalToolActivity'

    def __init__(self, command, inputMap=None, outputMap=None, **kw):
        Activity.__init__(self, **kw)
        self.command = command
        self.inputMap = inputMap or {}
        self.outputMap = outputMap or {}

    def getInputType(self, name):
        if name in ('STDIN'):
            return String
        else:
            return Activity.getInputType(self, name)

    def getOutputType(self, name):
        if name in ('STDOUT', 'STDERR'):
            return String
        else:
            return Activity.getOutputType(self, name)

    def exportConfigurationXML(self, xml, connectedInputs, connectedOutputs):
        with xml.namespace() as conf:
            with conf.net.sf.taverna.t2.activities.externaltool.ExternalToolActivityConfigurationBean:
                conf.mechanismType >> '789663B8-DA91-428A-9F7D-B3F3DA185FD4'
                conf.mechanismName >> 'default local'
                conf.mechanismXML >> '''<?xml version="1.0" encoding="UTF-8"?>
<localInvocation><shellPrefix>/bin/sh -c</shellPrefix><linkCommand>/bin/ln -s %%PATH_TO_ORIGINAL%% %%TARGET_NAME%%</linkCommand></localInvocation>
'''
                conf.externaltoolid >> getUUID()
                with conf.useCaseDescription:
                    conf.usecaseid
                    conf.description
                    conf.command >> self.command
                    conf.preparingTimeoutInSeconds >> '1200'
                    conf.executionTimeoutInSeconds >> '1800'
                    conf.tags
                    conf.REs
                    conf.queue__preferred
                    conf.queue__deny
                    conf.static__inputs
                    with conf.inputs:
                        for name, type in self.inputs.items():
                            with conf.entry:
                                conf.string >> name
                                with conf.de.uni__luebeck.inb.knowarc.usecases.ScriptInputUser:
                                    # tag is either inputMap[name] or else just name
                                    tag = self.inputMap.get(name, name)
                                    conf.tag >> tag
                                    conf.file >> T2Boolean[isinstance(type, (BinaryFileType, TextFileType))]
                                    conf.tempFile >> T2Boolean[False]
                                    conf.binary >> T2Boolean[isinstance(type, BinaryFileType)]
                                    conf.charsetName >> 'UTF-8'
                                    conf.forceCopy >> T2Boolean[False]
                                    conf.list >> T2Boolean[False]
                                    conf.concatenate >> T2Boolean[False]
                                    conf.mime
                    with conf.outputs:
                        for name, type in self.outputs.items():
                            with conf.entry:
                                conf.string >> name
                                with conf.de.uni__luebeck.inb.knowarc.usecases.ScriptOutput:
                                    tag = self.outputMap.get(name, name)
                                    conf.path >> tag
                                    conf.binary >> T2Boolean[isinstance(type, BinaryFileType)]
                                    conf.mime
                    conf.includeStdIn >> T2Boolean['STDIN' in connectedInputs]
                    conf.includeStdOut >> T2Boolean['STDOUT' in connectedOutputs]
                    conf.includeStdErr >> T2Boolean['STDERR' in connectedOutputs]
                    with conf.validReturnCodes:
                        conf.int >> '0'
                conf.edited >> T2Boolean[False]

ExternalTool = ExternalToolActivity

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
            else:
                raise

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
            else:
                raise

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
                # Input ports are set before the script is run. To prevent the
                # workspace from overriding values provided as input ports,
                # save the workspace containing the input ports, then load the
                # provided workspace, then reload the input ports workspace.
                prefix += 'save(list=ls(all.names=FALSE), file="ws.tmp")\nload(.wsfile)\nload("ws.tmp")\n'
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
                            inputPort.allowsLiteralValues >> T2Boolean[False]
                with config.outputs:
                    for name, type in outputs.items():
                        with config.net.sf.taverna.t2.workflowmodel.processor.activity.config.ActivityOutputPortDefinitionBean as outputPort:
                            outputPort.name >> name
                            outputPort.depth >> type.getDepth()
                            outputPort.mimeTypes
                            outputPort.granularDepth >> type.getDepth()
                config.rVersion >> T2Boolean[False]
                config.script >> prefix >> self.script >> suffix
                with config.connectionSettings as conn:
                    self.rserve.exportXML(xml)
                    conn.keepSessionAlive >> T2Boolean[False]
                    conn.newRVersion >> T2Boolean[False]
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
