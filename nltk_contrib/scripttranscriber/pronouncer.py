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

"""Pronouncer class.

Takes a token as input and calls an appropriate method to fill in the
pronunciation field.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

import tokens
import Unitran.unitran
import Utils.chinese
import Utils.kunyomi_new
import Utils.english
import Utils.latin
from __init__ import BASE_

DUMMY_PHONE_ = 'DUM'

UNITRAN_PATH_ = '%s/Unitran' % BASE_
UTILS_PATH_ = '%s/Utils' % BASE_

class Pronouncer:
  def __init__(self, token):
    self.token_ = token

  def InitData(self, data = []):
    return

  def Pronounce(self):
    self.token_.AddPronunciation(self.token_.String())

  def Token(self):
    return self.token_


class UnitranPronouncer(Pronouncer):
  """Uses Unitran to compute the pronunciation of a UTF-8 token. Works
  for any script except Latin and Hanzi/Hanja/Kanji.
  """
  def __init__(self, token):
    self.token_ = token
    self.InitData()
  
  def InitData(self):
    Unitran.unitran.JOINER_ = ' '
    Unitran.unitran.IndicCon= \
        Unitran.unitran.IndicCV('%s/IndicCon.txt' % UNITRAN_PATH_)
    Unitran.unitran.IndicVowel = \
        Unitran.unitran.IndicCV('%s/IndicVowel.txt' % UNITRAN_PATH_)
    Unitran.unitran.IndicComp = \
        Unitran.unitran.IndicTwoPartVowels('%s/IndicTwoPartVowel.txt' % 
                                           UNITRAN_PATH_)
    Unitran.unitran.UpdateTransTable(Unitran.unitran.Tables.TransTable)

  def Pronounce(self):
    pron = Unitran.unitran.ProcToken(self.token_.String())
    if pron and ''.join(pron.split()) != self.token_.String():
      try: pron.encode('ascii')
      except UnicodeDecodeError:
        pron2 = []
        for p in pron.split():
          try: p2 = p.encode('ascii')
          except: p2 = DUMMY_PHONE_
          pron2.append(p2)
        pron = ' '.join(pron2)
      self.token_.AddPronunciation(pron)

class HanziPronouncer(Pronouncer):
  """Mandarin and kunyomi (native Japanese) pronunciations.
  """
  def __init__(self, token):
    self.token_ = token
    self.InitData()
  
  def InitData(self):
    Utils.chinese.LoadMandarinWbTable('%s/Mandarin.wb' % UTILS_PATH_)
    Utils.kunyomi_new.LoadKunyomiWbTable('%s/Kunyomi_new.wb' % UTILS_PATH_)

  def Pronounce(self):
    pronc, successc = Utils.chinese.HanziToWorldBet(self.token_.String())
    pronk, successk = Utils.kunyomi_new.KanjiToWorldBet(self.token_.String())
    if successc:
      try: pronc.encode('ascii')
      except UnicodeDecodeError:
        pronc2 = []
        for p in pronc.split():
          try: p2 = p.encode('ascii')
          except: p2 = DUMMY_PHONE_
          pronc2.append(p2)
        pronc = ' '.join(pronc2)
      self.token_.AddPronunciation(pronc)
    if successk:
      try: pronk.encode('ascii')
      except UnicodeDecodeError:
        pronk2 = []
        for p in pronk.split():
          try: p2 = p.encode('ascii')
          except: p2 = DUMMY_PHONE_
          pronk2.append(p2)
        pronk = ' '.join(pronk2)
      self.token_.AddPronunciation(pronk)

class EnglishPronouncer(Pronouncer):
  """Uses a static list compiled from Festival to look up the word
  """
  def __init__(self, token):
    self.token_ = token
    self.InitData()

  def InitData(self):
    Utils.english.LoadEnglishWbTable('%s/English.wb' % UTILS_PATH_)

  def Pronounce(self):
    pron = Utils.english.EnglishToWorldBet(self.token_.String())
    if pron:
      try: pron.encode('ascii')
      except UnicodeDecodeError:
        pron2 = []
        for p in pron.split():
          try: p2 = p.encode('ascii')
          except: p2 = DUMMY_PHONE_
          pron2.append(p2)
        pron = ' '.join(pron2)
      self.token_.AddPronunciation(pron)

class LatinPronouncer(Pronouncer):
  """Fallback pronouncer for arbitrary latin1
  """
  def __init__(self, token):
    self.token_ = token
    self.InitData()
  
  def InitData(self):
    Utils.latin.LoadLatinWbTable('%s/Latin.wb' % UTILS_PATH_)

  def Pronounce(self):
    pron, success = Utils.latin.LatinToWorldBet(self.token_.String())
    if success:
      try: pron.encode('ascii')
      except UnicodeDecodeError:
        pron2 = []
        for p in pron.split():
          try: p2 = p.encode('ascii')
          except: p2 = DUMMY_PHONE_
          pron2.append(p2)
        pron = ' '.join(pron2)
      self.token_.AddPronunciation(pron)
