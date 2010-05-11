# -*- coding: utf-8 -*-

## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

"""Handler for XML format for extracted data. Input-text looks as follows:

<?xml version="1.0" encoding="UTF-8"?>
<doclist>
  <doc>
    <lang id="eng">
      <token count="3" morphs="Clinton" prons="k l I n t &amp; n">Clinton</token>
      <token count="3" morphs="Bush 's" prons="b U S">Bush</token>
    </lang>
    <lang id="zho">
      <token count="3" morphs="克林頓" prons="kh &amp; l i n t u n">克林頓</token>
      <token count="1" morphs="" prons="k a u t a u u ; t A k A s i m A j a">高島屋</token>
    </lang>
  </doc>
  <doc>
    <lang id="eng">
      <token count="2" morphs="Clinton" prons="k l I n t &amp; n">Clinton</token>
      <token count="3" morphs="Bush 's" prons="b U S">Bush</token>
    </lang>
    <lang id="ara">
      <token count="3" morphs="كلينتون" prons="k l j n t w n">كلينتون</token>
    </lang>
  </doc>
</doclist>

Also provides functions for converting from raw text to XML format.

"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
hollingk@cslu.ogi.edu (Kristy Hollingshead)
"""

import xml.sax.handler
import documents
import tokens
from __init__ import BASE_

class XmlHandler(xml.sax.handler.ContentHandler):
  def __init__(self):
    self.parser_ = xml.sax.make_parser()
    self.parser_.setContentHandler(self)
    self.in_token_ = False
    self.lang_ = None
    self.doc_ = None
    self.doclist_ = None

  def startElement(self, name, attributes):
    if name == 'doclist':
      self.in_token_ = False
      self.doclist_ = documents.Doclist()
      pass
    elif name == 'doc':
      self.in_token_ = False
      self.doc_ = documents.Doc()
      pass
    elif name == 'lang':
      self.in_token_ = False
      self.lang_ = tokens.Lang()
      try: self.lang_.SetId(attributes['id'])
      except KeyError: pass
    elif name == 'token':
      self.token_string_ = ''
      self.in_token_ = True
      try: self.count_ = int(attributes['count'])
      except KeyError: self.count_ = 1
      try: self.morphs_ = attributes['morphs']
      except KeyError: self.morphs_ = ''
      try: self.prons_ = attributes['prons']
      except KeyError: self.prons_ = ''

  def characters(self, data):
    if self.in_token_:
      self.token_string_ += data
 
  def endElement(self, name):
    if name == 'doclist':
      pass
    elif name == 'doc':
      self.doclist_.AddDoc(self.doc_)
      self.doc_ = None
    elif name == 'lang':
      self.doc_.AddLang(self.lang_)
      self.lang_ = None
    elif name == 'token':
      token_ = tokens.Token(self.token_string_)
      token_.SetCount(self.count_)
      token_.SetMorphs(self.morphs_.split())
      prons = self.prons_.split(';')
      for pron in prons:
        token_.AddPronunciation(pron.strip())
      self.lang_.AddToken(token_)

  def Decode(self, filename):
    self.parser_.parse(filename)
    return self.doclist_

  def DocList(self):
    return self.doclist_
