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

"""Definition for tokens, languages, documents and doclists, to store
the results of extraction, and express in XML.

For the XML format see dochandler.py
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
hollingk@cslu.ogi.edu (Kristy Hollingshead)
"""

import xml.sax.saxutils
from math import sqrt
from __init__ import BASE_
import documents

XML_HEADER_ = '<?xml version="1.0" encoding="UTF-8"?>'
LANG_INDENT_  = ' ' * 4
TOKEN_INDENT_ = ' ' * 6

def SumProd(x, y):
  return sum(map(lambda x, y: x * y, x, y))

class Token:
  """A token is a term extracted from text, with attributes
  count, pronunciation, morphological decomposition
  """
  def __init__(self, string):
    try: self.string_ = string.encode('utf-8')
    except UnicodeDecodeError: self.string_ = string
    self.count_ = 1
    self.morphs_ = []
    self.pronunciations_ = []
    self.frequencies_ = []
    self.langid_ = ''

  def __eq__(self, other):
    skey = self.EncodeForHash()
    okey = other.EncodeForHash()
    return skey == okey

  def __repr__(self):
    return '#<%s %d %s %s %s>' % (self.string_,
                                  self.count_,
                                  self.morphs_,
                                  self.pronunciations_,
                                  self.langid_)

  def XmlEncode(self):
    xml_string_ = '<token count="%d" morphs="%s" prons="%s">%s</token>'
    morphs = ' '.join(self.morphs_)
    morphs = xml.sax.saxutils.escape(morphs)
    prons = ' ; '.join(self.pronunciations_)
    prons = xml.sax.saxutils.escape(prons)
    string_ = xml.sax.saxutils.escape(self.string_)
    xml_result = xml_string_ % (self.count_, morphs, prons, string_)
    return  TOKEN_INDENT_ + xml_result

  def EncodeForHash(self):
    return '%s<%s><%s><%s>' % (self.String(),
                               ' '.join(self.Morphs()),
                               ' '.join(self.Pronunciations()),
                               self.LangId())

  def String(self):
    return self.string_

  def SetCount(self, count):
    self.count_ = count

  def IncrementCount(self, increment = 1):
    self.count_ += increment

  def Count(self):
    return self.count_

  def AddPronunciation(self, pron):
    if pron not in self.pronunciations_:
      try: self.pronunciations_.append(pron.encode('utf-8'))
      except UnicodeDecodeError: self.pronunciations_.append(pron)

  def Pronunciations(self):
    return self.pronunciations_

  def SetMorphs(self, morphs):
    self.morphs_ = []
    for m in morphs:
      try: self.morphs_.append(m.encode('utf-8'))
      except UnicodeDecodeError: self.morphs_.append(m)

  def Morphs(self):
    return self.morphs_

  def SetLangId(self, lang):
    self.langid_ = lang

  def LangId(self):
    return self.langid_

class TokenFreqStats:
  """Holder for token frequency-statistics such as
  relative frequency-counts and variance.
  """
  def __init__(self, tok):
    self.token_ = tok
    self.frequencies_ = []
    self.freqsum_ = 0
    self.freqsumsq_ = 0
    self.variance_ = 0

  def __repr__(self):
    return '#<%s %s %.6f %.6f %.6f>' % (self.token_,
                                        self.frequencies_,
                                        self.freqsum_,
                                        self.freqsumsq_,
                                        self.variance_)

  def Token(self):
    return self.token_

  def Frequencies(self):
    return self.frequencies_

  def AddFrequency(self, f):
    self.frequencies_.append(f)

  def SetFrequencies(self, freq):
    self.frequencies_ = []
    for f in freq:
      self.frequencies_.append(f)

  def NormFrequencies(self):
    self.frequencies_ = [float(f) for f in self.frequencies_]
    sumfreqs = float(sum(self.frequencies_))
    if sumfreqs != 0.0:
      self.frequencies_ = [f/sumfreqs for f in self.frequencies_]

  def CalcFreqStats(self):
    n = len(self.frequencies_)
    self.freqsum_ = float(sum(self.frequencies_))
    self.freqsumsq_ = SumProd(self.frequencies_, self.frequencies_)
    self.variance_ = self.freqsumsq_/n - (self.freqsum_**2)/(n**2)

  def FreqSum(self):
    return self.freqsum_
    
  def FreqVariance(self):
    return self.variance_

