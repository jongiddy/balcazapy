# Copyright (C) 2013 Cardiff University
# Beanshell code Copyright (C) 2007 The University of Manchester
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
from balcaza.t2activity import BeanshellCode

ByteArrayToString = BeanshellCode(
'''if ((bytes == void) || (bytes == null)) {
    throw new RuntimeException("The 'bytes' parameter must be specified");
}
if (encoding == void) {
    string = new String(bytes);
} else {
    string = new String(bytes, encoding);
}
''',
    inputs = dict(
        bytes = String,
        encoding = Optional[String]
        ),
    outputs = dict(
        string = String
        ),
    defaultInput = 'bytes',
    name = 'ByteArrayToString'
    )
