# -*- coding: utf-8 -*-
#
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

from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import *

flow = Workflow(
    title='Convert Taverna list of RExpr to R list',
    author='Jonathan Giddy',
    description="""This workflow accepts a Taverna list of arbitrary R expressions and returns a single R expression representing an R list containing the original expressions.

This workflow relies on the current Taverna behaviour of an R expression being represented by a list of strings containing the deparsed expression. If this changes, this workflow will likely break.

The first BeanShell converts each R expression (actually a list of strings) to a single string. This uses implicit iteration to do this for each R expression, so input port depth is 2 but the BeanShell input depth is 1. 

The second Beanshell creates a comma-separated list of the deparsed R expressions and wraps the string with the R list() function. So now we have a single string s that can be turned into an R list using eval(parse(text=s)).

But RShell already does that parsing for us, so we just need to ensure the string looks like an R expression by turning it into a list of strings. So we actually output a 1-element list containing the string.

Version 1: initial implementation
Version 2: reduce number of BeanShells
""")

from balcaza.activity.local.list import MergeStringListToString

Flatten = flow.task.RExpressionToString << MergeStringListToString

Join = flow.task.JoinListOfStringsIntoRList = BeanshellFile(
    "RStringsToRList.bsh",
    inputs = dict(stringlist=List[String]),
    outputs = dict(output=RExpression),
    name = 'JoinListOfStringsIntoRList'
    )

flow.input.list_of_r_expressions |+ Flatten |- Join | flow.output.r_list_of_expressions

ListRtoRList = NestedWorkflow(flow, name='ListRtoRList')
