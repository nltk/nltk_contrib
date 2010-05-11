# -*- coding: utf-8 -*-

"""Loads Tables.py and produces X_Tables.py, mapping to XSampa rather
than WorldBet.

X_Tables.py.unc will contain unconverted symbols
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

import sys
sys.path.append('../')
import Tables
import Wb2Xs


def Main():
  newTable = {}
  unconverted = {}
  for u in Tables.TransTable:
    wbstring, utf = Tables.TransTable[u]
    wbs = wbstring.split()
    xslist = []
    for wb in wbs:
      try:
        xs = Wb2Xs.WorldBetToXSampa[wb]
      except KeyError:
        xs = wb
        unconverted[xs] = True
      xslist.append(xs)
    newTable[u] = [' '.join(xslist), utf]
  p = open('X_Tables.py', 'w')
  p.write('# coding=utf-8\n')
  p.write('TransTable = {\n')
  keys = newTable.keys()
  keys.sort()
  for u in keys:
    xstring, utf = newTable[u]
    p.write("    %s : ['%s', '%s'],\n" % (repr(u), xstring, utf))
  p.write('}\n')
  p.close()
  p = open('X_Tables.py.unc', 'w')
  for xs in unconverted:
    p.write('%s\n' % xs)
  p.close()


if __name__ == '__main__':
  Main()


