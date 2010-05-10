
import align_util
import align
import distance_measures

import sys

# import for madame_bovary_test()
from nltk.corpus.reader import plaintext, util
from nltk.text import Text
from nltk.data import *
from nltk.tokenize import *
import codecs

##//////////////////////////////////////////////////////
##  Demonstration code
##//////////////////////////////////////////////////////

"""
def demo_eval(alignments, gold_file):
    
    alignment_mappings = align_util.get_alignment_links(alignments)
    
    print "Alignment mappings: %s" % alignment_mappings
    
    #test_values = align_util.get_test_values(alignments)
    
    reference_values = align_util.get_reference_values(gold_file)
    
    print "Reference values: %s" % reference_values
         
    #accuracy = scores.accuracy(reference_values, test_values)
    
    #print "accuracy: %.2f" % accuracy
"""
                
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
    
    gc = align.GaleChurchAligner(distance_measures.two_side_distance, 'original', 
                                    'bead_objects', print_flag=True)
    
    (regions1, regions2) = gc.get_delimited_regions('token',
                                                    input_file1, input_file2, 
                                                    hard_delimiter, soft_delimiter)
    
    gc_alignment = gc.batch_align(regions1, regions2)  
    
    print "Alignment0: %s" % gc_alignment
        
    #demo_eval(gc_alignment, gold_file)    
        
    # demo 2
    
    hard_delimiter = '.EOP'
    soft_delimiter = '.EOS'
    
    input_file1 = 'data/bovaryen.tok'
    input_file2 = 'data/bovaryfr.tok'
    gold_file = 'data/ground_truth_bovary.txt'
    
    gc = align.GaleChurchAligner(distance_measures.two_side_distance, 'original', 
                                    'text_tuples', print_flag=True)
    
    (regions1, regions2) = gc.get_delimited_regions('token',
                                                    input_file1, input_file2, 
                                                    hard_delimiter, soft_delimiter)
                                                                
    gc_alignment = gc.batch_align(regions1, regions2)  
    
    print "Alignment1: %s" % gc_alignment
        
    #demo_eval(gc_alignment, gold_file)
    
    # demo 3
    
    std = align.GaleChurchAligner(distance_measures.two_side_distance, 'original', 
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
    
    #s3 = [['asddd','a','rrg'],['hg']]
    #t3 = [['12345','6','78'],['910']]
    
    s3 = [[['asddd','a','rrg'],['hg']],[['xxxxx','y','rrg'],['pp']]]
    t3 = [[['12345','6','78'],['910']],[['wally','i','am'],['dob']]]
    
    standard_alignment3 = std.align(s3, t3)
    
    print "Alignment3: %s" % standard_alignment3
    
    # demo 5
    
    top_down_alignments = std.recursive_align(s3, t3, [])  
    
    for alignment in top_down_alignments:
        print "Top down align: %s" % alignment

def madame_bovary_test(source_file, target_file, source_pickle_file, target_pickle_file):
    
    source_plaintext_reader = plaintext.PlaintextCorpusReader('', 
        [source_file],
        word_tokenizer=WhitespaceTokenizer(),
        sent_tokenizer=LazyLoader(source_pickle_file),              
        encoding='utf8')
        
    target_plaintext_reader = plaintext.PlaintextCorpusReader('', 
        [target_file],
        word_tokenizer=WhitespaceTokenizer(),
        sent_tokenizer=LazyLoader(target_pickle_file),              
        encoding='utf8')
 
    source_chapter = [source_para for source_para in source_plaintext_reader.paras()]
       
    target_chapter = [target_para for target_para in target_plaintext_reader.paras()]
      
    std = align.GaleChurchAligner(distance_measures.three_side_distance, 'extended', 'bead_objects', print_flag=True)
        
    source_paras = source_plaintext_reader.paras()
    target_paras = target_plaintext_reader.paras()
 
    top_down_alignments = std.recursive_align(source_chapter, target_chapter, [])  
        
if __name__=='__main__':
    demo()    
    
    # usage: python test2.py data/chapter1_madame_bovary_fr.txt data/chapter1_madame_bovary_en.txt fr en
    if len(sys.argv) > 1:
        source_file = sys.argv[1]
        target_file = sys.argv[2]
        source_lang = sys.argv[3]
        target_lang = sys.argv[4]
    else:
        sys.exit('Usage: arg1 - input filename arg2 - output filename arg3 - source language arg4 - target language')
    
        
    if (source_lang == "fr"):
        source_pickle_file = 'tokenizers/punkt/french.pickle'
    elif (source_lang == "en"):
        source_pickle_file = 'tokenizers/punkt/english.pickle'
    else:
        source_pickle_file = ''
   
    if (target_lang == "fr"):
        target_pickle_file = 'tokenizers/punkt/french.pickle'
    elif (target_lang == "en"):
        target_pickle_file = 'tokenizers/punkt/english.pickle'
    else:
        target_pickle_file = ''
    
        
    if (source_pickle_file) and (target_pickle_file):
        madame_bovary_test(source_file, target_file, source_pickle_file, target_pickle_file)
    

