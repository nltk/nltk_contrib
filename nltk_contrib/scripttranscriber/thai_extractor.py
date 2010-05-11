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

"""Extractor for Thai. 

Uses a perceptron-based segmenter trained on the Thai LCTL data from
LDC. However, this tends to oversegment (even though it has 98%
accuracy on the tags...) so we also include the whole space-delimited
token as a candidate.

Something similar should also work for Lao...
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

import extractor
import tokens
import Utils.script
import snow
from __init__ import BASE_

FEATURES_FILE_ = '%s/Utils/thaifeats.txt' % BASE_
NETWORK_FILE_  = '%s/Utils/thaiseg.net' % BASE_

MIN_CNT_ = 5
MIN_LEN_ = 5
MAX_REASONABLE_SINGLE_WORD_ = 15


class FeatureMap:
  def __init__(self):
    self.table_ = {}
    self.itable_ = {}
    self.curr_label_ = 1
    self.immutable_ = False
  
  def Encode(self, feat):
    try:
      return self.table_[feat]
    except KeyError:
      if self.immutable_: return None
      self.table_[feat] = self.curr_label_
      self.curr_label_ += 1
      return self.table_[feat]

  def Decode(self, val):
    try:
      return self.itable_[val]
    except KeyError:
      return None

  def Dump(self, file):
    keys = self.table_.keys()
    keys.sort(lambda x, y: cmp(self.table_[x], self.table_[y]))
    p = open(file, 'w')
    for k in keys:
      p.write('%s\t%d\n' % (k, self.table_[k]))
    p.close()

  def Load(self, file, immutable = True):
    """By default if we load from a file we assume that the features
    come from an already trained system, so we don't add new features.
    """
    self.immutable_ = immutable
    p = open(file, 'r')
    lines = p.readlines()
    p.close()
    for line in lines:
      (k, v) = line.strip().split('\t')
      v = int(v)
      self.table_[k] = v
      self.itable_[v] = k


def Listify(text):
  """Split out the characters of the text into a list for fast feature
  extraction.
  """
  list = []
  for u in unicode(text, 'utf8'):
    list.append(u.encode('utf8'))
  return list


def FeatureExtract(i, corpus, fmap):
  try: l4 = corpus[i-4]
  except IndexError: l4 = '#'
  try: l3 = corpus[i-3]
  except IndexError: l3 = '#'
  try: l2 = corpus[i-2]
  except IndexError: l2 = '#'
  try: l1 = corpus[i-1]
  except IndexError: l1 = '#'
  try: r1 = corpus[i+1]
  except IndexError: r1 = '#'
  try: r2 = corpus[i+2]
  except IndexError: r2 = '#'
  try: r3 = corpus[i+3]
  except IndexError: r3 = '#'
  try: r4 = corpus[i+4]
  except IndexError: r4 = '#'
  t = corpus[i]
  ifeats = []
  ifeats.append(fmap.Encode('%s%s%s%s_' % (l4,l3,l2,l1)))
  ifeats.append(fmap.Encode('%s%s%s_%s' % (l3,l2,l1,r1)))
  ifeats.append(fmap.Encode('%s%s_%s%s' % (l2,l1,r1,r2)))
  ifeats.append(fmap.Encode('%s_%s%s%s' % (l1,r1,r2,r3)))
  ifeats.append(fmap.Encode('_%s%s%s%s' % (r1,r2,r3,r4)))
  ifeats.append(fmap.Encode('%s%s%s_' % (l3,l2,l1)))
  ifeats.append(fmap.Encode('%s%s_%s' % (l2,l1,r1)))
  ifeats.append(fmap.Encode('%s_%s%s' % (l1,r1,r2)))
  ifeats.append(fmap.Encode('_%s%s%s' % (r1,r2,r3)))
  ifeats.append(fmap.Encode('%s%s_' % (l2,l1)))
  ifeats.append(fmap.Encode('%s_%s' % (l1,r1)))
  ifeats.append(fmap.Encode('_%s%s' % (r1,r2)))
  ifeats.append(fmap.Encode('%s' % t))
  feats = []
  for f in ifeats:
    if f == None: continue
    feats.append(f)
  return feats


class ThaiExtractor(extractor.Extractor):
  """Extractor of potential Thai terms.
  """

  def FileExtract(self, filename):
    """This is like EastAsianExtractor but also keeps tabs on how many
    times each segment occurs in a text.
    """
    fp = open(filename, 'r')
    nlines = []
    for line in fp.readlines():
      line = line.strip()
      if line == '': line = ' ' ## Keep empty line
      nlines.append(line)
    text = ''.join(nlines)
    for line in text.split():
      self.LineSegment(line)
    return self.tokens_

  def LineSegment(self, line):
    """Replace this with the call to SNoW. Segment before a char if it
    is classified as B or I. After if it is classified as I or
    F. Conflicts are:
    
    F M
    F F
    M I
    M B
    B F
    B M
    I B

    """
    try: self.feature_map_
    except AttributeError:
      self.feature_map_ = FeatureMap()
      self.feature_map_.Load(FEATURES_FILE_)
    try: self.snow_session_
    except AttributeError:
      snow_test_args = {'F':NETWORK_FILE_,\
                        'o':"allactivations",\
                        'v':"off"
                        }
      self.snow_session_ = snow.SnowSession(snow.MODE_SERVER,
                                            snow_test_args)
    try: utext = unicode(line.strip(), 'utf-8')
    except TypeError: utext = line.strip()
    segments = utext.split()
    for segment in segments:
      if len(segment) < MAX_REASONABLE_SINGLE_WORD_:
        t = tokens.Token(segment) ## the whole segment too...
        self.tokens_.append(t)
      seglist = Listify(segment.encode('utf8'))
      features = []
      for i in range(len(seglist)):
        feats = ', '.join(map(lambda x: str(x),
                              FeatureExtract(i, seglist,
                                             self.feature_map_))) + ':\n'
        result = self.snow_session_.evaluateExample(feats)
        target, a, b, activation = result.split('\n')[1].split()
        target = int(target[:-1]) ## remove ':'
        if activation[-1] == '*':
          activation = activation[:-1]
        activation = float(activation)
        feature = self.feature_map_.Decode(target)
        features.append((feature, target, activation))
      tok = ''
      for i in range(len(seglist)):
        if features[i][0] == 'B' or features[i][0] == 'F':
          tok += seglist[i]
          t = tokens.Token(tok)
          self.tokens_.append(t)
          tok = ''
        elif features[i][0] == 'I':
          if tok:
            t = tokens.Token(tok)
            self.tokens_.append(t)
            tok = ''
          tok += seglist[i]
        else:
          tok += seglist[i]
      if tok:
        t = tokens.Token(tok)
        self.tokens_.append(t)
