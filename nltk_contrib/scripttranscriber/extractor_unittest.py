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

"""Unit test for extractor class.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

import sys
import chinese_extractor
import japanese_extractor
from __init__ import BASE_

CHINESE_TESTFILE_ = '%s/testdata/chinese_isi_test.txt' % BASE_
JAPANESE_TESTFILE_ = '%s/testdata/japanese_test.txt' % BASE_
GOLDEN_FILE_ =  '%s/testdata/extractor_test.out' % BASE_ 
GOLDEN_ = []


def LoadGolden():
  p = open(GOLDEN_FILE_)
  lines = p.readlines()
  for line in lines:
    GOLDEN_.append(line.strip())
  p.close()


def main(output = False):
  if output: file = open(GOLDEN_FILE_, 'w')
  else: LoadGolden()
  extractor = chinese_extractor.ChineseExtractor()
  extractor.FileExtract(CHINESE_TESTFILE_)
  pname_extractor = chinese_extractor.ChinesePersonalNameExtractor()
  pname_extractor.FileExtract(CHINESE_TESTFILE_)
  katakana_extractor = japanese_extractor.KatakanaExtractor()
  katakana_extractor.FileExtract(JAPANESE_TESTFILE_)
  if output:
    for t in extractor.Tokens():
      file.write('%s\n' % t.String())
    for t in pname_extractor.Tokens():
      file.write('%s\n' % t.String())
    for t in katakana_extractor.Tokens():
      file.write('%s\n' % t.String())
    file.close()
  else:
    all_tokens = (extractor.Tokens() + 
                  pname_extractor.Tokens() +
                  katakana_extractor.Tokens())
    assert len(all_tokens) == len(GOLDEN_), \
        'Extracted different numbers of tokens'
    for i in range(len(GOLDEN_)):
      assert all_tokens[i].String() == GOLDEN_[i], \
          'Token %d differs: %s != %s' %  (i,
                                           all_tokens[i].String(),
                                           GOLDEN_[i])
    print '%s successful' % sys.argv[0]


if __name__ == '__main__':
  if len(sys.argv) > 1 and sys.argv[1] == 'generate':
    main(True)
  else:
    main()
