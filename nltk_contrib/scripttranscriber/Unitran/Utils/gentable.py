"""Given a list of the form

1401    Ai
1402    A: i
1403    i
1404    i:
1405    u
1406    u:
1407    o:

where the lefthand column is the Unicode codepoint and the second to
the last column is the WorldBet translation, produce entries for a table of the
form:

TransTable = {
  unicode : [worldbet, utf-8],
  unicode : [worldbet, utf-8],
  unicode : [worldbet, utf-8],
  ...
}

"""

__author__ = "rws@uiuc.edu (Richard Sproat)"

import sys, re

sys.stdout = open('Tables.py', 'w')

print '# coding=utf-8'

print "TransTable = {"

for line in sys.stdin.readlines():
  if not '#' in line:
    line = line.strip().split('\t')
    if len(line[0]) > 1:
      if len(line) == 1: worldbet = '(##)'
      else: worldbet = line[1]
      unistring = "u'\u%s'" % line[0]
      uni = eval(unistring)
      utf8 = uni.encode('utf8')
      print "    %s : ['%s','%s']," % (unistring, worldbet, utf8)
print "    }"
