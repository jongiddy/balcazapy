from t2activity import ExternalTool
from t2types import BinaryFile, String

# ExternalToolZipper creates the zip file from files, and should be fairly
# memory-friendly.  However, due to use of Unix shell, it does not work on
# Windows machines.

INDENT = '  '


class ExternalToolZipper:

    def __init__(self):
        self.lines = []
        self.files = set()
        self.vars = set()

    def checkVars(self, zippedName):
        for i in range(1, len(zippedName), 2):
            var = zippedName[i]
            if var in self.files:
                raise RuntimeError('"%s" is both a filename and a variable in a filename' % var)
            self.vars.add(var)

    def copyToZip(self, portName, zippedName, indent=0):
        if portName in self.vars:
            raise RuntimeError('"%s" is both a filename and a variable in a filename' % portName)
        self.files.add(portName)
        self.checkVars(zippedName)
        spaces = INDENT * indent
        filename = '%%'.join(zippedName)
        if portName != filename:
            self.lines.append(spaces + "mv '%s' '%s'\n" % (portName, filename))

    def copyToZipIfNotEmpty(self, portName, zippedName, indent=0):
        if portName in self.vars:
            raise RuntimeError('"%s" is both a filename and a variable in a filename' % portName)
        self.files.add(portName)
        self.checkVars(zippedName)
        spaces = INDENT * indent
        self.lines.append(spaces + "if [ ! -s '%s' ]; then rm '%s'\n" % (portName, portName))
        filename = '%%'.join(zippedName)
        if portName != filename:
            self.lines.append(spaces + "else mv '%s' '%s'\n" % (portName, filename))
        self.lines.append(spaces + 'fi\n')

    def code(self):
        return ''.join(self.lines) + 'zip outputs.zip *\n'

    def activity(self):
        inputs = {}
        for file in self.files:
            inputs[file] = BinaryFile
        for var in self.vars:
            inputs[var] = String
        return ExternalTool(
            command=self.code(),
            inputs=inputs,
            outputs=dict(zipFile=BinaryFile),
            outputMap=dict(zipFile='outputs.zip')
            )

    def zippedPorts(self):
        return self.files

    def filenameVars(self):
        return self.vars

if __debug__:
    if __name__ == '__main__':
        zipper = ExternalToolZipper()
        zipper.copyToZip('graph', ['graph.png'])
        zipper.copyToZipIfNotEmpty('matrix', ['matrix.csv'])
        zipper.copyToZip('another', ['result', 'pop', '', 'foo', '.txt'])
        print(zipper.code())
