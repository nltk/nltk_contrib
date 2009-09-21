# Natural Language Toolkit (NLTK) Coreference Chunking Utilities
#
# Copyright (C) 2001-2009 NLTK Project 
# Author: Joseph Frazee <jfrazee@mail.utexas.edu>
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT

import re
import os
import sys

import nltk
from nltk.util import LazyMap
from nltk.data import BufferedGzipFile
from nltk.tree import Tree
from nltk.classify import NaiveBayesClassifier, MaxentClassifier
from nltk.tag import ClassifierBasedTagger
from nltk.tag.crf import MalletCRF
from nltk.chunk import ChunkScore

from nltk_contrib.coref import ChunkTaggerI

class ChunkTaggerFeatureDetector(dict):
    """
    A simple feature detector for training a C{ChunkTagger}.
    """
    def __init__(self, tokens, index=0, history=None, **kwargs):
        """
        @param tokens: a list of tokens containing a token to featurize.
        @type tokens: C{list} of C{tuple}
        @param index: the list position of the token to featurize.
        @type index: C{int}
        @param history: the previous features and classifier predictions
        @type history: C{list} of C{dict}
        @kwparam window: the number of previous/next tokens to include in the
            features
        @type window: C{int}
        """
        dict.__init__(self)
        
        window = kwargs.get('window', 2)
        # TODO: This will tag (X, Y, Z) to ((X, Y, Z), W) as well as (X, Y) to
        # ((X, Y), W). Do we want this?
        spelling, pos = tokens[index][:2]
        
        self['spelling'] = spelling
        self['word'] = spelling.lower()
        self['pos'] = pos
        self['isupper'] = spelling.isupper()
        self['islower'] = spelling.islower()
        self['istitle'] = spelling.istitle()
        self['isalnum'] = spelling.isalnum()
        self['isnumeric'] = \
            bool(re.match(r'^(\d{1,3}(\,\d{3})*|\d+)(\.\d+)?$', spelling))
        for i in range(1, 4):
            self['prefix_%d' % i] = spelling[:i]
            self['suffix_%d' % i] = spelling[-i:]
        
        if window > 0 and index > 0:
            prev_feats = \
                self.__class__(tokens, index - 1, history, window=window - 1)
            for key, val in prev_feats.items():
                if not key.startswith('next_'):
                    self['prev_%s' % key] = val
        
        if window > 0 and index < len(tokens) - 1:
            next_feats = self.__class__(tokens, index + 1, window=window - 1)
            for key, val in next_feats.items():
                if not key.startswith('prev_'):
                    self['next_%s' % key] = val
        
        if 'prev_pos' in self:
            self['prev_pos_pair'] = '%s/%s' % \
                (self.get('prev_pos'), self.get('pos'))
        
        if history and index > 0:
            self['prev_tag'] = history[index - 1]


class AbstractChunkTagger(ChunkTaggerI):
    def parse(self, sent):
        return self.__iob2tree(self.tag(sent))
        
    def batch_parse(self, sents):
        return map(self.__iob2tree, self.batch_tag(sents))
    
    def chunk(self, sent):
        return self.__tree2chunks(self.parse(sent))
        
    def batch_chunk(self, sents):
        return map(self.__tree2chunks, self.batch_parse(sents))
        
    def __iob2tree(self, tagged_sent):
        return tokens2tree(map(flatten, tagged_sent))
        
    def __tree2chunks(self, tree):
        chunks = []
        for chunk in tree:
            if isinstance(chunk, Tree):
                chunks.append(chunk.leaves())
            elif isinstance(chunk, tuple):
                chunks.append(chunk)
            else:
                raise
        return chunks    
        
    def test(self, iob_sents, **kwargs):
        return test_chunk_tagger(self, iob_sents, 
            verbose=kwargs.get('verbose', False))


class NaiveBayesChunkTagger(ClassifierBasedTagger, AbstractChunkTagger):
    @classmethod
    def train(cls, iob_sents, **kwargs):
        train = LazyMap(lambda sent: map(unflatten, sent), iob_sents)
        fd = ChunkTaggerFeatureDetector
        return cls(fd, train, NaiveBayesClassifier.train)
        

