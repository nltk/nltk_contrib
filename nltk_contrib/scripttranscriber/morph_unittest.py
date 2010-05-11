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

"""Unit test for morph.py
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

import os
import sys
import xml.sax
import unittest
import tokens
import xmlhandler
import morph
from __init__ import BASE_

SOURCE_FILE_ =  '%s/testdata/morphtest_src.xml' % BASE_ 
GOLDEN_FILE_ =  '%s/testdata/morphtest.xml' % BASE_ 
TEST_FILE_ = '/tmp/morphtest.xml'

def main(output = False):
  parser = xml.sax.make_parser()
  handler = xmlhandler.XmlHandler()
  parser.setContentHandler(handler)
  parser.parse(SOURCE_FILE_)
  doclist = handler.DocList()
  analyzer = morph.PrefixAnalyzer(doclist, 'eng')
  analyzer.Initialize()
  analyzer.LabelDoclist()
  if output:
    doclist.XmlDump(GOLDEN_FILE_, utf8=True)
  else:
    doclist.XmlDump(TEST_FILE_)
    unittest.TestUnitOutputs(sys.argv[0], GOLDEN_FILE_, TEST_FILE_)

if __name__ == '__main__':
  if len(sys.argv) > 1 and sys.argv[1] == 'generate':
    main(True)
  else:
    main()

