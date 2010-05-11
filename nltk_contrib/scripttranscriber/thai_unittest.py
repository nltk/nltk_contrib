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
import token_comp
import extractor
import thai_extractor
import pronouncer
import unittest
from __init__ import BASE_

## A sample of 10,000 from each:

ENGLISH_       = '%s/testdata/thai_test_eng.txt' % BASE_
THAI_          = '%s/testdata/thai_test_thai.txt' % BASE_
XML_FILE_      = '%s/testdata/thai_test.xml' % BASE_
TMP_XML_FILE_  = '/tmp/thai_test.xml'
MATCH_FILE_    = '%s/testdata/thai_test.matches' % BASE_
TMP_MATCH_FILE_ = '/tmp/thai_test.matches'
BAD_COST_      = 6.0

def LoadData():
  t_extr = thai_extractor.ThaiExtractor()
  e_extr = extractor.NameExtractor()
  doclist = documents.Doclist()
  doc = documents.Doc()
  doclist.AddDoc(doc)
  #### Thai
  lang = tokens.Lang()
  lang.SetId('th')
  doc.AddLang(lang)
  t_extr.FileExtract(THAI_)
  lang.SetTokens(t_extr.Tokens())
  lang.CompactTokens()
  for t in lang.Tokens():
    pronouncer_ = pronouncer.UnitranPronouncer(t)
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


def ComputePhoneMatches(doclist, match_file):
  matches = {}
  for doc in doclist.Docs():
    lang1 = doc.Langs()[0]
    lang2 = doc.Langs()[1]
    for t1 in lang1.Tokens():
      hash1 = t1.EncodeForHash()
      for t2 in lang2.Tokens():
        hash2 = t2.EncodeForHash()
        try: result = matches[(hash1, hash2)] ## don't re-calc
        except KeyError:
          comparator = token_comp.OldPhoneticDistanceComparator(t1, t2)
          comparator.ComputeDistance()
          result = comparator.ComparisonResult()
          matches[(hash1, hash2)] = result
  values = matches.values()
  values.sort(lambda x, y: cmp(x.Cost(), y.Cost()))
  p = open(match_file, 'w') ## zero out the file
  p.close()
  for v in values:
    if v.Cost() > BAD_COST_: break
    v.Print(match_file, 'a')


def main(output = False):
  doclist = LoadData()
  if output:
    doclist.XmlDump(XML_FILE_, utf8 = True)
    ComputePhoneMatches(doclist, MATCH_FILE_)
  else:
    doclist.XmlDump(TMP_XML_FILE_, utf8 = True)
    ComputePhoneMatches(doclist, TMP_MATCH_FILE_)
    unittest.TestUnitOutputs(sys.argv[0] + ': token parsing',\
                             XML_FILE_, TMP_XML_FILE_)
    unittest.TestUnitOutputs(sys.argv[0] + ': string matching',\
                             MATCH_FILE_, TMP_MATCH_FILE_)

    
if __name__ == '__main__':
  if len(sys.argv) > 1 and sys.argv[1] == 'generate':
    main(True)
  else:
    main()
