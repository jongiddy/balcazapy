from t2activity import BeanshellCode
from t2types import BinaryFile, String

assert False, 'Module "%s" does not currently work!' % __name__
# The zip file is encoded correctly (it unzips OK), but binary files stored
# inside are corrupt, whether using the original String, or converting to a
# byte array using either the default character encoding or using UTF-8.

prefix = '''import java.io.*;
import java.util.zip.*;
void addToZip(ZipOutputStream out, String source, String zippedName) {
  byte[] b = source.getBytes();
  # byte[] b = source.getBytes("UTF-8");
  out.putNextEntry(new ZipEntry(zippedName));
  out.write(source, 0, source.length);
  # out.write(b, 0, b.length);
  out.closeEntry();
}
_baos = new ByteArrayOutputStream();
_out = new ZipOutputStream(_baos);
try {
'''

suffix = '''}
finally {
  _out.close();
  zipFile = _baos.toByteArray();
}
'''

INDENT = '  '


class BeanShellZipper:

    def __init__(self):
        self.lines = [prefix]
        self.files = set()
        self.vars = set()

    def copyToZip(self, portName, zippedName, indent=1):
        if portName in self.vars:
            raise RuntimeError('"%s" is both a filename and a variable in a filename' % portName)
        self.files.add(portName)
        spaces = INDENT * indent
        assert len(zippedName) % 2 == 1, zippedName
        filename = ''
        while len(zippedName) >= 3:
            quoted = zippedName[0]
            var = zippedName[1]
            if var in self.files:
                raise RuntimeError('"%s" is both a filename and a variable in a filename' % var)
            self.vars.add(var)
            if quoted:
                filename += '"%s"+%s+' % (quoted, var)
            else:
                filename += '%s+' % var
            del zippedName[:2]
        filename += '"%s"' % zippedName[0]
        self.lines.append(spaces + 'addToZip(_out, %s, %s);\n' % (portName, filename))

    def copyToZipIfNotEmpty(self, portName, zippedName, indent=1):
        spaces = INDENT * indent
        self.lines.append(spaces + 'if (%s.length() > 0) {\n' % portName)
        self.copyToZip(portName, zippedName, indent + 1)
        self.lines.append(spaces + '}\n')

    def code(self):
        return ''.join(self.lines) + suffix

    def activity(self):
        inputs = {name: String for name in (self.files | self.vars)}
        return BeanshellCode(
            self.code(),
            inputs=inputs,
            outputs=dict(zipFile=BinaryFile)
            )

    def zippedPorts(self):
        return self.files

    def filenameVars(self):
        return self.vars

if __debug__:
    if __name__ == '__main__':
        zipper = BeanShellZipper()
        zipper.copyToZip('graph', ['graph.png'])
        zipper.copyToZipIfNotEmpty('matrix', ['matrix.csv'])
        zipper.copyToZip('another', ['result', 'pop', '', 'foo', '.txt'])
        print(zipper.code())
