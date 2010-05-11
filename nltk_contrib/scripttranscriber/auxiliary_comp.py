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

"""Additional string-based comparators:

1) pinyin comparator: match a sequence of Chinese characters against
   its pinyin transcription.

"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

import sys
import tokens
import token_comp
import Utils.script
from __init__ import BASE_


PINYIN_TABLE_FILE_ = '%s/Utils/pinyin.txt' % BASE_
PINYIN_TABLE_ = {}
PINYIN_TABLE_LOADED_ = False
PY_WG_MAP_FILE_ = '%s/Utils/py2wg.txt' % BASE_
PY_WG_MAP_ = {}
PY_WG_MAP_LOADED_ = False
MATCH_ = 0
NO_MATCH_ = 10000


def LoadPinyinTable():
  global PINYIN_TABLE_LOADED_
  p = open(PINYIN_TABLE_FILE_)
  for line in p.readlines():
    line = line.strip().split()
    try: PINYIN_TABLE_[line[0]].append(line[1])
    except KeyError: PINYIN_TABLE_[line[0]] = [line[1]]
  p.close()
  PINYIN_TABLE_LOADED_ = True


def LoadPYWGMap():
  global PY_WG_MAP_LOADED_
  p = open(PY_WG_MAP_FILE_)
  for line in p.readlines():
    line = line.strip().split()
    PY_WG_MAP_[line[0]] = line[1]
  p.close()
  PY_WG_MAP_LOADED_ = True


def Catenations(pys, result, string=''):
  if not pys:
    result.append(string)
  else:
    first = pys[0]
    for f in first:
      Catenations(pys[1:], result, string=string + f)


def LookupString(chars, convert=False):
  pys = []
  for u in unicode(chars, 'utf8'):
    try:
      py = PINYIN_TABLE_[u.encode('utf8')]
      npy = []
      if convert and PY_WG_MAP_LOADED_:
        for p in py:
          p = PY_WG_MAP_[p]
          p = p.replace("'", '')
          npy.append(p)
        py = npy
      pys.append(py)
    except KeyError:
      return []
  result = []
  Catenations(pys, result=result, string='')
  return result

class PinyinComparator(token_comp.TokenComparator):
  """Compare Chinese character sequence to Pinyin transcription such
  as one would find in standard newspapers.
  """
  def __init__(self, token1, token2):
    self.token1_ = token1
    self.token2_ = token2
    self.InitData()

  def InitData(self):
    if not PINYIN_TABLE_LOADED_: LoadPinyinTable()

  def ComputeDistance(self):
    """Assumes pinyin with no tone marks
    """
    latin = self.token1_.String()
    hanzi = self.token2_.String()
    result = token_comp.ComparisonResult(self.token1_, self.token2_)
    result.SetInfo('%s <-> %s' % (latin, hanzi))
    self.comparison_result_ = result
    script1 = Utils.script.StringToScript(latin)
    script2 = Utils.script.StringToScript(hanzi)
    if script1 == 'Latin' and script2 == 'CJK':
      pass
    elif script2 == 'Latin' and script1 == 'CJK': 
      latin, hanzi = hanzi, latin
    else:
      result.SetCost(NO_MATCH_)
      return
    latin = ''.join(latin.split()).lower()
    latin = latin.replace("'", '') ## ' sometimes used to mark boundary
    latin = latin.replace("-", '') ## - sometimes used to mark boundary
    pinyins = LookupString(hanzi)
    if latin in pinyins: result.SetCost(MATCH_)
    else: result.SetCost(NO_MATCH_)


class WadeGilesComparator(token_comp.TokenComparator):
  """Compare Chinese character sequence to Wade-Giles transcription such
  as one would find in older texts.
  """
  def __init__(self, token1, token2):
    self.token1_ = token1
    self.token2_ = token2
    self.InitData()

  def InitData(self):
    if not PINYIN_TABLE_LOADED_: LoadPinyinTable()
    if not PY_WG_MAP_LOADED_: LoadPYWGMap()

  def ComputeDistance(self):
    """Assumes pinyin with no tone marks
    """
    latin = self.token1_.String()
    hanzi = self.token2_.String()
    result = token_comp.ComparisonResult(self.token1_, self.token2_)
    result.SetInfo('%s <-> %s' % (latin, hanzi))
    self.comparison_result_ = result
    script1 = Utils.script.StringToScript(latin)
    script2 = Utils.script.StringToScript(hanzi)
    if script1 == 'Latin' and script2 == 'CJK':
      pass
    elif script2 == 'Latin' and script1 == 'CJK': 
      latin, hanzi = hanzi, latin
    else:
      result.SetCost(NO_MATCH_)
      return
    latin = ''.join(latin.split()).lower()
    latin = latin.replace("'", '') ## ' sometimes used to mark boundary
    latin = latin.replace("-", '') ## - sometimes used to mark boundary
    pinyins = LookupString(hanzi, convert=True)
    if latin in pinyins: result.SetCost(MATCH_)
    else: result.SetCost(NO_MATCH_)
