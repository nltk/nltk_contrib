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

"""Class definition for filters for reducing the set of terms to be
considered in a doclist.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

import tokens
import xmlhandler
from __init__ import BASE_

MIN_COUNT_ = 3
 
class Filter:
  """Base class for filters that take in a document list and return a
  list with some terms removed.
  """
  def __init__(self, doclist):
    self.doclist_ = doclist

  def InitData(self, args = []):
    return
  
  def Filter(self):
    return

  def Doclist(self):
    return self.doclist_

class FrequencyFilter(Filter):
  """Simple filter based on a minimum frequency count for a term.
  """
  
  def SetMinCount(self, min_count):
    self.min_count_ = min_count

  def Filter(self):
    try:
      self.min_count_
    except AttributeError:
      self.min_count_ = MIN_COUNT_
    counts = {}
    for doc in self.doclist_.Docs():
      for lang in doc.Langs():
        for token_ in lang.Tokens():
          hash_string = token_.EncodeForHash()
          try:
            counts[hash_string] += token_.Count()
          except KeyError:
            counts[hash_string] = token_.Count()
    for key in counts:
      if counts[key] < self.min_count_: counts[key] = None
    for doc in self.doclist_.Docs():
      for lang in doc.Langs():
        ntokens = []
        for token_ in lang.Tokens():
          hash_string = token_.EncodeForHash()
          if counts[hash_string]: ntokens.append(token_)
        lang.SetTokens(ntokens)
