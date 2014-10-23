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

import string

alphanumeric = string.letters + string.digits


def BeanshellEscapeString(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')


def getAbsolutePathRelativeToCaller(path):
    import inspect
    import os
    # the caller of the caller of this function is 3rd in the stack
    callerFrame = inspect.stack()[2]
    # the pathname is 2nd element n the returned tuple
    callerPath = callerFrame[1]
    # Get the absolute directory containing the caller's file
    directory = os.path.dirname(os.path.abspath(callerPath))
    # Create an absolute path for the given file
    return os.path.join(directory, path)
