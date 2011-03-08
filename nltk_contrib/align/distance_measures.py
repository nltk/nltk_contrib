
# Natural Language Toolkit: Gale-Church Aligner Distance Functions
#
# Copyright (C) 2001-2011 NLTK Project
# Author: Chris Crowner <ccrowner@gmail.com>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

import math

BIG_DISTANCE = 2500

# Based on Gale & Church 1993, "A Program for Aligning Sentences in Bilingual Corpora"
# This is a Python version of the C implementation by Mike Riley presented in the appendix
# of the paper. The documentation in the C program is retained where applicable.
    
# Local Distance Function


def pnorm(z):
    """ 
    Returns the area under a normal distribution
    from -inf to z standard deviations 
    
    @type z: C{float}
    @param z: 
        
    @return: the area under a normal distribution
             from -inf to z standard deviations
    @rtype: C{float}    
        
    """
    t = 1/(1 + 0.2316419 * z)
    pd = 1 - 0.3989423 *  \
    math.exp(-z * z/2) * \
      ((((1.330274429 * t - 1.821255978) * t \
     + 1.781477937) * t - 0.356563782) * t + 0.319381530) * t
    # /* see Gradsteyn & Rhyzik, 26.2.17 p932 */
    return pd
   
def match(len1, len2):
    """
    Return -100 * log probability that an English sentence of length
    len1 is a translation of a foreign sentence of length len2.  The
    probability is based on two parameters, the mean and variance of
    number of foreign characters per English character.
        
    @type len1: C{int}
    @param len1: 
        
    @type len2: C{int}
    @param len2: 
        
    
    @return: the probability that an English sentence of length
             len1 is a translation of a foreign sentence of length len2.
    @rtype: C{int}    
   
    """
    #/* foreign characters per english character */
    foreign_chars_per_eng_char = 1
    
    #/* variance per english character */
    var_per_eng_char = 6.8 	
    
    if (len1==0 and len2==0): 
        return 0    
    
    try:
        mean = (len1 + len2/foreign_chars_per_eng_char)/2          
    
        z = (foreign_chars_per_eng_char * len1 - len2)/math.sqrt(var_per_eng_char * mean)
    except ZeroDivisionError:
        z = float(999999999999999999999)
    
    #/* Need to deal with both sides of the normal distribution */
    if (z < 0):
        z = -z
        
    pd = 2 * (1 - pnorm(z))
    
    if (pd > 0):
        return (-100 * math.log(pd))
    else:
        return (BIG_DISTANCE);

def two_side_distance(x1, y1, x2, y2):
    """
    Calculate a distance metric .
    
    @type x1: C{int}
    @param x1:
        
    @type y1: C{int}
    @param y1:
        
    @type x2: C{int}
    @param x2:
        
    @type y2: C{int}
    @param y2:    
    
    @return: 
    @rtype: C{int}    
   
    """
    penalty21 = 230		
    #/* -100 * log([prob of 2-1 match] / [prob of 1-1 match]) */
    
    penalty22 = 440
    #/* -100 * log([prob of 2-2 match] / [prob of 1-1 match]) */
    
    penalty01 = 450
    #/* -100 * log([prob of 0-1 match] / [prob of 1-1 match]) */
        
    if (x2 == 0 and y2 == 0):    
        if (x1 == 0):			
            # /* insertion */
            return (match(x1, y1) + penalty01)          
        elif(y1 == 0):		
            # /* deletion */
            return (match(x1, y1) + penalty01)    
        else: 
            #/* substitution */
            return (match(x1, y1))     
    elif (x2 == 0):		
        #/* expansion */
        return (match(x1, y1 + y2) + penalty21)    
    elif (y2 == 0):		
        #/* contraction */
        return (match(x1 + x2, y1) + penalty21)     
    else:				
        # /* melding */
        return (match(x1 + x2, y1 + y2) + penalty22)
    
        
def three_side_distance(x1, y1, x2, y2, x3, y3):
    """
    Calculate a distance metric .
    
    @type x1: C{int}
    @param x1:
        
    @type y1: C{int}
    @param y1:
        
    @type x2: C{int}
    @param x2:
        
    @type y2: C{int}
    @param y2:    
    
    @return: 
    @rtype: C{int}    
   
    """
    penalty21 = 230		
    #/* -100 * log([prob of 2-1 match] / [prob of 1-1 match]) */
    
    penalty22 = 440
    #/* -100 * log([prob of 2-2 match] / [prob of 1-1 match]) */
    
    penalty01 = 450
    #/* -100 * log([prob of 0-1 match] / [prob of 1-1 match]) */
    
    penalty31 = 230
    
    penalty13 = 230
    
    penalty32 = 600
    
    penalty23 = 600
    
    penalty33 = 650
    
    if (x3 == 0 and y3 == 0):
        if (x2 == 0 and y2 == 0):    
            if (x1 == 0):			
                # /* insertion */
                return (match(x1, y1) + penalty01)          
            elif(y1 == 0):		
                # /* deletion */
                return (match(x1, y1) + penalty01)    
            else: 
                #/* substitution */
                return (match(x1, y1))     
        elif (x2 == 0):		
            #/* expansion */
            return (match(x1, y1 + y2) + penalty21)    
        elif (y2 == 0):		
            #/* contraction */
            return (match(x1 + x2, y1) + penalty21)     
        else:				
            # /* melding */
            return (match(x1 + x2, y1 + y2) + penalty22)
    else:
        if (x3 == 0):
            if (x2 == 0):
                #/* expansion  1-3 */
                return (match(x1, y1 + y2 + y3) + penalty13)
            else:
                #/* expansion  2-3 */
                return (match(x1 + x2, y1 + y2 + y3) + penalty23)
        elif (y3 == 0):
            if (y2 == 0):
                #/* contraction  3-1 */
                return (match(x1 + x2 + x3, y1) + penalty31)
            else:
                #/* contraction  3-2 */
                return (match(x1 + x2 + x3, y1 + y2) + penalty32)                 
        else:				
            # /* melding */
            return (match(x1 + x2 + x3, y1 + y2 + y3) + penalty33)
