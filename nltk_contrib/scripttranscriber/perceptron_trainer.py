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

"""A string-based discrinimative model for transcribing between
pairs of source and target tokens
"""

__author__ = """
ting.qian@rochester.edu (Ting Qian)
"""

import perceptron
import random
import os
import tempfile

DEBUG_ = False

def Distance(a, b):
  """Function that calculates the Levenshtein distance between any two
  indexable objects.
  """
  c = {}
  n = len(a); m = len(b)
  
  for i in range(0, n + 1):
    c[i, 0] = i
  for j in range(0, m + 1):
    c[0, j] = j

  for i in range(1, n + 1):
    for j in range(1, m + 1):
      x = c[i - 1, j] + 1
      y = c[i, j - 1] + 1
      if a[i - 1] == b[j - 1]:
        z = c[i - 1, j - 1]
      else:
        z = c[i - 1, j - 1] + 2
      c[i, j] = min(x, y, z)
  return c[n, m] 

class ParallelTrainer:
  """A perceptron class for training a discriminative model from a parallel dictionary.
  """
  def __init__(self, feature_map_file=None, network_file=None):
    """Constructor. Optional arguments are the filenames of the feature map
    and the network file (existing or to be generated).
    If no parameters are given, default names will be used (not recommended).
    """
    if feature_map_file is not None:
      self.feature_map_file_ = feature_map_file
      try: self.feature_map_ = perceptron.FeatureMap(self.LoadFeatureMap(feature_map_file))
      except: self.feature_map_ = perceptron.FeatureMap()
    else:
      self.feature_map_file_ = 'perceptron.featuremap'
      self.feature_map_ = perceptron.FeatureMap()

    if network_file is not None:
      self.snow_p_ = perceptron.Perceptron(network_file)
    else:
      self.snow_p_ = perceptron.Perceptron()

    self.token2_tri_index_ = {}

  def TrigramSubstr(self, str):
    """Return all possible letter trigrams for a string.
    """
    trigram_substrs = []
    str = '_ ' + str + ' _'
    chars = str.split()
    for i in range(len(chars) - 2):
      trigram_substrs.append(chars[i] + chars[i + 1] + chars[i + 2])
    return trigram_substrs

  def Train(self, pos_examples_list):
    """Given a list of positive examples, generate random negative examples,
    and train a perceptron model.
    Input: a list of positive examples in the form of tuples (token1, token2).
    Output: True if the process is successful. Feature map and network file are
    dumped to the current directory.
    """
    # if the peceptron is already trained, warn and abort
    if self.snow_p_.IsTrained():
      if DEBUG_: print 'Perceptron already trained (use Retrain?)'
      return False

    for example in pos_examples_list:
      for tri in self.TrigramSubstr(example[1]):
        try: self.token2_tri_index_[tri].add(example[1])
        except KeyError:
          self.token2_tri_index_[tri] = set()
          self.token2_tri_index_[tri].add(example[1])        
     
    train_examples = []

    # get positive examples
    for pair in pos_examples_list:
      temp_ex = TRExample(pair[0], pair[1], 1)
      for sc in temp_ex.GenerateCouplings():
        temp_ex.AddFeatureID(self.feature_map_.AddFeature(str(sc)))
      train_examples.append(temp_ex)

    # shuffle to create negative examples
    neg_examples_list = self.ShuffleWords(pos_examples_list)
    for pair in neg_examples_list:
      temp_ex = TRExample(pair[0], pair[1], 0)
      for sc in temp_ex.GenerateCouplings():
        temp_ex.AddFeatureID(self.feature_map_.AddFeature(str(sc)))
      train_examples.append(temp_ex)

    # write the training examples to a file
    random.shuffle(train_examples)
    train_file = tempfile.mkstemp()[1]
    net_fp = open(train_file, 'w')
    for ex in train_examples:
      net_fp.write(ex.DisplayFeatureID())
    net_fp.close()

    # train the model
    self.snow_p_.TrainFromFile(train_file)

    try: os.remove(train_file)
    except: pass
    self.DumpFeatureMap()
    
    return True

  def Retrain(self, new_positives):
    """Incrementally learn from new examples (require a trained perceptron)
    Input: a list of positive examples in the form of tuples (token1, token2).
    Output: True if successful, False otherwise. Feature map and network file
    are updated/created.
    """
    # if the perceptron has not been trained, warn and abort
    if not self.snow_p_.IsTrained():
      if DEBUG_: print 'Perceptron is not trained (use Train?)'
      return False
    
    for example in new_positives:
      for tri in self.TrigramSubstr(example[1]):
        try: self.token2_tri_index_[tri].add(example[1])
        except KeyError:
          self.token2_tri_index_[tri] = set()
          self.token2_tri_index_[tri].add(example[1])     
    
    train_examples = []
    
    # get positive examples
    for pair in new_positives:
      temp_ex = TRExample(pair[0], pair[1], 1)
      for sc in temp_ex.GenerateCouplings():
        temp_ex.AddFeatureID(self.feature_map_.AddFeature(str(sc)))
      train_examples.append(temp_ex)

    # shuffle to create negative examples
    new_negatives = self.ShuffleWords(new_positives)
    for pair in new_negatives:
      temp_ex = TRExample(pair[0], pair[1], 0)
      for sc in temp_ex.GenerateCouplings():
        temp_ex.AddFeatureID(self.feature_map_.AddFeature(str(sc)))
      train_examples.append(temp_ex)

    # append the training examples
    learning_file = tempfile.mkstemp()[1]
    random.shuffle(train_examples)
    net_fp = open(learning_file, 'w')
    for ex in train_examples:
      net_fp.write(ex.DisplayFeatureID())
    net_fp.close()

    # retrain the model
    self.snow_p_.IncremLearn(learning_file)

    try: os.remove(learning_file)
    except: pass
    self.DumpFeatureMap()

    return True

  def Evaluate(self, s_token, t_token):
    """Evaluate a pair of test case.
    Return: a tuple of activated target and activation, in the order as mentioned.
    """
    if not self.snow_p_.IsTrained():
      if DEBUG_: print 'Perceptron not trained'
      return False
    
    test_ex = Example(s_token, t_token)
    for sc in test_ex.GenerateCouplings():
      try: test_ex.AddFeatureID(self.feature_map_.GetFeatureDic()[str(sc)])
      except KeyError: pass
    return self.snow_p_.TestActivation(test_ex.DisplayFeatureID())

  def DumpFeatureMap(self):
    """Dump the entire feature to the current directory. Helper method.
    """
    try:
      self.feature_map_.DumpToFile(self.feature_map_file_)
      return True
    except:
      return False

  def LoadFeatureMap(self, feature_map_file):
    """Load a feature map object from a feature map file. Helper method.
    """
    f_map = {}
    fm_fp = open(feature_map_file, 'r')
    for line in fm_fp.readlines():
      [f, fid] = line.strip().split('\t')
      f_map[f] = int(fid)
    return f_map

  def ShuffleWords(self, positives):
    """Create a list of negative examples by mismatching positive ones. Helper method.
    """
    negatives = []
    ps = WordShuffler(positives)
    for size in range(0,4):
      negatives.extend(ps.CreateShuffledList())
    return negatives

  def ShuffleCharacters(self, positives):
    """Create a list of negative examples by shuffling characters in the second token in each pair.
    """
    negatives = []
    for pair in positives:
      chars = pair[1].split()
      random.shuffle(chars)
      new_str = ' '.join(chars)
      negatives.append((pair[0], new_str))
    return negatives

  def NearestNeighbors(self, positives):
    """Create a list of negative examples by matching token1 in each pair with
    four other token2 strings that have shortest editing distance to the original
    token2. Intensive computation.
    """
    negatives = []
    for pair in positives:
      token2 = pair[1]
      candidates = []
      for tri in self.TrigramSubstr(token2):
        try: candidates.extend(self.token2_tri_index_[tri])
        except: pass

      candidates = set(candidates)
      candidates = list(candidates)

      distances = map(lambda x:
                      (x, Distance(x.split(), token2.split())), candidates)
      distances = sorted(distances, lambda x,y: x[1] - y[1])

      for new_str in distances[1:5]:
        negatives.append((pair[0], new_str[0]))
