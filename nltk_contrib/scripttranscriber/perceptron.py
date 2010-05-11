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

"""Definition for a SNoW-based peceptron model.
"""

__author__ = """
ting.qian@rochester.edu (Ting Qian)
"""
import os
import shutil
import snow
import random
import copy

class Perceptron:
  """A Perceptron model
  """  
  def __init__(self, network_file=None):
    """Constructor, with an optional parameter accepting the name of a network file.
    If the network file exists, a trained perceptron will be constructed,
    and is available for testing. If the file does not exist, network file generated
    during training will be written to its content.
    """
    if network_file is not None:
      self.network_file_ = network_file
      if os.path.exists(network_file):
        self.isTrained_ = True
      else:
        self.isTrained_ = False
    else:
      self.isTrained_ = False
      self.network_file_ = 'perceptron.net'

    self.cut_off_value_ = 2
    self.iteration_ = 2
    self.snow_session_ = None
    self.snow_session_retrained_ = False

  def TrainFromFile(self, train_file):
    """Train a perceptron model given input from the file "train_file", which
    should consist of examples formatted as SNoW input (e.g. 1, 232, 421, 121).
    Return True if the model is successfully trained.
    """
    # using PySnow to train the model
    snow_training_args = {'I':train_file,\
                          'F':self.network_file_,\
                          'P':':0,1',\
                          'r':str(self.iteration_),\
                          'e':'count:' + str(self.cut_off_value_),\
                          'g':'-', \
                          'v':'off'
                          }
    snow.train(snow_training_args)

    # flag the perceptron as trained
    self.isTrained_ = True
    return True

  def IncremLearn(self, increm_file):
    """Learn from additional examples, formatted as SNoW input.
    Return True if the model successfully learns new features.
    """
    # using PySnow to test the file with 'i +' argument
    # for incremental learning
    snow_learning_args = {'I': increm_file, \
                          'F': self.network_file_, \
                          'i': '+', \
                          'o': 'accuracy', \
                          'v': 'off'
                          }
    snow.test(snow_learning_args)
    shutil.move(self.network_file_ + '.new', self.network_file_)

    self.snow_session_retrained_ = True

    return True

  def TestActivation(self, example):
    """Test a given example formatted as SNoW input.
    Return a tuple of activated target and activation, in the order as mentioned.
    """
    # snow testing arguments
    snow_test_args = {'F': self.network_file_,\
                      'o': "allactivations",\
                      'v': "off",
                      'P': ":0-1"
                      }

    if self.snow_session_ is None:
      self.snow_session_ = snow.SnowSession(snow.MODE_SERVER, snow_test_args)
      result = self.snow_session_.evaluateExample(example)
    else:
      if self.snow_session_retrained_:
        tmp_session = snow.SnowSession(snow.MODE_SERVER, snow_test_args)
        result = tmp_session.evaluateExample(example)
        self.snow_session_ = tmp_session
        self.snow_session_retrained_ = False
      else:
        result = self.snow_session_.evaluateExample(example)
 
    try: [target, a, b, activation] = result.split('\n')[1].split()
    except IndexError: return (0, 0)

    # ad-hoc case:
    if activation[-1] == '*':
      activation = activation[:-1]

    return (int(target[0]), float(activation))

  def IsTrained(self):
    """Return whether a model is trained or not.
    """
    return self.isTrained_

  def CleanUp(self):
    """Remove network files of the current trained model.
    """
    if self.isTrained_:
      del self.snow_session_
      os.remove(self.network_file_)
      self.isTrained_ = False

class FeatureMap:
  """A feature definition class, implemented as a hash (dictionary).
  Note: for maximum compatibility, please convert all feature contents (as opposed to feature IDs)
  to strings before hashing.
  """
  def __init__(self, feature_map=None):
    """Constructor, with an optional parameter to load an existing feature map.
    """
    # feature_dic contains a hashtable with features as keys
    # feature ids as values
    if feature_map is None:
      self.feature_dic_ = {}
      self.cur_id_ = 10
    else:
      self.feature_dic_ = feature_map
      self.cur_id_ = max(self.feature_dic_.values())

  def AddFeature(self, feature):
    """Add a new feature to the map.
    Return the newly assigned ID of that feature; if the given feature exists,
    return the currently assigned ID.
    """
    if feature not in self.feature_dic_:
      self.cur_id_ += 1
      self.feature_dic_[feature] = self.cur_id_
      return self.cur_id_
    else:
      return self.feature_dic_[feature]

  def GetFeatureDic(self):
    """Return a copy of the hash/dictionary held by a FeatureMap object.
    """
    return self.feature_dic_

  def DumpToFile(self, feature_map_file):
    """Dump the entire feature map to a file whose name is given as the parameter.
    """
    fm_fp = open(feature_map_file, 'w')
    for k, v in self.feature_dic_.iteritems():
      fm_fp.write(k + '\t' + str(v) + '\n')
    fm_fp.close()
    return True
  
