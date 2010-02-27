
# Based on Gale & Church 1993, "A Program for Aligning Sentences in Bilingual Corpora"
# This is a Python version of the C implementation by Mike Riley presented in the appendix
# of the paper. The documentation in the C program is retained where applicable.

import sys

from nltk.metrics import scores

import distance_measures
import alignment_util

##//////////////////////////////////////////////////////
##  Alignment
##//////////////////////////////////////////////////////

class Alignment(object):
    """
    
    
    """
    def __init__(self): 
        """
        
        """
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.d = 0  
        self.category = ''
        self.hard_regions_index = 0
        self.soft_regions_index = 0
        self.alignment_mappings = []
    
    def set_alignment_mappings(self):        
        """
        
        """
        if (self.category == '1 - 1'):
            align_triple = (self.hard_regions_index,
                            self.soft_regions_index,
                            self.soft_regions_index)
            self.alignment_mappings.append(align_triple)
        elif (self.category == '1 - 0'):
            align_triple = (self.hard_regions_index,
                            self.soft_regions_index,
                            -1)
            self.alignment_mappings.append(align_triple)
        elif (self.category == '0 - 1'):
            align_triple = (self.hard_regions_index,
                            -1,
                            self.soft_regions_index)
            self.alignment_mappings.append(align_triple)
        elif (self.category == '2 - 1'):
            align_triple = (self.hard_regions_index,
                            self.soft_regions_index + 1,
                            self.soft_regions_index)
            
            self.alignment_mappings.append(align_triple)
            align_triple = (self.hard_regions_index,
                            self.soft_regions_index,
                            self.soft_regions_index)
            self.alignment_mappings.append(align_triple)
        elif (self.category == '1 - 2'):
            align_triple = (self.hard_regions_index,
                            self.soft_regions_index,
                            self.soft_regions_index + 1)            
            self.alignment_mappings.append(align_triple)
            align_triple = (self.hard_regions_index,
                            self.soft_regions_index,
                            self.soft_regions_index)
            self.alignment_mappings.append(align_triple)
        elif (self.category == '2 - 2'):
            align_triple = (self.hard_regions_index,
                            self.soft_regions_index + 1,
                            self.soft_regions_index + 1)            
            self.alignment_mappings.append(align_triple)
            align_triple = (self.hard_regions_index,
                            self.soft_regions_index,
                            self.soft_regions_index)
            self.alignment_mappings.append(align_triple)
        else:
            print "not supported alignment type"

##//////////////////////////////////////////////////////
##  Aligner
##//////////////////////////////////////////////////////

