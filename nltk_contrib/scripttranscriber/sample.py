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

"""Sample transcription extractor based on the ISI parallel
Chinese/English data.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
hollingk@cslu.ogi.edu (Kristy Hollingshead)
"""

import sys
import os
import documents
import tokens
import token_comp
import extractor
import chinese_extractor
import pronouncer
from __init__ import BASE_

## A sample of 10,000 from each:

CHINESE_       = '%s/data/ISI_chi_eng_parallel_corpus.chi' % BASE_
ENGLISH_       = '%s/data/ISI_chi_eng_parallel_corpus.eng' % BASE_
CONFIDENCE_    = '%s/data/ISI_chi_eng_parallel_corpus.score' % BASE_
MINCONFIDENCE_ = 0.90
XML_FILE_      = '%s/data/isi.xml' % BASE_
MATCH_FILE_    = '%s/data/isi.matches' % BASE_
CORR_FILE_    = '%s/data/isi.corr' % BASE_
BAD_COST_      = 6.0

def LoadData():
  mp = open(CHINESE_)
  ep = open(ENGLISH_)
  cp = open(CONFIDENCE_)
  doclist = documents.Doclist()
  while True:
    eline = ep.readline()
    mline = mp.readline()
    cline = cp.readline()
    if not cline: break
    if float(cline.strip()) < MINCONFIDENCE_: continue
    doc = documents.Doc()
    ### Chinese
    extractor_ = chinese_extractor.ChineseExtractor()
    extractor_.InitData()
    extractor_.LineSegment(mline)
    lang = tokens.Lang()
    lang.SetId('zho')
    for t in extractor_.Tokens():
      lang.AddToken(t)
    lang.CompactTokens() ## Combine duplicates
    for t in lang.Tokens():
      pronouncer_ = pronouncer.HanziPronouncer(t)
      pronouncer_.Pronounce()
    doc.AddLang(lang)
    ### English
    extractor_ = extractor.NameExtractor()
    extractor_.InitData()
    extractor_.LineSegment(eline)
    lang = tokens.Lang()
    lang.SetId('eng')
    for t in extractor_.Tokens():
      lang.AddToken(t)
    lang.CompactTokens() ## Combine duplicates
    for t in lang.Tokens():
      pronouncer_ = pronouncer.EnglishPronouncer(t)
      pronouncer_.Pronounce()
      if not t.Pronunciations():
        pronouncer_ = pronouncer.LatinPronouncer(t)
        pronouncer_.Pronounce()
    doc.AddLang(lang)
    doclist.AddDoc(doc)
  mp.close()
  ep.close()
  cp.close()
  return doclist


def ComputePhoneMatches(doclist):
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
  p = open(MATCH_FILE_, 'w') ## zero out the file
  p.close()
  for v in values:
    if v.Cost() > BAD_COST_: break
    v.Print(MATCH_FILE_, 'a')


def ComputeTimeCorrelation(doclist):
  correlates = {}
  stats = tokens.DocTokenStats(doclist)
  for doc in doclist.Docs():
    lang1 = doc.Langs()[0]
    lang2 = doc.Langs()[1]
    for t1 in lang1.Tokens():
      hash1 = t1.EncodeForHash()
      for t2 in lang2.Tokens():
        hash2 = t2.EncodeForHash()
        try: result = correlates[(hash1, hash2)] ## don't re-calc
        except KeyError:
          comparator = token_comp.TimeCorrelator(t1, t2, stats)
          comparator.ComputeDistance()
          result = comparator.ComparisonResult()
          correlates[(hash1, hash2)] = result
  values = correlates.values()
  values.sort(lambda x, y: cmp(x.Cost(), y.Cost()))
  p = open(CORR_FILE_, 'w') ## zero out the file
  p.close()
  for v in values:
    if v.Cost() <= 0.0: continue
    v.Print(CORR_FILE_, 'a')


if __name__ == '__main__':
  doclist = LoadData()
  doclist.XmlDump(XML_FILE_, utf8 = True)
  ComputePhoneMatches(doclist)
  ComputeTimeCorrelation(doclist)
    # this should really only be run for one term at a time!
  
