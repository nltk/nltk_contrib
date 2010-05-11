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

"""Definition of a morph analyzer. Defines one base classe:

MorphAnalyzer: class of methods to preprocess a doclist
to produce data for morphological analysis, and populate the morph
fields of the tokens
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

import Utils.script

DEFAULT_SUBSTRING_LENGTH_ = 5

class MorphAnalyzer:
  """Preprocesses the entire doclist to produce data to use in
  morphological analysis. In general, since morphological analysis may
  depend upon context, or else
  """
  def __init__(self, doclist, lang):
    self.doclist_ = doclist
    self.mapping_table_ = {}
    self.lang_ = lang
    self.initialized_ = False

  def ProcessDoclist(self):
    pass

  def LabelDoclist(self):
    pass

  def Morphs(self, string):
    return ''

class PrefixAnalyzer(MorphAnalyzer):
  """Follow Alex Klementiev's approach and cluster words together that
  share a prefix of 5 or more letters.

  TODO(rws): fix the substring match so it's right
  """

  def Initialize(self, type='prefix'):
    try: self.substring_length_ == DEFAULT_SUBSTRING_LENGTH_
    except AttributeError: self.substring_length_ = DEFAULT_SUBSTRING_LENGTH_
    vocab = {}
    self.morphs_ = {}
    for doc in self.doclist_.Docs():
      for lang in doc.Langs():
        if lang.Id() == self.lang_:
          for token in lang.Tokens():
            str = token.String()
            for k in range(self.substring_length_, len(str) + 1):
              if type == 'prefix': sub = str[:k]
              else: sub = str[-k:]
              sub = Utils.script.Lower(sub)
              try: 
                if str not in vocab[sub]:
                  vocab[sub].append(str)
              except KeyError:
                vocab[sub] = [str]
    for sub in vocab:
      if len(vocab[sub]) > 1: ## otherwise not interesting
        for str in vocab[sub]:
          try:
            if len(self.morphs_[str]) < len(sub):
              self.morphs_[str] = sub
          except KeyError:
            self.morphs_[str] = sub
    self.initialized_ = True

  def SetSubstringLength(self, length=DEFAULT_SUBSTRING_LENGTH_):
    self.substring_length_ = length
  
  def Morphs(self, string):
    try: return self.morphs_[string]
    except AttributeError, KeyError: return ''

  def LabelDoclist(self):
    assert self.initialized_ == True, 'Must Initialize() the analyzer!'
    for doc in self.doclist_.Docs():
      for lang in doc.Langs():
        if lang.Id() == self.lang_:
          for token in lang.Tokens():
            try:
              morph = self.morphs_[token.String()]
              token.SetMorphs([morph])
            except KeyError:
              pass
