# Natural Language Toolkit: WALS interface
#
# Copyright (C) 2001-2011 NLTK Project
# Author: Michael Wayne Goodman <goodmami@uw.edu>
#
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT
#
# For more information about WALS (the World Atlas of Language Structures),
# see http://wals.info. WALS is curated by Matthew S. Dryer and Martin
# Haspelmath. WALS Online is hosted by the Max Planck Digital Library.
#
# The data used with this class can be obtained from http://wals.info/export

from collections import defaultdict
import csv
import os.path
import re

"""
Class for loading and interacting with the WALS database of linguistic
typological information.
"""

# Used for removing location information from language names.
_lg_variety_re = re.compile(r'\s*\(.*$')

# These are the columns for the feature, value, and language tables
feature_fields = ['id', 'name']
value_fields = ['feature_id', 'value_id', 'description', 'long_description']
language_fields = ['wals_code', 'name', 'latitude', 'longitude',
                   'genus', 'family', 'subfamily', 'iso_codes']

class LHNode(object):
    """
    Language hierarchy node, for storing genus/family/subfamily info.
    """

    def __init__(self, name):
        """
        @param name: The name of the genus/family/subfamily at this node.
        """
        self.name = name
        self.languages = {}
        self.subclasses = {}
        self.superclass = None

class WALS(object):
    """
    A container and interface for a WALS database.
    """

    def __init__(self, data_dir, dialect='excel-tab', encoding='utf-8'):
        """
        @param data_dir: The directory where the WALS data files exist.
        @param dialect: The CSV dialect used in the database (values are
                        'excel' and 'excel-tab'.
        """

        if dialect == 'tab': dialect = 'excel-tab'
        if dialect == 'csv': dialect = 'excel'
        self.dialect = dialect
        self.load(os.path.expanduser(data_dir), encoding)
        self._build_indices()
        self._build_language_hierarchy()

    def load(self, data_dir, encoding):
        """
        Read and store the data from the WALS database.
        
        @param data_dir: The directory where the WALS data files exist.
        @param encoding: The character encoding of the files.
        """

        # The features, values, and languages files are simply rows with an
        # equal number of columns per row. We can use csv.reader to parse.
        # For each file, the first line is header information. Discard it.
        file_ext = 'csv' if self.dialect == 'excel' else 'tab'
        def open_csv(filename, remove_header=True):
            filename = os.path.join(data_dir, filename + '.' + file_ext)
            wals_file = csv.reader(open(filename, 'r'), dialect=self.dialect)
            if remove_header: wals_file.next()
            for row in wals_file:
                yield [unicode(cell, encoding) for cell in row]

        def map_fields(vectors, fields):
            for vector in vectors:
                yield dict(zip(fields, vector))

        # Features
        self.features = dict((f['id'], f) for f in
                             map_fields(open_csv('features'),
                                        feature_fields))
        # Values
        self.values = defaultdict(dict)
        for v in map_fields(open_csv('values'), value_fields):
            self.values[v['feature_id']][v['value_id']] = v
        # Languages
        self.languages = dict((l['wals_code'], l) for l in
                              map_fields(open_csv('languages'),
                                         language_fields))
        # convert longitude and latitude to float from string
        for l in self.languages.values():
            l['latitude'] = float(l['latitude'])
            l['longitude'] = float(l['longitude'])
        # The datapoints file is more complicated. There is a column for
        # every feature, and a row for every language. Each cell is either
        # empty or contains a value dependent on the feature.
        rows = open_csv('datapoints', remove_header=False)
        header = rows.next()
        self.data = defaultdict(dict)
        self.feat_lg_map = defaultdict(list)
        for row in rows:
            lg = row[0]
            for i, val in enumerate(row[1:]):
                if val != '':
                    self.feat_lg_map[header[i+1]] += [self.languages[lg]]
                    self.data[lg][header[i+1]] = val

    def _build_indices(self):
        """
        For efficient lookup, build indices for language names and iso codes.
        """

        self.iso_index = defaultdict(list)
        self.language_name_index = defaultdict(list)
        for lg in self.languages.values():
            for iso in lg['iso_codes'].split():
                self.iso_index[iso] += [lg]
            name = lg['name'].lower()
            self.language_name_index[_lg_variety_re.sub('', name)] += [lg]

    def _build_language_hierarchy(self):
        """
        Use the 'family', 'subfamily', and 'genus' information to build
        a hierarchical representation of language relations.
        """

        # all languages in WALS have family and genus, but some also have
        # subfamily. This intervenes between family and genus:
        #    family -> genus
        #    family -> subfamily -> genus
        lg_hier = {}
        for lg in self.languages.values():
            family = lg_hier.setdefault(lg['family'],
                                 LHNode(lg['family']))
            family.languages[lg['wals_code']] = lg
            if lg['subfamily']:
                subfamily = family.subclasses.setdefault(lg['subfamily'],
                                                  LHNode(lg['subfamily']))
                subfamily.superclass = family
                subfamily.languages[lg['wals_code']] = lg
                # set family to subfamily so genus info is added correctly
                family = subfamily
            genus = family.subclasses.setdefault(lg['genus'],
                                            LHNode(['genus']))
            genus.languages[lg['wals_code']] = lg
            genus.superclass = family
        self.language_hierarchy = lg_hier

    def show_language(self, wals_code):
        """
        Given a WALS code, print the data for a language to STDOUT.

        @param wals_code: The WALS code for a language.
        """

        print self.languages[wals_code]['name'], '(%s):' % wals_code
        data = self.data[wals_code]
        for feat in sorted(data.keys()):
            print ' ', self.features[feat]['name'], '(%s):' % feat,\
                  self.values[feat][data[feat]]['description'],\
                  '(%s)' % self.values[feat][data[feat]]['value_id']

    def get_wals_codes_from_iso(self, iso_code):
        """
        Given a ISO-639 language code, return a list of WALS codes that
        match the ISO code. This may be a one-to-many mapping.

        @param iso_code: The ISO-639 code for a language.
        """

        return [lg['wals_code'] for lg in self.iso_index[iso_code]]

    def get_wals_codes_from_name(self, name):
        """
        Given a language name, return a list of WALS codes that match
        the name. This may be a one-to-many mapping.
        
        @param name: The name of a language.
        """

        name = _lg_variety_re.sub('', name).lower()
        return [lg['wals_code'] for lg in self.language_name_index[name]]

    def get_languages_with_feature(self, feature, value=None, superclass=None):
        """
        Given at least a feature index, find all languages that have
        the feature. Feature values and a language superclass (family,
        subfamily, or genus) may be used to narrow the results.

        @param feature: A WALS feature index.
        @param value: A WALS value index.
        @param superclass: A string that is matched against language family,
                           subfamily, and genus.
        """

        if value: value = str(value) # be robust to int values
        supermatch = lambda x: superclass in (x['genus'],
                                              x['subfamily'],
                                              x['family'])
        valmatch = lambda x: self.data[l['wals_code']].get(feature) == value
        return [l for l in self.feat_lg_map[feature]
                if (not value or valmatch(l)) and \
                   (not superclass or supermatch(l))]