#        print pair[0] + ' <=> ' + new_str[0] + ' : ' + str(new_str[1])
    return negatives

  def CleanUp(self):
    """Remove generated feature maps and network files (i.e. the current
    trained model) from the current directory.
    """
    if self.snow_p_.IsTrained():
      try:
        os.remove(self.feature_map_file_)
      except: pass
      try:
        self.snow_p_.CleanUp()
      except: pass

  def IsTrained(self):
    """Return True if an instance is trained, false otherwise.
    """
    return self.snow_p_.IsTrained()

class WordShuffler:
  """A helper class for shuffling positive examples between columns. Do not use directly.
  """
  def __init__(self, l):
    self.l_ = l
    self.left_els_ = map(lambda x: x[0], self.l_)

  def CreateShuffledList(self):
    shuffled_list = []
    # for each left element, get a different left element,
    # store the new (element, value) tuple/pair in a new list
    for left_e in self.left_els_:
      ind = self.left_els_.index(left_e)
      alt_ind = self.GetAlternativeInd(ind)
      shuffled_list.append((left_e, self.l_[alt_ind][1]))
    return shuffled_list

  def GetAlternativeInd(self, ind):
    alt_ind = ind
    while alt_ind == ind:
      alt_ind = random.randint(0, len(self.left_els_) - 1)
    return alt_ind

