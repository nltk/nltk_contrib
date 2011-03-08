# Natural Language Toolkit (NLTK) Coreference Named Entity Components
#
# Copyright (C) 2001-2011 NLTK Project 
# Author: Joseph Frazee <jfrazee@mail.utexas.edu>
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT

import re
import os
import sys
import optparse

from tempfile import mkstemp

import nltk
from nltk.util import LazyMap, LazyZip
from nltk.data import BufferedGzipFile
from nltk.tree import Tree
from nltk.classify import NaiveBayesClassifier, MaxentClassifier
from nltk.tag import ClassifierBasedTagger
from nltk.tag.crf import MalletCRF
from nltk.chunk import ChunkScore
from nltk.corpus import names, gazetteers, stopwords

from nltk_contrib.coref.chunk import NaiveBayesChunkTagger, MaxentChunkTagger
from nltk_contrib.coref.tag import MXPostTaggerCorpusReader

NUMBERS = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
           'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen',
           'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen',
           'nineteen', 'twenty', 'thirty', 'fourty', 'fifty',
           'sixty', 'seventy', 'eighty', 'ninety', 'hundred',
           'thousand', 'million', 'billion', 'trillion']

ORDINALS = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 
            'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth']

DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 
        'friday', 'saturday', 'sunday']

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
          'august', 'september', 'october', 'november', 'december',
          'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'sept',
          'oct', 'nov', 'dec']

NAMES = set([name.lower() for filename in ('male.txt', 'female.txt') for name
             in names.words(filename)])

US_CITIES = set([city.lower() for city in gazetteers.words('uscities.txt')])

# [XX] contains some non-ascii chars
COUNTRIES = set([country.lower() for filename in ('isocountries.txt','countries.txt')
                 for country in gazetteers.words(filename)])

# States in North America
NA_STATES = set([state.lower() for filename in
    ('usstates.txt','mexstates.txt','caprovinces.txt') for state in
    gazetteers.words(filename)])
                     
US_STATE_ABBREVIATIONS = set([state.lower() for state in 
    gazetteers.words('usstateabbrev.txt')])

NATIONALITIES = set([nat.lower() for nat in 
    gazetteers.words('nationalities.txt')])
                     
PERSON_PREFIXES = ['mr', 'mrs', 'ms', 'miss', 'dr', 'rev', 'judge',
                   'justice', 'honorable', 'hon', 'rep', 'sen', 'sec',
                   'minister', 'chairman', 'succeeding', 'says', 'president']

PERSON_SUFFIXES = ['sr', 'jr', 'phd', 'md']

ORG_SUFFIXES = ['ltd', 'inc', 'co', 'corp', 'plc', 'llc', 'llp', 'gmbh',
                'corporation', 'associates', 'partners', 'committee',
                'institute', 'commission', 'university', 'college',
                'airlines', 'magazine', 'association', 'staff', 'family',
                'administration']

PERSON_ORG_ACTIONS = ['says', 'said', 'call', 'called', 'ask', 'asks',
                      'give', 'gave', 'who']

CURRENCY_UNITS = ['dollar', 'cent', 'pound', 'euro']

ENGLISH_PRONOUNS = ['i', 'you', 'he', 'she', 'it', 'we', 'you', 'they']

STOPWORDS = set(stopwords.words())

NUMERIC = r'(\d{1,3}(\,\d{3})*|\d+)(\.\d+)?'
RE_PUNCT = re.compile(r'[-!"#$%&\'\(\)\*\+,\./:;<=>^\?@\[\]\\\_`{\|}~]')
RE_NUMERIC = re.compile(NUMERIC)
RE_NUMBER = re.compile(r'(%s)(\s+(%s))*' % ('|'.join(NUMBERS), 
    '|'.join(NUMBERS)), re.I)
RE_QUOTE = re.compile(r'[\'"`]', re.I)
RE_ROMAN = re.compile(r'M?M?M?(CM|CD|D?C?C?C?)(XC|XL|L?X?X?X?)(IX|IV|V?I?I?I?)', re.I)
RE_INITIAL = re.compile(r'[A-Z]\.', re.I)
RE_TLA = re.compile(r'([A-Z0-9][\.\-]?){2,}', re.I)
RE_ALPHA = re.compile(r'[A-Za-z]+', re.I)
RE_DATE = re.compile(r'\d+\/\d+(\/\d+)?')
RE_CURRENCY = re.compile(r'\$\s*(%s)?' % NUMERIC)
RE_CURRENCY_UNIT = re.compile(r'%s' % ('|'.join(CURRENCY_UNITS)), re.I)
RE_PERCENT = re.compile(r'%s\s*' % NUMERIC + '%')
RE_YEAR = re.compile(r'(\d{4}s?|\d{2}s)')
RE_TIME = re.compile(r'\d{1,2}(\:\d{2})?(\s*[aApP]\.?[mM]\.?)?', re.I)
RE_ORDINAL = re.compile(r'%s' % ('|'.join(ORDINALS)))
RE_DAY = re.compile(r'%s' % ('|'.join(DAYS)), re.I)
RE_MONTH = re.compile(r'%s' % ('|'.join(MONTHS)), re.I)
RE_PERSON_PREFIX = re.compile(r'%s' % ('|'.join(PERSON_PREFIXES)), re.I)
RE_PERSON_SUFFIX = re.compile(r'%s' % ('|'.join(PERSON_SUFFIXES)), re.I)
RE_ORG_SUFFIX = re.compile(r'%s' % ('|'.join(ORG_SUFFIXES)), re.I)

