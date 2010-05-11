"""String edit distance computation for two strings in WorldBet using
phonetic distance.

Depends upon the file 'phoneFeature2.txt', which should be included in
this distribution.

NOTE THAT THIS CODE DOES NOT FOLLOW THE (GOOGLE) STYLE CONVENTIONS.
"""

__author__ = """syoon9@uiuc.edu (Su-Youn Yoon)
rws@uiuc.edu (Richard Sproat)"""

import sys

_PHONE_FEATURES_FILE = 'phoneFeature2.txt' 


## Insertion, deletion and substitution costs of features.
## If you add a new feature in the phone features file, then
## the substitution cost should also be added here.

FCDic = {
    # Major features

    'c': 20,     # consonant
    's': 20,     # sonorant

    # Manner features
    'n': 5,      # nasal
    'l': 3,      # lateral
    'cnt': 1.5,  # continuous
    'v': 1.5,    # voicing

    # Place features
    'L': 20,     # Labial
    'C': 7,      # Coronal
    'A': 1.5,    # Anterior
    'D': 8,      # Dorsal
    
    # Vowel feature
    'r': 2,      # round
    'h': 2,      # high
    'w': 2,      # low
    'f': 2,      # front
    'b': 2,      # back
    'rh': 3,     # rhotic - r-coloured vowel
    'g': 8,      # glottalized vowel 
    'lg': 8,     # long vowel 
    'p': 3,      # pharyngealized 
    'nas': 3     # nasalized vowel
    }

## List of all features

featList = FCDic.keys()

LClist = ['L', 'C', 'D']
PClist = ['C', 'D'] 
VClist = ['c', 's', 'r', 'h', 'w', 'f', 'b', 'rh', 'g', 'lg']
jlist  = ['tS', 'tSh', 'tS>', 'dZ', 'c', 'ch', 'cC', 'cCh', 'cC>', 'J']
wlist  = ['v', 'f']
sList  = ['w', 'j']
hlist  = ['h', 'x', 'G', 'X', 'K']


def readFile(file):
    """Reads file and returns lines from file.

    Args:
      string: file name

    Returns:
      list: lines from file
    """

    fin = open(file)
    lines = fin.readlines()
    fin.close()
    return lines


def conTable(phonefile):
    """Read in the file of phone definition and set up the mapping
    between each phone and the associated features.

    Args:
      string: name of file of phones

    Returns:
      a list: lines containing phone, feature maps
    """

    lines = readFile(phonefile)
    nlines = []
    llen = len(lines)
    fList = lines[0].strip().split()
    flen = len(fList)
    for i in range(1, llen):
        x = lines[i].strip().split()
        xlen = len(x)
        if flen != xlen-1:
            sys.stderr.write("Error in phone feature file, line %d.\n" % i)
            sys.exit(1)
        out = ''
        ph = x[0]
        for j in range(1, xlen):
            if fList[j-1] in featList:
                out = ph + '\t' + fList[j-1] + '\t' + x[j] 
                nlines.append(out)
    return nlines


def addPhoneFeatureValue(phone, feat, val, dic):
    """Add a phone/feature/value triple to the dictionary.

    Args:
      string: phone
      string: feat
      string: val
      dictionary: dic

    Returns:
      None
    """

    try:
        dic[phone][feat] = int(val)
    except KeyError:
        dic[phone] = {}
        dic[phone][feat] = int(val)


def loadPFDic(fPF):
    """Loads the phonetic feature dictionary. Each phoneme has
    associated features and values, where the values are one of
    [-1, 0, 1].

    Args:
      string: phonetic feature file name

    Returns:
      dictionary: instantiated dictionary
    """

    PFDic = {} 
    lines = conTable(fPF)
    for line in lines:
        x = line.strip().split()
        phone = x[0]
        feat = x[1]
        val = x[2]
        addPhoneFeatureValue(phone, feat, val, PFDic)
    return PFDic


def loadTargetLanguagePhList(fPL):
    """Load just that subset of phones needed for the language pair in
    question. This is desirable since we will compute an all-pairs
    cost matrix for all relevant phones for the language pair in
    question, and this will be smaller than computing this for the
    entire set of phones.

    Args:
      string: file name for phone subset

    Returns:
      list: phone subset
    """

    phList = []
    lines = readFile(fPL)
    for line in lines:
        x = line.strip().split()
        if not '#' in x[0]:
           if not x[0] in phList: phList.append(x[0])
    return phList
   