def demo(wals_directory=None, dialect='excel-tab', encoding='utf-8'):
    if not wals_directory:
        import sys
        print >>sys.stderr, 'Error: No WALS data directory provided.'
        print >>sys.stderr, '       You may obtain the database from ' +\
            'http://wals.info/export'
        return
    w = WALS(wals_directory, dialect, encoding)
    
    # Basic statistics
    print 'In database:\n  %d\tlanguages\n  %d\tfeatures ' %\
        (len(w.languages), len(w.features))
    # values are a nested dictionary (w.values[feature_id][value_id])
    num_vals = sum(map(len, w.values.values()))
    print '  %d\ttotal values (%f avg. number per feature)' %\
        (num_vals, float(num_vals)/len(w.features))
    # More statistics
    print "  %d languages specify feature 81A (order of S, O, and V)" %\
        (len(w.get_languages_with_feature('81A')))
    print "  %d langauges have VOS order" %\
        (len(w.get_languages_with_feature('81A', value='4')))

    # Getting language data
    print "\nGetting data for languages named 'Irish'"
    for wals_code in w.get_wals_codes_from_name('Irish'):
        l = w.languages[wals_code]
        print '  %s (ISO-639 code: %s WALS code: %s)' %\
            (l['name'], l['iso_codes'], wals_code)
    print "\nGetting data for languages with ISO 'isl'"
    for wals_code in w.get_wals_codes_from_iso('isl'):
        w.show_language(wals_code)
    print "\nLocations of dialects for the Min Nan language (ISO 'nan'):"
    for wals_code in w.get_wals_codes_from_iso('nan'):
        l = w.languages[wals_code]
        print "  %s\tlat:%f\tlong:%f" %\
            (l['name'], l['latitude'], l['longitude'])