class Aligner(object):
    """
    
      usage
    
      align -D '.EOP' -d '.EOS' <File1> <File2>
    
      outputs two files: <File11>.al & <File2>.al
    
      regions are delimited by the -D and -d args
    
      the program is allowed to delete -d delimiters as necessary in order
      align the files, but it cannot change -D delimiters.
      
    """
    
    def __init__(self, input_file1, input_file2, hard_delimiter, soft_delimiter):
        """
        
        """
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        
        self.hard_delimiter = hard_delimiter
        self.soft_delimiter = soft_delimiter         
    
    def align_regions(self, dist_funct, debug=False, verbose=False):        
        """
        
        """
        alignments = {}
                
        (lines1, number_of_lines1) = alignment_util.readlines(self.input_file1)
        (lines2, number_of_lines2) = alignment_util.readlines(self.input_file2)
        
        tmp = Region(lines1, number_of_lines1)
        
        (hard_regions1, number_of_hard_regions1) = tmp.find_sub_regions(self.hard_delimiter)
        
        tmp.lines = lines2
        tmp.length = number_of_lines2
        
        (hard_regions2, number_of_hard_regions2) = tmp.find_sub_regions(self.hard_delimiter)        
        
        if (number_of_hard_regions1 != number_of_hard_regions2):
            print "align_regions: input files do not contain the same number of hard regions" + '\n'
            print "%s" % hard_delimiter + '\n'
            print "%s has %d and %s has %d" % (self.input_file1, number_of_hard_regions1, \
                                               self.input_file2, number_of_hard_regions2) + '\n'
            
            return
        
        hard_regions_index = 0        
        
        while (hard_regions_index < len(hard_regions1)):    
            (soft_regions1, number_of_soft_regions1) = \
                hard_regions1[hard_regions_index].find_sub_regions(self.soft_delimiter)            
            (soft_regions2, number_of_soft_regions2) = \
                hard_regions2[hard_regions_index].find_sub_regions(self.soft_delimiter)
                
            if (debug):
               out1.write("Text 1:number of soft regions=%d\n" % number_of_soft_regions1 + '\n')
               out1.write("Text 2:number of soft regions=%d\n" % number_of_soft_regions2 + '\n')
               out2.write("Text 1:number of soft regions=%d\n" % number_of_soft_regions1 + '\n')
               out2.write("Text 2:number of soft regions=%d\n" % number_of_soft_regions2 + '\n')
               
            len1 = []
            for reg in soft_regions1:
                len_lines = 0
                for li in reg.lines:
                    len_lines = len_lines + len(li)
                
                len1.append(len_lines)
                
            len2 = []
            for reg in soft_regions2:
                len_lines = 0
                for li in reg.lines:
                    len_lines = len_lines + len(li)
                
                len2.append(len_lines)                
                        
            (n, align) = self.seq_align(len1, 
                                        len2, 
                                        number_of_soft_regions1, 
                                        number_of_soft_regions2, 
                                        dist_funct,
                                        hard_regions_index)                                       
            
            alignments[hard_regions_index] = align
            
            self.output_alignment(n, align, 
                                  soft_regions1, soft_regions2,
                                  debug, verbose)
            
            hard_regions_index = hard_regions_index + 1
                        
        return alignments        
    
    def seq_align(self, x, y, nx, ny, dist_funct, hard_regions_index):    
        """
        
        Sequence alignment routine.
        This version allows for contraction/expansions.
        
        x and y are sequences of objects, represented as non-zero ints, to be aligned.
        
        dist_funct(x1, y1, x2, y2) is a distance function of 4 args:          
        
        dist_funct(x1, y1, 0, 0) gives cost of substitution of x1 by y1.
        dist_funct(x1, 0, 0, 0) gives cost of deletion of x1.
        dist_funct(0, y1, 0, 0) gives cost of insertion of y1.
        dist_funct(x1, y1, x2, 0) gives cost of contraction of (x1,x2) to y1.
        dist_funct(x1, y1, 0, y2) gives cost of expansion of x1 to (y1,y2).
        dist_funct(x1, y1, x2, y2) gives cost to match (x1,x2) to (y1,y2).
        
        align is the alignment, with (align[i].x1, align[i].x2) aligned
        with (align[i].y1, align[i].y2).  Zero in align[].x1 and align[].y1
        correspond to insertion and deletion, respectively.  Non-zero in
        align[].x2 and align[].y2 correspond to contraction and expansion,
        respectively.  align[].d gives the distance for that pairing.
        
        The function returns the length of the alignment.
        (The Python version also returns the alignment as a Python dictionary)
        
        """
        
        distances = []
        path_x = []
        path_y = [] 
        
        first_len = nx + 1
        second_len = ny + 1
        
        distances = [[0] * second_len for c in range(first_len)]         
        path_x = [[0] * second_len for c in range(first_len)]              
        path_y = [[0] * second_len for c in range(first_len)]
                  
        d1 = d2 = d3 = d4 = d5 = d6 = sys.maxint
        
        for j in range(0, ny + 1):    
            for i in range(0, nx + 1):            
                if (i > 0 and j > 0):		
                    #/* substitution */
                    d1 = distances[i-1][j-1] + \
                        dist_funct(x[i-1], y[j-1], 0, 0)
                else:
                    d1 = sys.maxint
                    
                if (i > 0):	
                    #/* deletion */
                    d2 = distances[i-1][j] + \
                        dist_funct(x[i-1], 0, 0, 0)
                else:
                    d2 = sys.maxint
                    
                if (j > 0):		
                    #/* insertion */
                    d3 = distances[i][j-1] + \
                        dist_funct(0, y[j-1], 0, 0)
                else:
                    d3 = sys.maxint
                    
                if (i > 1 and j > 0):		
                    #/* contraction */
                    d4 = distances[i-2][j-1] + \
                        dist_funct(x[i-2], y[j-1], x[i-1], 0)
                else:
                    d4 = sys.maxint
                    
                if (i > 0 and j > 1):		
                    #/* expansion */
                    d5 = distances[i-1][j-2] + \
                        dist_funct(x[i-1], y[j-2], 0, y[j-1])
                else:
                    d5 = sys.maxint
                    
                if (i > 1 and j > 1):		
                    #/* melding */
                    d6 = distances[i-2][j-2] + \
                        dist_funct(x[i-2], y[j-2], x[i-1], y[j-1])
                else:
                    d6 = sys.maxint
     
                dmin = min(d1, d2, d3, d4, d5, d6)
                
                if (dmin == sys.maxint):
                    distances[i][j] = 0
                elif (dmin == d1):
                    distances[i][j] = d1                
                    path_x[i][j] = i - 1
                    path_y[i][j] = j - 1              
                elif (dmin == d2):
                    distances[i][j] = d2                
                    path_x[i][j] = i - 1
                    path_y[i][j] = j                
                elif (dmin == d3):
                    distances[i][j] = d3                
                    path_x[i][j] = i
                    path_y[i][j] = j - 1                
                elif (dmin == d4):
                    distances[i][j] = d4                
                    path_x[i][j] = i - 2
                    path_y[i][j] = j - 1                 
                elif (dmin == d5):
                    distances[i][j] = d5                
                    path_x[i][j] = i - 1
                    path_y[i][j] = j - 2
                else:			
                    # /* dmin == d6 */ {
                    distances[i][j] = d6                
                    path_x[i][j] = i - 2
                    path_y[i][j] = j - 2
        n = 0
        
        ralign_dict = {}
        
        i = nx
        j = ny
        while (i > 0 or j > 0):                
            oi = path_x[i][j]       
            oj = path_y[i][j]
            di = i - oi
            dj = j - oj
            
            ralign = Alignment()
                          
            if (di == 1 and dj == 1):
                #/* substitution */            
                ralign.x1 = x[i-1]
                ralign.y1 = y[j-1]
                ralign.x2 = 0
                ralign.y2 = 0
                ralign.d = distances[i][j] - distances[i-1][j-1] 
                ralign.category = '1 - 1'
                
            elif (di == 1 and dj == 0):
                #/* deletion */
                ralign.x1 = x[i-1]
                ralign.y1 = 0
                ralign.x2 = 0
                ralign.y2 = 0
                ralign.d = distances[i][j] - distances[i-1][j]
                ralign.category = '1 - 0'
            elif (di == 0 and dj == 1):
                #/* insertion */
                ralign.x1 = 0
                ralign.y1 = y[j-1]
                ralign.x2 = 0
                ralign.y2 = 0
                ralign.d = distances[i][j] - distances[i][j-1]        
                ralign.category = '0 - 1'
            elif (dj == 1):
                #/* contraction */
                ralign.x1 = x[i-2]
                ralign.y1 = y[j-1]
                ralign.x2 = x[i-1]
                ralign.y2 = 0
                ralign.d = distances[i][j] - distances[i-2][j-1]     
                ralign.category = '2 - 1'
            elif (di == 1):
                #/* expansion */
                ralign.x1 = x[i-1]
                ralign.y1 = y[j-2]
                ralign.x2 = 0
                ralign.y2 = y[j-1]
                ralign.d = distances[i][j] - distances[i-1][j-2]    
                ralign.category = '1 - 2'
            else: 
                #/* di == 2 and dj == 2 */ { /* melding */
                ralign.x1 = x[i-2]
                ralign.y1 = y[j-2]
                ralign.x2 = x[i-1]
                ralign.y2 = y[j-1]
                ralign.d = distances[i][j] - distances[i-2][j-2]
                ralign.category = '2 - 2'
            
            ralign.hard_regions_index = hard_regions_index
            ralign.soft_regions_index = n
            ralign.set_alignment_mappings()
            
            ralign_dict[n] = ralign
            
            n = n + 1
            
            i = oi
            j = oj
           
        align_dict = {}
            
        for e in range(0, n):
            align_dict[n-e-1] = ralign_dict[e] 
               
        return (n, align_dict)
        
    def output_alignment(self, n, align, soft_regions1, soft_regions2, debug, verbose):
        """
        
        """
        out1 = open(self.input_file1 + '.al', 'w')
        out2 = open(self.input_file2 + '.al', 'w')
        
        prevx = 0
        prevy = 0
        ix = 0
        iy = 0
        
        for i in range(0,n):
            a = align[i]
            
            if (a.x2 > 0):
              ix = ix + 1
            elif(a.x1 == 0): 
              ix = ix - 1
              
            if (a.y2 > 0): 
              iy = iy + 1
            elif(a.y1 == 0):
              iy = iy - 1
                            
            if (a.x1 == 0 and a.y1 == 0 and a.x2 == 0 and a.y2 == 0):
              ix = ix + 1
              iy = iy + 1
                        
            ix = ix + 1
            iy = iy + 1
            
            if (debug):
                out1.write("Par nr %d:\n" % i+1 + '\n')
                out2.write("Par nr %d:\n" % i+1 + '\n')
      
            if (verbose):
                out1.write(".Score %d\n" % a.d + '\n')
                out2.write(".Score %d\n" % a.d + '\n')
                
            out1.write("*** Link: %s ***\n" % (a.category) + '\n')            
            out2.write("*** Link: %s ***\n" % (a.category) + '\n')            
            
            while (prevx < ix):
              if (debug):
                  out1.write("Text 1:ix=%d prevx=%d\n" % (ix, prevx) + '\n')
                  out2.write("Text 1:ix=%d prevx=%d\n" % (ix, prevx) + '\n')
              soft_regions1[prevx].print_region(out1, out2, a.d)                  
              prevx = prevx + 1
            
            while (prevy < iy):
              if (debug): 
                  out1.write("Text 2:ix=%d prevx=%d\n" % (iy, prevy) + '\n')
                  out2.write("Text 2:ix=%d prevx=%d\n" % (iy, prevy) + '\n')                      
              soft_regions2[prevy].print_region(out1, out2, a.d)                  
              prevy = prevy + 1        
        
