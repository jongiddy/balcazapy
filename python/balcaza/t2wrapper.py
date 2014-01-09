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

class WrapperWorkflow(Workflow):

	def __init__(self, flow):
		self.flow = flow
		Workflow.__init__(self, flow.title, flow.author, flow.description)
		nested = self.task[flow.name] << NestedWorkflow(flow)
		for port in flow.input:
			# Set type to same depth, but basetype of String
			depth = port.type.getDepth()
			if depth == 0:
				type = String
			else:
				type = ListType('List', String, depth)
			# Copy any annotations
			type.dict = port.type.dict
			self.input[port.name] = type
			self.input[port.name] | nested.input[port.name]
		for port in flow.output:
			# Set type to same depth, but basetype of String
			depth = port.type.getDepth()
			if depth == 0:
				type = String
			else:
				type = ListType('List', String, depth)
			# Copy any annotations
			type.dict = port.type.dict
			self.output[port.name] = type
			nested.output[port.name] | self.output[port.name]

