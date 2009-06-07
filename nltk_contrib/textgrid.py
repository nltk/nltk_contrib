# Natural Language Toolkit: TextGrid analysis
#
# Copyright (C) 2001-2009 NLTK Project
# Author: Margaret Mitchell <itallow@gmail.com>
#         Steven Bird <sb@csse.unimelb.edu.au> (revisions)
# URL: <http://www.nltk.org>
# For license information, see LICENSE.TXT
#

"""
Tools for reading TextGrid files, the format used by Praat.
"""

# needs more cleanup, subclassing, epydoc docstrings

import sys
import re

TEXTTIER = "TextTier"
INTERVALTIER = "IntervalTier"

OOTEXTFILE = re.compile(r"""(?x)
            xmin\ =\ (.*)[\r\n]+
            xmax\ =\ (.*)[\r\n]+
            [\s\S]+?size\ =\ (.*)[\r\n]+  # num_tiers
""")

CHRONTEXTFILE = re.compile(r"""(?x)
            [\r\n]+(\S+)\ 
            (\S+)\ +!\ Time\ domain.\ *[\r\n]+
            (\S+)\ +!\ Number\ of\ tiers.\ *[\r\n]+"
""")

OLDOOTEXTFILE = re.compile(r"""(?x)
            [\r\n]+(\S+)
            [\r\n]+(\S+)
            [\r\n]+.+[\r\n]+(\S+)
""")



#################################################################
# TextGrid Class
#################################################################

class TextGrid(object):
    """
    Class to manipulate the TextGrid format used by Praat.
    Separates each tier within this file into its own Tier
    object.  Each TextGrid object has
    a number of tiers (num_tiers), xmin, xmax, a text type to help
    with the different styles of TextGrid format, and tiers with their
    own attributes.
    """

    def __init__(self, fid):
        """
        Takes open read file as input, initializes attributes 
        of the TextGrid file.
        """

        self.read_file = fid
        self.num_tiers = 0
        self.xmin = 0
        self.xmax = 0
        self.idx = -1
        self.text_type = self._check_type()
        self.tiers = self.find_tiers()

    def __iter__(self):
        for tier in self.tiers:
            yield tier

    def next(self):
        if self.idx == (self.num_tiers - 1):
            raise StopIteration
        self.idx += 1
        return self.tiers[self.idx]

    @staticmethod
    def load(file):
        """
        @param file: a file in TextGrid format
        """

        return TextGrid(open(file).read())

    def _load_tiers(self, header):
        """
        Iterates over each tier and grabs tier information.
        """ 

        tier_re1 = header + "[\s\S]+?(?=" + header + "|$$)"
        m = re.compile(tier_re1)
        tier_iter = m.finditer(self.read_file)
        tiers = []
        for iterator in tier_iter:
            (begin, end) = iterator.span()
            tier_info = self.read_file[begin:end]
            tiers.append(Tier(tier_info, self.text_type))
        return tiers
    
    def _check_type(self):
        """
        Figures out the TextGrid format.
        """
        
        m = re.match("(.*)[\r\n](.*)[\r\n](.*)[\r\n](.*)", self.read_file)
        try:
            type_id = m.group(1)
        except AttributeError:
            raise TypeError("Cannot read file -- try TextGrid.load()")
        xmin = m.group(4)
        if type_id == "File type = \"ooTextFile\"":
            if "xmin" not in xmin:
                text_type = "OldooTextFile"
            else:
                text_type = "ooTextFile"
        elif type_id == "\"Praat chronological TextGrid text file\"":
            text_type = "ChronTextFile"
        else: 
            raise TypeError("Unknown format '(%s)'", (type_id))
        return text_type
	
    def find_tiers(self):
        """
        Splits the textgrid file into substrings corresponding to tiers. 
        """

        if self.text_type == "ooTextFile":
            m = OOTEXTFILE
            header = " +item \["
        elif self.text_type == "ChronTextFile":
            m = CHRONTEXTFILE
            header = "\"\S+\" \".*\" \d+\.?\d* \d+\.?\d*"
        elif self.text_type == "OldooTextFile":
            m = OLDOOTEXTFILE
            header = "\".*\"[\r\n]+\".*\""

        file_info = m.findall(self.read_file)[0]
        self.xmin = float(file_info[0])
        self.xmax = float(file_info[1])
        self.num_tiers = int(file_info[2])
        tiers = self._load_tiers(header)
        return tiers


#################################################################
# Tier Class
#################################################################

