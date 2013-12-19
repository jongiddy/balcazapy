from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import Workflow

flow = Workflow(title = 'Web Page Headers and Title')

Web = flow.task.RetrieveWebPage << HTTP.GET('http://www.biovel.eu/')

flow.output.headers = Web.output.responseHeaders

GetTitle = flow.task.GetTitle << XPath('/xhtml:html/xhtml:head/xhtml:title', {'xhtml': 'http://www.w3.org/1999/xhtml'})

Web.output.responseBody >> GetTitle.input.xml_text

Web.extendUnusedPorts()
GetTitle.extendUnusedPorts()
