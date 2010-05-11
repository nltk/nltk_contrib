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

"""Token extractor class.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
hollingk@cslu.ogi.edu (Kristy Hollingshead)
"""

import Utils.script
import tokens
from __init__ import BASE_

MIN_LEN_ = 3
SENTENCE_END_ = ['.', ':', '?', '!']

class Extractor:
  """Input is raw UTF-8 text. Output is a sequence of "interesting"
  tokens.
  """
  def __init__(self):
    self.text_ = ''
    self.tokens_ = []

  def InitData(self, args = []):
    self.tokens_ = []
    return
  
  def LineSegment(self, text):
    self.text_ = text
    for word in text.split():
      self.tokens_.append(tokens.Token(word))
    return

  def FileExtract(self, filename):
    fp = open(filename, 'r')
    for line in fp:
      line = line.strip()
      self.LineSegment(line)
    fp.close()
    return self.tokens_

  def Tokens(self):
    return self.tokens_

class NameExtractor(Extractor):
  """Simple extractor based on capitalization (for scripts that
  support this) or any word (for scripts that do not). Also
  discards any words containing digits.
  """

  def LineSegment(self, line):
    ulinelist = []
    ## Go 'word' by word to make this more robust to unicode decode
    ## errors.
    for w in line.split():
      try: ulinelist.append(unicode(w, 'utf-8'))
      except UnicodeDecodeError: pass
    uline = ' '.join(ulinelist)
    clist = []
    for u in uline:
      if Utils.script.IsUnicodePunctuation(u):
        clist.append(' ')
        clist.append(u.encode('utf-8'))
        clist.append(' ')
      else:
        clist.append(u.encode('utf-8'))
    text = ''.join(clist)
    lastw = '.'
    for word in text.split():
      if len(word) < MIN_LEN_:
        continue # ignore word
      ## check for digits, discard word if found
      if Utils.script.HasDigit(word):
        continue
      ## for scripts that support capitalization...
      if Utils.script.SupportsCapitalization(word):
        if lastw in SENTENCE_END_:
          ## ignore sentence-initial capitalization
          pass
        ## check for initial-capitalization,
        ## ignore word if not capitalized
        elif Utils.script.IsCapitalized(word):
          self.tokens_.append(tokens.Token(word))
      else:
        self.tokens_.append(tokens.Token(word))
      lastw = word

