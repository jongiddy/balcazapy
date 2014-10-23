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


def readZapyFile(sourceFile, flowName):
    with open(sourceFile) as f:
        source = f.read()
    code = compile(source, sourceFile, 'exec')
    module = {}
    exec(code, module)
    return module[flowName]


def printSig(sourceFile, flowName):
    import sys
    flow = readZapyFile(sourceFile, flowName)
    sys.stdout.write("NestedZapyFile(\n")
    sys.stdout.write("    '%s',\n" % sourceFile)
    if flow.input:
        sys.stdout.write("    inputs = dict(\n")
        sys.stdout.write(",\n".join(["        %s = %s" % (port.name, port.type) for port in flow.input]))
        sys.stdout.write("\n        ),\n")
    if flow.output:
        sys.stdout.write("    outputs = dict(\n")
        sys.stdout.write(",\n".join(["        %s = %s" % (port.name, port.type) for port in flow.output]))
        sys.stdout.write("\n        )\n")
    sys.stdout.write(")\n")


class T2FlowBuilder:

    def convert(self, sourceFile, t2flow, flowName, compressed, validate, zip):
        import codecs
        import maximal.XMLExport as XMLExport

        flow = readZapyFile(sourceFile, flowName)

        if validate:
            from t2wrapper import WrapperWorkflow
            flow = WrapperWorkflow(flow, validate, zip)

        UTF8Writer = codecs.getwriter('utf8')
        output = UTF8Writer(t2flow)

        if compressed:
            flow.exportXML(XMLExport.XMLExporter(XMLExport.XMLCompressor(output)))
        else:
            flow.exportXML(XMLExport.XMLExporter(XMLExport.XMLIndenter(output)))

if __name__ == '__main__':
    import argparse
    import os
    import sys
    prog = os.path.basename(os.environ.get('BALCAZAPROG', sys.argv[0]))
    parser = argparse.ArgumentParser(prog=prog, description='Create a Taverna 2 workflow (t2flow) file from a Zapy description file')
    parser.add_argument('--indent', dest='compressed', action='store_false', help='create a larger but more readable indented file')
    parser.add_argument('--validate', dest='validate', action='store_true', help='modify workflow to validate input ports')
    parser.add_argument('--zip', dest='zip', action='store_true', help='create a zip file containing outputs')
    parser.add_argument('--signature', dest='signature', action='store_true', help='print workflow signature')
    parser.add_argument('--flow', dest='flowName', action='store', default='flow', help='name of the workflow in the source file (default: %(default)s)')
    parser.add_argument('source', help='Zapy (.py) description file')
    parser.add_argument('target', nargs='?', help='Taverna 2 Workflow (.t2flow) filename (default: stdout)')
    args = parser.parse_args()
    if args.signature:
        printSig(args.source, args.flowName)
    else:
        target = args.target
        if target is None:
            t2flow = sys.stdout
        else:
            if not target.endswith('.t2flow'):
                target += '.t2flow'
            t2flow = open(target, 'w')
        builder = T2FlowBuilder()
        builder.convert(args.source, t2flow, args.flowName, args.compressed, args.validate, args.zip)
