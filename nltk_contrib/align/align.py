
# Natural Language Toolkit: Gale-Church Aligner
#
# Copyright (C) 2001-2011 NLTK Project
# Author: Chris Crowner <ccrowner@gmail.com>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

import sys
from itertools import izip

from nltk.metrics import scores

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
                    
class AlignmentExtended(object):
    def __init__(self): 
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.x3 = 0
        self.y3 = 0
        self.d = 0  
        self.category = ''
                    
##//////////////////////////////////////////////////////
##  GaleChurchAligner
##//////////////////////////////////////////////////////

class GaleChurchAligner(AlignerI):
    def __init__(self, dist_funct, alignment_type, output_format, print_flag=False):
        self.dist_funct = dist_funct
        # either 'original' or 'extended'
        self.alignment_type = alignment_type
        # either 'bead_objects' (the Alignment objects above - in a dict)
        # or 'text_tuples' (source text to target text mappings - in a list)
        # or 'index_tuples' (source indices to target indices - in a list)
        self.output_format = output_format
        # ideally, bead objects would be printed from the calling routines
        # unfortunately, the source and target text may be unavailable then for printing
        # (eg recursive_align) hence the print_flag, which is used in 'align' which is
        # common to both batch_align and recursive_align
        # note: in future, will post update that adds ability to output alignment files 
        # in formats such as ARCADE and TEI (also can read TEI files as input)
        # also coming later is printing in unicode - sorry about that
        self.print_flag = print_flag
    
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
                
        if (self.alignment_type == 'original'):
            alignment = self._seq_align(len1, len2, number_of_soft_regions1, number_of_soft_regions2)
        elif (self.alignment_type == 'extended'):
            alignment = self._seq_align_extended(len1, len2, number_of_soft_regions1, number_of_soft_regions2)

        if (self.output_format == 'text_tuples'):      
            (output_alignment, indices_mapping) = \
                align_util.convert_bead_to_tuples(alignment, hard_region1, hard_region2)
            if (self.print_flag):
                align_util.print_alignment_text_mapping(output_alignment)
        elif (self.output_format == 'index_tuples'):      
            (text_mapping, output_alignment) = \
                align_util.convert_bead_to_tuples(alignment, hard_region1, hard_region2)
            if (self.print_flag):
                align_util.print_alignment_index_mapping(output_alignment)
        else: # the Gale-Church alignment "bead"  objects - a dictionary of objects
            output_alignment = alignment
            if (self.print_flag):
                align_util.print_alignments(output_alignment, hard_region1, hard_region2)
            
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
                  
        d1 = d2 = d3 = d4 = d5 = d6 = sys.maxint
        
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
                               
            ralign_dict[n] = ralign
            
            n = n + 1
            
            i = oi
            j = oj
           
        align_dict = {}
            
        for e in range(0, n):
            align_dict[n-e-1] = ralign_dict[e] 
               
        return align_dict
        
    def _seq_align_extended(self, x, y, nx, ny):    
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
                  
        d1 = d2 = d3 = d4 = d5 = d6 = d7 = d8 = d9 = d10 = d11 = sys.maxint
        
        for j in range(0, ny + 1):    
            for i in range(0, nx + 1):            
                if (i > 0 and j > 0):		
                    #/* substitution */          /* 1-1 */
                    d1 = distances[i-1][j-1] + \
                        self.dist_funct(x[i-1], y[j-1], 0, 0, 0, 0)
                else:
                    d1 = sys.maxint
                    
                if (i > 0):	
                    #/* deletion */              /* 1-0 */
                    d2 = distances[i-1][j] + \
                        self.dist_funct(x[i-1], 0, 0, 0, 0, 0)
                else:
                    d2 = sys.maxint
                    
                if (j > 0):		
                    #/* insertion */             /* 0-1 */
                    d3 = distances[i][j-1] + \
                        self.dist_funct(0, y[j-1], 0, 0, 0, 0)
                else:
                    d3 = sys.maxint
                    
                if (i > 1 and j > 0):		
                    #/* contraction */           /* 2-1 */
                    d4 = distances[i-2][j-1] + \
                        self.dist_funct(x[i-2], y[j-1], x[i-1], 0, 0, 0)
                else:
                    d4 = sys.maxint
                    
                if (i > 0 and j > 1):		     
                    #/* expansion */             /* 1-2 */
                    d5 = distances[i-1][j-2] + \
                        self.dist_funct(x[i-1], y[j-2], 0, y[j-1], 0, 0)
                else:
                    d5 = sys.maxint
                    
                if (i > 1 and j > 1):		
                    #/* melding */               /* 2-2 */
                    d6 = distances[i-2][j-2] + \
                        self.dist_funct(x[i-2], y[j-2], x[i-1], y[j-1], 0, 0)
                else:
                    d6 = sys.maxint
                    
                if (i > 2 and j > 0):		
                    #/* contraction */           /* 3-1 */
                    d7 = distances[i-3][j-1] + \
                        self.dist_funct(x[i-3], y[j-1], x[i-2], 0, x[i-1], 0)
                else:
                    d7 = sys.maxint
                    
                if (i > 2 and j > 1):		
                    #/* contraction */           /* 3-2 */
                    d8 = distances[i-3][j-2] + \
                        self.dist_funct(x[i-3], y[j-1], x[i-2], y[j-2], x[i-1], 0)
                else:
                    d8 = sys.maxint
                    
                if (i > 0 and j > 2):		
                    #/* expansion */             /* 1-3 */
                    d9 = distances[i-1][j-3] + \
                        self.dist_funct(x[i-1], y[j-3], 0, y[j-2], 0, y[j-1])
                else:
                    d9 = sys.maxint
                    
                if (i > 1 and j > 2):		
                    #/* expansion */             /* 2-3 */
                    d10 = distances[i-2][j-3] + \
                        self.dist_funct(x[i-3], y[j-3], x[i-2], y[j-2], 0, y[j-1])
                else:
                    d10 = sys.maxint
                                                        
                if (i > 2 and j > 2):		
                    #/* melding */               /* 3-3 */
                    d11 = distances[i-3][j-3] + \
                        self.dist_funct(x[i-3], y[j-3], x[i-2], y[j-2], x[i-1], y[j-1])
                else:
                    d11 = sys.maxint
     
                dmin = min(d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11)
                
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
                elif (dmin == d6):			                   
                    distances[i][j] = d6                
                    path_x[i][j] = i - 2
                    path_y[i][j] = j - 2
                elif (dmin == d7):
                    distances[i][j] = d7                
                    path_x[i][j] = i - 3
                    path_y[i][j] = j - 1               
                elif (dmin == d8):
                    distances[i][j] = d8                
                    path_x[i][j] = i - 3
                    path_y[i][j] = j - 2                
                elif (dmin == d9):
                    distances[i][j] = d9                
                    path_x[i][j] = i - 1
                    path_y[i][j] = j - 3                 
                elif (dmin == d10):
                    distances[i][j] = d10                
                    path_x[i][j] = i - 2
                    path_y[i][j] = j - 3
                elif (dmin == d11):			                   
                    distances[i][j] = d11                
                    path_x[i][j] = i - 3
                    path_y[i][j] = j - 3
        n = 0
        
        ralign_dict = {}
        
        i = nx
        j = ny
        while (i > 0 or j > 0):                
            oi = path_x[i][j]       
            oj = path_y[i][j]
            di = i - oi
            dj = j - oj
            
            ralign = AlignmentExtended()
                          
            if (di == 1 and dj == 1):
                #/* substitution */            
                ralign.x1 = x[i-1]
                ralign.y1 = y[j-1]
                ralign.x2 = 0
                ralign.y2 = 0
                ralign.x3 = 0
                ralign.y3 = 0
                ralign.d = distances[i][j] - distances[i-1][j-1] 
                ralign.category = '1 - 1'                
            elif (di == 1 and dj == 0):
                #/* deletion */
                ralign.x1 = x[i-1]
                ralign.y1 = 0
                ralign.x2 = 0
                ralign.y2 = 0
                ralign.x3 = 0
                ralign.y3 = 0
                ralign.d = distances[i][j] - distances[i-1][j]
                ralign.category = '1 - 0'
            elif (di == 0 and dj == 1):
                #/* insertion */
                ralign.x1 = 0
                ralign.y1 = y[j-1]
                ralign.x2 = 0
                ralign.y2 = 0
                ralign.x3 = 0
                ralign.y3 = 0
                ralign.d = distances[i][j] - distances[i][j-1]        
                ralign.category = '0 - 1'
            elif (dj == 1):
                #/* contraction */
                ralign.x1 = x[i-2]
                ralign.y1 = y[j-1]
                ralign.x2 = x[i-1]
                ralign.y2 = 0
                ralign.x3 = 0
                ralign.y3 = 0
                ralign.d = distances[i][j] - distances[i-2][j-1]     
                ralign.category = '2 - 1'
            elif (di == 1):
                #/* expansion */
                ralign.x1 = x[i-1]
                ralign.y1 = y[j-2]
                ralign.x2 = 0
                ralign.y2 = y[j-1]
                ralign.x3 = 0
                ralign.y3 = 0
                ralign.d = distances[i][j] - distances[i-1][j-2]    
                ralign.category = '1 - 2'
            elif (di == 2 and dj == 2): 
                #/* di == 2 and dj == 2 */ { /* melding */
                ralign.x1 = x[i-2]
                ralign.y1 = y[j-2]
                ralign.x2 = x[i-1]
                ralign.y2 = y[j-1]
                ralign.x3 = 0
                ralign.y3 = 0
                ralign.d = distances[i][j] - distances[i-2][j-2]
                ralign.category = '2 - 2'
            elif (di == 3 and dj == 1):
                #/* deletion */
                ralign.x1 = x[i-3]
                ralign.y1 = y[j-1]
                ralign.x2 = x[i-2]
                ralign.y2 = 0
                ralign.x3 = x[i-1]
                ralign.y3 = 0
                ralign.d = distances[i][j] - distances[i-3][j-1]
                ralign.category = '3 - 1'
            elif (di == 3 and dj == 2):
                #/* insertion */
                ralign.x1 = x[i-3]
                ralign.y1 = y[j-1]
                ralign.x2 = x[i-2]
                ralign.y2 = y[j-2]
                ralign.x3 = x[i-1]
                ralign.y3 = 0
                ralign.d = distances[i][j] - distances[i-3][j-2]        
                ralign.category = '3 - 2'
            elif (di == 1 and dj == 3):
                #/* deletion */
                ralign.x1 = x[i-1]
                ralign.y1 = y[j-3]
                ralign.x2 = 0
                ralign.y2 = y[j-2]
                ralign.x3 = 0
                ralign.y3 = y[j-1]
                ralign.d = distances[i][j] - distances[i-1][j-3]
                ralign.category = '1 - 3'
            elif (di == 2 and dj == 3):
                #/* insertion */
                ralign.x1 = x[i-3]
                ralign.y1 = y[j-3]
                ralign.x2 = x[i-2]
                ralign.y2 = y[j-2]
                ralign.x3 = 0
                ralign.y3 = y[j-1]
                ralign.d = distances[i][j] - distances[i-2][j-3]        
                ralign.category = '2 - 3'
            elif (di == 3 and dj == 3): 
                ralign.x1 = x[i-3]
                ralign.y1 = y[j-3]
                ralign.x2 = x[i-2]
                ralign.y2 = y[j-2]
                ralign.x3 = x[i-1]
                ralign.y3 = y[j-1]
                ralign.d = distances[i][j] - distances[i-3][j-3]
                ralign.category = '3 - 3'
                               
            ralign_dict[n] = ralign
            
            n = n + 1
            
            i = oi
            j = oj
           
        align_dict = {}
            
        for e in range(0, n):
            align_dict[n-e-1] = ralign_dict[e] 
               
        return align_dict
        
    
