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

"""Unit test for token_comp. Also exercises pronouncer
and doc handler a bit.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
hollingk@cslu.ogi.edu (Kristy Hollingshead)
ting.qian@rochester.edu (Ting Qian)
"""

import os
import sys
import unittest
import documents
import tokens
import pronouncer
import token_comp
import auxiliary_comp
from __init__ import BASE_

PAIRS_ = [(u'高島屋', u'Takashimaya'),
          (u'共產黨', u'공산당'),
          (u'Kuomintang', u'國民黨'),
          (u'ᏣᎳᎩ', u'Cherokee'),
          (u'niqitsiavaliriniq', u'ᓂᕿᑦᓯᐊᕙᓕᕆᓂᖅ')
          ]

GOLDEN_FILE_ =  '%s/testdata/token_comp_test.txt' % BASE_ 
TEST_FILE_ = '/tmp/token_comp_test.txt'

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
  token_ = tokens.Token(u'克林頓')
  token_.SetCount(3)
  token_.AddPronunciation('kh & l i n t u n')
  token_.SetMorphs([u'克林頓'])
  lang.AddToken(token_)
  token_ = tokens.Token(u'高島屋')
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
  token_ = tokens.Token(u'كلينتون')
  token_.SetCount(3)
  token_.AddPronunciation('k l j n t w n')
  token_.SetMorphs([u'كلينتون'])
  lang.AddToken(token_)
  doc.AddLang(lang)
  doclist.AddDoc(doc)
  return doclist


def TestPronunciations(tok):
  pronouncer_ = pronouncer.UnitranPronouncer(tok)
  pronouncer_.Pronounce()
  pronouncer_ = pronouncer.HanziPronouncer(tok)
  pronouncer_.Pronounce()
  pronouncer_ = pronouncer.EnglishPronouncer(tok)
  pronouncer_.Pronounce()
  if not tok.Pronunciations():
    pronouncer_ = pronouncer.LatinPronouncer(tok)
    pronouncer_.Pronounce()


def TestCorrelations(doclist, outfile):
  correlates = []
  stats = tokens.DocTokenStats(doclist)
  for doc in doclist.Docs():
    for lang1 in doc.Langs():
      for lang2 in doc.Langs():
        for t1 in lang1.Tokens():
          for t2 in lang2.Tokens():
            comparator = token_comp.TimeCorrelator(t1, t2, stats)
            comparator.ComputeDistance()
            result = comparator.ComparisonResult()
            correlates.append(result)
  correlates.sort(lambda x, y: cmp(x.Cost(), y.Cost()))
  for c in correlates:
    if c.Cost() <= 0.0: continue
    c.Print(outfile, 'a')

def TestSnowActivations(doclist, outfile):
  activations = []
  comparator = token_comp.SnowPronComparator('1.fm', '1.network')
  tr_list = []
  tr_fp = open('testdata/perceptron.ce.dict.training', 'r')
  for line in tr_fp.readlines():
    [pron1, pron2] = line.strip().split('\t')
    tr_list.append((pron1, pron2))
  comparator.Train(tr_list[0:2000])
  
  for doc in doclist.Docs():
    for lang1 in doc.Langs():
      for lang2 in doc.Langs():
        for t1 in lang1.Tokens():
          for t2 in lang2.Tokens():
            if t1.LangId() == 'eng' and t2.LangId() == 'zho':
              comparator.ComputeDistance(t1, t2)
              result = comparator.ComparisonResult()
              activations.append(result)

  out = open(outfile, 'a')
  for a in activations:
    a.Print()
    str_repr = str(a)
    if str_repr.split(', ')[1] != '0':
      out.write(str_repr.split(', ')[0] + ': sucessfully activated one target>\n')
    else:
      out.write(str_repr.split(', ')[0] + ': no activation on any target>\n')
  out.close()
  comparator.Forget()
            
def TestAuxiliaryComparators(unitname):
  ## Added tests for Wade-Giles and Pinyin comparators
  t1 = tokens.Token('毛泽东')
  t2 = tokens.Token('周恩来')
  t1py = tokens.Token('Mao Zedong')
  t2py = tokens.Token('Zhou Enlai')
  t1wg = tokens.Token('Mao Tse-tung')
  t2wg = tokens.Token('Chou Enlai')
  comparator = auxiliary_comp.PinyinComparator(t1, t1py)
  comparator.ComputeDistance()
  assert comparator.ComparisonResult().Cost() == auxiliary_comp.MATCH_, \
      '%s should match %s' % (t1.String(), t1py.String())
  comparator = auxiliary_comp.PinyinComparator(t2, t2py)
  comparator.ComputeDistance()
  assert comparator.ComparisonResult().Cost() == auxiliary_comp.MATCH_, \
      '%s should match %s' % (t2.String(), t2py.String())
  comparator = auxiliary_comp.WadeGilesComparator(t1, t1wg)
  comparator.ComputeDistance()
  assert comparator.ComparisonResult().Cost() == auxiliary_comp.MATCH_, \
      '%s should match %s' % (t1.String(), t1wg.String())
  comparator = auxiliary_comp.WadeGilesComparator(t2, t2wg)
  comparator.ComputeDistance()
  assert comparator.ComparisonResult().Cost() == auxiliary_comp.MATCH_, \
      '%s should match %s' % (t2.String(), t2wg.String())
  comparator = auxiliary_comp.WadeGilesComparator(t2, t2py)
  comparator.ComputeDistance()
  assert comparator.ComparisonResult().Cost() == auxiliary_comp.NO_MATCH_, \
      '%s should not match %s' % (t2.String(), t2py.String())
  print '%s (auxiliary tests) successful' % unitname


def main(output = False):
  phonecmps = []
  timecmps = []
  doclist = CreateDoclist()
  for pair in PAIRS_:
    token1 = tokens.Token(pair[0])
    TestPronunciations(token1)
    token2 = tokens.Token(pair[1])
    TestPronunciations(token2)
    comparator = token_comp.OldPhoneticDistanceComparator(token1, token2)
    comparator.ComputeDistance()
    phonecmps.append(comparator)
  if output:
    p = open(GOLDEN_FILE_, 'w')  ## clear golden file
    p.close()
    for pc in phonecmps:
      pc.ComparisonResult().Print(GOLDEN_FILE_, 'a')
    TestCorrelations(doclist, GOLDEN_FILE_)
    TestSnowActivations(doclist, GOLDEN_FILE_)
  else:
    p = open(TEST_FILE_, 'w') ## clear test file
    p.close()
    for pc in phonecmps:
      pc.ComparisonResult().Print(TEST_FILE_, 'a')
    TestCorrelations(doclist, TEST_FILE_)
    TestSnowActivations(doclist, TEST_FILE_)
    unittest.TestUnitOutputs(sys.argv[0] + ' (main test & perceptron test)', \
                             GOLDEN_FILE_, TEST_FILE_)
    TestAuxiliaryComparators(sys.argv[0])

if __name__ == '__main__':
  if len(sys.argv) > 1 and sys.argv[1] == 'generate':
    main(True)
  else:
    main()
