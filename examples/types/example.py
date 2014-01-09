# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Cardiff University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import *

# This example demonstrates validation checks of input ports
# Create the t2flow file using the --validate option

flow = Workflow(title='Validation Example')


flow.task.Process << BeanshellCode("output = input1 + input2;",
	inputs=dict(
		input1=String['YES', 'NO'](description="Choose YES or NO", example="YES"),
		input2=Logical(description="Choose TRUE or FALSE", example="TRUE")
		),
	outputs=dict(output=String))
	
flow.input.Choice = flow.task.Process.input.input1
# Note, as we are changing the depth of the input, we need to redo the annotations
flow.input.Logicals = List[Logical](description="Choose TRUE or FALSE", example="TRUE")
flow.input.Logicals |+ flow.task.Process.input.input2

flow.task.Process |- flow.output.Output
