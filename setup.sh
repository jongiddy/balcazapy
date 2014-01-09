#!/bin/sh
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

BALCAZAPY_HOME=`pwd`
PYTHON=`which python`

[ -d ${BALCAZAPY_HOME}/bin ] || mkdir ${BALCAZAPY_HOME}/bin

sed -e "s:@BALCAZAPY_HOME@:${BALCAZAPY_HOME}:g" -e "s:@PYTHON@:${PYTHON}:g" scripts/balc.in > bin/balc
chmod 755 bin/balc
