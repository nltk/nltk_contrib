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

"""Unit test for pronouncer class.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

import sys
import tokens
import pronouncer
from __init__ import BASE_

WORDS_ =  [ '﻿ᓵᓕ ᓴᕕᐊᕐᔪ',
            'հայտնում',
            'совместно',
            'πρεσβυτερων',
            ' נצטר',
            'สิริ',
            '曼德尔森',
            '高島屋',
            '동지사',
            'うずまき',
            'ᎠᏓᏔᏍᏘ',
            'cheese',
            'CHEESE',
            'loogoowoogoo',
            'ἄτομος',
            'ადიშის',
            'आदिवासी',
            'ਪੰਜਾਬ',
            'ذِھِنُ',
            'અનુપ',
            'தினபூமி',
            'பரமேஸ்வரன்', ## example involving virama (pulli)
             ]

GOLDEN_FILE_ = '%s/testdata/pronounce_golden.txt' % BASE_
GOLDEN_ = {}


def LoadGolden():
  p = open(GOLDEN_FILE_)
  for line in p:
    line = line.strip()
    word, pron = line.split('\t')
    try: word = unicode(word, 'utf-8')
    except TypeError: pass
    try: pron = unicode(pron, 'utf-8')
    except TypeError: pass
    try:
      GOLDEN_[word].AddPronunciation(pron)
    except KeyError:
      GOLDEN_[word] = tokens.Token(word)
      GOLDEN_[word].AddPronunciation(pron)
  p.close()


def main(output = False):
  if output: file = open(GOLDEN_FILE_, 'w')
  else: LoadGolden()
  for w in WORDS_:
    try: w = unicode(w.strip(), 'utf-8')
    except TypeError: pass
    token_ = tokens.Token(w)
    pronouncer_ = pronouncer.UnitranPronouncer(token_)
    pronouncer_.Pronounce()
    pronouncer_ = pronouncer.HanziPronouncer(token_)
    pronouncer_.Pronounce()
    pronouncer_ = pronouncer.EnglishPronouncer(token_)
    pronouncer_.Pronounce()
    pronouncer_ = pronouncer.LatinPronouncer(token_)
    pronouncer_.Pronounce()
    if output:
      for p in pronouncer_.Token().Pronunciations():
        file.write('%s\t%s\n' % (pronouncer_.Token().String(), p))
    else:
      try:
        string = unicode(pronouncer_.Token().String(), 'utf-8')
      except TypeError:
        string = pronouncer_.Token().String()
      assert string in GOLDEN_, \
          "Can't find string %s in gold standard" % \
            string.encode('utf-8')
      nprons = pronouncer_.Token().Pronunciations()
      gprons = GOLDEN_[string].Pronunciations()
      assert len(nprons) == len(gprons), \
          '# of prons in gold standard differs for %s' % \
            string.encode('utf-8')
      for i in range(len(nprons)):
        assert nprons[i] == gprons[i], \
            'pron %d differs for %s (%s->%s)' % (i,
                                                 string.encode('utf-8'),
                                                 nprons[i],
                                                 gprons[i])
  if output:
    print 'generated %s' % GOLDEN_FILE_
    file.close()
  else:
    print '%s successful' % sys.argv[0]


if __name__ == '__main__':
  if len(sys.argv) > 1 and sys.argv[1] == 'generate':
    main(True)
  else:
    main()
