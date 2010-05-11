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

"""Handler for documents and document-lists.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
hollingk@cslu.ogi.edu (Kristy Hollingshead)
"""

import xml.sax.saxutils
import xmlhandler
import tokens
from __init__ import BASE_

XML_HEADER_ = '<?xml version="1.0" encoding="UTF-8"?>'
DOC_INDENT_   = ' ' * 2

class Doc:
  """Holder for languages. Represents one aligned "document" across
  languages/scripts, where "document" could be an actual n-tuple of
  translated documents, a single pair of terms known to be
  transcriptions of each other, or multiple documents in n languages
  that are roughly time aligned to each other.
  """
  def __init__(self):
    self.langs_ = []

  def XmlEncode(self):
    if len(self.langs_) == 0: return
    xml_string_ = '<doc>\n%s\n%s</doc>'
    langs = []
    for lang in self.langs_:
      langs.append(lang.XmlEncode())
    xml_result = xml_string_ % ('\n'.join(langs), DOC_INDENT_)
    return DOC_INDENT_ + xml_result

  def Langs(self):
    return self.langs_

  def AddLang(self, lang):
    self.langs_.append(lang)

  def AddTokens(self, toks, langid):
    success = False
    for lang in self.langs_:
      if lang.Id() == langid:
        for t in toks:
          lang.AddToken(t)
        lang.CompactTokens()
        success = True
    if not success:
      lang = tokens.Lang()
      lang.SetId(langid)
      lang.SetTokens(toks)
      lang.CompactTokens()
      self.AddLang(lang)

  def LookupLang(self, langid):
    for lang in self.langs_:
      if lang.Id() == langid:
        return lang
    return None

  def LookupToken(self, tokstr, langid=None):
    ## warning!: this will return the first instance of tokstr,
    ## regardless of pronunciations, morphs, or (if langid is
    ## not provided) language id.
    if langid is None: langset = self.langs_
    else: langset = [self.LookupLang(langid)]
    for lang in langset:
      if not lang: continue
      for t in lang.Tokens():
        if t.String() == tokstr:
          return t
    return None

class Doclist:
  """Holder for docs. It is assumed these are stored in some sensible
  sequence (e.g. in temporal order).
  """
  def __init__(self):
    self.docs_ = []
    self.tokenfreq_ = []

  def XmlDecode(self, filename):
    decoder = xmlhandler.XmlHandler()
    doclist = decoder.Decode(filename)
    self.docs_ = doclist.Docs()

  def XmlEncode(self, utf8=False):
    if len(self.docs_) == 0: return ''
    xml_string_ = '<doclist>\n%s\n</doclist>'
    xml_docs = []
    for doc in self.docs_:
      xml_docs.append(doc.XmlEncode())
    xml_result = '%s\n%s' % (XML_HEADER_, xml_string_ % '\n'.join(xml_docs))
    """
    TODO(rws): investigate why this is necessary. In
    dochandler_unittest when the XML is created internally from utf8
    text one can write it out without the explicit encode. However,
    when it is parsed back from the file and then written again, we
    get the error

    UnicodeEncodeError: 'ascii' codec can't encode characters in 
    position 255-257: ordinal not in range(128)
    """
    ## Result is already in utf8, as when generated internally
    if utf8: return xml_result
    ## Result is not in utf8, as when parsed from an XML file
    else: return xml_result.encode('utf-8')

  def XmlDump(self, file=None, utf8=False):
    if file is None:
      print '%s\n' % (self.XmlEncode(utf8))
      return
    p = open(file, 'w')
    p.write('%s\n' % self.XmlEncode(utf8))
    p.close()

  def Docs(self):
    return self.docs_

  def AddDoc(self, doc):
    self.docs_.append(doc)

  def LookupLang(self, langid):
    for doc in self.docs_:
      retlang = doc.LookupLang(langid)
      if retlang is not None: return retlang
    return None

  def LookupToken(self, tokstr, langid=None):
    ## warning!: this will return the first instance of tokstr,
    ## regardless of pronunciations, morphs, or (if langid is
    ## not provided) language id.
    for doc in self.docs_:
      rettok = doc.LookupToken(tokstr, langid)
      if rettok is not None: return rettok
    return None
