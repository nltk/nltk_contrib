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

"""Uses the FST library to construct FSTs of two phone-strings
and align them using the provided cost-matrix.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
hollingk@cslu.ogi.edu (Kristy Hollingshead)
"""

import sys
import os
import getopt
import tempfile

UNK_ = '<unk>'
EPSILON_ = '<eps>'
SHORT_EPS_ = '-'
INF_ = 1e10

def MyOpen(*args):
  f = open(*args)
  return f

def MyTemporaryFile(sfx):
  fd, name = tempfile.mkstemp(suffix=sfx)
  os.close(fd)
  return name

def ReadSymbols(symbolfile):
  symbols = []
  symbolFP = MyOpen(symbolfile, 'r')
  for line in symbolFP:
    line = line.strip()
    for s in line.split():
      if s not in symbols: symbols.append(s)
  symbolFP.close()
  return symbols

def ReadCostMatrix(matfile, symbols):
  rows = []
  cols = []
  matrix = {}
  if matfile is None: matfp = sys.stdin
  else: matfp = MyOpen(matfile, 'r')
  if len(symbols) == 0: genSymbols = True
  else: genSymbols = False
  # read column labels off first line
  line = matfp.readline()
  line = line.strip()
  cols = line.split()
  if genSymbols:
    for c in cols:
      symbols.append(c)
  for line in matfp:
    line = line.strip()
    row_label, costs = line.split(None,1)
    if genSymbols: symbols.append(row_label)
    if row_label not in symbols:
      print "Error: label (%s) not in defined symbols list" % row_label
      sys.exit(1)
    rows.append(row_label)
    costs = costs.split()
    if len(costs) != len(cols):
      print 'Error: wrong number of costs on line %s' % line
      sys.exit(1)
    for c in range(len(costs)):
      if costs[c] in ('inf', 'Inf', 'INF'): costs[c] = INF_
      matrix[(row_label, cols[c])] = float(costs[c])
  symbols = set(symbols)
  if matfile is not None: matfp.close()
  return matrix, rows, cols, symbols

def PrintFSTSymbols(symbols, symfile=None):
  symbols = set(symbols) # no duplicates
  if symfile is None:
    symfile = MyTemporaryFile('.sym.txt.fst')
  fp = MyOpen(symfile, 'w')
  fp.write('%s\t0\n' % (EPSILON_))
  fp.write('%s\t1\n' % (UNK_))
  id = 2
  for s in symbols:
    if s == EPSILON_ or s == UNK_: continue
    fp.write(s+'\t'+str(id)+'\n')
    id += 1
  fp.close()
  return symfile

def PrintChainFST(inputstr, symbols=[], txtfst=None):
  # inputstr is space-delimited string of characters
  if txtfst is None:
    txtfst = MyTemporaryFile('.chain.txt.fst')
  fstfp = MyOpen(txtfst, 'w')
  if len(symbols) == 0: genSymbols = True
  else: genSymbols = False
  # simple chain fst
  start = 0
  next = start+1
  curr = start
  for p in inputstr.split():
    if genSymbols: symbols.append(p)
    if p not in symbols: p = UNK_
    fstfp.write('%d\t%d\t%s\t%s\n' % (curr, next, p, p))
    curr = next
    next += 1
  fstfp.write('%d\n' % curr) # final state
  fstfp.close()
  symbols = set(symbols)
  return (txtfst, symbols)

def PrintDaisyFST(matrix, rows, cols, symbols=[], txtfst=None):
  if len(symbols) == 0: genSymbols = True
  else: genSymbols = False
  if txtfst is None:
    txtfst = MyTemporaryFile('.daisy.txt.fst')
  fstfp = MyOpen(txtfst, 'w')
  for x in rows:
    if genSymbols: symbols.append(x)
    if x not in symbols: x = UNK_
    for y in cols:
      if genSymbols: symbols.append(y)
      if y not in symbols: y = UNK_
      fstfp.write("0\t0\t"+x+'\t'+y+'\t'+\
                  str(matrix[(x,y)])+'\n')
  fstfp.write("0\n")
  fstfp.close()
  symbols = set(symbols)
  return (txtfst, symbols)

def PrintExtDaisyFST(matrix, rows, cols, symbols=[], txtfst=None):
  global SONORANTS_
  SONORANTS_ = ReadSymbols("sonorants.arpabet.txt")
  if len(symbols) == 0: genSymbols = True
  else: genSymbols = False
  if txtfst is None:
    txtfst = MyTemporaryFile('.extdaisy.txt.fst')
  fstfp = MyOpen(txtfst, 'w')
  # simple daisy fst + init cost
  for x in rows:
    if genSymbols: symbols.append(x)
    if x not in symbols: x = UNK_
    for y in cols:
      if genSymbols: symbols.append(y)
      if y not in symbols: y = UNK_
      # init cost (double cost)
      fstfp.write('0\t1\t'+x+'\t'+y+'\t'+ \
                  str(2*matrix[(x,y)])+'\n')
      # simple daisy fst
      fstfp.write('1\t1\t'+x+'\t'+y+'\t'+ \
                  str(matrix[(x,y)])+'\n')
      # exception for word-final sonorants
      if x in SONORANTS_ or y in SONORANTS_:
        fstfp.write('1\t2\t'+x+'\t'+y+'\t0\n') # for free
      else:
        fstfp.write('1\t2\t'+x+'\t'+y+'\t'+ \
                    str(matrix[(x,y)])+'\n')
    fstfp.write('1\n')
    fstfp.write('2\n')
  fstfp.close()
  symbols = set(symbols)
  return (txtfst, symbols)

