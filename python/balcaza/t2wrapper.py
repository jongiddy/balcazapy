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

from t2activity import NestedWorkflow, ExternalTool
from t2types import ListType, String, BinaryFile, TextFile, TextFileType
from t2flow import Workflow

class WrapperWorkflow(Workflow):

	def __init__(self, flow, validate=True, zip=False):
		self.flow = flow
		Workflow.__init__(self, flow.title, flow.author, flow.description)
		nested = self.task[flow.name] << NestedWorkflow(flow)
		for port in flow.input:
			if validate:
				# Set type to same depth, but basetype of String
				depth = port.type.getDepth()
				if depth == 0:
					type = String
				else:
					type = ListType('List', String, depth)
				# Copy any annotations
				type.dict = port.type.dict
			else:
				type = port.type
			self.input[port.name] = type
			self.input[port.name] | nested.input[port.name]
		if zip:
			inputs = {}
			inputPorts = {}
			outputPorts = {}
			lines = []
			for port in flow.output:
				portName = port.name
				portType = port.type
				if portType.getDepth() == 0:
					type = (BinaryFile, TextFile)[isinstance(portType, TextFileType)]
					type.dict = portType.dict
					outputPorts[portName] = type
					if 'filename' in portType.dict:
						filename = portType.dict['filename']
						if filename != portName:
							lines.append("mv '%s' '%s'\n" % (portName, filename))
						# If filename contains %%var%% markers, ensure relevant
						# workflow input port is provided as input here.
						parts = filename.split('%%')
						while len(parts) >= 3:
							var = parts[1]
							inputPorts[var] = String
							del parts[:2]
				else:
					nested.output[portName] | self.output[portName]
			inputs = outputPorts.copy()
			for name, type in inputPorts.items():
				if name in inputs:
					raise RuntimeError('input and output name "%s" conflict' % (name,))
				if type.getDepth() != 0:
					raise RuntimeError('cannot use input port "%s" of depth %d in filename' % (name, type.getDepth()))
				inputs[name] = type
			# Add any input ports to the zip file, as long as its name doesn't clash
			for port in self.input:
				portName = port.name
				portType = port.type
				if portName not in inputs and portType.getDepth() == 0:
					if 'filename' in portType.dict:
						filename = portType.dict['filename']
						if filename != portName:
							lines.append("mv '%s' '%s'\n" % (portName, filename))
					inputs[portName] = BinaryFile
					inputPorts[portName] = BinaryFile
			lines.append('zip outputs.zip *\n')
			command = ''.join(lines)
			ZipOutputs = self.task.ZipOutputs << ExternalTool(
				command = command,
				inputs = inputs,
				outputs = dict(zipFile=BinaryFile),
				outputMap = dict(zipFile='outputs.zip')
				)
			for name, type in outputPorts.items():
				nested.output[name] | ZipOutputs.input[name]
			for name, type in inputPorts.items():
				self.input[name] | ZipOutputs.input[name]
			ZipOutputs.output.zipFile | self.output.zipFile
			ZipOutputs.output.STDOUT | self.output.stdout
			ZipOutputs.output.STDERR | self.output.stderr
		else:
			for port in flow.output:
				nested.output[port.name] | self.output[port.name]