def calPhoneToPhoneCost(ph1, ph2, PFDic):
    """Calculate the phoneme substitution/insertion/deletion cost
    based on the substitution/insertion/deletion costs for the
    features.

    Args:
      string: phone 1
      string: phone 2
      dictionary: phonetic feature dictionary

    Returns:
      int: sum
    """

    oph1 = ph1
    oph2 = ph2
    ph1 = ph1.replace('_c', '')
    ph2 = ph2.replace('_c', '')
    sum = 1.5
    # Deletion or insertion cost:
    if ph2 =='NA':            
        if PFDic[ph1]['c'] == 1 :	
            sum += 20
            # Coda consonant:
            if oph1.find('_c') > -1:
                sum = sum - 5 
        else :	
            sum += 8
            # If vowel is low add 2 to cost:
            if PFDic[ph1]['h'] != 1:  
                sum += 2
    # Substitution:
    else:		       
        # ph1 and ph2 are not consonants:
        if (PFDic[ph1]['c']!= 1) and (PFDic[ph2]['c']!=1): 
            for feat in VClist:
                if PFDic[ph1][feat]!=0:
                    # Default value - no cost:
                    if PFDic[ph2][feat]!=0:	
                        # Two values are different:
                        if PFDic[ph1][feat] != PFDic[ph2][feat]:	
                            cost = float(FCDic[feat]) 
                            sum += cost
        # Consonant - consonant, consonant - vowel/semivowel:
        else:	
            for feat in PFDic[ph1]:
                if PFDic[ph1][feat]!=0:
                    # Default value - no cost:
                    if PFDic[ph2][feat]!=0:	
                        # Two values are different:
                        if PFDic[ph1][feat] != PFDic[ph2][feat]:	
                            cost = float(FCDic[feat]) 
                            if (ph1 == 'h') or (ph2 =='h'): 
                                # 'h'-exception: there is no specific
                                # place of articulation for 'h'.
                                # h -> into fricatives:
                                if feat == 'cnt': cost = 10 
                                elif feat == 'D': cost = cost - 5
                            if feat in LClist:
                                # Vowel/semivowel - consonant:
				if ((PFDic[ph1]['c']!=1 and ph1!='h')
                                    or (PFDic[ph2]['c']!=1 and ph2!='h')): 
                                    cost = cost - 5
                                # Palatal consonant substitution :
			        elif ((((PFDic[ph1]['C'] ==1) and
                                        (PFDic[ph1]['D'] ==1)) or
                                       ((PFDic[ph2]['C'] ==1) and
                                        (PFDic[ph2]['D'] ==1))) and
                                      (feat!='L')):
                                    cost = cost - 5 
                            sum += cost
    # Semi-vowel penalty:
    if ((ph1 in sList and PFDic[ph2]['c']==-1) or
        (PFDic[ph1]['c']==-1 and ph2 in sList)):
        sum += 5  
    elif (((ph1 == 'j') and (ph2 in jlist)) or
          ((ph2=='j') and (ph1 in jlist))):
        sum = 5
    elif (((ph1 == 'w') and (ph2 in wlist)) or
          ((ph2=='w') and (ph1 in wlist))):
        sum = 5
    # Nasal substitution cost in coda position: since nasal is
    # frequently substituted in coda position, the high substitution 
    # costs of place features are adjusted:
    elif ((PFDic[ph1]['n']==1) and
          (PFDic[ph2]['n']==1) and
          ((oph2.find('_c') > -1) and (oph1.find('_c') > -1))):
        sum = 10 
    return (sum)


def getCDic(fPL, PFDic, writeFile=None):
    """Sets the language (pair) specific phone-to-phone cost
    mappings. Makes the cost table for all possible insertions,
    deletions and substitutions.

    Args:
      string:  file name for phone subset
      dictionary: phonetic feature dictionary
      string: file to write output (default: None)

    Returns:
      dictionary: language-pair specific cost mapping
    """

    CDic =  {}	
    phList = loadTargetLanguagePhList(fPL)
    for ph1 in phList:
        if ph1!='NA':
           for ph2 in phList:
               cost = calPhoneToPhoneCost(ph1, ph2, PFDic)
               key = (ph1, ph2)
               CDic[key] = cost
    if writeFile:
        fout = open(writeFile, 'w')
        for key in CDic:
            fout.write('%s\t%s\t%d\n' % (key[0],  key[1], CDic[key]))
        fout.close()
    return CDic	


