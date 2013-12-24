from balcaza.t2types import *
from balcaza.t2activity import *
from balcaza.t2flow import Workflow

flow = Workflow(title = 'Web Page Headers and Title')

GetWebPage = flow.task.RetrieveWebPage << HTTP.GET('http://www.biovel.eu/')

# We can chain several tasks together using the pipe symbol
# We can use activities, which get converted to tasks, as long as a non-activity
# appears in the first two objects in the chain
# Activities are good, because they can be reused, like MergeStringListToString
# Some activities have a default port defined, but we can define a default port
# as above in the Beanshell
from balcaza.activity.local.list import MergeStringListToString

GetWebPage | XPath('/xhtml:html/xhtml:head/xhtml:title', {'xhtml': 'http://www.w3.org/1999/xhtml'}) | MergeStringListToString | flow.output.title

GetWebPage.output.responseHeaders | MergeStringListToString | flow.output.headers
