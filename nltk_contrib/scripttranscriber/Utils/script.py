"""Script classifier, based on
/usr/share/perl/5.8.8/unicore/Blocks.txt

and generally useful script utilities.
"""

__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

import unicodedata

UNKNOWN_SCRIPT_ = 'UNKNOWN_SCRIPT_'

SCRIPTS_WITH_CAPITALIZATION_ = [ 'Latin', 'Greek', 'Cyrillic',
                                 'Armenian' ]

def CharacterToScript(u):
  """ Return the script of a unicode codepoint, only considering those
  codepoints that correspond to characters of a script.
  """
  if u >= u'\u0000' and u <= u'\u007F': return 'Latin'
  elif u >= u'\u0080' and u <= u'\u00FF': return 'Latin'
  elif u >= u'\u0100' and u <= u'\u017F': return 'Latin'
  elif u >= u'\u0180' and u <= u'\u024F': return 'Latin'
  elif u >= u'\u0370' and u <= u'\u03FF': return 'Greek'
  elif u >= u'\u0400' and u <= u'\u04FF': return 'Cyrillic'
  elif u >= u'\u0500' and u <= u'\u052F': return 'Cyrillic'
  elif u >= u'\u0530' and u <= u'\u058F': return 'Armenian'
  elif u >= u'\u0590' and u <= u'\u05FF': return 'Hebrew'
  elif u >= u'\u0600' and u <= u'\u06FF': return 'Arabic'
  elif u >= u'\u0700' and u <= u'\u074F': return 'Syriac'
  elif u >= u'\u0750' and u <= u'\u077F': return 'Arabic'
  elif u >= u'\u0780' and u <= u'\u07BF': return 'Thaana'
  elif u >= u'\u0900' and u <= u'\u097F': return 'Devanagari'
  elif u >= u'\u0980' and u <= u'\u09FF': return 'Bengali'
  elif u >= u'\u0A00' and u <= u'\u0A7F': return 'Gurmukhi'
  elif u >= u'\u0A80' and u <= u'\u0AFF': return 'Gujarati'
  elif u >= u'\u0B00' and u <= u'\u0B7F': return 'Oriya'
  elif u >= u'\u0B80' and u <= u'\u0BFF': return 'Tamil'
  elif u >= u'\u0C00' and u <= u'\u0C7F': return 'Telugu'
  elif u >= u'\u0C80' and u <= u'\u0CFF': return 'Kannada'
  elif u >= u'\u0D00' and u <= u'\u0D7F': return 'Malayalam'
  elif u >= u'\u0D80' and u <= u'\u0DFF': return 'Sinhala'
  elif u >= u'\u0E00' and u <= u'\u0E7F': return 'Thai'
  elif u >= u'\u0E80' and u <= u'\u0EFF': return 'Lao'
  elif u >= u'\u0F00' and u <= u'\u0FFF': return 'Tibetan'
  elif u >= u'\u1000' and u <= u'\u109F': return 'Burmese'
  elif u >= u'\u10A0' and u <= u'\u10FF': return 'Georgian'
  elif u >= u'\u1100' and u <= u'\u11FF': return 'Hangul'
  elif u >= u'\u1200' and u <= u'\u137F': return 'Ethiopic'
  elif u >= u'\u1380' and u <= u'\u139F': return 'Ethiopic'
  elif u >= u'\u13A0' and u <= u'\u13FF': return 'Cherokee'
  elif u >= u'\u1400' and u <= u'\u167F': return 'UCS'
  elif u >= u'\u1680' and u <= u'\u169F': return 'Ogham'
  elif u >= u'\u16A0' and u <= u'\u16FF': return 'Runic'
  elif u >= u'\u1700' and u <= u'\u171F': return 'Tagalog'
  elif u >= u'\u1720' and u <= u'\u173F': return 'Hanunoo'
  elif u >= u'\u1740' and u <= u'\u175F': return 'Buhid'
  elif u >= u'\u1760' and u <= u'\u177F': return 'Tagbanwa'
  elif u >= u'\u1780' and u <= u'\u17FF': return 'Khmer'
  elif u >= u'\u1800' and u <= u'\u18AF': return 'Mongolian'
  elif u >= u'\u1900' and u <= u'\u194F': return 'Limbu'
  elif u >= u'\u1950' and u <= u'\u197F': return 'Tai Le'
  elif u >= u'\u1980' and u <= u'\u19DF': return 'New Tai Lue'
  elif u >= u'\u19E0' and u <= u'\u19FF': return 'Khmer'
  elif u >= u'\u1A00' and u <= u'\u1A1F': return 'Buginese'
  elif u >= u'\u1E00' and u <= u'\u1EFF': return 'Latin'
  elif u >= u'\u1F00' and u <= u'\u1FFF': return 'Greek'
  elif u >= u'\u2C00' and u <= u'\u2C5F': return 'Glagolitic'
  elif u >= u'\u2C80' and u <= u'\u2CFF': return 'Coptic'
  elif u >= u'\u2D00' and u <= u'\u2D2F': return 'Georgian'
  elif u >= u'\u2D30' and u <= u'\u2D7F': return 'Tifinagh'
  elif u >= u'\u2D80' and u <= u'\u2DDF': return 'Ethiopic'
  elif u >= u'\u2E80' and u <= u'\u2EFF': return 'CJK'
  elif u >= u'\u2F00' and u <= u'\u2FDF': return 'Kangxi Radicals'
  elif u >= u'\u3040' and u <= u'\u309F': return 'Hiragana'
  elif u >= u'\u30A0' and u <= u'\u30FF': return 'Katakana'
  elif u >= u'\u3100' and u <= u'\u312F': return 'Bopomofo'
  elif u >= u'\u3130' and u <= u'\u318F': return 'Hangul'
  elif u >= u'\u3190' and u <= u'\u319F': return 'Kanbun'
  elif u >= u'\u31A0' and u <= u'\u31BF': return 'Bopomofo'
  elif u >= u'\u31F0' and u <= u'\u31FF': return 'Katakana'
  elif u >= u'\u3300' and u <= u'\u33FF': return 'CJK'
  elif u >= u'\u3400' and u <= u'\u4DBF': return 'CJK'
  elif u >= u'\u4E00' and u <= u'\u9FFF': return 'CJK'
  elif u >= u'\uA000' and u <= u'\uA48F': return 'Yi'
  elif u >= u'\uA490' and u <= u'\uA4CF': return 'Yi'
  elif u >= u'\uA800' and u <= u'\uA82F': return 'Syloti Nagri'
  elif u >= u'\uAC00' and u <= u'\uD7AF': return 'Hangul'
  elif u >= u'\uF900' and u <= u'\uFAFF': return 'CJK'
  elif u >= u'\uFE30' and u <= u'\uFE4F': return 'CJK'
  elif u >= u'\uFE70' and u <= u'\uFEFF': return 'Arabic'
  elif u >= u'\u10000' and u <= u'\u1007F': return 'Linear B'
  elif u >= u'\u10080' and u <= u'\u100FF': return 'Linear B'
  elif u >= u'\u10300' and u <= u'\u1032F': return 'Old Italic'
  elif u >= u'\u10330' and u <= u'\u1034F': return 'Gothic'
  elif u >= u'\u10380' and u <= u'\u1039F': return 'Ugaritic'
  elif u >= u'\u103A0' and u <= u'\u103DF': return 'Old Persian'
  elif u >= u'\u10400' and u <= u'\u1044F': return 'Deseret'
  elif u >= u'\u10450' and u <= u'\u1047F': return 'Shavian'
  elif u >= u'\u10480' and u <= u'\u104AF': return 'Osmanya'
  elif u >= u'\u10800' and u <= u'\u1083F': return 'Cypriot Syllabary'
  elif u >= u'\u10A00' and u <= u'\u10A5F': return 'Kharoshthi'
  elif u >= u'\u20000' and u <= u'\u2A6DF': return 'CJK'
  elif u >= u'\u2F800' and u <= u'\u2FA1F': return 'CJK'
  else: return UNKNOWN_SCRIPT_


