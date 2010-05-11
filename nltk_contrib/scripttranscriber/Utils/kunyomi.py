"""
Native Japanese pronunciations for characters
"""
__author__ = """
rws@uiuc.edu (Richard Sproat)
kkim36@uiuc.edu (Kyoung-young Kim)
"""

DUMMY_PHONE_ = 'DUM'

KUNYOMI_ = {}

def LoadKunyomiWbTable(table):
  if KUNYOMI_: return          ## already loaded
  p = open(table)
  lines = p.readlines()
  p.close()
  for line in lines:
    line = line.split()
    KUNYOMI_[line[0]] = ' '.join(line[1:])


def KanjiToWorldBet(string):
  output = []
  some_success = False
  for c in unicode(string, 'utf8'):
    c = c.encode('utf-8')
    try:
      output.append(KUNYOMI_[c])
      some_success = True
    except KeyError:
      output.append(DUMMY_PHONE_)
  return ' '.join(output), some_success

