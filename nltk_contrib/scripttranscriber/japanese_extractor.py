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

"""Japanese katakana extractor
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

import extractor
import tokens
import chinese_extractor
import Utils.script
from __init__ import BASE_


class KatakanaExtractor(chinese_extractor.EastAsianExtractor):
  """Katataka sequence extractor
  """

  def LineSegment(self, line):
    try: utext = unicode(line.strip(), 'utf-8')
    except TypeError: utext = line.strip()
    word = []
    for u in utext:
      if Utils.script.CharacterToScript(u) == 'Katakana':
        word.append(u.encode('utf-8'))
      else:
        if word and word != ['・']:
          self.tokens_.append(tokens.Token(''.join(word)))
          word = []