def CompileFST(txtfstfile, symbols):
  # by default, will delete txtfstfile and symfile
  symfile = PrintFSTSymbols(symbols)
  binfstfile = MyTemporaryFile('.bin.fst')
  fstcompile = 'fstcompile --isymbols=%s --osymbols=%s \
                --keep_isymbols --keep_osymbols %s > %s' % \
                (symfile, symfile, txtfstfile, binfstfile)
  ret = os.system(fstcompile)
  if ret != 0:
    sys.stderr.write('Error in fstcompile\'ing\n')
    sys.exit(2)
  ret = os.system('rm -f %s %s' % (symfile, txtfstfile))
  if ret != 0:
    sys.stderr.write('Error in rm\'ing txt.fst\n')
    sys.exit(2)
  return binfstfile

def AlignFSTs(fst1, fst2, costfst, symbols):
  symfile = PrintFSTSymbols(symbols)
  alnfile = MyTemporaryFile('.aln.fst')
  fstcompose = 'fstcompose %s %s | fstinvert | fstarcsort | \
    fstcompose %s - >  %s' % (fst2, costfst, fst1, alnfile)
  ret = os.system(fstcompose)
  if ret != 0:
    sys.stderr.write('Error in fstcompose\'ing\n')
    sys.exit(2)
  fstbest = 'fstshortestpath %s | fsttopsort | fstprint' % (alnfile)
  fin, fout = os.popen2(fstbest)
  fin.close()
  alnmat = fout.read()
  fout.close()
  #sys.stderr.write('alnmatrix: '+alnmat+'\n')
  ret = os.system('rm -f %s %s %s %s' % (fst1, fst2, symfile, alnfile))
  if ret != 0:
    sys.stderr.write('Error in rm\'ing alignment files\n')
    sys.exit(2)
  aln1 = []
  aln2 = []
  cost = 0.0
  for line in alnmat.split('\n'):
    line = line.strip()
    cols = line.split('\t')
    if len(cols) == 1: break
    aln1.append(cols[2])
    aln2.append(cols[3])
    try: cost += float(cols[4])
    except IndexError:
      # sys.stderr.write('zero cost\n')
      cost += 0.0
    except ValueError:
      sys.stderr.write('Error: non-float cost\n')
  return ' '.join(aln1), ' '.join(aln2), cost

def main(matrixfile, symfile=None, infile=None):
  if symfile is not None:
    syms = ReadSymbols(symfile)
  else: syms = []
  inputmatrix, row_heads, col_heads, syms = \
    ReadCostMatrix(matrixfile, syms)
  txtmatrix, syms = \
    PrintDaisyFST(inputmatrix, row_heads, col_heads, syms)
    # or:
    # PrintExtDaisyFST(inputmatrix, row_heads, col_heads, syms)
  binmatrix = CompileFST(txtmatrix, syms)
  if infile is not None: infp = MyOpen(infile, 'r')
  else: infp = sys.stdin
  for line in infp:
    line = line.strip()
    ph1, ph2 = line.split('\t')
    txtph1, syms = PrintChainFST(ph1, syms)
    binph1 = CompileFST(txtph1, syms)
    txtph2, syms = PrintChainFST(ph2, syms)
    binph2 = CompileFST(txtph2, syms)
    aln1, aln2, cost = AlignFSTs(binph1, binph2, binmatrix, syms)
    #aln1 = aln1.replace(EPSILON_, SHORT_EPS_)
    #aln2 = aln2.replace(EPSILON_, SHORT_EPS_)
    print '%s\t%s\t%.6f' % (aln1, aln2, cost)
  ret = os.system('rm -f %s' % (binmatrix))
  if ret != 0:
    sys.stderr.write('Error in rm\'ing matrix\n')
    sys.exit(2)
  if infile is not None: infp.close()

def usage(called):
  print '%s -m <matrix-file> [-s <symbols-file>]' % (called),
  print '[-i <phone-pairs-file>]'

if __name__ == '__main__':
  try:
    opts, args = \
      getopt.getopt(sys.argv[1:], '?m:s:i:', \
      ['help', 'matrix', 'symbols', 'input'])
  except getopt.GetoptError:
    # print help information and exit:
    usage(argv[0])
    sys.exit(2)
  matfile = None
  symfile = None
  infile = None
  for op, a in opts:
    if op in ('-?', '--help'):
      usage(sys.argv[0])
      sys.exit()
    if op in ('-m', '--matrix'):
      matfile = a
    if op in ('-s', '--symbols'):
      symfile = a
    if op in ('-i', '--input'):
      infile = a
  if matfile is None:
    usage(sys.argv[0])
    print "Error: must provide a cost-matrix file."
    sys.exit(2)
  main(matfile, symfile, infile)