class Tier(object):
    """ 
    A container for each tier.
    """

    def __init__(self, tier, text_type):
        """
        Initializes attributes of the tier: class, name, xmin, xmax
        size, total time.  Utilizes the text type from the TextGrid class
        to know how to parse the file.
        """

        self.tier = tier
        self.text_type = text_type
        self.classid = ""
        self.nameid = ""
        self.xmin = 0
        self.xmax = 0
        self.size = 0
        self.transcript = ""
        self.tier_info = ""
        self.make_info()
        self.simple_transcript = self.make_simple_transcript()
        self.time()

    def __iter__(self):
        return self
  
    def make_info(self):
        """
        Figures out most attributes of the tier object:
        class, name, xmin, xmax, transcript.
        """

        trans = "([\S\s]*)"
        if self.text_type == "ChronTextFile":
            classid = "\"(.*)\" +"
            nameid = "\"(.*)\" +"
            xmin = "(\d+\.?\d*) +"
            xmax = "(\d+\.?\d*) *[\r\n]+"
            # No size values are given in the Chronological Text File format.
            self.size = None
            size = ""
        elif self.text_type == "ooTextFile":
            classid = " +class = \"(.*)\" *[\r\n]+"
            nameid = " +name = \"(.*)\" *[\r\n]+"
            xmin = " +xmin = (\d+\.?\d*) *[\r\n]+"
            xmax = " +xmax = (\d+\.?\d*) *[\r\n]+"
            size = " +\S+: size = (\d+) *[\r\n]+"
        elif self.text_type == "OldooTextFile":
            classid = "\"(.*)\" *[\r\n]+"
            nameid = "\"(.*)\" *[\r\n]+"
            xmin = "(\d+\.?\d*) *[\r\n]+"
            xmax = "(\d+\.?\d*) *[\r\n]+"
            size = "(\d+) *[\r\n]+"
        m = re.compile(classid + nameid + xmin + xmax + size + trans)
        self.tier_info = m.findall(self.tier)[0]
        self.classid = self.tier_info[0]
        self.nameid = self.tier_info[1]
        self.xmin = float(self.tier_info[2])
        self.xmax = float(self.tier_info[3])
        if self.size != None:
            self.size = int(self.tier_info[4])
        self.transcript = self.tier_info[-1]
            
    def make_simple_transcript(self):
        """ 
        Makes a transcript of the form:
        start_time end_time  label
        """

        if self.text_type == "ChronTextFile":
            trans_head = ""
            trans_xmin = " (\S+)"
            trans_xmax = " (\S+)[\r\n]+"
            trans_text = "\"([\S\s]*?)\""
        elif self.text_type == "ooTextFile":
            trans_head = " +\S+ \[\d+\]: *[\r\n]+"
            trans_xmin = " +\S+ = (\S+) *[\r\n]+"
            trans_xmax = " +\S+ = (\S+) *[\r\n]+"
            trans_text = " +\S+ = \"([^\"]*?)\""    
        elif self.text_type == "OldooTextFile":
            trans_head = ""
            trans_xmin = "(.*)[\r\n]+"
            trans_xmax = "(.*)[\r\n]+"
            trans_text = "\"([\S\s]*?)\""
        if self.classid == TEXTTIER:
            trans_xmin = ""
        trans_m = re.compile(trans_head + trans_xmin + trans_xmax + trans_text)
        self.simple_transcript = trans_m.findall(self.transcript)
        return self.simple_transcript

    def transcript(self):
        """
        Returns the transcript of the tier, separated by utterance.
        """
       
        return self.transcript

    def time(self, non_speech_char="."):
        """
        Returns the utterance time of a given tier.
        Screens out entries that begin with a non-speech marker.	
        """

        total = 0.0
        if self.classid != TEXTTIER:
            for (time1, time2, utt) in self.simple_transcript:
                utt = utt.strip()
                if utt and not utt[0] == ".":
                    total += (float(time2) - float(time1))
        return total
                    
    def tier_name(self):
        """
        Returns the tier name of a tier with a given number.
        """

        return self.nameid

    def classid(self, tiernum):
        """
        Returns the type of transcription on tier:  interval or point (text).
        """

        return self.classid

    def min_max(self):
        """
        Returns xmin and xmax for a given tier.
        """

        return (self.xmin, self.xmax)

    def __repr__(self):
        return "<%s \"%s\" (%.2f, %.2f) %.2f%%>" % (self.classid, self.nameid, self.xmin, self.xmax, 100*self.time())

    def __str__(self):
        return self.__repr__() + "\n  " + "\n  ".join(" ".join(row) for row in self.simple_transcript)

def demo_TextGrid(demo_data):
    print "** Demo of the TextGrid class. **"

    fid = TextGrid(demo_data)
    print "Tiers:", fid.num_tiers

    for i, tier in enumerate(fid):
        print "\n***"
        print "Tier:", i
        print tier

