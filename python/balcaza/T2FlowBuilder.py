
class T2FlowBuilder:

    def convert(self, sourceFile, t2flow, flowName, compressed):
        import codecs
        import maximal.XMLExport as XMLExport

        with open(sourceFile) as f:
            source = f.read()
        code = compile(source, sourceFile, 'exec')
        module = {}
        exec(code, module)
        flow = module[flowName]

        UTF8Writer = codecs.getwriter('utf8')
        output = UTF8Writer(t2flow)

        if compressed:
            flow.exportXML(XMLExport.XMLExporter(XMLExport.XMLCompressor(output)))
        else:
            flow.exportXML(XMLExport.XMLExporter(XMLExport.XMLIndenter(output)))

if __name__ == '__main__':
    import argparse, os, sys
    prog = os.path.basename(os.environ.get('BALCAZAPROG', sys.argv[0]))
    parser = argparse.ArgumentParser(prog=prog, description='Create a Taverna 2 workflow (t2flow) file from a Python script')
    parser.add_argument('--indent', dest='compressed', action='store_false', help='create a larger but more readable indented file')
    parser.add_argument('--flow', dest='flowName', action='store', default='flow', help='name of the workflow in the source file (default: %(default)s)')
    parser.add_argument('source', help='Python source filename')
    parser.add_argument('target', nargs='?', help='Taverna 2 Workflow (t2flow) filename (default: stdout)')
    args = parser.parse_args()
    target = args.target
    if target is None:
        t2flow = sys.stdout
    else:
        if not target.endswith('.t2flow'):
            target += '.t2flow'
        t2flow = open(target, 'w')
    builder = T2FlowBuilder()
    builder.convert(args.source, t2flow, args.flowName, args.compressed)