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

