# Copyright (C) 2013 Cardiff University, Jonathan Giddy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from xml.sax.saxutils import escape, quoteattr

initialNamespace = {
    'xml': 'http://www.w3.org/XML/1998/namespace',
    'xmlns': 'http://www.w3.org/2000/xmlns/'
}

# Namespaces:
#   prefixMap: url -> prefix - use user-supplied prefix, else create one on first use
#   prefixToUri: prefix -> url # used to check whether prefix is in use
#   default = url
#   active = {url: prefix}
#   pending = {prefix: url} - default = None: url
class NamespaceSet:

    def __init__(self):
        self.uriPrefix = {}
        self.prefixUri = initialNamespace.copy()
        self.activeDefault = ''
        self.active = {}
        self.pendingDefault = None
        self.pending = {}
        for prefix, uri in initialNamespace.items():
            self.uriPrefix[uri] = self.active[uri] = prefix

    def clone(self):
        clone = NamespaceSet()
        clone.uriPrefix = self.uriPrefix
        clone.prefixUri = self.prefixUri
        clone.activeDefault = self.activeDefault
        clone.active = self.active.copy()
        clone.pendingDefault = self.pendingDefault
        clone.pending = self.pending.copy()
        return clone

    def setDefaultNamespace(self, uri=''):
        if uri in ('http://www.w3.org/XML/1998/namespace', 'http://www.w3.org/2000/xmlns/'):
            raise RuntimeError('this namespace must not be set to default [http://www.w3.org/TR/REC-xml-names/]')
        if uri != self.activeDefault:
            self.pendingDefault = uri

    def addNamespace(self, uri, prefixCandidate):
        if uri == 'http://www.w3.org/XML/1998/namespace' and prefixCandidate != 'xml':
            raise RuntimeError('the xml namespace must not be bound to any other name [http://www.w3.org/TR/REC-xml-names/]')
        if uri == 'http://www.w3.org/2000/xmlns/':
            raise RuntimeError('the xmlns namespace must not be bound to any name [http://www.w3.org/TR/REC-xml-names/]')
        if self.uriPrefix.has_key(uri):
            # use a cached prefix, if this namespace has been named before
            prefix = self.uriPrefix[uri]
        else:
            # use the prefix supplied as a parameter, but check whether the
            # prefix has been used for a different namespace
            i = 1
            prefix = prefixCandidate
            while self.prefixUri.has_key(prefix):
                # prefix is used for another namespace - we enforce a good
                # practice of not reusing prefixes for different namespaces
                prefix = prefixCandidate + str(i)
                i += 1
            # record the selected prefix
            self.prefixUri[prefix] = uri
            self.uriPrefix[uri] = prefix

        self.pending[prefix] = uri

    def getPendingNamespaces(self):
        parts = []
        if self.pendingDefault is not None:
            parts.append('xmlns=%s' % quoteattr(self.pendingDefault))
        for prefix, uri in self.pending.items():
            parts.append('xmlns:%s=%s' % (prefix, quoteattr(uri)))
        return parts

    def activatePending(self):
        if self.pendingDefault is not None:
            self.activeDefault = self.pendingDefault
            self.pendingDefault = None
        if self.pending:
            for prefix, uri in self.pending.items():
                self.active[uri] = prefix
            self.pending = {}
        return self

    def getActivePrefix(self, uri):
        if uri == self.activeDefault:
            # return None to indicate the URI is the default namespace
            return None
        else:
            # return the prefix entry for the URI. If no entry exists, just
            # return the URI
            return self.active.get(uri, uri)

    def expandTag(self, uri, tag):
        prefix = self.getActivePrefix(uri)
        if prefix is None:
            fulltag = tag
        elif not prefix:
            # tag needs no namespace, but no namespace is not the default
            raise RuntimeError('<%s> requires default namespace set to no namespace' % tag)
        else:
            fulltag = '%s:%s' % (prefix, tag)
        return fulltag


class XMLCompressor:

    def __init__(self, file):
        file.write
        self.file = file

    def indent(self):
        pass

    def dedent(self):
        pass

    def writeLine(self, parts):
        self.file.write(' '.join(parts))


class XMLIndenter:

    # TODO - use width to restrict width of XML, and additional for extra indent for lines 2+

    def __init__(self, file, width=80, increment=2, additional=4, initial=0):
        self.file = file
        self.spaces = initial
        self.increment = increment

    def indent(self):
        self.spaces += self.increment

    def dedent(self):
        self.spaces -= self.increment

    def writeLine(self, parts):
        write = self.file.write
        write(' ' * self.spaces)
        for part in parts[:-1]:
            write(part)
            write(' ')
        write(parts[-1])
        write('\n')


class Element:

    def __init__(self, xml, namespace, uri, tag):
        self.__xml = xml
        self.__namespace = namespace
        self.__uri = uri
        self.__tag = tag

    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError(name)
        # tav.foo.bar => <tav:foo.bar>
        if self.__tag is None:
            raise RuntimeError('Element is no longer in scope')
        self.__tag += '.' + name
        self.__xml.setPendingTag(self.__tag)
        return self

    def __call__(self, *args, **attributes):
        # tav.foo('text', {'from': 0}, to=10) => <tav:foo from='0' to='10'>
        if self.__tag is None:
            raise RuntimeError('Element is no longer in scope')
        attr = {}
        for arg in args:
            if isinstance(arg, dict):
                attr.update(arg)
            else:
                self.__xml.setPendingText(arg)
        if attr is not None:
            attributes.update(attr)
        self.__xml.setPendingAttributes(attributes)
        return self

    def __rshift__(self, s):
        if self.__tag is None:
            raise RuntimeError('Element is no longer in scope')
        self.__xml.setPendingText(s)
        return self

    def __enter__(self):
        if self.__tag is None:
            raise RuntimeError('Element is no longer in scope')
        self.__xml.openPendingTag()
        return self.__namespace

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is None:
            xml = self.__xml
            xml.closePendingTag()
            xml.closeTag(self.__uri, self.__tag)
            self.__tag = None


