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

"""
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

import sys
import os
import getopt
import xml.sax.handler
import documents
import tokens
import token_comp
import extractor
import chinese_extractor
import thai_extractor
import pronouncer
import morph
import filter
import def_pronouncers
from __init__ import BASE_

DEF_BAD_COST_ = 6.0

DEF_MINCNT_ = 20

USAGE_      = """
  -l/--list=[file list] 
  -b/--base=[directory base] (default: .)
  -x/--xml_dump=[location of xml dump file (default: /tmp/pid.xml)]
  -p/--phonetic_match_dump=[phonetic match dump (def: /tmp/pid.pmatch)]
  -t/--temporal_match_dump=[temporal match dump (def: /tmp/pid.tmatch)]
  -m/--min_count=[minimum corpus count for keeping term (def: %d)]
  -b/--bad_cost=[minimum cost to keep phonetic match (def: %.1f)]
""" % (DEF_MINCNT_, DEF_BAD_COST_)
USAGE_       = "Usage: %s [args]\n  Arguments:" + USAGE_


def LoadData(filelist,
             base='.',
             extractor_=extractor.NameExtractor,
             xdump=None,
             mincnt=DEF_MINCNT_):
  lastgroup = -1
  lastlanguage = ''
  doc = None
  lang = None
  doclist = documents.Doclist()
  xtractr = extractor_()
  sys.stderr.write('Extracting terms...\n')
  fp = open(filelist)
  for line in fp:
    toks = line.split()
    group = int(toks[0])
    language = toks[1]
    files = toks[2:]
    if group != lastgroup:
      if lastgroup > 0:
        assert group == lastgroup + 1,\
            'Failed sanity check: group %d != group %d + 1' % (group, lastgroup)
      doc = documents.Doc()
      doclist.AddDoc(doc)
    if language != lastlanguage:
      if lang:
        lang.CompactTokens()
      lang = tokens.Lang()
      lang.SetId(language)
      doc.AddLang(lang)
    for file in files:
      file = base + '/' + file
      xtractr.InitData()
      xtractr.FileExtract(file)
      for t in xtractr.Tokens():
        lang.AddToken(t)
    lastgroup = group
    lastlanguage = language
    #lines = p.readlines()
  fp.close()
  if mincnt > 0:
    sys.stderr.write('Filtering to remove terms less frequent than %d...\n' %
                     mincnt)
    filter_ = filter.FrequencyFilter(doclist)
    filter_.SetMinCount(mincnt)
    filter_.Filter()
  if xdump:
    sys.stderr.write('Dumping doclist to %s...\n' % xdump)
    doclist.XmlDump(xdump, utf8 = True)    
  return doclist


def Pronounce(doclist, xdump=None):
  cached_prons = {}
  did = 0
  for doc in doclist.Docs():
    for lang in doc.Langs():
      lid = lang.Id()
      sys.stderr.write('Pronouncing doc %d, language %s\n' % (did, lid))
      for t in lang.Tokens():      
        try:
          prons = cached_prons[t.String()]
          for p in prons:
            t.AddPronunciation(p)
        except KeyError:
          for pronouncer_ in def_pronouncers.DefPronouncers(lid):
            p = pronouncer_(t)
            p.Pronounce()
          cached_prons[t.String()] = t.Pronunciations()
    did += 1
  if xdump:
    sys.stderr.write('Dumping doclist to %s...\n' % xdump)
    doclist.XmlDump(xdump, utf8 = True)    


def CompLT(i, j):
  if i < j: return 1
  if i == j: return 0
  if i > j: return -1


def CompGT(i, j):
  if i < j: return -1
  if i == j: return 0
  if i > j: return 1


def Comparator(doclist,
               comparator=token_comp.OldPhoneticDistanceComparator,
               pdump=None,
               bad_cost=DEF_BAD_COST_,
               comp=CompLT):
  matches = {}
  did = 0
  if comparator == token_comp.TimeCorrelator:
    stats = tokens.DocTokenStats(doclist)
  for doc in doclist.Docs():
    k = len(doc.Langs())
    for i in range(k):
      for j in range(i+1, k):
        lang1 = doc.Langs()[i]
        lang2 = doc.Langs()[j]
        sys.stderr.write('Computing comparison for doc %d, l1=%s, l2=%s\n'
                         % (did, lang1.Id(), lang2.Id()))
        for t1 in lang1.Tokens():
          hash1 = t1.EncodeForHash()
          for t2 in lang2.Tokens():
            hash2 = t2.EncodeForHash()
            try:
              result = matches[(hash1, hash2)] ## don't re-calc
            except KeyError:
              if comparator == token_comp.TimeCorrelator:
                comparator_ = comparator(t1, t2, stats)
              else:
                comparator_ = comparator(t1, t2)
              comparator_.ComputeDistance()
              result = comparator_.ComparisonResult()
              matches[(hash1, hash2)] = result
    did += 1
  values = matches.values()
  values.sort(lambda x, y: comp(y.Cost(), x.Cost()))
  if pdump:
    sys.stderr.write('Dumping comparisons to %s...\n' % pdump)
    p = open(pdump, 'w') ## zero out the file
    p.close()
    for v in values:
      if comp(v.Cost(), bad_cost) < 0: break
      v.Print(pdump, 'a')


def Usage(argv):
  sys.stderr.write(USAGE_ % argv[0])
  sys.exit(2)


def main(argv):
  list = ''
  bad_cost = DEF_BAD_COST_
  mincnt = DEF_MINCNT_
  pid = os.getpid()
  xdump = '/tmp/%d.xml' % pid
  pdump = '/tmp/%d.pmatch' % pid
  tdump = None
  base = '.'
  try:
    opts, args = getopt.getopt(argv[1:],
                               "l:b:x:p:t:m:B:",
                               ["list=", "base=",
                                "xml_dump=", "phonetic_match_dump=",
                                "temporal_match_dump=",
                                "min_count=", "bad_cost="])
  except getopt.GetoptError:
    Usage(argv)
  for opt, arg in opts:
    if opt in ("-l", "--list"):
      list = arg
    elif opt in ("-b", "--base"):
      base = arg
    elif opt in ("-x", "--xml_dump"):
      xdump = arg
    elif opt in ("-p", "--phonetic_match_dump"):
      pdump = arg
    elif opt in ("-t", "--temporal_match_dump"):
      tdump = arg
    elif opt in ("-m", "--min_count"):
      mincnt = float(arg)
    elif opt in ("-B", "--bad_cost"):
      bad_cost = float(arg)
  if not list: Usage(argv)
  doclist = LoadData(list,
                     base=base,
                     extractor_=extractor.NameExtractor,
                     xdump=xdump,
                     mincnt=mincnt)
  Pronounce(doclist,
            xdump=xdump)
  Comparator(doclist,
             pdump=pdump,
             bad_cost=bad_cost,
             comp=CompLT)
  if tdump:
    Comparator(doclist,
               pdump=tdump,
               comparator=token_comp.TimeCorrelator,
               bad_cost=0.1 ** 10,
               comp=CompGT)


if __name__ == '__main__':
  main(sys.argv)
