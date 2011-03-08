# Natural Language Toolkit (NLTK) Coreference Chunking Utilities
#
# Copyright (C) 2001-2011 NLTK Project 
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

from nltk.corpus import stopwords

from nltk_contrib.coref import ChunkTaggerI

STOPWORDS = set(stopwords.words())

RE_PUNCT = re.compile(r'[-!"#$%&\'\(\)\*\+,\./:;<=>^\?@\[\]\\\_`{\|}~]')
RE_NUMERIC = re.compile(r'(\d{1,3}(\,\d{3})*|\d+)(\.\d+)?')

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
        if pos: self['pos'] = pos
        self['isupper'] = int(spelling.isupper())
        self['islower'] = int(spelling.islower())
        self['istitle'] = int(spelling.istitle())
        self['isalnum'] = int(spelling.isalnum())
        
        for i in range(2, 4):
            self['prefix_%d' % i] = spelling.lower()[:i]
            self['suffix_%d' % i] = spelling.lower()[-i:]
        
        self['ispunct'] = int(bool(RE_PUNCT.match(spelling)))
        self['isstopword'] = int(spelling.lower() in STOPWORDS)        
        self['isnumeric'] = int(bool(RE_NUMERIC.match(spelling)))       
        self['startofsent'] = int(index == 0)         
        self['endofsent'] = int(index == len(tokens) - 1)
                    
        if window > 0 and index > 0:
            prev_feats = \
                self.__class__(tokens, index - 1, history, window=window - 1)
            for key, val in prev_feats.items():
                if not key.startswith('next_') and key != 'word':
                    self['prev_%s' % key] = val
        
        if window > 0 and index < len(tokens) - 1:
            next_feats = self.__class__(tokens, index + 1, window=window - 1)
            for key, val in next_feats.items():
                if not key.startswith('prev_') and key != 'word':
                    self['next_%s' % key] = val
        
        if 'prev_pos' in self:
            self['prev_pos_pair'] = '%s/%s' % \
                (self.get('prev_pos'), self.get('pos'))
        
        if history is not None:
            if len(history) > 0 and index > 0:
                self['prev_tag'] = history[index - 1]
            else:
                self['prev_tag'] = 'O'


class AbstractChunkTagger(ChunkTaggerI):
    chunk_types = None
    
    def parse(self, sent):
        return self.__iob2tree(self.tag(sent))
        
    def batch_parse(self, sents):
        return map(self.__iob2tree, self.batch_tag(sents))
    
    def chunk(self, sent):
        return self.__tree2chunks(self.parse(sent))
        
    def batch_chunk(self, sents):
        return map(self.__tree2chunks, self.batch_parse(sents))
        
    def __iob2tree(self, tagged_sent):
        return tokens2tree(map(flatten, tagged_sent), self.chunk_types)
        
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
            chunk_types=self.chunk_types,
            verbose=kwargs.get('verbose', False))


class NaiveBayesChunkTagger(ClassifierBasedTagger, AbstractChunkTagger):
    @classmethod
    def train(cls, iob_sents, **kwargs):  
        fd = kwargs.get('feature_detector', ChunkTaggerFeatureDetector)
        chunk_types = kwargs.get('chunk_types', _DEFAULT_CHUNK_TYPES)        
        train = LazyMap(lambda sent: map(unflatten, sent), iob_sents)
        chunker = cls(fd, train, NaiveBayesClassifier.train)
        chunker.chunk_types = chunk_types
        return chunker
        

class MaxentChunkTagger(ClassifierBasedTagger, AbstractChunkTagger):
    @classmethod
    def train(cls, iob_sents, **kwargs):
        fd = kwargs.get('feature_detector', ChunkTaggerFeatureDetector)        
        chunk_types = kwargs.get('chunk_types', _DEFAULT_CHUNK_TYPES)
                
        algorithm = kwargs.get('algorithm', 'megam')
        gaussian_prior_sigma = kwargs.get('gaussian_prior_sigma', 100)
        count_cutoff = kwargs.get('count_cutoff', 1)
        min_lldelta = kwargs.get('min_lldelta', 1e-7)
        trace = int(not kwargs.get('verbose', False) or 3)
        
        def __maxent_train(fs):
            return MaxentClassifier.train(fs, 
                algorithm=algorithm,
                gaussian_prior_sigma=gaussian_prior_sigma,
                count_cutoff=count_cutoff,
                min_lldelta=min_lldelta,
                trace=trace)
        train = LazyMap(lambda sent: map(unflatten, sent), iob_sents)
        chunker = cls(fd, train, __maxent_train)
        chunker.chunk_types = chunk_types
        return chunker