class Example:
  """An example, with a pair of source and target tokens,
  and feature set represented as feature IDs.
  """
  def __init__(self, s_token, t_token):
    """Constructor.
    """
    self.s_token_ = s_token
    self.t_token_ = t_token
    self.feature_id_set_ = set()

  def Display(self):
    """Return a string representation of the example.
    """
    return ((self.s_token_, self.t_token_))

  def DisplayFeatureID(self):
    """Return a string representation of the example in feature IDs,
    also a line of SNoW input.
    """
    return ', '.join([str(f) for f in self.feature_id_set_]) + '\n'
  
  def GetSPron(self):
    return self.s_token_

  def GetTPron(self):
    return self.t_token_

  def AddFeatureID(self, f_id):
    """Add a feature ID to this example.
    """
    self.feature_id_set_.add(f_id)

  def GenerateCouplings(self):
    """Return n-gram couplings for the two tokens in this example.
    """
    s_substrs = self.BigramSubstr(self.s_token_)
    t_substrs = self.BigramSubstr(self.t_token_)
    return self.CoupleSubstrs(s_substrs, t_substrs)
  
  def BigramSubstr(self, str):
    """Return all possible letter bigrams for a string.
    """
    bigram_substrs = []
    if not str.find(' '):
      str = ' '.join(list(str))
    str = "_ " + str + " _"
    chars = str.split()
    for i in range(len(chars)-1):
      bigram_substrs.append(chars[i] + chars[i+1])
    return bigram_substrs

  def CoupleSubstrs(self, substrs1,substrs2):
    """Return a set of coupled bigram strings for the current example.
    """
    # coupling set
    c_set = set()
    for i in range(len(substrs1)):
      if (i - 1) >= 0 and (i - 1) < len(substrs2):
        c_set.add((substrs1[i], substrs2[i - 1]))
      if (i) < len(substrs2):
        c_set.add((substrs1[i], substrs2[i]))
      if (i + 1) < len(substrs2):
        c_set.add((substrs1[i], substrs2[i + 1]))
    return c_set

class TRExample(Example):
  """A training example, extending the class Example, with the addition of
  category labels
  """
  def __init__(self, s_token, t_token, cate):
    Example.__init__(self, s_token, t_token)
    self.cate_ = cate

  def DisplayFeatureID(self):
    """Return a string representation of the current example in feature IDS,
    with the category label as the starting feature.
    """
    return str(self.cate_) + ', ' + \
           ', '.join([str(f) for f in self.feature_id_set_]) + \
           '\n'
