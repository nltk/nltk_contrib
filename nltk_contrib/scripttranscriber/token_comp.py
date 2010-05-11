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

"""String-based comparator. Takes two tokens and returns a result that
includes the cost for the comparison. The comparator may be based on
any features of the two tokens, but reasonable features are phoneme
sequences, grapheme sequences (possibly based on a portion of the
morphological decomposition rather than the raw token), combinations
of these, or features derived from them.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
hollingk@cslu.ogi.edu (Kristy Hollingshead)
ting.qian@rochester.edu (Ting Qian)
"""

import sys
import tokens
import MinEditDist.mEdit
import perceptron_trainer
from __init__ import BASE_

CDIC_        = None
PFDIC_       = None
PHONE_TABLE_ = {}
DUMMY_PHONE_ = 'DUM'
MEDIT_PATH_ = '%s/MinEditDist' % BASE_

class ComparisonResult:
  """Value returned by TokenComparator. Includes the two tokens, the
  comparison cost, and informative string explaining how the cost was
  achieved.
  """
  def __init__(self, token1, token2):
    self.token1_ = token1
    self.token2_ = token2
    self.cost_ = 0
    self.info_ = ''

  def __repr__(self):
    return \
        '#<comparator: %s <-> %s, %2.4f, "%s">' % (self.token1_.String(),
                                                   self.token2_.String(),
                                                   self.cost_,
                                                   self.info_)

  def Print(self, file=None, mode='w'):
    if file: stream = open(file, mode)
    else: stream = sys.stdout
    info = '%s\t%s\t%f\t%s' % (self.token1_.String(),
                               self.token2_.String(),
                               self.cost_,
                               self.info_)
    #info = info.decode('utf-8')
    stream.write('%s\n' % info)
    if file: stream.close()

  def Cost(self):
    return self.cost_

  def SetCost(self, cost):
    self.cost_ = cost

  def Info(self):
    return self.info_

  def SetInfo(self, info):
    self.info_ = info

class TokenComparator:
  """Base class for token comparators.
  """
  def __init__(self, token1, token2):
    self.token1_ = token1
    self.token2_ = token2

  def InitData(self, data = []):
    return

  def ComparisonResult(self):
    return self.comparison_result_

  def ComputeDistance(self):
    self.comparison_result_ = ComparisonResult(self.token1_, self.token2_)

class OldPhoneticDistanceComparator(TokenComparator):
  """Phonetic distance comparator based on hand-derived features and
  old mEdit code.
  """
  def __init__(self, token1, token2):
    self.token1_ = token1
    self.token2_ = token2
    self.InitData()

  def LoadPhones(self, file):
    p = open(file)
    lines = p.readlines()
    p.close()
    phone_table = {}
    for phone in lines:
      PHONE_TABLE_[phone.strip()] = True

  def ProcessStringforMEditDistance(self, string):
    phones = string.split()
    nphones = []
    for phone in phones:
      if phone in PHONE_TABLE_: nphones.append(phone)
      else: nphones.append(DUMMY_PHONE_)
    return ' '.join(nphones)

  def InitData(self):
    global CDIC_
    global PFDIC_
    MinEditDist.mEdit._PHONE_FEATURES_FILE = \
        '%s/phoneFeature2.txt' % MEDIT_PATH_
    if CDIC_ and PFDIC_ and PHONE_TABLE_:
      pass
    else:
      phon_vocab = '%s/total_c.vocab' % MEDIT_PATH_
      CDIC_, PFDIC_ = MinEditDist.mEdit.init(phon_vocab)
      self.LoadPhones(phon_vocab)

  def ComputeDistance(self):
    bestcost = 100000
    bestinfo = ''
    for trans1 in self.token1_.Pronunciations():
      trans1 = self.ProcessStringforMEditDistance(trans1)
      for trans2 in self.token2_.Pronunciations():
        trans2 = self.ProcessStringforMEditDistance(trans2)
        cost = MinEditDist.mEdit.mEdit(trans1, trans2, CDIC_, PFDIC_)
        if cost < bestcost:
          bestcost = cost
          bestinfo = '%s <-> %s' % (trans1, trans2)
    result = ComparisonResult(self.token1_, self.token2_)
    result.SetCost(bestcost)
    result.SetInfo(bestinfo)
    self.comparison_result_ = result

class TimeCorrelator(TokenComparator):
  """Time distance comparator based on using the Pearson's correlation
  coefficient to calculate the similarity of two terms' frequency
  distribution.
  """
  def __init__(self, token1, token2, doctokstats):
    self.token1_ = token1
    self.token2_ = token2
    self.stats_ = doctokstats

  def ComputeDistance(self):
    bestcost = 0
    bestinfo = ''
    corr = self.stats_.PearsonsCorrelation(self.token1_, self.token2_)
    bestcost = corr
    bestinfo = 'Pearson\'s correlation'
    result = ComparisonResult(self.token1_, self.token2_)
    result.SetCost(bestcost)
    result.SetInfo(bestinfo)
    self.comparison_result_ = result

class SnowPronComparator(TokenComparator):
  """Snow comparator based on using a perceptron's activation given a
  pair of two terms.
  """
  def __init__(self, fm_file=None, net_file=None):
    perceptron_trainer.DEBUG_ = True
    self.snow_ = perceptron_trainer.ParallelTrainer(fm_file, net_file)

  def Train(self, pos_example_list):
    return self.snow_.Train(pos_example_list)

  def LearnFromNewExamples(self, new_example_list):
    self.snow_.Retrain(new_example_list)

  def ComputeDistance(self, token1, token2):
    if self.snow_.IsTrained():
      max_act_value = 0
      max_act_sign = 1
      bestinfo = 'Pronunciation Perceptron'

      for p1 in token1.Pronunciations():
        for p2 in token2.Pronunciations():
          cost = 0
          act_tuple = self.snow_.Evaluate(p1, p2)
          target = act_tuple[0]
          activation = act_tuple[1]
          if target == 0:
            if activation > max_act_value:
              max_act_sign = -1
              max_act_value = activation
          elif target == 1:
            if activation > max_act_value:
              max_act_sign = 1
              max_act_value = activation

      bestcost = max_act_value * max_act_sign
      result = ComparisonResult(token1, token2)
      result.SetCost(bestcost)
      result.SetInfo(bestinfo)
      self.comparison_result_ = result
    else:
      result = ComparisonResult(token1_, token2_)
      result.SetCost(0)
      result.SetInfo('Pronunciation Perceptron')
      self.comparison_result_ = result

  def Forget(self):
    self.snow_.CleanUp()
    
    
    
