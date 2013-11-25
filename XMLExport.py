class NamespaceSet:

	def __init__(self):
		self.longtoprfx = {}
		self.prfxtolong = {}

	def clone(self):
		clone = NamespaceSet()
		clone.longtoprfx = self.longtoprfx.copy()
		clone.prfxtolong = self.prfxtolong.copy()
		return clone

	def addNamespace(self, prefix, namespace):
		self.longtoprfx[namespace] = prefix
		self.prfxtolong[prefix] = namespace

	def getPrefix(self, namespace):
		return self.longtoprfx.get(namespace, namespace)

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

	def initLine(self):
		self.file.write(' ' * self.spaces)
		
	def newLine(self):
		self.file.write('\n' + ' ' * self.spaces)

	def write(self, s):
		self.file.write(s)

	def writeLine(self, parts):
		write = self.file.write
		write(' ' * self.spaces)
		for part in parts[:-1]:
			write(part)
			write(' ')
		write(parts[-1])
		write('\n')


class XMLExporter:

	# TODO - output lines as list of parts which can be separated by whitespace to provide formatting
	# TODO - add default namespace handling

	def __init__(self, indenter):
		self.indenter = indenter
		self.stack = []
		self.tagPrev = None
		self.prevStart = None
		self.namespaces = NamespaceSet()
		self.pendingNamespaces = []

	def namespace(self, prefix, namespace):
		self.pendingNamespaces.append((prefix, namespace))

	def tag(self, tag, ns=None, text=None, **attributes):
		self.start(tag, ns, **attributes)
		if text is not None:
			self.text(text)
		self.end(tag)

	def start(self, tag, ns=None, **attributes):
		nsparts = []
		if self.pendingNamespaces:
			old = self.namespaces
			self.namespaces = old.clone()
			for (prefix, ns) in self.pendingNamespaces:
				self.namespaces.addNamespace(prefix, ns)
				nsparts.append("xmlns:%s='%s'" % (prefix, ns))
			self.pendingNamespaces = []
		else:
			old = None
		if ns is None:
			fulltag = tag
		else:
			fulltag = '%s:%s' % (self.namespaces.getPrefix(ns), tag)
		self.stack.append((tag, fulltag, old))
		parts = ['<' + fulltag]
		for (k, v) in attributes.items():
			if v is None:
				parts.append(k)
			else:
				parts.append("%s='%s'" % (k, v))
		parts += nsparts
		if self.prevStart:
			self.indenter.write(self.prevStart + '>')
			self.indenter.indent()
		if self.tagPrev is None:
			self.indenter.initLine()
		else:
			self.indenter.newLine()
		# At this point, we are about to write the start tag, but we actually keep it
		# and write it out just before the next thing. This way, we can close it with
		# a /> if the end tag is presented next. To force separate open and close tags
		# call text('') between start and end
		self.prevStart = " ".join(parts)
		self.tagPrev = True

	def end(self, *tags):
		for tag in tags:
			expected, fulltag, prevns = self.stack.pop()
			if tag != expected:
				raise RuntimeError("expected end tag </%s>, got </%s>" % (expected, tag))
			if prevns is not None:
				self.namespaces = prevns
			if self.prevStart:
				self.indenter.write(self.prevStart + ' />')
				self.prevStart = None
			else:
				self.indenter.dedent()
				if self.tagPrev:
					self.indenter.newLine()
				self.indenter.write('</%s>' % fulltag)
			self.tagPrev = True

	def freeText(self, text, tag=None, ns=None, **attributes):
		# Text can have whitespace reformatted, to provide better XML formatting.
		# If this is not the case, use the text method instead.
		# We don't yet do the reformatting, so just call the text method
		self.text(text)

	def text(self, text, tag=None, ns=None, **attributes):
		# Text that cannot be reformatted.
		if tag is not None:
			self.start(tag, ns, **attributes)
		if self.prevStart:
			self.indenter.write(self.prevStart + '>')
			self.indenter.indent()
			self.prevStart = None
		self.indenter.write(text)
		self.tagPrev = False
		if tag is not None:
			self.end(tag)
