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

"""Unit test for letter-based perceptron models for parallel dictionaries
"""

__author__ = """
ting.qian@rochester.edu (Ting Qian)
"""

import perceptron_trainer
import os

def GetDictionary():
  training_dict = []

  # read a parallel dictionary into a hash structure
  dict_fp = open("testdata/perceptron.ce.dict.training", "r")
  for line in dict_fp.readlines():
    item = line.strip().split('\t')
    training_dict.append((item[0], item[1]))
  return training_dict

def EvaluateExamples(pt):
  return \
         str(pt.Evaluate("on > r m &", "n u &r m a")) + \
         str(pt.Evaluate("t I k h & n & v I tS", "cC i x a n w o w e i cCh i")) + \
         str(pt.Evaluate("t I k h & n & v I tS", "n u &r m a"))

def main():
  dict = GetDictionary()
  perceptron_trainer.DEBUG_ = True
  # initialize a new perceptron
  pt = perceptron_trainer.ParallelTrainer('2.fm', '2.net')
  
  # train the perceptron
  pt.Train(dict[0:1000])
  first_run = EvaluateExamples(pt)
  print first_run

  # results here should be the same
  second_run = EvaluateExamples(pt)
  print second_run
  
  # learn from new examples
  # produce new results
  pt.Retrain(dict[1001:3000])
  third_run = EvaluateExamples(pt)
  print third_run

  # this result should be the same as the third run
  fourth_run = EvaluateExamples(pt)
  print fourth_run

  # test
  if first_run == second_run and first_run != third_run \
         and third_run == fourth_run:
    print 'unittest successful'
  else:
    print 'unsuccessful'

  # clean up
  pt.CleanUp()

if __name__ == '__main__':
  main()
