#!/usr/bin/env python

#-*- coding:utf-8 -*-

import sys, os, re, codecs, string
import unicodedata
# decomposing syllables
from kdictmap import * 

# Tae-Jin Yoon
# MaMaster University
# tjyoon@mcmaster.ca
# (c) 2011

""" Usage:
          python make_kdict.py

    A Python Script Designed to Make a Pronunciation Dictionary Using 
    Korean Phonological Rules

    input: kdict0.txt (from han2uniconversion.py)
    output kdict1.txt (sorted and uniq with kdictmap)
"""

# I made a dictionary datastructure using:
# awk {'printf "\047%s\047\t:\t\047%s\047,\n", $1, $1'} ksylfreq.txt | sort > junk
# Here \047 is for apostrophe and \t for tabbing
# See han2uniconversion.py for ksylfreq.txt
# The contents in junk were cut and pasted below, and the space in each value was manually supplied.

# Complex coda: need to account for coda neutralization
# 'GG', 'GS', 'NJ', 'NG', 'NH', 'DD', 'LG', 'LM', 'LS', 'LT', 'LP', 'LH', 'LB', 'BB', 'BS', 'SS', 'JJ'

debug = 0

def read_file(infile, ofile):
    fin = open(infile)
    fout = open(ofile, "a")

    for line in fin.readlines():
        # example line: ABI A BI
        line = line.strip().split()
        # The first eleement in line is a word
        word = line[0]

        pronunciation = []
        
        nsyll = len(line[1:])
        for i in range(nsyll):
            syl = line[i+1]

            # print out {word syl} pair for debugging 
            if debug: print line[0], syl

            # Check whether the syllable is in the kdictmap dictionary
	    if kdictmap.has_key(syl): pronunciation.append(kdictmap[syl])
	    else: 
                if debug: print "#### Syllable not in kdictmap"
                pronunciation.append(syl)
        
        # The broken up segements in each syllable are not glued together
        # with a space between segments.
        pronstring = ' '.join(pronunciation)

        if debug: print "pronunciation string: ", pronstring

        final_dict_entry = []

	
        # WITHIN-WORD PHONOLOGICAL RULES ARE DEFINED HERE 
        # Using regular expressions:

        # (?=[...]) is a lookahead assertion that mathes if ... matches next
        # (?![...]) matches if ... does not match next.
         
        # 1. Coda neutralization 
        # 1.1. SS + consonant

        # Coda neutralization
        # {GG, DD, BB, JJ, SS, S, K, T, P, C } --> {G, D, B, J} / __ Consnants
        pronstring = re.sub('GG (?![A Y E O W U I])', 'G ', pronstring)
        pronstring = re.sub('DD (?![A Y E O W U I])', 'D ', pronstring)
        pronstring = re.sub('BB (?![A Y E O W U I])', 'B ', pronstring)
        pronstring = re.sub('JJ (?![A Y E O W U I])', 'J ', pronstring)
        pronstring = re.sub('K (?![A Y E O W U I])', 'G ', pronstring)
        pronstring = re.sub('T (?![A Y E O W U I])', 'D ', pronstring)
        pronstring = re.sub('P (?![A Y E O W U I])', 'B ', pronstring)
        pronstring = re.sub('C (?![A Y E O W U I])', 'J ', pronstring)
              
        pronstring = re.sub(r'SS (?![A Y E O W U I])', 'D ', pronstring)
        # SS D --> D D --> D
        pronstring = re.sub(' D D ', ' D ', pronstring)
        pronstring = re.sub(r' S (?![A Y E O W U I])', ' D ', pronstring)

        
        # nasalization: SS N --> N N
        pronstring = re.sub(r'SS (?=[N])', 'N ', pronstring)

        # 2. Coda cluster simplification
        # Underlying consonant clusters are subject to simplification, 
        # resulting in removal of either the first or the second consonant
        pronstring = re.sub(r'LG H', 'L G', pronstring)
        pronstring = re.sub(r'LG (?=[A E])', 'L G ', pronstring)
        pronstring = re.sub(r'LG (?=[N, B, G])', 'G ', pronstring)
        pronstring = re.sub(r'LH (?=[A, D, EO, G, J])', 'L ', pronstring)
        pronstring = re.sub(r'NH (?=[E])', 'N ', pronstring)
        pronstring = re.sub(r'NJ (?=[A E I O U])', 'N J ', pronstring)
        pronstring = re.sub(r'NJ (?![A Y E O W U I])', 'N ', pronstring)
        # coda cluster simplification + aspiration
        pronstring = re.sub('LM (?=[D, G])', 'M ', pronstring)
        pronstring = re.sub('LM (?=[E, I, YI])', 'L M ', pronstring)

        pronstring = re.sub('LB (?=[EU])', 'L B ', pronstring)
        pronstring = re.sub('LB (?=[G])', 'B ', pronstring)
        pronstring = re.sub('LB (?=[G])', 'L ', pronstring)
        pronstring = re.sub('LT (?=[A])', 'L T ', pronstring)
        pronstring = re.sub('GS (?=[A E I O U])', 'G S ', pronstring)
        pronstring = re.sub('BS (?![A Y E O W U I])', 'B ', pronstring)
        pronstring = re.sub('BS (?=[A E I O U])', 'B S ', pronstring) 
        # Nasalization
        # {D, DD, T} --> {N} / __ {N, M}
        pronstring = re.sub('[D DD T] (?=[N, M])', 'N ', pronstring)
        # {B, BB, P} --> {M} / ___ {M}
        pronstring = re.sub('[B BB P] (?=[M])', 'M ', pronstring)

        # SALM --> SAM
        pronstring = re.sub('LM$', 'M', pronstring)
        # GGADALG --> GGADAG
        pronstring = re.sub('LG$', 'G', pronstring)

        # Collapse some ambiguous vowels
        # {YAE YE} -> {YE}
        pronstring = re.sub(' YAE ', ' YE ', pronstring)
        pronstring = re.sub(' WE ', ' OE ', pronstring)
 
        pronstring = re.sub('YAE$', 'YE', pronstring)
        pronstring = re.sub('WE$', 'OE', pronstring)
        final_dict_entry.append([word, pronstring])

        # FINALLY SORT THE NEWLY GENERATED PRONUNCIATION DICTIONARY
        final_dict_entry.sort()
        for i in final_dict_entry:
            final_pronunciation = ' '.join(i)
            #print final_pronunciation
            fout.write(final_pronunciation+"\n")

    fin.close()
    fout.close()
        
if __name__ == "__main__":
    if os.path.exists("kdict1.txt"):
        os.remove("kdict1.txt")
    # input and output is, again, hard-coded
    read_file(infile="kdict0.txt", ofile="kdict1.txt")