# Functions for Manipulating Regions

##//////////////////////////////////////////////////////
##  Region
##//////////////////////////////////////////////////////

class Region(object):
    """
    
    
    """
    def __init__(self, lines, length): 
        """
        
        """
        self.lines = lines
        self.length = length
        
    def print_region(self, out1, out2, score):
        """
        
        """        
        sentence_text = " ".join(self.lines)    
        out1.write("score: %s %s" % (score, sentence_text) + '\n')
        out2.write("score: %s %s" % (score, sentence_text) + '\n')
    
    def find_sub_regions(self, delimiter):
        """
        
        """
        result = []  
        
        region_lines = []
        num_lines = 0
        
        for line in self.lines:          
          if delimiter and not(line.find(delimiter) == -1):
              result.append(Region(region_lines, num_lines))
              num_lines = 0
              region_lines = []   
          else:              
              region_lines.append(line)
              num_lines = num_lines + 1
        
        if (region_lines): 
          result.append(Region(region_lines, num_lines))
           
        return (result, len(result))

##//////////////////////////////////////////////////////
##  Demonstration code
##//////////////////////////////////////////////////////

def demo_eval(alignments, gold_file):
    """
    
    """
    test_values = alignment_util.get_test_values(alignments)
    
    reference_values = alignment_util.get_reference_values(gold_file)
         
    accuracy = scores.accuracy(reference_values, test_values)
    
    print "accuracy: %.2f" % accuracy   
                
def demo():
    """
    A demonstration for the C{Aligner} class.  
    """
    
    hard_delimiter = '.EOP'
    soft_delimiter = '.EOS'
    
    # demo 1
    input_file1 = 'data/turinen.tok'
    input_file2 = 'data/turinde.tok'
    gold_file = 'data/ground_truth.txt'
    aligner = Aligner(input_file1, input_file2, hard_delimiter, soft_delimiter)
    
    alignments = aligner.align_regions(distance_measures.two_side_distance)
    
    demo_eval(alignments, gold_file)    
    
    # demo 2
    input_file1 = 'data/bovaryen.tok'
    input_file2 = 'data/bovaryfr.tok'
    gold_file = 'data/ground_truth_bovary.txt'
    aligner = Aligner(input_file1, input_file2, hard_delimiter, soft_delimiter)
    
    alignments = aligner.align_regions(distance_measures.two_side_distance)
    
    demo_eval(alignments, gold_file)    
    
if __name__=='__main__':
    demo()
    
    """
    if len(sys.argv) > 1:
        source_file_name = sys.argv[1]
        target_file_name = sys.argv[2]               
    else:
        sys.exit('Usage: arg1 - source input filename arg2 - target input filename')
    """
    
    

