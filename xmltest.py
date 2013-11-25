import sys
import XMLExport

x = XMLExport.XMLExporter(XMLExport.XMLIndenter(sys.stdout))

ns = 'http://taverna.org/2013/'

x.namespace('tav', ns)
x.start('workflow', ns, author='Jon Giddy')
x.tag('input', ns, 'Hello', name='fido')
x.start('output', ns)
x.text('bogs')
x.end('output', 'workflow')
# x.end('output', 'workflow')
# x.backTo('workflow', ns)
# x.endAll()