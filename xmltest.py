# -*- coding: utf-8 -*-
import sys
from maximal import XMLExport

x = XMLExport.XMLExporter(XMLExport.XMLCompressor(sys.stdout))

with x.namespace('http://taverna.org/2013/') as tav:
    with tav.workflow(author='Jon Giddy'):
        tav.input.routine(u'Hλ1ello', {'complex.name': u'hλ1h'}, name='fido', x=2)
        with tav.output as foo:
            foo.hd("World!")



# x.namespace returns a namespace linked to the exporter
# a namespace getattr returns a tag with the same namespace
# e.g. namespace.foo returns a tag foo <foo>
# tag getattr returns an extended tag
# e.g. namespace.foo.bar returns a tag <foo.bar>
# tag __call__(text, )