class MaxentChunkTagger(ClassifierBasedTagger, AbstractChunkTagger):
    @classmethod
    def train(cls, iob_sents, **kwargs):
        algorithm = kwargs.get('algorithm', 'megam')
        gaussian_prior_sigma = kwargs.get('gaussian_prior_sigma', 100)
        count_cutoff = kwargs.get('count_cutoff', 1)
        min_lldelta = kwargs.get('min_lldelta', 1e-7)        
        def __maxent_train(fs):
            return MaxentClassifier.train(fs, 
                algorithm=algorithm,
                gaussian_prior_sigma=gaussian_prior_sigma,
                count_cutoff=count_cutoff,
                min_lldelta=min_lldelta)
        train = LazyMap(lambda sent: map(unflatten, sent), iob_sents)
        fd = ChunkTaggerFeatureDetector
        return cls(fd, train, __maxent_train)


class CRFChunkTagger(MalletCRF, AbstractChunkTagger):
    def tag(self, sent):
        return self.batch_tag([sent])[0]
    
    @classmethod
    def train(cls, iob_sents, **kwargs):
        gaussian_variance = kwargs.get('gaussian_variance', 10)
        default_label = kwargs.get('default_label', 'O')
        transduction_type = kwargs.get('transduction_type', 'VITERBI_FBEAMKL')
        if kwargs.get('trace'):
            trace = kwargs.get('trace', 2)
        elif kwargs.get('verbose'):
            trace = 3
        else:
            trace = 0
        
        train = LazyMap(lambda sent: map(unflatten, sent), iob_sents)
        fd = ChunkTaggerFeatureDetector

        mallet_home = os.environ.get('MALLET_HOME', '/usr/local/mallet-0.4')
        nltk.classify.mallet.config_mallet(mallet_home) 
               
        crf = MalletCRF.train(fd, train, 
            gaussian_variance=gaussian_variance, 
            default_label=default_label, 
            transduction_type=transduction_type, 
            trace=trace)

        return cls(crf.filename, crf.feature_detector)


# tokens2tree() is almost entirely based on nltk.chunk.util.conllstr2tree()
# but works for a list of tokens instead of a CoNLL string.
def tokens2tree(tokens, chunk_types=('NP', 'PP', 'VP'), top_node="S"):
    stack = [Tree(top_node, [])]
    
    for token in tokens:
        word, tag = token[:2]
        state, chunk_type = re.match(r'([IOB])-?(\S+)?', token[-1]).groups()
        
        # If it's a chunk type we don't care about, treat it as O.
        if (chunk_types is not None and
            chunk_type not in chunk_types):
            state = 'O'
        
        # For "Begin"/"Outside", finish any completed chunks -
        # also do so for "Inside" which don't match the previous token.
        mismatch_I = state == 'I' and chunk_type != stack[-1].node
        if state in 'BO' or mismatch_I:
            if len(stack) == 2: stack.pop()
        
        # For "Begin", start a new chunk.
        if state == 'B' or mismatch_I:
            chunk = Tree(chunk_type, [])
            stack[-1].append(chunk)
            stack.append(chunk)
        
        # Add the new word token.
        stack[-1].append((word, tag))
    
    return stack[0]
    
def flatten(tokens):
    if not tokens:
        return ()
    if not getattr(tokens, '__iter__', False):
        return (tokens,)
    return flatten(tokens[0]) + flatten(tokens[1:])
    
def unflatten(token):
    return (token[:-1], token[-1])
    
def test_chunk_tagger(chunk_tagger, iob_sents, **kwargs):
    correct = map(tokens2tree, iob_sents)
    guesses = chunk_tagger.batch_parse(map(lambda c: c.leaves(), correct))
    
    chunkscore = ChunkScore()    
    for c, g in zip(correct, guesses):
        chunkscore.score(c, g)
        
    print 'Precision: %.2f' % chunkscore.precision()
    print 'Recall:    %.2f' % chunkscore.recall()
    print 'Accuracy:  %.2f' % chunkscore.accuracy()                
    print 'F-measure: %.2f' % chunkscore.f_measure()
    
    return chunkscore
    
