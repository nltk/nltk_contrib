# Natural Language Toolkit: source Makefile
#
# Copyright (C) 2001-2011 NLTK Project
# Author: Steven Bird <sb@csse.unimelb.edu.au>
#	 Edward Loper <edloper@gradient.cis.upenn.edu>
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT

PYTHON = python
VERSION = $(shell $(PYTHON) -c 'import nltk; print nltk.__version__' | sed '/^Warning: */d')
NLTK_URL = $(shell $(PYTHON) -c 'import nltk; print nltk.__url__' | sed '/^Warning: */d')
GOOGLE_ACCT = StevenBird1
UPLOAD = $(PYTHON) tools/googlecode_upload.py --project=nltk --config-dir=none --user=$(GOOGLE_ACCT) --labels=Featured

.PHONY: usage all doc clean clean_code clean_up

usage:
	@echo "make dist -- Build distributions (output to dist/)"
	@echo "make upload -- Upload files to NLTK website"
	@echo "make clean -- Remove all built files and temporary files"
	@echo "make clean_up -- Remove temporary files"

all: dist

upload:
	$(UPLOAD) --summary="NLTK-Contrib $(VERSION) Source (zip)" dist/nltk-contrib-$(VERSION)*.zip

doc:
	$(MAKE) -C doc all

########################################################################
# DISTRIBUTIONS
########################################################################

dist: clean_code
	$(PYTHON) setup.py -q sdist --format=zip

########################################################################
# CLEAN
########################################################################

.PHONY: clean clean_up

clean:	clean_up
	rm -rf build dist MANIFEST nltk-contrib-$(VERSION)
	$(MAKE) -C doc clean

clean_up: clean_code
	$(MAKE) -C doc clean_up

clean_code:
	rm -f `find . -name '*.pyc'`
	rm -f `find . -name '*.pyo'`
	rm -f `find . -name '*~'`
	rm -f MANIFEST # regenerate manifest from MANIFEST.in
