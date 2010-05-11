"""Simple table-lookup for pronunciation of extended latin strings.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

## Extended Latin

LATIN_ = {}
DUMMY_PHONE_ = 'DUM'

def LoadLatinWbTable(table):
  p = open(table)
  lines = p.readlines()
  p.close()
  for line in lines:
    line = line.split()
    LATIN_[line[0]] = ' '.join(line[1:])

def LatinToWorldBet(string):
  output = []
  some_success = False
  for c in unicode(string, 'utf8'):
    c = c.encode('utf-8')
    try:
      output.append(LATIN_[c])
      some_success = True
    except KeyError:
      if c.isdigit():
        output.append(DUMMY_PHONE_)
      else:
        output.append(c)
  return ' '.join(output), some_success