class CRFChunkTagger(MalletCRF, AbstractChunkTagger):
    def tag(self, sent):
        return self.batch_tag([sent])[0]
    
    @classmethod
    def train(cls, iob_sents, **kwargs):
        fd = kwargs.get('feature_detector', ChunkTaggerFeatureDetector)        
        chunk_types = kwargs.get('chunk_types', _DEFAULT_CHUNK_TYPES)
                
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

        mallet_home = os.environ.get('MALLET_HOME', '/usr/local/mallet-0.4')
        nltk.classify.mallet.config_mallet(mallet_home) 
               
        crf = MalletCRF.train(fd, train, 
            gaussian_variance=gaussian_variance, 
            default_label=default_label, 
            transduction_type=transduction_type, 
            trace=trace)

        crf = cls(crf.filename, crf.feature_detector)
        crf.chunk_types = chunk_types
        return crf

_DEFAULT_CHUNK_TYPES = ('NP', 'PP', 'VP')
# tokens2tree() is almost entirely based on nltk.chunk.util.conllstr2tree()
# but works for a list of tokens instead of a CoNLL string.
def tokens2tree(tokens, chunk_types=_DEFAULT_CHUNK_TYPES, top_node='S'):
    stack = [Tree(top_node, [])]
    
    for token in tokens:
        token, tag = unflatten(token)
        if isinstance(token, basestring):
            word = token
            pos = None
        elif isinstance(token, tuple):
            word, pos = token
        else:
            ValueError, 'invalid type for variable \'token\': %s' % type(token)
        state, chunk_type = re.match(r'([IOB])-?(\S+)?', tag).groups()
        
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
        stack[-1].append((word, pos or ''))
    
    return stack[0]
    
def flatten(tokens):
    if not tokens:
        return ()
    if not getattr(tokens, '__iter__', False):
        return (tokens,)
    return flatten(tokens[0]) + flatten(tokens[1:])
    
def unflatten(token):
    if not token:
        return ()
    if not getattr(token, '__iter__', False):
        return (token,)
    if len(token) == 1 or len(token[:-1]) == 1:
        return tuple(token)
    return (token[:-1], token[-1])
    
def test_chunk_tagger(chunk_tagger, iob_sents, **kwargs):
    chunk_types = chunk_tagger.chunk_types
    correct = map(lambda sent: tokens2tree(sent, chunk_types), iob_sents)
    guesses = chunk_tagger.batch_parse(map(lambda c: c.leaves(), correct))
    
    chunkscore = ChunkScore()    
    for c, g in zip(correct, guesses):
        chunkscore.score(c, g)
    
    if kwargs.get('verbose'):
        guesses = chunk_tagger.batch_tag(map(lambda c: c.leaves(), correct))
        correct = iob_sents
        
        print
        for c, g in zip(correct, guesses):        
            for tokc, tokg in zip(map(flatten, c), map(flatten, g)):
                word = tokc[0]
                iobc = tokc[-1]
                iobg = tokg[-1]
                star = ''
                if iobg != iobc: star = '*'
                print '%3s %20s %20s %20s' % (star, word, iobc, iobg)
            print      
        
    print 'Precision: %.2f' % chunkscore.precision()
    print 'Recall:    %.2f' % chunkscore.recall()
    print 'Accuracy:  %.2f' % chunkscore.accuracy()                
    print 'F-measure: %.2f' % chunkscore.f_measure()
    
    return chunkscore
    
def unittest(verbose=False): 
    import doctest
    failed, tested = doctest.testfile('test/chunk.doctest', verbose)
    if not verbose:
        print '%d passed and %d failed.' % (tested - failed, failed)
        if failed == 0:
            print 'Test passed.'
        else:
            print '***Test Failed*** %d failures.' % failed
    return (tested - failed), failed

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
            
    except ValueError, v:
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
        num_train = num_train or int(len(corpus) * 0.9)
        num_test = num_test or (len(corpus) - num_train)
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
            except Exception, e:
                print "error: %s" % e

        if test:
            if options.verbose:
                print 'Testing %s on %d sentences' % \
                    (options.trainer, num_test)
            chunker.test(test, verbose=options.verbose)