from xml.sax.saxutils import escape, quoteattr

# Namespaces:
# 	prefixMap: url -> prefix - use user-supplied prefix, else create one on first use
# 	prefixToUri: prefix -> url # used to check whether prefix is in use
# 	default = url
# 	active = {url: prefix}
# 	pending = {prefix: url} - default = None: url
class NamespaceSet:

	def __init__(self):
		self.uriPrefix = {}
		self.prefixUri = {}
		self.activeDefault = ''
		self.active = {}
		self.pendingDefault = None
		self.pending = {}

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
		if uri != self.activeDefault:
			self.pendingDefault = uri

	def addNamespace(self, uri, prefixCandidate):
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
		file.write # a.ssertParameters(file.write, (a.string))
		# a.ssertType(initial, a.int[0, 255])
		# a.ssertType(x, a.ny(a.int[0, 255], a.string, a.boolean, None))
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

	def __call__(self, attr=None, **attributes):
		# tav.foo({'from': 0}, to=10) => <tav:foo from='0' to='10'>
		if self.__tag is None:
			raise RuntimeError('Element is no longer in scope')
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
			self.xml.setNamespaces(self.old)


# 	
# 	enter namespace:
# 	- old = xml.getNamespaces()
# 	- clone = old.clone() # same prefix*, copy default, pendingUris
# 	- add namespace to pendingUris
# 	- xml.setNamespaces(clone)
# 	
# 	exit namespace:
# 	- xml.setNamespace(old)
# 	
#   openTag:
#  	- if pending has entries, get them as 
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
					parts.append("%s=%s" % (k, quoteattr(str(v))))
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
		self.pendingText += str(text)