class Namespace:

    def __init__(self, xml, uri):
        self.__xml = xml
        self.__uri = uri

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, name):
        # tav['my-name'] => <tav:my-name>
        if name.startswith('xmlns'):
            raise RuntimeError('element name must not start with xmlns [http://www.w3.org/TR/REC-xml-names/]')
        xml = self.__xml
        xml.closePendingTag()
        xml.setPendingNamespace(self.__uri)
        xml.setPendingTag(name)
        return Element(xml, self, self.__uri, name)

    def __call__(self, attr, **attributes):
        # tav.myname(tav(fish=foo, dish=bar)) => <tav:myname tav:fish="foo" tav:dish=bar>
        pass


class NamespaceScope:

    def __init__(self, xml, uri, prefix):
        assert uri is not None
        self.xml = xml
        self.uri = uri
        self.prefix = prefix

    def __enter__(self):
        self.old = self.xml.getNamespaces()
        new = self.old.clone()
        if self.prefix is None:
            new.setDefaultNamespace(self.uri)
        else:
            new.addNamespace(self.prefix, self.uri)
        self.xml.setNamespaces(new)
        return Namespace(self.xml, self.uri)

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is None:
            self.xml.closePendingTag()
            self.xml.setNamespaces(self.old)


#
#   enter namespace:
#   - old = xml.getNamespaces()
#   - clone = old.clone() # same prefix*, copy default, pendingUris
#   - add namespace to pendingUris
#   - xml.setNamespaces(clone)
#
#   exit namespace:
#   - xml.setNamespace(old)
#
#   openTag:
#   - if pending has entries, get them as
# enter namespace: xml.pendingMap
# on entering namespace(), add pendingMap[prefix] -> URI (but if URI has an existing prefix ignore)
# treat default as special, and always add it, even if it has a prefix
# similarly, add prefix if only entry is default
# on leaving namespace, revert pendingMap[prefix] -> old value (if it was changed)
# on starting tag, add all pendingMap entries to tag and set pendingMap to {} and include in namespace to include
# on close tag, revert pendingMap to value before start tag and namespace to old

class XMLExporter:

    # TODO - output lines as list of parts which can be separated by whitespace to provide formatting
    # TODO - add default namespace handling

    def __init__(self, indenter):
        self.indenter = indenter
        self.stack = []
        self.namespaces = NamespaceSet()
        self.clearPending()

    def clearPending(self):
        self.pendingUri = None
        self.pendingTag = None
        self.pendingAttributes = None
        self.pendingText = ''

    def closeTag(self, uri, tag):
        fulltag = self.namespaces.expandTag(uri, tag)
        expected, self.namespaces = self.stack.pop()
        if fulltag != expected:
            raise RuntimeError(fulltag, expected)
        self.indenter.dedent()
        self.indenter.writeLine(('</%s>' % fulltag,))

    def closePendingTag(self):
        if self.pendingTag is not None:
            parts, closetag = self.openPendingTagPrefix()
            if self.pendingText:
                parts[-1] += '>%s%s' % (escape(self.pendingText), closetag)
            else:
                parts.append('/>')
            self.indenter.writeLine(parts)
            fulltag, self.namespaces = self.stack.pop()
        self.clearPending()

    def openPendingTag(self):
        if self.pendingTag is not None:
            parts, closetag = self.openPendingTagPrefix()
            parts[-1] += '>%s' % escape(self.pendingText)
            self.indenter.writeLine(parts)
            self.indenter.indent()
            self.clearPending()

    def openPendingTagPrefix(self):
        assert self.pendingTag is not None
        oldns = self.namespaces
        nsparts = oldns.getPendingNamespaces()
        if nsparts:
            newns = oldns.clone().activatePending()
        else:
            newns = oldns
        fulltag = newns.expandTag(self.pendingUri, self.pendingTag)
        self.stack.append((fulltag, oldns))
        self.namespaces = newns
        parts = ['<' + fulltag]
        if self.pendingAttributes is not None:
            for (k, v) in self.pendingAttributes.items():
                if v is None:
                    parts.append(k)
                else:
                    parts.append("%s=%s" % (k, quoteattr(unicode(v))))
        parts += nsparts
        return parts, '</%s>' % fulltag

    def namespace(self, uri='', prefix=None):
        self.closePendingTag()
        return NamespaceScope(self, uri, prefix)

    def getNamespaces(self):
        return self.namespaces

    def setNamespaces(self, namespaces):
        self.namespaces = namespaces

    def setPendingNamespace(self, namespace):
        self.pendingUri = namespace

    def setPendingTag(self, name):
        self.pendingTag = name

    def setPendingAttributes(self, attributes):
        self.pendingAttributes = attributes

    def setPendingText(self, text):
        try:
            self.pendingText += unicode(text)
        except UnicodeDecodeError:
            import sys
            sys.stderr.write('Error writing:\n"%s"\n' % text)
            raise
