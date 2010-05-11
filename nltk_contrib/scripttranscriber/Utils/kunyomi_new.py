"""
Native Japanese pronunciations for characters based on Kunyomi
pronunciations from Wiktionary. These include guesses on application
of rendaku.
"""
__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

KUNYOMI_ = {}
RENDAKU_ = {}


def RendakuWorldBet(worldbet):
  """If the romaji is marked with '*' the form may undergo rendaku
  """
  worldbet = worldbet.split()
  if worldbet[0] == 'h': return 'b ' + ' '.join(worldbet[1:])
  if worldbet[0] == 't': return 'd ' + ' '.join(worldbet[1:])
  if worldbet[0] == 'k': return 'g ' + ' '.join(worldbet[1:])
  if worldbet[0] == 's': return 'z ' + ' '.join(worldbet[1:])
  if worldbet[0] == 'ts': return 'z ' + ' '.join(worldbet[1:])
  if worldbet[0] == 'S': return 'j ' + ' '.join(worldbet[1:])
  return ' '.join(worldbet)


def LoadKunyomiWbTable(table):
  if KUNYOMI_: return          ## already loaded
  p = open(table)
  lines = p.readlines()
  p.close()
  for line in lines:
    line = line.strip().split('\t')
    romaji = line[2].strip()
    pron = line[3].strip()
    KUNYOMI_[line[0]] = pron
    if romaji[0] == '*': RENDAKU_[line[0]] = True


def KanjiToWorldBet(string):
  output = []
  some_success = False
  internal = False
  for c in unicode(string, 'utf8'):
    c = c.encode('utf-8')
    try:
      pron = KUNYOMI_[c]
      if internal and c in RENDAKU_:
        pron = RendakuWorldBet(pron)
      output.append(pron)
      some_success = True
    except KeyError:
      output.append(c)
    internal = True
  return ' '.join(output), some_success