class DocTokenStats:
  """Holder for Doclist-specific token statistics, such as frequency
  counts. Also allows for calculation of pairwise comparison metrics
  such as Pearson's correlation.
  """
  def __init__(self, doclist=None):
    if doclist is None:
      self.doclist_ = documents.Doclist()
    else: self.doclist_ = doclist
    self.n_ = len(self.doclist_.Docs())
    self.tokstats_ = {}

  def InitTokenStats(self, tok):
    tstats = TokenFreqStats(tok)
    tfreq = []
    for doc in self.doclist_.Docs():
      c = 0
      for lang in doc.Langs():
        if tok.LangId() != lang.Id(): continue
        tmptok = lang.MatchToken(tok)
        if tmptok is not None:
          c += tmptok.Count()
      tfreq.append(c)
    tstats.SetFrequencies(tfreq)
    tstats.NormFrequencies()
    tstats.CalcFreqStats()
    self.tokstats_[tok.EncodeForHash()] = tstats
    return tstats

  def AddTokenStats(self, tstats):
    tokhash = tstats.Token().EncodeForHash()
    if tokhash not in self.tokstats_:
      self.tokstats_[tokhash] = tstats

  def GetTokenStats(self, tok):
    try: return self.tokstats_[tok.EncodeForHash()]
    except KeyError: return self.InitTokenStats(tok)

  def TokenStats(self):
    return self.tokstats_.values()

  def SetN(self, n):
    self.n_ = n

  def GetN(self):
    return self.n_

  def PearsonsCorrelation(self, token1, token2):
    stats1 = self.GetTokenStats(token1)
    stats2 = self.GetTokenStats(token2)
    freq1 = stats1.Frequencies()
    freq2 = stats2.Frequencies()
    sumxy = sum(map(lambda x, y: x * y, freq1, freq2))
    covxy = sumxy/float(self.n_) - \
            (stats1.FreqSum()*stats2.FreqSum())/float(self.n_**2)
    try:
      rho = covxy/sqrt(stats1.FreqVariance()*stats2.FreqVariance())
    except ZeroDivisionError:
      rho = 0.0
    #print x.String(),y.String(),sumx2,sumy2,varx,vary,sumxy,covxy,rho
    return rho

class Lang:
  """Holder for tokens in a language.
  """
  def __init__(self):
    self.id_ = ''
    self.tokens_ = []

  def XmlEncode(self):
    if len(self.tokens_) == 0: return ''
    xml_string_ = '<lang id="%s">\n%s\n%s</lang>'
    xml_tokens = []
    for token_ in self.Tokens():
      xml_tokens.append(token_.XmlEncode())
    xml_result = xml_string_ % (self.id_, '\n'.join(xml_tokens),
                                LANG_INDENT_)
    return LANG_INDENT_ + xml_result

  def Id(self):
    return self.id_

  def SetId(self, id):
    self.id_ = id.encode('utf-8')

  def Tokens(self):
    return self.tokens_

  def SetTokens(self, tokens):
    self.tokens_ = []
    for t in tokens:
      self.AddToken(t)

  def AddToken(self, token, merge=False):
    """If an identical token already exists in dictionary,
    will merge tokens and cumulate their counts. Checks to
    see that morphology and pronunciations are identical,
    otherwise the tokens will not be merged.
    """
    token.SetLangId(self.id_)
    if not merge:
      self.tokens_.append(token)
    else:
      exists = self.MatchToken(token)
      if exists is None:
        self.tokens_.append(token)
      else:
        exists.IncrementCount(token.Count())

  def MatchToken(self, token):
    try:
      i = self.tokens_.index(token)
      return self.tokens_[i]
    except ValueError:
      return None

  def CompactTokens(self):
    """Merge identical tokens and cumulate their counts. Checks to see
    that morphology and pronunciations are identical, otherwise the
    tokens will not be merged.
    """
    map = {}
    for token_ in self.tokens_:
      hash_string = token_.EncodeForHash()
      try: map[hash_string].append(token_)
      except KeyError: map[hash_string] = [token_]
    ntokens = []
    keys = map.keys()
    keys.sort()
    for k in keys:
      token_ = map[k][0]
      for otoken in map[k][1:]:
        token_.IncrementCount(otoken.Count())
      ntokens.append(token_)
    self.tokens_ = ntokens