class NERChunkTaggerFeatureDetector(dict):
    def __init__(self, tokens, index=0, history=None, **kwargs):
        dict.__init__(self)
        window = kwargs.get('window', 3)
        
        spelling, pos = tokens[index][:2]

        self['spelling'] = spelling
        self['word'] = spelling.lower()
        self['wordlen'] = len(spelling)
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
        self['ispercent'] = int(bool(RE_PERCENT.match(spelling)))
        self['isnumber'] = int(bool(RE_PERCENT.match(spelling)))
        self['isnumeric'] = int(bool(RE_NUMERIC.match(spelling)))
        self['isquote'] = int(bool(RE_QUOTE.match(spelling)))
        self['isroman'] = int(bool(RE_ROMAN.match(spelling)))
        self['isinitial'] = int(bool(RE_INITIAL.match(spelling)))
        self['istla'] = int(bool(RE_TLA.match(spelling)))
        self['isdate'] = int(bool(RE_DATE.match(spelling)))
        self['iscurrency'] = int(bool(RE_CURRENCY.match(spelling)))
        self['iscurrencyunit'] = int(bool(RE_CURRENCY_UNIT.match(spelling)))
        self['isyear'] = int(bool(RE_YEAR.match(spelling)))
        self['istime'] = int(bool(RE_TIME.match(spelling)))
        self['isordinal'] = int(bool(RE_ORDINAL.match(spelling)))
        self['isday'] = int(bool(RE_DAY.match(spelling)))
        self['ismonth'] = int(bool(RE_MONTH.match(spelling)))        
        self['isname'] = int(spelling.lower() in NAMES)
        self['iscity'] = int(spelling.lower() in US_CITIES)
        self['isstateabbrev'] = spelling.lower() in US_STATE_ABBREVIATIONS
        self['isnastate'] = int(spelling.lower() in NA_STATES)
        self['isnationality'] = int(spelling.lower() in NATIONALITIES)
        self['personprefix'] = int(bool(RE_PERSON_PREFIX.match(spelling)))
        self['personsuffix'] = int(bool(RE_PERSON_PREFIX.match(spelling)))                                                                      
        self['orgsuffix'] = int(bool(RE_ORG_SUFFIX.match(spelling)))
        self['personorgaction'] = int(bool(spelling.lower() in PERSON_ORG_ACTIONS))
        self['endofsent'] = int(index == len(tokens) - 1)
        self['startofsent'] = int(index == 0)

        if window > 0 and index > 0:
            prev_feats = \
                self.__class__(tokens, index - 1, history, window=window - 1)
            for key, val in prev_feats.items():
                if not key.startswith('next_') and not key == 'word':
                    self['prev_%s' % key] = val

        if window > 0 and index < len(tokens) - 1:
            next_feats = self.__class__(tokens, index + 1, window=window - 1)        
            for key, val in next_feats.items():
                if not key.startswith('prev_') and not key == 'word':
                    self['next_%s' % key] = val        

        if 'prev_pos' in self:
            self['prev_pos_pair'] = '%s/%s' % \
                (self.get('prev_pos'), self.get('pos'))

        if history is not None:
            if len(history) > 0 and index > 0:
                self['prev_tag'] = history[index - 1]
            else:
                self['prev_tag'] = 'O'


def unittest(verbose=False): 
    import doctest
    failed, passed = doctest.testfile('test/ne.doctest', verbose)
    if not verbose:
        print '%d passed and %d failed.' % (failed, passed)
        if failed == 0:
            print 'Test passed.'
        else:
            print '***Test Failed*** %d failures.' % failed
    return failed, passed

_NE_CHUNK_TYPES = ('PERSON', 'LOCATION', 'ORGANIZATION', 'MONEY')
_TRAINERS = ['NaiveBayesChunkTagger.train', 'MaxentChunkTagger.train',
             'CRFChunkTagger.train']
