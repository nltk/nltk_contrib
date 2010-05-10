
5/5/10

This directory contains 2 implementations of the Gale-Church alignment algorithm:

1. gale_church.py
2. align.py 
        api.py
        align_util.py
        distance_measures.py
    
This README concerns the second implementation which I am the author of
(ccrowner@gmail.com).

########################################################
TESTING

align.py can be tested using:

python test2.py chapter1_madame_bovary_fr.txt chapter1_madame_bovary_en.txt fr en
(using data/ versions causes decode problems in the plaintext reader)

This will print output from various demo alignments (see test.py code) as well as
an alignment of the first chapter of Madame Bovary in the original French to an English
translation (non-copyrighted!)

The ground truth for the demo alignments is in the data folder. The demo_eval() routine
in test.py could be activated to do an evaluation (currently not sure if it works)

The ground truth to Madame Bovary alignment is not in data (I will make it available).

The test.py program runs the Gale-Church alignment on Madame Bovary using an 
'extended' option which unlike the 'original' option of the Gale-Church algorithm
considers 3-1, 3-2, 1-3, 2-3, 3-3 alignments. This is a 1-3 and a 3-1 alignment in the
ground truth of Madame Bovary. The program did not correctly handle these (all other
alignments output were correct). It may have erred because of the probabilities
(penalties) in the distance_measures.three_side_distance() routine. It may have 
erred because of a faulty implementation. Finally, Gale-Church may simply fail on
these cases. If someone discovers the real reason PLEASE let me know!

##########################################################
CHANGES

The following are the major changes since the last version:

1. align_util.covert_bead_to_tuples() now works!!
2. print_alignments now works!!

both these routines are for output - the base algorithm produced correct
results (though they may have not have looked that way in the output!)

3. the api.py includes a recursive_align call which can do alignments from chapters,
to paragraphs, to sentences, to words, to ...

4. the test.py program show how a plain text file can be used as input using the
nltk PlaintextCorpusReader (using punkt for sentence breaking)

5. As mentioned in the testing section above there is a new 'extended' alignment
option which considers 3-1, 3-2, 1-3, 2-3, 3-3 alignments

6. other minor changes 

###########################################################
TO DO:
Unicode problems. The printed alignment are not UTF-8. This may best be handled 
at input (which also has problems which may be a simple as BOM or file formats). 
Haven't worked at it yet (if anyone has some fix, please pass it on)

The program should have option to print out an ARCADE or TEI style alignment file.

Eventually, I hope to make available a Madame Bovary corpus with 6 English translations
of Madame Bovary along with German, Spanish, Italian and Russian translations.
All these translations are written by humans - I also have translations produced using
Google Translate toolkit (any preferred languages let me know)

Again, eventually all these translations will be easily worked with using TEI formats
Why not NOW?? Well, "data management/integration" is a pain and I hope to use 
alignment algorithms of my own devising to produce ground truth (first pass at least) 
for the translations (leaving something undone gives me motivation on this ;-)