def unittest(verbose=False): 
    import doctest
    failed, passed = doctest.testfile('test/chunk.doctest', verbose)
    if not verbose:
        print '%d passed and %d failed.' % (failed, passed)
        if failed == 0:
            print 'Test passed.'
        else:
            print '***Test Failed*** %d failures.' % failed
    return failed, passed

def demo():
    pass
    
_TRAINERS = ['NaiveBayesChunkTagger.train', 'MaxentChunkTagger.train',
             'CRFChunkTagger.train']
_CORPORA = ['nltk.corpus.conll2000']
if __name__ == '__main__':
    import optparse
    
    try:
        import cPickle as pickle
    except:
        import pickle    
    
    import nltk_contrib
    from nltk_contrib.coref.chunk import *
    
    try:
        parser = optparse.OptionParser()
        parser.add_option('-d', '--demo', action='store_true', dest='demo',
            default=False, help='run demo')
        parser.add_option('-t', '--trainer', metavar='TRAINER', 
            dest='trainer',
            type='choice', choices=_TRAINERS, default=_TRAINERS[0], 
            help='train model using TRAINER, e.g. %s' % ', '.join(_TRAINERS))
        parser.add_option('-n', '--num-sents', metavar='TRAIN,TEST',  
            dest='numsents', type=str, default=None,
            help='number of TRAIN and TEST sentences to train model with')
        parser.add_option('-c', '--corpus', metavar='CORPUS', dest='corpus',
            type=str, default=_CORPORA[0],
            help='train model using CORPUS, e.g. %s' % ', '.join(_CORPORA))
        parser.add_option('-m', '--model', metavar='MODEL',
            dest='model', type='str', default=None,
            help='save model file to MODEL')
        parser.add_option('-u', '--unit-test', action='store_true', 
            default=False, dest='unittest', help='run unit tests')
        parser.add_option('-v', '--verbose', action='store_true', 
            default=False, dest='verbose', help='verbose')
        (options, args) = parser.parse_args()
    
        if options.numsents:
            m = re.match('^(?P<train>\d+)\s*(\,\s*(?P<test>\d+))?$', 
                options.numsents)
            if m:
                num_train = int(m.group('train'))
                num_test = int(m.group('test') or 0)
                options.numsents = (num_train, num_test)
            else:
                raise ValueError, "malformed argument for option -n"
        else:
            options.numsents = (None, None)
            
    except ValueError as v:
        print 'error: %s' % v.message
        parser.print_help()            
    
    if options.unittest:
        failed, passed = unittest(options.verbose)
        sys.exit(int(bool(failed)))

    if options.demo:
        demo()
        sys.exit(0)
    
    if options.trainer:
        corpus = eval(options.corpus).iob_sents()
        
        num_train, num_test = options.numsents
        if not num_train and not num_test:
            num_train = int(len(corpus) * 0.9)
            num_test = len(corpus) - num_train
        train = corpus[:num_train]
        test = corpus[num_train:num_train + num_test]

        trainer = eval(options.trainer)        
        if options.verbose:
            print 'Training %s with %d sentences' % \
                (options.trainer, num_train)
        chunker = trainer(train, verbose=options.verbose)
        
        if options.model:
            options.model = os.path.abspath(options.model)
            try:
                if chunker.__class__ == CRFChunkTagger:
                    pass
                else:
                    if options.model.endswith('.gz'):
                        _open = BufferedGzipFile
                    else:
                        _open = open                    
                    stream = _open(options.model, 'w')
                    pickle.dump(chunker, stream)
                    stream.close()                    
                    chunker = pickle.load(_open(options.model, 'r'))
                if options.verbose:
                    print 'Model saved as %s' % options.model                    
            except Exception as e:
                print "error: %s" % e

        if test:
            if options.verbose:
                print 'Testing %s on %d sentences' % \
                    (options.trainer, num_test)
            chunker.test(test)