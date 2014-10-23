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

DecodeBase64toBytes = BeanshellCode(
'''import org.apache.commons.codec.binary.Base64;
bytes = Base64.decodeBase64(base64.getBytes());''',
    inputs = dict(
        base64 = String
        ),
    outputs = dict(
        bytes = String
        ),
    name = 'DecodeBase64toBytes'
    )

EncodeBytesToBase64 = BeanshellCode(
'''import org.apache.commons.codec.binary.Base64;
base64 = new String(Base64.encodeBase64(bytes));''',
    inputs = dict(
        bytes = String
        ),
    outputs = dict(
        base64 = String
        ),
    name = 'EncodeBytesToBase64'
    )
