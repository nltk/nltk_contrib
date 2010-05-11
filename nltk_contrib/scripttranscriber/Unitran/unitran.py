"""UTF-8 to WorldBet/XSampa decoder

The main complexity here involves Indic systems, which have inherent
vowels and (many of which have) two-part vowels.

Indic systems are handled by globals IndicCon, IndicVowel,
IndicComp. If a sequence is a combination of a consonant and a vowel,
the inherent vowel is removed from the preceding consonant. If a
sequence is two compound-vowel portions, these are combined.

Virama (cancellation sign) is handled in a similar way: it cancels out
the inherent vowel, but in this case it deletes itself
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
kkim36@uiuc.edu (Kyoung-young Kim)
"""

import sys
import getopt
import Tables
import X_Tables
import thaifix

JOINER_ = ''
TransTable = {}
VIRAMA_ = '(P)'


def UpdateTransTable(table):
  """Update local module's TransTable with data from table.
  """
  for k in table: TransTable[k] = table[k]


def IndicCV(file):
  """Load Indic-specific CV data
  """
  Indic = []
  p = open(file)
  for line in p.readlines():
    line = line.split('\n')
    unis = "u'\u%s'"%line[0]
    uni = eval(unis)
    Indic.append(uni)
  return Indic


def IndicTwoPartVowels(file):
  """Load Indic-specific two-part vowel data
  """
  vowels = []
  p = open(file)
  for line in p.readlines():
    line = line.split('\t')
    prev = "u'\u%s'"%line[0]
    cur = "u'\u%s'"%line[1]
    comp = "u'\u%s'"%line[2].strip('\n')
    pre = eval(prev)
    curr = eval(cur)
    comps = eval(comp)
    vowel = [pre, curr, comps]
    vowels.append(vowel)
  return vowels
    

def RemoveSpacesFromDescriptor(token):
  """Remove JOINER_ from the likes of "(POETIC VERSE SIGN)"
  """
  if not token: return token
  if token[0] == '(' and token[-1] == ')':
    token = token.replace(JOINER_, '_')
  return token


def ProcToken (token):
  """Process individual text token, however defined, converting
  from utf-8 to phonetic encoding.
  """
  new = ''
  prev = None
  token = thaifix.ThaiFix(token)
  try: utoken = unicode(token.strip() + ' ', 'utf8')
  except UnicodeDecodeError: return token
  for c in utoken:
    if prev:
      bigram = prev + c
      if c in IndicVowel and prev in IndicCon:
        try:
          T = TransTable[prev][0].split(',')
          ntoken = JOINER_.join(T[0].strip('A').strip('>').split())
          ntoken = RemoveSpacesFromDescriptor(ntoken)
          new = new + JOINER_ + ntoken
        except KeyError:
          new = new + JOINER_ + prev.encode('utf-8')
      else:
        ## TODO: fix this sequential search with something more
        ## efficient:
        for i in range(len(IndicComp)):
          if bigram == IndicComp[i][0]+IndicComp[i][1]:
            prev = IndicComp[i][2]
            c = None
        try:
          T = TransTable[prev][0].split(',')
          ntoken = JOINER_.join(T[0].split())
          ntoken = RemoveSpacesFromDescriptor(ntoken)
          if ntoken != VIRAMA_:
            new = new + JOINER_ + ntoken
        except KeyError:
          new = new + JOINER_ + prev.encode('utf-8')
    prev = c
  return new


def TransFile (infile=None,outfile=None):
  """Top-level function to translate utf-8 file into phonetic transcription
  """
  if infile == None: instream = sys.stdin
  else: instream = open(infile)
  if outfile == None: outstream = sys.stdout
  else: outstream = open(outfile,'w')
  for line in instream.readlines(): outstream.write(ProcToken(line) + '\n')
  instream.close()
  outstream.close()


def Usage(argv):
  sys.stderr.write('Usage: %s [-x/--x-sampa] (files)\n' % argv[0])


def main(argv):
  global IndicCon, IndicVowel, IndicComp
  global JOINER_
  xsampa = False
  try:
    opts, args = getopt.getopt(argv[1:], "xj:", ["x-sampa", "joiner="])
  except getopt.GetoptError:
    Usage(argv)
    sys.exit(2)
  for opt, arg in opts:
    if opt in ("-x", "--x-sampa"):
      xsampa = True
    elif opt in ("-j", "--joiner"):
      JOINER_ = arg
  if xsampa:
    UpdateTransTable(X_Tables.TransTable)
  else:
    UpdateTransTable(Tables.TransTable)
  IndicCon= IndicCV('IndicCon.txt')
  IndicVowel = IndicCV('IndicVowel.txt')
  IndicComp = IndicTwoPartVowels('IndicTwoPartVowel.txt')
  if len(args) > 0:
    for file in args:
      TransFile(file, file + '.out')
  else:
    TransFile()


if __name__ == '__main__':
    main(sys.argv)