def demo():
    # Each demo demonstrates different TextGrid formats.
    print "Format 1"
    demo_TextGrid(demo_data1)
    print "\nFormat 2"
    demo_TextGrid(demo_data2)
    print "\nFormat 3"
    demo_TextGrid(demo_data3)


demo_data1 = """File type = "ooTextFile"
Object class = "TextGrid"

xmin = 0 
xmax = 2045.144149659864
tiers? <exists> 
size = 3 
item []: 
    item [1]:
        class = "IntervalTier" 
        name = "utterances" 
        xmin = 0 
        xmax = 2045.144149659864 
        intervals: size = 5 
        intervals [1]:
            xmin = 0 
            xmax = 2041.4217474125382 
            text = "" 
        intervals [2]:
            xmin = 2041.4217474125382 
            xmax = 2041.968276643991 
            text = "this" 
        intervals [3]:
            xmin = 2041.968276643991 
            xmax = 2042.5281632653062 
            text = "is" 
        intervals [4]:
            xmin = 2042.5281632653062 
            xmax = 2044.0487352585324 
            text = "a" 
        intervals [5]:
            xmin = 2044.0487352585324 
            xmax = 2045.144149659864 
            text = "demo" 
    item [2]:
        class = "TextTier" 
        name = "notes" 
        xmin = 0 
        xmax = 2045.144149659864 
        points: size = 3 
        points [1]:
            time = 2041.4217474125382 
            mark = ".begin_demo"
        points [2]:
            time = 2043.8338291031832
            mark = "voice gets quiet here" 
        points [3]:
            time = 2045.144149659864
            mark = ".end_demo" 
    item [3]:
        class = "IntervalTier" 
        name = "phones" 
        xmin = 0 
        xmax = 2045.144149659864
        intervals: size = 12
        intervals [1]:
            xmin = 0 
            xmax = 2041.4217474125382 
            text = "" 
        intervals [2]:
            xmin = 2041.4217474125382 
            xmax = 2041.5438290324326 
            text = "D"
        intervals [3]:
            xmin = 2041.5438290324326
            xmax = 2041.7321032910372
            text = "I"
        intervals [4]:
            xmin = 2041.7321032910372            
            xmax = 2041.968276643991 
            text = "s" 
        intervals [5]:
            xmin = 2041.968276643991 
            xmax = 2042.232189031843
            text = "I"
        intervals [6]:
            xmin = 2042.232189031843
            xmax = 2042.5281632653062 
            text = "z" 
        intervals [7]:
            xmin = 2042.5281632653062 
            xmax = 2044.0487352585324 
            text = "eI" 
        intervals [8]:
            xmin = 2044.0487352585324 
            xmax = 2044.2487352585324
            text = "dc"
        intervals [9]:
            xmin = 2044.2487352585324
            xmax = 2044.3102321849011
            text = "d"
        intervals [10]:
            xmin = 2044.3102321849011
            xmax = 2044.5748932104329
            text = "E"
        intervals [11]:
            xmin = 2044.5748932104329
            xmax = 2044.8329108578437
            text = "m"
        intervals [12]:
            xmin = 2044.8329108578437
            xmax = 2045.144149659864 
            text = "oU" 
"""

demo_data2 = """File type = "ooTextFile"
Object class = "TextGrid"

0
2.8
<exists>
2
"IntervalTier"
"utterances"
0
2.8
3
0
1.6229213249309031
""
1.6229213249309031
2.341428074708195
"demo"
2.341428074708195
2.8
""
"IntervalTier"
"phones"
0
2.8
6
0
1.6229213249309031
""
1.6229213249309031
1.6428291382019483
"dc"
1.6428291382019483
1.65372183721983721
"d"
1.65372183721983721
1.94372874328943728
"E"
1.94372874328943728
2.13821938291038210
"m"
2.13821938291038210
2.341428074708195
"oU"
2.341428074708195
2.8
""
"""

demo_data3 = """"Praat chronological TextGrid text file"
0 2.8   ! Time domain.
2   ! Number of tiers.
"IntervalTier" "utterances" 0 2.8
1 0 1.6229213249309031
""
1 1.6229213249309031 2.341428074708195
"demo"
1 2.341428074708195 2.8
""
"IntervalTier" "phones" 0 2.8
2 0 1.6229213249309031
""
2 1.6229213249309031 1.6428291382019483
"dc"
2 1.6428291382019483 1.65372183721983721
"d"
2 1.65372183721983721 1.94372874328943728
"E"
2 1.94372874328943728 2.13821938291038210
"m"
2 2.13821938291038210 2.341428074708195
"oU"
2 2.341428074708195 2.8
""
"""

if __name__ == "__main__":
    demo()
