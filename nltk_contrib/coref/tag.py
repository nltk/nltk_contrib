import os
import re
import subprocess

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from nltk.util import LazyMap, LazyConcatenation
from nltk.internals import find_binary, java
from nltk.tag import TaggerI

from nltk_contrib.coref import CorpusReaderDecorator

class TaggerCorpusReader(CorpusReaderDecorator):
    """
    A C{CorpusReaderDecorator} that adds tagger functionality to an arbitrary
    C{CorpusReader}.
    """
    
    def __init__(self, reader, **kwargs):
        """
        @return: a corpus reader
        @rtype: C{TaggerCorpusReader}
        @param reader: the corpus reader to decorate
        @type reader: C{CorpusReader}
        @kwparam tagger: a tagger object to defer tagging to
        @type tagger: C{TaggerI}
        """
        self._tagger = kwargs.get('tagger') 
        CorpusReaderDecorator.__init__(self, reader, **kwargs)
    
    def tagged_sents(self):
        return LazyMap(self._tagger.tag, self.sents())
    
    def tagged_words(self):
        return LazyConcatenation(LazyMap(self._tagger.tag, self.sents()))

    def tagger(self):
        return self._tagger
        
        
class MXPostTaggerCorpusReader(TaggerCorpusReader):
    def __init__(self, reader, **kwargs):
        kwargs['tagger'] = MXPostTagger()
        TaggerCorpusReader.__init__(self, reader, **kwargs)
        
    def tagged_sents(self):
        sents = self.sents()
        batch_indices = range(len(sents) / 1024 + 1)
        return LazyConcatenation(LazyMap(lambda i: 
                self._tagger.batch_tag(sents[i * 1024: i * 1024 + 1024]),
            batch_indices))


class MXPostTagger(TaggerI):
    def tag(self, tokens):
        return self.batch_tag([tokens])[0]
    
    def batch_tag(self, sents):
        return mxpost_tag(sents)
        

_mxpost_home = None
_mxpost_classpath = None
def config_mxpost(mxpost_home=None):
    global _mxpost_classpath, _mxpost_home
    classpath = os.environ.get('CLASSPATH', '').split(':')
    mxpost_jar = filter(lambda c: c.endswith('mxpost.jar'), classpath)
    if mxpost_jar:
        _mxpost_home = os.path.dirname(mxpost_jar[0])
        _mxpost_classpath = mxpost_jar[0]
    elif os.environ.get('MXPOST'):
        _mxpost_home = os.environ.get('MXPOST')
        _mxpost_classpath = '%s/mxpost.jar' % os.environ.get('MXPOST')
    elif os.environ.get('MXPOST_HOME'):
        _mxpost_home = os.environ.get('MXPOST_HOME')
        _mxpost_classpath = '%s/mxpost.jar' % os.environ.get('MXPOST_HOME')
    elif os.path.exists('/usr/local/mxpost/mxpost.jar'):
        _mxpost_home = '/usr/local/mxpost'
        _mxpost_classpath = '/usr/local/mxpost/mxpost.jar'
    else:
        _mxpost_home = None
        _mxpost_classpath = None
        raise Exception, "can't find mxpost.jar"

def call_mxpost(classpath=None, stdin=None, stdout=None, stderr=None,
                blocking=False):
    if not classpath:
        config_mxpost()
    
    if not classpath:
        classpath = _mxpost_classpath
    elif 'mxpost.jar' not in classpath:
        classpath += ':%s' % _mxpost_classpath
    
    cmd = ['tagger.TestTagger', '%s/%s' % (_mxpost_home, 'wsj-02-21.mxpost')]
    return java(cmd, classpath, stdin, stdout, stderr, blocking)

_MXPOST_OUTPUT_RE = \
    re.compile(r'^\s*(?P<word>\S+)\_(?P<tag>\S+)\s*$')
def mxpost_parse_output(mxpost_output):
    result = []
    mxpost_output = mxpost_output.strip()
    for sent in filter(None, mxpost_output.split('\n')):
        tokens = filter(None, re.split(r'\s+', sent))
        if tokens:
            result.append([])
        for token in tokens:
            m = _MXPOST_OUTPUT_RE.match(token)
            if not m:
                raise Exception, "invalid mxpost tag pattern: %s, %s" % (token, tokens)
            word = m.group('word')
            tag = m.group('tag')
            result[-1].append((word, tag))
    return result

def mxpost_tag(sents, **kwargs):
    p = call_mxpost(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = \
        p.communicate('\n'.join([' '.join(sent) for sent in sents]))
    rc = p.returncode
    if rc != 0:
        raise Exception, 'exited with non-zero status %s' % rc
    if kwargs.get('verbose'):
        print 'warning: %s' % stderr
    return mxpost_parse_output(stdout)