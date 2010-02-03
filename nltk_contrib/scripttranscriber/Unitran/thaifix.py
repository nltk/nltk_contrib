# coding=utf-8

"""thaifix

For backwards compatibility reasons, Unicode decided on the lovely
property of having Thai left-catenating vowels appear in their
*visual* rather than their *logical* order. This necessitates some
jiggery-pokery to reorder these after consonant sequences.

Basically Thai can have consonant clusters that include a stop
followed by a liquid (l, r), including cases where the liquid (r) is
not pronounced.

Also possible are "h" and "?" (empty consonant) followed by a
sonorant.

A prefixed vowel (PV) must skip over a single consonant, or one of
these sequences.

See http://www.thai-language.com/ref/double_consonants

"""
__author__ = """
rws@uiuc.edu (Richard Sproat)
"""

ThaiTable = {
  u'\u0E01' : ["C", "ก", "THAI CHARACTER KO KAI"],
  u'\u0E02' : ["C", "ข", "THAI CHARACTER KHO KHAI"],
  u'\u0E03' : ["C", "ฃ", "THAI CHARACTER KHO KHUAT"],
  u'\u0E04' : ["C", "ค", "THAI CHARACTER KHO KHWAI"],
  u'\u0E05' : ["C", "ฅ", "THAI CHARACTER KHO KHON"],
  u'\u0E06' : ["C", "ฆ", "THAI CHARACTER KHO RAKHANG"],
  u'\u0E07' : ["C", "ง", "THAI CHARACTER NGO NGU"],
  u'\u0E08' : ["C", "จ", "THAI CHARACTER CHO CHAN"],
  u'\u0E09' : ["C", "ฉ", "THAI CHARACTER CHO CHING"],
  u'\u0E0A' : ["C", "ช", "THAI CHARACTER CHO CHANG"],
  u'\u0E0B' : ["C", "ซ", "THAI CHARACTER SO SO"],
  u'\u0E0C' : ["C", "ฌ", "THAI CHARACTER CHO CHOE"],
  u'\u0E0D' : ["S", "ญ", "THAI CHARACTER YO YING"],
  u'\u0E0E' : ["C", "ฎ", "THAI CHARACTER DO CHADA"],
  u'\u0E0F' : ["C", "ฏ", "THAI CHARACTER TO PATAK"],
  u'\u0E10' : ["C", "ฐ", "THAI CHARACTER THO THAN"],
  u'\u0E11' : ["C", "ฑ", "THAI CHARACTER THO NANGMONTHO"],
  u'\u0E12' : ["C", "ฒ", "THAI CHARACTER THO PHUTHAO"],
  u'\u0E13' : ["S", "ณ", "THAI CHARACTER NO NEN"],
  u'\u0E14' : ["C", "ด", "THAI CHARACTER DO DEK"],
  u'\u0E15' : ["C", "ต", "THAI CHARACTER TO TAO"],
  u'\u0E16' : ["C", "ถ", "THAI CHARACTER THO THUNG"],
  u'\u0E17' : ["C", "ท", "THAI CHARACTER THO THAHAN"],
  u'\u0E18' : ["C", "ธ", "THAI CHARACTER THO THONG"],
  u'\u0E19' : ["S", "น", "THAI CHARACTER NO NU"],
  u'\u0E1A' : ["C", "บ", "THAI CHARACTER BO BAIMAI"],
  u'\u0E1B' : ["C", "ป", "THAI CHARACTER PO PLA"],
  u'\u0E1C' : ["C", "ผ", "THAI CHARACTER PHO PHUNG"],
  u'\u0E1D' : ["C", "ฝ", "THAI CHARACTER FO FA"],
  u'\u0E1E' : ["C", "พ", "THAI CHARACTER PHO PHAN"],
  u'\u0E1F' : ["C", "ฟ", "THAI CHARACTER FO FAN"],
  u'\u0E20' : ["C", "ภ", "THAI CHARACTER PHO SAMPHAO"],
  u'\u0E21' : ["S", "ม", "THAI CHARACTER MO MA"],
  u'\u0E22' : ["C", "ย", "THAI CHARACTER YO YAK"],
  u'\u0E23' : ["L", "ร", "THAI CHARACTER RO RUA"],
  u'\u0E24' : ["C", "ฤ", "THAI CHARACTER RU"],
  u'\u0E25' : ["L", "ล", "THAI CHARACTER LO LING"],
  u'\u0E26' : ["C", "ฦ", "THAI CHARACTER LU"],
  u'\u0E27' : ["S", "ว", "THAI CHARACTER WO WAEN"],
  u'\u0E28' : ["C", "ศ", "THAI CHARACTER SO SALA"],
  u'\u0E29' : ["C", "ษ", "THAI CHARACTER SO RUSI"],
  u'\u0E2A' : ["C", "ส", "THAI CHARACTER SO SUA"],
  u'\u0E2B' : ["H", "ห", "THAI CHARACTER HO HIP"],
  u'\u0E2C' : ["C", "ฬ", "THAI CHARACTER LO CHULA"],
  u'\u0E2D' : ["H", "อ", "THAI CHARACTER O ANG"],
  u'\u0E2E' : ["C", "ฮ", "THAI CHARACTER HO NOKHUK"],
  u'\u0E2F' : ["V", "กฯ", "THAI CHARACTER PAIYANNOI (combined with ko kai (ก))"],
  u'\u0E30' : ["V", "กะ", "THAI CHARACTER SARA A (combined with ko kai (ก))"],
  u'\u0E31' : ["V", "กั", "THAI CHARACTER MAI HAN-AKAT (combined with ko kai (ก))"],
  u'\u0E32' : ["V", "กา", "THAI CHARACTER SARA AA (combined with ko kai (ก))"],
  u'\u0E33' : ["V", "กำ", "THAI CHARACTER SARA AM (combined with ko kai (ก))"],
  u'\u0E34' : ["V", "กิ", "THAI CHARACTER SARA I (combined with ko kai (ก))"],
  u'\u0E35' : ["V", "กี", "THAI CHARACTER SARA II (combined with ko kai (ก))"],
  u'\u0E36' : ["V", "กึ", "THAI CHARACTER SARA UE (combined with ko kai (ก))"],
  u'\u0E37' : ["V", "กื", "THAI CHARACTER SARA UEE (combined with ko kai (ก))"],
  u'\u0E38' : ["V", "กุ", "THAI CHARACTER SARA U (combined with ko kai (ก))"],
  u'\u0E39' : ["V", "กู", "THAI CHARACTER SARA UU (combined with ko kai (ก))"],
  u'\u0E3A' : ["V", "กฺ", "THAI CHARACTER PHINTHU (combined with ko kai (ก))"],
  u'\u0E40' : ["PV", "กเ", "THAI CHARACTER SARA E (combined with ko kai (ก))"],
  u'\u0E41' : ["PV", "กแ", "THAI CHARACTER SARA AE (combined with ko kai (ก))"],
  u'\u0E42' : ["PV", "กโ", "THAI CHARACTER SARA O (combined with ko kai (ก))"],
  u'\u0E43' : ["PV", "กใ", "THAI CHARACTER SARA AI MAIMUAN (combined with ko kai (ก))"],
  u'\u0E44' : ["PV", "กไ", "THAI CHARACTER SARA AI MAIMALAI (combined with ko kai (ก))"],
  u'\u0E45' : ["V", "กๅ", "THAI CHARACTER LAKKHANGYAO (combined with ko kai (ก))"],
  u'\u0E46' : ["V", "กๆ", "THAI CHARACTER MAIYAMOK (combined with ko kai (ก))"],
  u'\u0E47' : ["V", "ก็", "THAI CHARACTER MAITAIKHU (combined with ko kai (ก))"],
  u'\u0E48' : ["V", "ก่", "THAI CHARACTER MAI EK (combined with ko kai (ก))"],
  u'\u0E49' : ["V", "ก้", "THAI CHARACTER MAI THO (combined with ko kai (ก))"],
  u'\u0E4A' : ["V", "ก๊", "THAI CHARACTER MAI TRI (combined with ko kai (ก))"],
  u'\u0E4B' : ["V", "ก๋", "THAI CHARACTER MAI CHATTAWA (combined with ko kai (ก))"],
  u'\u0E4C' : ["V", "ก์", "THAI CHARACTER THANTHAKHAT (combined with ko kai (ก))"],
  u'\u0E4D' : ["V", "กํ", "THAI CHARACTER NIKHAHIT (combined with ko kai (ก))"],
}


PATTERNS_ = [('PV', 'C', 'L'),
             ('PV', 'H', 'S'),
             ('PV', 'C'),
             ('PV', 'L'),
             ('PV', 'S'),
             ('PV', 'H'),]


def ThaiFix(string):
  try: ustring = unicode(string, 'utf8')
  except UnicodeDecodeError: ustring = string
  i = 0
  length = len(ustring)
  nustring = []
  while i < length:
    c1 = c2 = c3 = ''
    try: 
      u1 = ustring[i]
      c1 = ThaiTable[u1][0]
    except (KeyError, IndexError): pass
    try:
      u2 = ustring[i+1]
      c2 = ThaiTable[u2][0]
    except (KeyError, IndexError): pass
    try:
      u3 = ustring[i+2]
      c3 = ThaiTable[u3][0]
    except (KeyError, IndexError): pass
    if (c1, c2, c3) in PATTERNS_:
      nustring += [u2, u3, u1]
      i += 3
    elif (c1, c2) in PATTERNS_:
      nustring += [u2, u1]
      i += 2
    else:
      nustring += [u1]
      i += 1
  return ''.join(nustring).encode('utf8')