def StringToScript(string, encoding='utf8'):
  stats = {}
  try: ustring = unicode(string, encoding)
  except TypeError: ustring = string
  for u in ustring:
    if u.isspace(): continue
    try: stats[CharacterToScript(u)] += 1
    except KeyError: stats[CharacterToScript(u)] = 1
  max_ = 0
  script = UNKNOWN_SCRIPT_
  for s in stats:
    if stats[s] > max_:
      max_ = stats[s]
      script = s
  return script


def Lower(string, encoding='utf8'):
  try:
    return unicode(string, encoding).lower().encode(encoding)
  except TypeError:
    return string.lower().encode(encoding)


def Upper(string, encoding='utf8'):
  return unicode(string, encoding).upper().encode(encoding)


def SupportsCapitalization(string, encoding='utf8'):
  return StringToScript(string) in SCRIPTS_WITH_CAPITALIZATION_


def IsCapitalized(string, encoding='utf8'):
  try: ustring = unicode(string, encoding)
  except TypeError: ustring = string
  if ustring.lower()[0] == ustring[0]:
    return False
  return True


def IsPunctuation(character, encoding='utf-8'):
  try: uchar = unicode(character, encoding)
  except TypeError: uchar = character
  return unicodedata.category(uchar)[:1] == 'P'


def IsUnicodePunctuation(ucharacter):
  return unicodedata.category(ucharacter)[:1] == 'P'


def HasPunctuation(word, encoding='utf-8'):
  haspunctuation = False
  try: uword = unicode(word, encoding)
  except TypeError: uword = word
  for uchar in uword:
    if unicodedata.category(uchar)[:1] == 'P':
      haspunctuation = True
      break
  return haspunctuation


def HasDigit(word, encoding='utf-8'):
  hasdigit = False
  try: uword = unicode(word, encoding)
  except TypeError: uword = word
  for uchar in uword:
    if unicodedata.category(uchar) == 'Nd':
      hasdigit = True
      break
  return hasdigit


def IsUnicodeDigit(ucharacter):
  return unicodedata.category(ucharacter) == 'Nd'
