#!/bin/sh

BALCAZAPY_HOME=`pwd`
PYTHON=`which python`

[ -d ${BALCAZAPY_HOME}/bin ] || mkdir ${BALCAZAPY_HOME}/bin

sed -e "s:@BALCAZAPY_HOME@:${BALCAZAPY_HOME}:g" -e "s:@PYTHON@:${PYTHON}:g" scripts/balc.in > bin/balc
chmod 755 bin/balc
