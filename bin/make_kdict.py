#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import os
import re
import codecs
import string
import unicodedata

# kdictmap includes files that decomposed syllables into segments
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
debug2 = 0
debug3 = 1
applyrule = 1

def read_file(infile, ofile):

    fin = codecs.open(infile, mode="r", encoding="utf-8")
    # overwrite output to avoid accidental appends across runs
    fout = codecs.open(ofile, mode="w", encoding="utf-8")

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
            if debug:
                print(line[0], syl)

            # Check whether the syllable is in the kdictmap dictionary
            if syl in kdictmap:
                pronunciation.append(kdictmap[syl])
            else:
                if debug:
                    print("#### Syllable not in kdictmap")
                pronunciation.append(syl)
        

        # change the pronunciation sequences to lower-case sequences
        # e.g. S A NG G I D OE N --> s a ng g i d oe n
        pronunciation = list(map(str.lower, pronunciation))

        # The broken up segements in each syllable are not glued together
        # with a space between segments.

        pronstring = ' '.join(pronunciation)


        #if debug: print "pronunciation string: ", pronstring

        final_dict_entry = []

        # If applyrule flag is on, the dictionary is made with phonological rules implemented
        # If applyrule flag is off, the dictionary contains phonemic sequences	
        if applyrule == 1:

            # WITHIN-WORD PHONOLOGICAL RULES ARE DEFINED HERE 
            # Using regular expressions:

            # (?=[...]) is a lookahead assertion that mathes if ... matches next
            # (?![...]) matches if ... does not match next.
         
            # (?<=[...]) is a positive lookbehind assertion
            # (?<![...]) is a negative lookbehind assertion
 

            # 1. Coda neutralization 
            # 1.1. SS + consonant      

            if debug and re.search(' gg (?![ayeowui])', pronstring): print("gg + Cons -> g + Cons: ", pronstring)
            elif debug and re.search(' dd (?![ayeowui])', pronstring): print("dd + Cons -> d + Cons: ", pronstring)
            elif debug and re.search(' bb (?![ayeowui])', pronstring): print("bb + Cons -> b + Cons: ", pronstring)
            elif debug and re.search(' jj (?![ayeowui])', pronstring): print("jj + Cons -> j + Cons: ", pronstring)
            elif debug and re.search(' [k] (?![ayeowui])', pronstring): print("k + cons -> g + Cons: ", pronstring)
            elif debug and re.search(' [t] (?![ayeowui])', pronstring): print("t + cons -> t + Cons: ", pronstring)
            elif debug and re.search(' [p] (?![ayeowui])', pronstring): print("p + cons -> b + Cons: ", pronstring)
            elif debug and re.search(' [c] (?![ayeowui])', pronstring): print("c + Cons -> j + cons: ", pronstring)

            # Coda neutralization
            # {gg, dd, bb, jj, ss, s, k, t, p, c } --> {G, D, B, J} / __ Consnants
            pronstring = re.sub('gg (?![ayeowui])', 'g ', pronstring)
            pronstring = re.sub('dd (?![ayeowui])', 'd ', pronstring)
            pronstring = re.sub('bb (?![ayeowui])', 'b ', pronstring)
            pronstring = re.sub('jj (?![ayeowui])', 'j ', pronstring)
            pronstring = re.sub('k (?![ayeowui])', 'g ', pronstring)
            pronstring = re.sub('t (?![ayeowui])', 'd ', pronstring)
            pronstring = re.sub('p (?![ayeowui])', 'b ', pronstring)
            pronstring = re.sub('c (?![ayeowui])', 'j ', pronstring)
              
            # {ss, s} --> {d} /___ consonant
            if debug and re.search('ss (?![ayeowui])', pronstring): print("ss + C --> d + C: ", pronstring)
            pronstring = re.sub(r'ss (?![ayeowui])', 'd ', pronstring)

            if debug and re.search(' s (?![ayeowui])', pronstring): print("s + C --> d + C: ", pronstring)
            pronstring = re.sub(r' s (?![ayeowui])', ' d ', pronstring)
            # SS D --> D D --> D

            pronstring = re.sub(' d d ', ' dd ', pronstring)
            if debug and re.search(' d d ', pronstring):
                print("d d: ", pronstring)
        
            # nasalization: ss n --> n n; s n --> n
            pronstring = re.sub(r'ss (?=[n])', 'n ', pronstring)
            pronstring = re.sub(r' s (?=[n])', ' n ', pronstring)

            # 2. Coda cluster simplification
            # Underlying consonant clusters are subject to simplification, 
            # resulting in removal of either the first or the second consonant
            pronstring = re.sub(r'lg h', 'l g', pronstring)
            pronstring = re.sub(r'lg (?=[a e])', 'l g ', pronstring)
            pronstring = re.sub(r'lg (?=[n b g])', 'g ', pronstring)
            pronstring = re.sub(r'lh (?=[a d eo g j])', 'l ', pronstring)
            pronstring = re.sub(r'nh (?=[n g s])', 'n ', pronstring)
            pronstring = re.sub(r'nh (?=[a e i o u y eu])', 'n ', pronstring)
            pronstring = re.sub(r'nj (?=[a e i o y eu])', 'n j', pronstring)

            # 3. g h --> k
            if debug2 and re.search(' [bdgj] h (?=[aeiouwy])', pronstring): print("b/d/g/j h V --> p/t/k/c V: ", pronstring)
            pronstring = re.sub(' g h (?=[aeiouwy])', ' k ', pronstring)
            pronstring = re.sub('b h (?=[aeiouwy])', ' p ', pronstring)
            pronstring = re.sub('d h (?=[aeiouwy])', ' t ', pronstring)
            pronstring = re.sub('j h (?=[aeiouwy])', ' c ', pronstring)

            # h g --> k 
            if debug3 and re.search(' h [bdgj] (?=[aeiouwy])', pronstring): print("b/d/g/j h V --> p/t/k/c V: ", pronstring)
            pronstring = re.sub(' h g (?=[aeiouwy])', ' k ', pronstring)
            pronstring = re.sub('h b (?=[aeiouwy])', ' p ', pronstring)
            pronstring = re.sub('h d (?=[aeiouwy])', ' t ', pronstring)
            pronstring = re.sub('h j (?=[aeiouwy])', ' c ', pronstring)

            

            # Intervocalic h-deletion and post-sonorant h deletion
            if debug2 and re.search('(?<=[m n ng l r w y]) h (?=[aeiouwy])', pronstring): print("sonorants h V --> sonorants V: ", pronstring)
            pronstring = re.sub('(?<=[m n ng l r w y]) h (?=[a e i o u])', ' ', pronstring)
            
            if debug2 and re.search('(?<=[aeiouwy]) h (?=[aeiouwy])', pronstring): print("V h V --> V V: ", pronstring)
            pronstring = re.sub('(?<=[aeiouwy]) h (?=[aeiouwy])', ' ', pronstring)

            # h + d --> t;  

            # manh.da -> man.ta
            pronstring = re.sub(r'nh d', 'n t', pronstring)
            # manh.ji -> man.ci
            pronstring = re.sub(r'nh j', 'n c', pronstring)

            pronstring = re.sub(r'nj (?=[a y e o w u i])', 'n j ', pronstring)
            pronstring = re.sub(r'nj (?![a y e o w u i])', 'n ', pronstring)

            # coda cluster simplification + aspiration
            pronstring = re.sub('lm (?=[d g])', 'm ', pronstring)
            pronstring = re.sub('lm (?=[e i yi])', 'l m ', pronstring)

            pronstring = re.sub(r'lb (?=[eu])', 'l b ', pronstring)
            pronstring = re.sub(r'lb (?=[g])', 'b ', pronstring)
            pronstring = re.sub(r'lb (?=[g])', 'l ', pronstring)
            pronstring = re.sub(r'lt (?=[a])', 'l t ', pronstring)
            pronstring = re.sub(r'gs (?=[a e i o u])', 'g s ', pronstring)
            pronstring = re.sub(r'gs (?![a e i o u])', 'g ', pronstring)
            pronstring = re.sub(r'bs (?![a y e o w u i])', 'b ', pronstring)
            pronstring = re.sub(r'bs (?=[a e i o u])', 'b s ', pronstring) 

            # Nasalization
            # {D, DD, T} --> {N} / __ {N, M}
            pronstring = re.sub(r'[d dd t] (?=[n m])', 'n ', pronstring)

            # {B, BB, P} --> {M} / ___ {M}
            pronstring = re.sub(r'[b bb p] (?=[n m])', 'm ', pronstring)

            # nasal place assimilation
            if debug2 and re.search(r'n m', pronstring): print("Nasal place assimilation n m --> m m", pronstring)
          
            pronstring = re.sub(r'm n', 'm m', pronstring)

            # h n --> n n (nohneun --> nonneun)
            pronstring = re.sub(r'h n', 'n n', pronstring)

            # l r --> ll
            pronstring = re.sub(r'l r', 'l l', pronstring)
            # V l V --> V r V
            pronstring = re.sub(r'(?<=[aeiouwy]) l (?=[aeiouwy])', ' r ', pronstring)
     
            # SALM --> SAM
            pronstring = re.sub(r'lm$', 'm', pronstring)
            # GGADALG --> GGADAG
            pronstring = re.sub(r'lg$', 'g', pronstring)
            pronstring = re.sub(r'gs$', 'g', pronstring)
            # Collapse some ambiguous vowels
            # {YAE YE} -> {YE}
            pronstring = re.sub(r' yae ', ' ye ', pronstring)
            pronstring = re.sub(r' we ', ' oe ', pronstring)
 
            # YO -> O
            pronstring = re.sub(r'yo', 'yo', pronstring)
            pronstring = re.sub(r'yae$', 'ye', pronstring)
            #pronstring = re.sub(r'we$', 'oe', pronstring)

        # Add "sp" at the end of dict for consistency with the main dictionary
        final_dict_entry.append([word, pronstring+" sp"])
        # Uncomment the line below if you don't want sp at the end
        # final_dict_entry.append([word, pronstring])

        # FINALLY SORT THE NEWLY GENERATED PRONUNCIATION DICTIONARY
        final_dict_entry.sort()
        for i in final_dict_entry:
            final_pronunciation = ' '.join(i)
            # if debug:
            #     print(final_pronunciation)
            fout.write(final_pronunciation+"\n")

    fin.close()
    fout.close()
        
if __name__ == "__main__":
    if os.path.exists("kdict1.txt"):
        os.remove("kdict1.txt")
    # input and output is, again, hard-coded
    read_file(infile="kdict0.txt", ofile="kdict1.txt")

