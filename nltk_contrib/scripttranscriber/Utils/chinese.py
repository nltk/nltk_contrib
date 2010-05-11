"""
Chinese (Mandarin) prons for characters 
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

DUMMY_PHONE_ = 'DUM'

MANDARIN_ = {}

def LoadMandarinWbTable(table):
  if MANDARIN_: return          ## already loaded
  p = open(table)
  lines = p.readlines()
  p.close()
  for line in lines:
    line = line.strip().split('\t')
    try: MANDARIN_[line[0]] = line[1].strip() ## just use first pron
    except IndexError: MANDARIN_[line[0]] = ''

def HanziToWorldBet(string):
  output = []
  some_success = False
  for c in unicode(string, 'utf8'):
    c = c.encode('utf-8')
    try:
      output.append(MANDARIN_[c])
      some_success = True
    except KeyError:
      output.append(DUMMY_PHONE_)
  return ' '.join(output), some_success
