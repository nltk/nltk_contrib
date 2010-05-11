"""English prons for about 600K strings via Festival
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

ENGLISH_ = {}


def LoadEnglishWbTable(table):
  if ENGLISH_: return          ## already loaded
  p = open(table)
  lines = p.readlines()
  p.close()
  for line in lines:
    line = line.split()
    ENGLISH_[line[0]] = ' '.join(line[1:])


def EnglishToWorldBet(string):
  try: return ENGLISH_[string]
  except KeyError: return None