_CORPORA = ['nltk_contrib.coref.muc6']
if __name__ == '__main__':
    import optparse

    try:
        import cPickle as pickle
    except:
        import pickle    

    import nltk_contrib
    from nltk_contrib.coref.ne import *
    from nltk_contrib.coref.chunk import NaiveBayesChunkTagger, \
        MaxentChunkTagger, CRFChunkTagger

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
        parser.add_option('-p', '--pos', action='store_true',
            default=False, dest='pos', help='create POS tags for CORPUS')
        parser.add_option('-m', '--model', metavar='MODEL',
            dest='model', type='str', default=None,
            help='save model file to MODEL')
        parser.add_option('-e', '--extract-features', metavar='TRAIN,TEST',
            dest='extract', type=str, default=None,
            help='extract features to TRAIN and TEST for use outside NLTK')
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
            
        if options.extract:        
            m = re.match('^(?P<train>[\w\.]+)\s*(\,\s*(?P<test>[\w\.]+))?$',
                options.extract)
            if m:
                file_train = m.group('train')
                file_test = m.group('test')
                options.extract = (file_train, file_test)
            else:
                raise ValueError, "malformed argument for option -e"            

    except ValueError, v:
        print 'error: %s' % v.message
        parser.print_help()            

    if options.unittest:
        failed, passed = unittest(options.verbose)
        sys.exit(int(bool(failed)))

    if options.demo:
        demo()
        sys.exit(0) 
        
    if options.extract:
        train_file, test_file = options.extract
                
        corpus = eval(options.corpus).iob_sents()
        
        num_train, num_test = options.numsents
        num_train = num_train or int(len(corpus) * 0.9)
        num_test = num_test or (len(corpus) - num_train)
        train = corpus[:num_train]
        test = corpus[num_train:num_train + num_test]               
        
        feature_detector = NERChunkTaggerFeatureDetector
        
        keys = set()
        
        fd, train_tmp = mkstemp('nltk-')
        stream = open(train_tmp, 'wb')
        for tokens in train:
            history = []
            for index in range(len(tokens)):
                tag = tokens[index][-1]                
                feats = feature_detector(tokens, index, history)    
                keys.update(feats.keys())                            
                stream.write('%s %s\n' % (tag, ' '.join(['%s=%s' % (k, re.escape(str(v)))
                    for k, v in feats.items()])))
                history.append(tag)                    
            history = []
        stream.close()
        
        fd, test_tmp = mkstemp('nltk-')
        stream = open(test_tmp, 'wb')
        for tokens in test:
            history = []
            for index in range(len(tokens)):
                tag = tokens[index][-1]
                feats = feature_detector(tokens, index, history)
                keys.update(feats.keys())
                stream.write('%s %s\n' % (tag, ' '.join(['%s=%s' % (k, re.escape(str(v)))
                    for k, v in feats.items()])))
                history.append(tag)
            history = []                    
        stream.close()
        
        keys = list(keys)
        keys.sort()
        
        stream = open(train_file, 'wb')
        stream.write('iob_tag,%s\n' % ','.join(keys))        
        for line in open(train_tmp, 'rb'):
            data = line.split()
            tag = data.pop(0)            
            feats = dict([tuple(f.split('=', 1)) for f in data])
            stream.write('"%s",%s\n' % (tag, ','.join(['"%s"' % feats.get(k, '') for k in keys])))
        stream.close() 
        os.remove(train_tmp)        
        
        stream = open(test_file, 'wb')
        stream.write('iob_tag,%s\n' % ','.join(keys))
        for line in open(test_tmp, 'rb'):
            data = line.split()
            tag = data.pop(0)
            feats = dict([tuple(f.split('=', 1)) for f in data])
            stream.write('"%s",%s\n' % (tag, ','.join(['"%s"' % feats.get(k, '') for k in keys])))
        stream.close()      
        os.remove(test_tmp)     
        
        sys.exit(0)                

    if options.trainer:
        if options.pos:
            reader = MXPostTaggerCorpusReader(eval(options.corpus))
            iob_sents = reader.iob_sents()
            tagged_sents = reader.tagged_sents()
            corpus = LazyMap(lambda (iob_sent, tagged_sent): 
                    [(iw, tt, iob) for ((iw, iob), (tw, tt))
                     in zip(iob_sent, tagged_sent)], 
                 LazyZip(iob_sents, tagged_sents))
        else:
            iob_sents = eval(options.corpus).iob_sents()
            corpus = LazyMap(lambda iob_sent:
                [(w, None, i) for w, i in iob_sent], iob_sents)

        num_train, num_test = options.numsents
        num_train = num_train or int(len(corpus) * 0.9)
        num_test = num_test or (len(corpus) - num_train)
        train = corpus[:num_train]
        test = corpus[num_train:num_train + num_test]

        trainer = eval(options.trainer)        
        if options.verbose:
            print 'Training %s with %d sentences' % \
                (options.trainer, num_train)
        ner = trainer(train, 
            feature_detector=NERChunkTaggerFeatureDetector,
            chunk_types=_NE_CHUNK_TYPES,
            verbose=options.verbose)

        if options.model:
            options.model = os.path.abspath(options.model)
            try:
                if ner.__class__ == CRFChunkTagger:
                    pass
                else:
                    if options.model.endswith('.gz'):
                        _open = BufferedGzipFile
                    else:
                        _open = open                    
                    stream = _open(options.model, 'w')
                    pickle.dump(ner, stream)
                    stream.close()                    
                    ner = pickle.load(_open(options.model, 'r'))
                if options.verbose:
                    print 'Model saved as %s' % options.model                    
            except Exception, e:
                print "error: %s" % e

        if test:
            if options.verbose:
                print 'Testing %s on %d sentences' % \
                    (options.trainer, num_test)
            ner.test(test, verbose=options.verbose)
