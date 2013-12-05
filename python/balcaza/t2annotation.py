class Annotation:

    def __init__(self, text):
        self.text = text
        self.chain = 'annotation_chain'
        self.label = 'text'

    def exportXML(self, xml, annotationClass):
        with xml.namespace("http://taverna.sf.net/2008/xml/t2flow") as tav:
            with tav[self.chain](encoding="xstream"):
                with xml.namespace() as annotation:
                    with annotation.net.sf.taverna.t2.annotation.AnnotationChainImpl:
                        with annotation.annotationAssertions:
                            with annotation.net.sf.taverna.t2.annotation.AnnotationAssertionImpl:
                                with annotation.annotationBean({'class': annotationClass}):
                                    annotation[self.label] >> self.text
                                annotation.date >> '2013-11-27 14:27:50.10 UTC'
                                annotation.creators
                                annotation.curationEventList

class Annotation_2_2(Annotation):

    def __init__(self, text):
        Annotation.__init__(self, text)
        self.chain = 'annotation_chain_2_2'
        self.label = 'identification'

