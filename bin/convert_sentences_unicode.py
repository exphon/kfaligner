#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys
import re
import codecs
import unicodedata

""" input: script_nmbd_by_sentence.txt
    output: script_by_sentence_unicode.txt"
"""
def read_file(infile, ofile):
    with codecs.open(infile, encoding="utf-8") as fin, codecs.open(ofile, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip().split()
            wordlist = []
            for word in line:
                word = str(word)
                words = []
                for ch in word:
                    try:
                        fullname = unicodedata.name(ch)
                    except ValueError:
                        # Some characters may not have a Unicode name; skip
                        continue
                    parts = fullname.split()
                    if len(parts) == 3 and parts[0] != "CJK":
                        words.append(parts[2])
                    elif len(parts) == 2:
                        # DIGIT ONE/TWO/...
                        digit_map = {
                            "ZERO": "0", "ONE": "1", "TWO": "2", "THREE": "3",
                            "FOUR": "4", "FIVE": "5", "SIX": "6", "SEVEN": "7",
                            "EIGHT": "8", "NINE": "9",
                        }
                        if parts[1] in digit_map:
                            words.append(digit_map[parts[1]])
                if words:
                    wordlist.append(''.join(words))
            if wordlist:
                sentences = ' '.join(wordlist)
                # GET RID OF ELLIPSIS, BRACKETS, etc.
                sentences = re.sub('ELLIPSIS', '', sentences)
                sentences = re.sub('BRACKETS', '', sentences)
                # PUT LEADING 0 IN SINGLE DIGITS at line start
                sentences = re.sub('^1 ', '01 ', sentences)
                sentences = re.sub('^2 ', '02 ', sentences)
                sentences = re.sub('^3 ', '03 ', sentences)
                sentences = re.sub('^4 ', '04 ', sentences)
                sentences = re.sub('^5 ', '05 ', sentences)
                sentences = re.sub('^6 ', '06 ', sentences)
                sentences = re.sub('^7 ', '07 ', sentences)
                sentences = re.sub('^8 ', '08 ', sentences)
                sentences = re.sub('^9 ', '09 ', sentences)
                fout.write(sentences + "\n")
        
if __name__ == "__main__":
    print("Sentence_unicode.txt will be made")
    if len(sys.argv) < 2:
        print("Usage: python3 convert_sentences_unicode.py <input_utf8_text>")
        sys.exit(1)
    infile = sys.argv[1]
    ofile = "sentence_unicode.txt"
    read_file(infile, ofile)

