
# Natural Language Toolkit: Gale-Church Aligner
#
# Copyright (C) 2001-2009 NLTK Project
# Author: Chris Crowner <ccrowner@gmail.com>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

import sys

import scores
from itertools import izip

## --NLTK--
## Import the nltk.aligner module, which defines the aligner interface
from api import *

import distance_measures
import align_util

# Based on Gale & Church 1993, "A Program for Aligning Sentences in Bilingual Corpora"
# This is a Python version of the C implementation by Mike Riley presented in the appendix
# of the paper. The documentation in the C program is retained where applicable.

##//////////////////////////////////////////////////////
##  Alignment
##//////////////////////////////////////////////////////

class Alignment(object):
    def __init__(self): 
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.d = 0  
        self.category = ''
                    
##//////////////////////////////////////////////////////
##  GaleChurchAligner
##//////////////////////////////////////////////////////

class GaleChurchAligner(AlignerI):
    def __init__(self, dist_funct, output_type):
        self.dist_funct = dist_funct
        # either 'standard_text_strings' or 'standard_id_strings'
        # or 'gc_text_strings' or 'gc_id_strings'
        self.output_type = output_type        
    
    def get_delimited_regions(self, base_type, input_file1, input_file2, hard_delimiter, soft_delimiter):
        lines1 = align_util.readlines(input_file1)
        if (base_type == 'token'):
            hard_regions1 = align_util.get_regions(lines1, hard_delimiter, soft_delimiter)
        elif (base_type == 'sentence'):
            hard_regions1 = align_util.get_paragraphs_sentences(lines1, hard_delimiter, soft_delimiter)
            
        lines2 = align_util.readlines(input_file2)
        if (base_type == 'token'):
            hard_regions2 = align_util.get_regions(lines2, hard_delimiter, soft_delimiter)
        elif (base_type == 'sentence'):
            hard_regions2 = align_util.get_paragraphs_sentences(lines2, hard_delimiter, soft_delimiter)
                
        if (len(hard_regions1) != len(hard_regions2)):
            print "align_regions: input files do not contain the same number of hard regions" + '\n'
            print "%s" % hard_delimiter + '\n'
            print "%s has %d and %s has %d" % (input_file1, len(hard_regions1), \
                                               input_file2, len(hard_regions2) + '\n')
            return ([],[])            
        
        return (hard_regions1, hard_regions2)        
    
    def align(self, hard_region1, hard_region2):                
        
        len1 = align_util.get_character_lengths(hard_region1)                
        number_of_soft_regions1 = len(hard_region1)
                
        len2 = align_util.get_character_lengths(hard_region2)            
        number_of_soft_regions2 = len(hard_region2)
        
        gc_alignment = self._seq_align(len1, len2, number_of_soft_regions1, number_of_soft_regions2)                
        
        if (self.output_type == 'standard_text_strings'):            
            output_alignment = align_util.convert_bead_to_tuples(gc_alignment, hard_region1, hard_region2)
        elif (self.output_type == 'gc_text_strings'):
            output_alignment = [gc_alignment]
                               
        return output_alignment        
           
    def _seq_align(self, x, y, nx, ny):    
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
                
        """
        distances = []
        path_x = []
        path_y = [] 
        
        first_len = nx + 1
        second_len = ny + 1
        
        distances = [[0] * second_len for c in range(first_len)]         
        path_x = [[0] * second_len for c in range(first_len)]              
        path_y = [[0] * second_len for c in range(first_len)]
                  
        d1 = sys.maxint
        d2 = sys.maxint
        d3 = sys.maxint
        d4 = sys.maxint
        d5 = sys.maxint
        d6 = sys.maxint
        
        for j in range(0, ny + 1):    
            for i in range(0, nx + 1):            
                if (i > 0 and j > 0):		
                    #/* substitution */
                    d1 = distances[i-1][j-1] + \
                        self.dist_funct(x[i-1], y[j-1], 0, 0)
                else:
                    d1 = sys.maxint
                    
                if (i > 0):	
                    #/* deletion */
                    d2 = distances[i-1][j] + \
                        self.dist_funct(x[i-1], 0, 0, 0)
                else:
                    d2 = sys.maxint
                    
                if (j > 0):		
                    #/* insertion */
                    d3 = distances[i][j-1] + \
                        self.dist_funct(0, y[j-1], 0, 0)
                else:
                    d3 = sys.maxint
                    
                if (i > 1 and j > 0):		
                    #/* contraction */
                    d4 = distances[i-2][j-1] + \
                        self.dist_funct(x[i-2], y[j-1], x[i-1], 0)
                else:
                    d4 = sys.maxint
                    
                if (i > 0 and j > 1):		
                    #/* expansion */
                    d5 = distances[i-1][j-2] + \
                        self.dist_funct(x[i-1], y[j-2], 0, y[j-1])
                else:
                    d5 = sys.maxint
                    
                if (i > 1 and j > 1):		
                    #/* melding */
                    d6 = distances[i-2][j-2] + \
                        self.dist_funct(x[i-2], y[j-2], x[i-1], y[j-1])
                else:
                    d6 = sys.maxint
     
                dmin = d1
                
                if (d2 < dmin):
                    dmin = d2
                    
                if (d3 < dmin):
                    dmin = d3
                    
                if (d4 < dmin):
                    dmin = d4
                    
                if (d5 < dmin):
                    dmin = d5
                    
                if (d6 < dmin):
                    dmin = d6
                     
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
                               
            ralign_dict[n] = ralign
            
            n = n + 1
            
            i = oi
            j = oj
           
        align_dict = {}
            
        for e in range(0, n):
            align_dict[n-e-1] = ralign_dict[e] 
               
        return align_dict
    
    """
    def output_alignments(self, filename1, filename2, debug, verbose):
        out1 = open(filename1 + '.al', 'w')
        out2 = open(filename2 + '.al', 'w')
        
        for alignment_key in self.alignments.keys():
            align = self.alignments[key]
            self._output_alignment(n, align, 
                                  soft_regions1, soft_regions2,
                                  debug, verbose)
    """
    def print_alignments(self, alignments, hard_regions1, hard_regions2): 
        hard_key = 0
        for hard_list in alignments:
            print "GC alignment: %s" % hard_list
            #print "hard regions 1: %s" % hard_regions1
            #print "hard regions 2: %s" % hard_regions2
            for alignment_dict in hard_list:
                print "Hard key: %s" % hard_key
                hard_region1 = hard_regions1[hard_key]
                print "Hard1: %s" % hard_region1
                hard_region2 = hard_regions2[hard_key]
                print "Hard2: %s" % hard_region2                
                print "align: %s" % alignment_dict                               
                
                for align_key in alignment_dict.keys():
                    alignment = alignment_dict[align_key]
                    print "inner align: (%s) %s" % (align_key, alignment)
                    if (alignment.category == '1 - 1'):
                        print "1-1: %s" % alignment.d
                        print "--------------------------"
                        print "%s" % hard_region1[align_key]
                        print "%s" % hard_region2[align_key]
                        print "--------------------------"
                    elif (alignment.category == '1 - 0'):
                        print "1-0: %s" % alignment.d
                        print "--------------------------"
                        print "%s" % hard_region1[align_key]                    
                        print "--------------------------"
                        pass
                    elif (alignment.category == '0 - 1'):
                        print "0-1: %s" % alignment.d
                        print "--------------------------"
                        print "%s" % hard_region2[align_key]                    
                        print "--------------------------"                    
                    elif (alignment.category == '2 - 1'):
                        print "2-1: %.2f" % alignment.d
                        print "--------------------------"
                        print "%s" % hard_region1[align_key]
                        print "%s" % hard_region1[align_key + 1]
                        print "%s" % hard_region2[align_key]
                        print "--------------------------"                    
                    elif (alignment.category == '1 - 2'):
                        print "1-2: %.2f" % alignment.d
                        print "--------------------------"
                        print "%s" % hard_region1[align_key]                    
                        print "%s" % hard_region2[align_key]
                        print "%s" % hard_region2[align_key + 1]
                        print "--------------------------"                        
                    elif (alignment.category == '2 - 2'):
                        print "1-2: %.2f" % alignment.d
                        print "--------------------------"
                        print "%s" % hard_region1[align_key]
                        print "%s" % hard_region1[align_key + 1]
                        print "%s" % hard_region2[align_key]
                        print "%s" % hard_region2[align_key + 1]
                        print "--------------------------"                        
                    else:
                        print "not supported alignment type"                
                
            hard_key = hard_key + 1        
    """
    
    def _output_alignment(self, n, align, soft_regions1, soft_regions2, debug, verbose):
        
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
              _print_region(soft_regions1[prevx], out1, out2, a.d)                  
              prevx = prevx + 1
            
            while (prevy < iy):
              if (debug): 
                  out1.write("Text 2:ix=%d prevx=%d\n" % (iy, prevy) + '\n')
                  out2.write("Text 2:ix=%d prevx=%d\n" % (iy, prevy) + '\n')                      
              _print_region(soft_regions2[prevy], out1, out2, a.d)                  
              prevy = prevy + 1        
              
   def _print_region(lines, out1, out2, score):
          
       sentence_text = " ".join(self.lines)    
       out1.write("score: %s %s" % (score, sentence_text) + '\n')
       out2.write("score: %s %s" % (score, sentence_text) + '\n')
    """
##//////////////////////////////////////////////////////
##  Demonstration code
##//////////////////////////////////////////////////////

def demo_eval(alignments, gold_file):
    """
    
    """
    alignment_mappings = align_util.get_alignment_links(alignments)
    
    print "Alignment mappings: %s" % alignment_mappings
    
    #test_values = align_util.get_test_values(alignments)
    
    reference_values = align_util.get_reference_values(gold_file)
    
    print "Reference values: %s" % reference_values
         
    #accuracy = scores.accuracy(reference_values, test_values)
    
    #print "accuracy: %.2f" % accuracy   
                
def demo():
    """
    A demonstration for the C{Aligner} class.  
    """
        
    hard_delimiter = '.EOP'
    soft_delimiter = '.EOS'
    
    # demo 1
    input_file1 = 'turinen.tok'
    input_file2 = 'turinde.tok'
    gold_file = 'ground_truth.txt'
    
    gc = GaleChurchAligner(distance_measures.two_side_distance, 'gc_text_strings')
    
    (regions1, regions2) = gc.get_delimited_regions('token',
                                                    input_file1, input_file2, 
                                                    hard_delimiter, soft_delimiter)
    
    gc_alignment = gc.batch_align(regions1, regions2)  
    
    print "Alignment0: %s" % gc_alignment
        
    gc.print_alignments(gc_alignment, regions1, regions2)
    
    demo_eval(gc_alignment, gold_file)    
        
    # demo 2
    
    hard_delimiter = '.EOP'
    soft_delimiter = '.EOS'
    
    input_file1 = 'bovaryen.tok'
    input_file2 = 'bovaryfr.tok'
    gold_file = 'ground_truth_bovary.txt'
    
    gc = GaleChurchAligner(distance_measures.two_side_distance, 'gc_text_strings')
    
    (regions1, regions2) = gc.get_delimited_regions('token',
                                                    input_file1, input_file2, 
                                                    hard_delimiter, soft_delimiter)
                                                                
    gc_alignment = gc.batch_align(regions1, regions2)  
    
    print "Alignment1: %s" % gc_alignment
        
    gc.print_alignments(gc_alignment, regions1, regions2)
    
    demo_eval(gc_alignment, gold_file)
    
    # demo 3
    
    std = GaleChurchAligner(distance_measures.two_side_distance, 'standard_text_strings')
    
    s_para_1 = [['asddd a rrg'],['hg']]
    s_para_2 = [['jk nkp'],['fg']]
    s2 = [s_para_1, s_para_2]
    
    t_para_1 = [['12345 6 78'],['910']]
    t_para_2 = [['45 67'],['89']]
    t2 = [t_para_1, t_para_2]
        
    standard_alignment2 = std.batch_align(s2, t2)
    
    print "Alignment2: %s" % standard_alignment2
    
    # demo 4
    
    s3 = [['asddd','a','rrg'],['hg']]
    t3 = [['12345','6','78'],['910']]
    
    standard_alignment3 = std.align(s3, t3)
    
    print "Alignment3: %s" % standard_alignment3
    
    # demo 5
    
    top_down_alignments = std.top_down_align(s3, t3)  
    
    for alignment in top_down_alignments:
        print "Top down align: %s" % alignment
    
if __name__=='__main__':
    demo()
        

