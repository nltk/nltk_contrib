# Natural Language Toolkit: Aligner Interface

"""
Interfaces for aligning bitexts

L{AlignerI} is a standard interface for X{bilingual alignment}

"""
from nltk.internals import deprecated, overridden
from itertools import izip

##//////////////////////////////////////////////////////
# Alignment Interfaces
##//////////////////////////////////////////////////////

class AlignerI(object):
    """
    A processing interface for I{aligning} two lists of text sections
    (i.e., mapping text sections from a source text to text sections from a target text)
    
    Subclasses must define:      
      - either L{align()} or L{batch_align()} (or both)
      
    Subclasses may define:
      - either L{prob_align()} or L{batch_prob_align()} (or both)
    """
    def align(self, source_text_sections, target_text_sections):
        """
        @return: the alignment of the two texts.
        @rtype: a C{list} of C{tuple} pairs where 
        1. the first element is a section of source text 
        2. the second element is the aligned section(s) of target text
           or 
        1. the first element is an identifier of a section of source text 
        2. the second element is identifier(s) of aligned section(s) of target text
        The second option is necessary for cases where crossing alignments are permitted, as
        in word alignment implementations.
        
        Both elements of the returned tuples are lists - either empty lists, 
        (in the case of ommitted/deleted text) or single or multiple element lists
        """
        if overridden(self.batch_align):
            return self.batch_align([source_text_sections], [target_text_sections])
        else:
            raise NotImplementedError()

    def batch_align(self, source, target):
        """
        Apply L{self.align()} to the elements of the C{source} and C{target}
            texts.  I.e.:

            >>> return [self.align(st, tt) for (st, tt) in izip(source, target)]

        @rtype: C{list} of I{alignments}
        """
        return [self.align(st, tt) for (st, tt) in izip(source, target)]
    
    def recursive_align(self, source, target, alignments):
        """
        Apply L{self.align()} to the elements of the C{source} and C{target}
            texts in a top-down manner

        @rtype: C{list} of I{alignments}
        """
        standard_alignment = self.align(source, target)
       
        alignments.append(standard_alignment)
                
        alignment_mapping = None
        if (self.output_format == 'text_tuples'):            
            alignment_mapping = standard_alignment
        
        import align_util
        
        if (self.output_format == 'bead_objects'):
            (alignment_mapping, alignment_mapping_indices) = align_util.convert_bead_to_tuples(standard_alignment, source, target)
             
        for entry in alignment_mapping:                            
            source_list = [item for item in entry[0]]                
            target_list = [item for item in entry[1]] 
            
            if len(source_list) == 0 or len(target_list) == 0:                
                break
            if not(isinstance(source_list[0], list)) or not(isinstance(target_list[0], list)):                
                break
                
            lower_align = self.recursive_align(source_list, target_list, alignments)                        
            
        return alignments
    
    def textfile_align(self, source_file, target_file):
        """
        Apply L{self.batch_align()} to the text of two files. This method will
        parse the input files into the list structures required
        (using an input routine? punkt.py?)            

        @rtype: C{list} of I{alignments}
        """
        pass
        
    def text_align(self, source_text, target_text):
        """
        Apply L{self.align()} to source and target text. This method will
        parse the input texts (using an input routine? punkt.py?).
        
        This method is for primarily for testing alignments using the Python interpreter.
        For example, cutting and pasting two texts from Google Translate.

        @rtype: C{list} of I{alignments}
        """
        pass
        
    def prob_align(self, featureset):
        """
        @return: a probability distribution over labels for the given
            featureset.
        @rtype: L{ProbDistI <nltk.probability.ProbDistI>}
        """
        if overridden(self.batch_prob_classify):
            return self.batch_prob_align([featureset])[0]
        else:
            raise NotImplementedError()
    

    def batch_prob_align(self, featuresets):
        """
        Apply L{self.prob_classify()} to each element of C{featuresets}.  I.e.:

            >>> return [self.prob_classify(fs) for fs in featuresets]

        @rtype: C{list} of L{ProbDistI <nltk.probability.ProbDistI>}
        """
        return [self.prob_classify(fs) for fs in featuresets]