##//////////////////////////////////////////////////////
##  Demonstration code
##//////////////////////////////////////////////////////

def demo_eval(alignments, gold_file):
    """
    
    """
    alignment_mappings = align_util2.get_alignment_links(alignments)
    
    print "Alignment mappings: %s" % alignment_mappings
    
    #test_values = align_util.get_test_values(alignments)
    
    reference_values = align_util2.get_reference_values(gold_file)
    
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
    input_file1 = 'data/turinen.tok'
    input_file2 = 'data/turinde.tok'
    gold_file = 'data/ground_truth.txt'
    
    gc = GaleChurchAligner(distance_measures2.two_side_distance, 'original', 
                            'bead_objects', print_flag=True)
    
    (regions1, regions2) = gc.get_delimited_regions('token',
                                                    input_file1, input_file2, 
                                                    hard_delimiter, soft_delimiter)
    
    gc_alignment = gc.batch_align(regions1, regions2)  
    
    print "Alignment0: %s" % gc_alignment
   
    demo_eval(gc_alignment, gold_file)    
        
    # demo 2
    
    hard_delimiter = '.EOP'
    soft_delimiter = '.EOS'
    
    input_file1 = 'data/bovaryen.tok'
    input_file2 = 'data/bovaryfr.tok'
    gold_file = 'data/ground_truth_bovary.txt'
    
    gc = GaleChurchAligner(distance_measures2.two_side_distance, 'original', 
                            'text_tuples', print_flag=True)
    
    (regions1, regions2) = gc.get_delimited_regions('token',
                                                    input_file1, input_file2, 
                                                    hard_delimiter, soft_delimiter)
                                                                
    gc_alignment = gc.batch_align(regions1, regions2)  
    
    print "Alignment1: %s" % gc_alignment
 
    demo_eval(gc_alignment, gold_file)
    
    # demo 3
    
    std = GaleChurchAligner(distance_measures2.two_side_distance, 'original', 
                            'text_tuples', print_flag=True)
    
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
    
    top_down_alignments = std.recursive_align(s3, t3)  
    
    for alignment in top_down_alignments:
        print "Top down align: %s" % alignment
    
if __name__=='__main__':
    demo()
        

