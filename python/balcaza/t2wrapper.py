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

from t2activity import NestedWorkflow
from t2types import ListType, String
from t2flow import Workflow
from ExternalToolZipper import ExternalToolZipper

class WrapperWorkflow(Workflow):

	def __init__(self, flow, validate=True, zip=False):
		self.flow = flow
		Workflow.__init__(self, flow.title, flow.author, flow.description)
		nested = self.task[flow.name] << NestedWorkflow(flow)
		for port in flow.input:
			if validate:
				# Set type to same depth, but basetype of String
				depth = port.type.getDepth()
				annotations = {name: port.type.getAnnotation(name) for name in port.type.dict}
				if depth == 0:
					type = String(**annotations)
				else:
					type = ListType('List', String, depth)(**annotations)
			else:
				type = port.type
			self.input[port.name] = type
			self.input[port.name] | nested.input[port.name]
		if zip:
			zipper = ExternalToolZipper()
			for port in flow.output:
				portName = port.name
				portType = port.type
				if portType.getDepth() == 0 and portType.dict.get('zip', True):
					filename = portType.dict.get('filename', portName).split('%%')
					if portType.dict.get('deleteIfEmpty', False):
						zipper.copyToZipIfNotEmpty(portName, filename)
					else:
						zipper.copyToZip(portName, filename)
				else:
					# Copy output port outside of zip if:
					# 1. it is a list (i.e. depth > 0), or
					# 2. it has the attribute zip=False
					nested.output[portName] | self.output[portName]
			ZipOutputs = self.task.ZipOutputs << zipper.activity()
			for name in zipper.zippedPorts():
				nested.output[name] | ZipOutputs.input[name]
			for name in zipper.filenameVars():
				depth = self.input[name].getDepth()
				if depth != 0:
					raise RuntimeError('cannot use input port "%s" of depth %d in filename' % (name, depth))
				self.input[name] | ZipOutputs.input[name]
			ZipOutputs.output.zipFile | self.output.zipFile
		else:
			for port in flow.output:
				nested.output[port.name] | self.output[port.name]