def fMin(j, k, dic, CM, sp, tp):
    """Calculate insertion cost.

    Args:
      dictionary: cost dictionary
      dictionary: ...Add explanation
      dictionary: ...Add explanation
      string: source phone
      string: target phone

    Returns:
      int: minimum cost
      string: action
    """

    if j == 0 and k==0: return(0, 'N')
    act = 'I'
    if j> 0:
       cost = dic[(tp, 'NA')]
       Min = CM[j-1][k] + cost
    else: Min = 1000
    # calculate deletion cost
    if k > 0:
      cost = dic[(sp, 'NA')]
      deL = CM[j][k-1] + cost
      if Min > deL:
	 act = 'D'
	 Min = deL
    if j> 0 and k > 0:
       cost = dic[(tp, sp)]
       sub = CM[j-1][k-1] + cost
       if Min > sub:
	  act = 'S'
	  Min = sub
    return (Min, act)


def getIcost(AM, CM, Tnlen, Snlen):
    """Get the minimum edit distance of the initial phonemes.
    Ins/del/subs rarely occur at word-initial position, and the
    pair with the high initial cost is usually incorrect pair. 
    Therefore, double the initial cost.

    Args:
      dictionary: ...Add explanation
      dictionary: ...Add explanation
      int: target length
      int: source length

    Returns:
      int: cost
    """

    state = AM[Tnlen-1][Snlen-1]
    pcost = CM[Tnlen-1][Snlen-1]
    x = Tnlen - 1
    y = Snlen - 1
    while state != 'N':
	  if state == 'S':
	        x = x - 1
	        y = y - 1
    	  elif state == 'I':
	   	x = x - 1
	  elif state == 'D':
	   	y = y - 1
          ## this fails sometimes for unclear reasons:
          try: state = AM[x][y]
          except IndexError: state = 'N'
          try:
              cost = pcost - CM[x][y]
              pcost = CM[x][y]
          except IndexError: state = 'N'
    icost = cost
    return icost
    

def mEdit(srcPronString, tarPronString, CDic, PFDic):
    """Get minimum edit distance cost for two strings.

    Args:
      string: source pronunciation string
      string: target pronunciation string
      dictionary: source-target pair phone dictionary
      dictionary: whole phonetic feature dictionary

    Returns:
      int: edit distance      
    """

    ini = ['NA']
    src = ini + srcPronString.strip().split()
    tar = ini + tarPronString.strip().split()
    Snlen = len(src)
    Tnlen = len(tar)
  
    # For minimum edit distance:
    # record the cost ;
    CM = [] 
    # record the action of minimum cost
    # (deletion: D, insertion:I, substitution:S).
    AM = [] 
            
    for j in range(Tnlen):
	CM.append([])
	AM.append([])
        for k in range(Snlen):
	    CM[j].append([])
	    AM[j].append([])
	
    # Fill CM and AM
    for j in range(Tnlen):
        for k in range(Snlen):
	  # set value of the first column, row as '0'
	  sp = src[k]
	  tp = tar[j]
	  (cost, act) = fMin(j, k, CDic, CM, sp, tp)
	  CM[j][k] = cost
	  AM[j][k] = act

    # calculate the distance between two strings, and compare with threshold.
    icost = getIcost(AM, CM, Tnlen, Snlen)
    # doubling initial cost
    dist = float((CM[Tnlen-1][Snlen-1] + icost) / max(Tnlen-1, Snlen-1)) 

    # In order to solve Festival error - final phoneme. 
    # Obstruent consonants such as [s,z,k...] are not pronounced
    # at word-final position frequently,  but the pronunciation
    # obtained by Festival includes these phonemes. 
    # ex> Phillipines 
    if (PFDic[tar[-1]]['s'] == -1 and
        len(src) > 5 and len(tar) > 5 and
        CM[Tnlen-1][Snlen-1] > CM[Tnlen-2][Snlen-1]): 
        dist = float((CM[Tnlen-2][Snlen-1])/ max(Tnlen-2, Snlen-1))
    return dist 


def init(phone_subset):
    """Initialize dictionaries.

    Args:
      string: phonetic feature file name

    Returns:
      dictionary: source-target pair phone dictionary
      dictionary: whole phonetic feature dictionary
    """

    PFDic = loadPFDic(_PHONE_FEATURES_FILE)
    CDic = getCDic(phone_subset, PFDic)
    return CDic, PFDic
