# Natural Language Toolkit (NLTK) Coreference Module
#
# Copyright (C) 2001-2011 NLTK Project
# Author: Joseph Frazee <jfrazee@mail.utexas.edu>
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT

"""
Classes and interfaces for coreference resolution.

"""

##//////////////////////////////////////////////////////
##  Metadata
##//////////////////////////////////////////////////////

# Copyright notice
__copyright__ = """\
Copyright (C) 2001-2011 NLTK Project 

Distributed and Licensed under provisions of the GNU Public
License, which is included by reference.
"""

# Maintainer, contributors, etc.
__maintainer__ = "Joseph Frazee"
__maintainer_email__ = "jfrazee@mail.utexas.edu"
__author__ = __maintainer__
__author_email__ = __maintainer_email__

# Import top-level functionality into top-level namespace

# Processing packages -- these all define __all__ carefully.
from api import *

import nltk.data
from nltk.corpus.util import LazyCorpusLoader

if os.environ.get('NLTK_DATA_MUC6') \
and os.environ.get('NLTK_DATA_MUC6') not in nltk.data.path:
    nltk.data.path.insert(0, os.environ.get('NLTK_DATA_MUC6'))
from muc import MUCCorpusReader
muc6 = LazyCorpusLoader('muc6/',
    MUCCorpusReader, r'.*\.ne\..*\.sgm')