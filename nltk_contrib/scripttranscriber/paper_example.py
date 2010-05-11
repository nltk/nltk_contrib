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

"""Sample transcription extractor based on the LCTL Thai parallel
data. Also tests Thai prons and alignment.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

import sys
import os
import documents
import tokens
import extractor
import chinese_extractor
import pronouncer
import unittest
from __init__ import BASE_

## A tiny example from the ISI parallel data:

ENGLISH_       = '%s/testdata/chinese_test_eng.txt' % BASE_
CHINESE_       = '%s/testdata/chinese_test_chi.txt' % BASE_
XML_FILE_      = '%s/testdata/chinese_test.xml' % BASE_
TMP_XML_FILE_  = '/tmp/chinese_test.xml'
MATCH_FILE_    = '%s/testdata/chinese_test.matches' % BASE_
TMP_MATCH_FILE_ = '/tmp/chinese_test.matches'
BAD_COST_      = 6.0

def LoadData():
  t_extr = chinese_extractor.ChineseExtractor()
  e_extr = extractor.NameExtractor()
  doclist = documents.Doclist()
  doc = documents.Doc()
  doclist.AddDoc(doc)
  #### Chinese
  lang = tokens.Lang()
  lang.SetId('zh')
  doc.AddLang(lang)
  t_extr.FileExtract(CHINESE_)
  lang.SetTokens(t_extr.Tokens())
  lang.CompactTokens()
  for t in lang.Tokens():
    pronouncer_ = pronouncer.HanziPronouncer(t)
    pronouncer_.Pronounce()
  #### English
  lang = tokens.Lang()
  lang.SetId('en')
  doc.AddLang(lang)
  e_extr.FileExtract(ENGLISH_)
  lang.SetTokens(e_extr.Tokens())
  lang.CompactTokens()
  for t in lang.Tokens():
    pronouncer_ = pronouncer.EnglishPronouncer(t)
    pronouncer_.Pronounce()
  return doclist


def main():
  doclist = LoadData()
  doclist.XmlDump(XML_FILE_, utf8 = True)

if __name__ == '__main__':
  main()
