#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import re
import codecs
import unicodedata

# Tae-Jin Yoon
# McMaster University
# tjyoon@mcmaster.ca
# (c) 2011
""" 
    Usage: python han2uniconversion.py
           If other input file, change the second to the bottom line
           in the code, i.e.,
           infile="YourFileName.txt"
    input
        1. script_nmbd_by_sentence.txt (in hangul)
        2. (with a change)  allscript.txt (in hangul)
    output files: 
        1. kdict0.txt    (dictionary for HTK)
        2. kwordfreq.txt (frequency list for words)
        3. ksylfreq.txt  (frequency list for syllables)
        4. kwordlist.txt (word in Korean and Unicode)
        NOTE: make_kdict.py is used to convert kdict0.txt to kdict1.txt
"""

debug = 0

def read_file(infile):
    # An input file in Korean
    f = codecs.open(infile, encoding="utf-8")
    # An output file of words both with Korean and Unicode
    ###fwlistout = codecs.open("kwordlist.txt", encoding='utf-8', mode="w+")

    # output files
    kdictout = codecs.open("kdict0.txt", "w+", encoding="utf-8")
    ###kwordfreq = codecs.open("kwordfreq.txt", "w+", encoding="utf-8")
    ###kwordlist = codecs.open("word.list", "w+", encoding="utf-8")
    ###ksylfreq = codecs.open("ksylfreq.txt", "w+", encoding="utf-8")

    # Dictionary to store words and syllable with frequency
    kworddict = {}
    ksyldict = {}
    
    for line in f.readlines():
        # A space (' ') is used to separate A sentence in each line to words.
        line = line.strip().split(' ')
        for wrd in line:

            # Python 3: strings are Unicode by default
            wrd = str(wrd)
            ###fwlistout.write(wrd)
            ###fwlistout.write("\n")

            # Each word chunk will be divided into syllabaries
            # Each syllabary is represented as fullname in the form of
            #   fullname: HANGUL SYLLABLE GI

            wordlist = []
            for i in range(len(wrd)):
                try:
                    fullname = unicodedata.name(wrd[i])
                except ValueError:
                    # Some characters may not have a name; skip them
                    continue
                if debug:
                    print("fullname: ", fullname)
                wordlist.append(fullname)

            # Now, we only select the last element in fullname
            # and process it. 
 
            wordlist2 = []
            for syllable in wordlist:
                syllable = syllable.strip().split()

                # "CJK" for Hanja (Chinese Characters)
                # BRACKETS and ELLIPSIS are removed 
                # DIGITS which are of the length 2of 2

                # note on continuation line
                # \ and implicite continaution line in {}, (), and []
                if len(syllable) == 3 and \
                   not(syllable[0]=="CJK" or
                        syllable[2]=="BRACKET" or
                        syllable[2] == "ELLIPSIS") :

                    # count the frequency of syllables (using dictionary)
                    if debug:
                        print("unicode chars: ", syllable[2])
                    ksyldict[syllable[2]] = ksyldict.get(syllable[2], 0) + 1
                    wordlist2.append(syllable[2])


            if debug:
                print("wordlist: ", wordlist2)
           
            # Put the syllables together into a word
            word = ''.join(wordlist2)
            eojeol = ' '.join(wordlist2)
            wordlist = word+" " + eojeol
            #print len(wordlist), wordlist

            # contruct a word frequency (using dictionary)
            if len(wordlist) > 2:
                kworddict[wordlist] = kworddict.get(wordlist, 0) + 1
                #kdictout.write(wordlist)

                # a pair of word and syllables ("NOGGI NOG GI")
                # will be saved to kwordlist.txt together with
                ###fwlistout.write(wordlist)
                ###fwlistout.write("\n")

    # Make a word frequency list
    wlist = list(kworddict.items())
    ###for word, freq in wlist: print(word, freq, file=kwordfreq)
    
    # Make a sorted Korean dictionary for HTK
    words = []
    for word, freq in wlist:
        words.append(word)

    # Sort the list of words
    words.sort()
    for w in words:
        word = w.split()
        ###print(word[0], file=kwordlist)
        kdictout.write(' '.join(word) + "\n")

    # Make a syllable frequency list
    syllist = list(ksyldict.items())
    ###for syl, freq in syllist: print(syl, freq, file=ksylfreq)

    # close all the open files
    ###fwlistout.close()
    kdictout.close()
    ###kwordfreq.close()
    ###kwordlist.close()
    ###ksylfreq.close() 
    f.close()
        
if __name__ == "__main__":
    # remove the existing files to prevent from being appended.
    for p in ["kdict0.txt", "kwordfreq.txt", "word.list", "ksylfreq.txt"]:
        if os.path.exists(p):
            os.remove(p)

    if len(sys.argv) < 2:
        print("Usage: python3 han2uniconversion.py <input_utf8_text>")
        sys.exit(1)

    infile = sys.argv[1]
    read_file(infile)
