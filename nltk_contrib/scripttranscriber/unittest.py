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

"""Generic unit-test functions.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
hollingk@cslu.ogi.edu (Kristy Hollingshead)
"""

import os
import sys

def CompareOutputFiles(gold_file, test_file):
  p = open(gold_file, 'r')
  glines = p.readlines()
  p.close()
  p = open(test_file, 'r')
  tlines = p.readlines()
  p.close()
  assert len(glines) == len(tlines), \
      'Test and gold differ, investigate with "diff %s %s"' % \
      (gold_file, test_file)
  for i in range(len(tlines)):
    assert glines[i] == tlines[i], \
        'Test and gold differ, investigate with "diff %s %s"' % \
        (gold_file, test_file)
  os.system('rm -f %s' % test_file)

def TestUnitOutputs(unitname, gold_file, test_file):
  CompareOutputFiles(gold_file, test_file)
  print '%s successful' % unitname
