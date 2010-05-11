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

"""Unit test for dochandler and token functions.
Also exercises token_comp a bit.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
hollingk@cslu.ogi.edu (Kristy Hollingshead)
"""

import os
import sys
import xml.sax
import unittest
import xmlhandler
import tokens
import documents
from __init__ import BASE_


GOLDEN_FILE_ =  '%s/testdata/doctest.xml' % BASE_ 
TEST_FILE_ = '/tmp/doctest.xml'

def CreateDoclist():
  doclist = documents.Doclist()
  doc = documents.Doc()
  lang = tokens.Lang()
  lang.SetId('eng')
  token_ = tokens.Token('Bush')
  token_.SetCount(1)
  token_.AddPronunciation('b U S')
  token_.SetMorphs(['Bush', "'s"])
  lang.AddToken(token_)
  token_ = tokens.Token('Clinton')
  token_.SetCount(3)
  token_.AddPronunciation('k l I n t & n')
  token_.AddPronunciation('k l I n t > n')
  token_.SetMorphs(['Clinton'])
  lang.AddToken(token_)
  token_ = tokens.Token('Bush')
  token_.SetCount(3)
  token_.AddPronunciation('b U S')
  token_.SetMorphs(['Bush', "'s",])
  lang.AddToken(token_)
  lang.CompactTokens()
  doc.AddLang(lang)
  lang = tokens.Lang()
  lang.SetId('zho')
  token_ = tokens.Token('克林頓')
  token_.SetCount(3)
  token_.AddPronunciation('kh & l i n t u n')
  token_.SetMorphs(['克林頓'])
  lang.AddToken(token_)
  token_ = tokens.Token('高島屋')
  token_.SetCount(1)
  token_.AddPronunciation('k a u t a u u')
  token_.AddPronunciation('t A k A s i m A j a')
  lang.AddToken(token_)
  doc.AddLang(lang)
  doclist.AddDoc(doc)
  doc = documents.Doc()
  lang = tokens.Lang()
  lang.SetId('eng')
  token_ = tokens.Token('Clinton')
  token_.SetCount(2)
  token_.AddPronunciation('k l I n t & n')
  token_.SetMorphs(['Clinton'])
  lang.AddToken(token_)
  token_ = tokens.Token('Bush')
  token_.SetCount(3)
  token_.AddPronunciation('b U S')
  token_.SetMorphs(['Bush', "'s"])
  lang.AddToken(token_)
  doc.AddLang(lang)
  lang = tokens.Lang()
  lang.SetId('ara')
  token_ = tokens.Token('كلينتون')
  token_.SetCount(3)
  token_.AddPronunciation('k l j n t w n')
  token_.SetMorphs(['كلينتون'])
  lang.AddToken(token_)
  doc.AddLang(lang)
  doclist.AddDoc(doc)
  return doclist


def main(output = False):
  if output:
    doclist = CreateDoclist()
    doclist.XmlDump(GOLDEN_FILE_, utf8 = True)
  else:
    handler = xmlhandler.XmlHandler()
    doclist = handler.Decode(GOLDEN_FILE_)
    doclist.XmlDump(TEST_FILE_, utf8 = True)
    unittest.TestUnitOutputs(sys.argv[0], \
                             GOLDEN_FILE_, TEST_FILE_)


if __name__ == '__main__':
  if len(sys.argv) > 1 and sys.argv[1] == 'generate':
    main(True)
  else:
    main()
