#!/usr/bin/env python3

"""
Command-line usage:
  python align.py [options] wave_file transcript_file output_file
  where options may include:
	-r sampling_rate -- override which sample rate model to use, one of 8000, 11025, and 16000
	-s start_time    -- start of portion of wavfile to align (in seconds, default 0)
	-e end_time      -- end of portion of wavfile to align (in seconds, default to end)

You can also import this file as a module and use the functions directly.
"""

import os
import sys
import getopt
import wave
import re
import subprocess
import unicodedata


def prep_wav(orig_wav, out_wav, sr_override, wave_start, wave_end):
	global sr_models

	# If we had previously generated out_wav and wanted to reuse it, we could early-return.
	# Currently disabled by design (kept for reference).
	if os.path.exists(out_wav) and False:
		f = wave.open(out_wav, 'r')
		SR = f.getframerate()
		f.close()
		print("Already re-sampled the wav file to " + str(SR))
		return SR

	f = wave.open(orig_wav, 'r')
	SR = f.getframerate()
	f.close()

	soxopts = ""
	if float(wave_start) != 0.0 or wave_end is not None:
		soxopts += " trim " + wave_start
		if wave_end is not None:
			soxopts += " " + str(float(wave_end) - float(wave_start))

	# Resample if needed (model SR mismatch or override), or if we need to trim.
	if (sr_models is not None and SR not in sr_models) or (sr_override is not None and SR != sr_override) or soxopts != "":
		# Default to 16000 Hz for better quality (was 11025)
		new_sr = 16000
		if sr_override is not None:
			new_sr = sr_override

		print("Resampling wav file from " + str(SR) + " to " + str(new_sr) + soxopts + "...")
		SR = new_sr
		# Correct sox syntax: sox input output [effects]
		os.system("sox \"" + orig_wav + "\" \"" + out_wav + "\" rate -v " + str(SR) + soxopts)
	else:
		# Already at the desired sample rate and no trimming required.
		os.system("cp -f " + orig_wav + " " + out_wav)

	return SR


def _read_text_any_encoding(path):
	"""Read text file trying common encodings and return a unicode string.
	Tries: utf-8, utf-16, utf-16le, utf-16be, cp949, euc-kr. Strips leading BOM if present."""
	encodings = [
		'utf-8', 'utf-16', 'utf-16le', 'utf-16be', 'cp949', 'euc-kr'
	]
	data = None
	with open(path, 'rb') as fb:
		data = fb.read()
	for enc in encodings:
		try:
			s = data.decode(enc)
			# strip BOM if any survived
			if s and s[0] == '\ufeff':
				s = s[1:]
			return s
		except Exception:
			continue
	# Fallback: best-effort utf-8 with replacement
	try:
		s = data.decode('utf-8', errors='replace')
		if s and s[0] == '\ufeff':
			s = s[1:]
		return s
	except Exception:
		return ''


def prep_mlf(trsfile, mlffile, word_dictionary, surround, between):
	"""
	Prepare an input MLF from a transcript, using only words present in the provided dictionary.
	Optionally surround the sentence with tokens and insert a token between words.
	"""
	# Read in the dictionary to ensure all of the words we put in the MLF file are in the dictionary.
	with open(word_dictionary, 'r') as f:
		dictionary = {}
		for line in f.readlines():
			if line != "\n" and line != "":
				dictionary[line.split()[0]] = True

	# Read transcript with robust encoding handling
	content = _read_text_any_encoding(trsfile)
	lines = content.splitlines()

	words = []

	if surround is not None:
		words += surround.split(',')

	# this pattern matches hyphenated words, such as TWENTY-TWO; however, it doesn't work
	# with longer things like SOMETHING-OR-OTHER
	hyphenPat = re.compile(r'([A-Z]+)-([A-Z]+)')

	i = 0
	while i < len(lines):
		txt = lines[i].replace('\n', '')
		txt = txt.replace('{breath}', '{BR}').replace('&lt;noise&gt;', '{NS}')
		txt = txt.replace('{laugh}', '{LG}').replace('{laughter}', '{LG}')
		txt = txt.replace('{cough}', '{CG}').replace('{lipsmack}', '{LS}')

		for pun in [',', '.', ':', ';', '!', '?', '"', '%', '(', ')', '--', '---']:
			txt = txt.replace(pun, '')

		txt = txt.upper()

		# break up any hyphenated words into two separate words
		txt = re.sub(hyphenPat, r'\1 \2', txt)

		txt = txt.split()

		for wrd in txt:
			if wrd in dictionary:
				words.append(wrd)
				if between is not None:
					words.append(between)
			else:
				print("SKIPPING WORD", wrd)

		i += 1

	# Remove the last 'between' token from the end if it exists
	# (though with between_token=None, this won't execute)
	if between is not None and len(words) > 0 and words[-1] == between:
		words.pop()

	if surround is not None:
		words += surround.split(',')

	writeInputMLF(mlffile, words)


def writeInputMLF(mlffile, words):
	with open(mlffile, 'w') as fw:
		fw.write('#!MLF!#\n')
		fw.write('"*/tmp.lab"\n')
		for wrd in words:
			fw.write(wrd + '\n')
		fw.write('.\n')


def readAlignedMLF(mlffile, SR, wave_start):
	"""
	Read a MLF alignment output file with phone and word alignments and return a list of words.
	Each word is a list containing the word label followed by the phones, each phone is a tuple
	(phone, start_time, end_time) with times in seconds.
	sp phones are extracted from words and treated as separate pause intervals.
	"""
	with open(mlffile, 'r') as f:
		lines = [l.rstrip() for l in f.readlines()]

	if len(lines) < 3:
		raise ValueError("Alignment did not complete succesfully.")

	j = 2
	ret = []
	while lines[j] != '.':
		if len(lines[j].split()) == 5:  # start of a word; have a word label?
			# Make a new word list in ret and put the word label at the beginning
			wrd = lines[j].split()[4]
			ret.append([wrd])

		# Append this phone to the latest word (sub-)list
		ph = lines[j].split()[2]
		if SR == 11025:
			st = (float(lines[j].split()[0]) / 10000000.0 + 0.0125) * (11000.0 / 11025.0)
			en = (float(lines[j].split()[1]) / 10000000.0 + 0.0125) * (11000.0 / 11025.0)
		else:
			st = float(lines[j].split()[0]) / 10000000.0 + 0.0125
			en = float(lines[j].split()[1]) / 10000000.0 + 0.0125
		
		# Only add phones with duration > 0
		if st < en:
			ret[-1].append([ph, st + wave_start, en + wave_start])

		j += 1

	# Separate sp from words: if a word ends with sp, move it to a separate entry
	separated_ret = []
	for wrd in ret:
		if len(wrd) > 1 and wrd[-1][0] == 'sp':
			# Word has sp at the end - split it off
			sp_entry = wrd.pop()  # Remove sp from word
			separated_ret.append(wrd)  # Add word without sp
			separated_ret.append(['sp', sp_entry])  # Add sp as separate entry
		else:
			separated_ret.append(wrd)
	
	return separated_ret


def writeTextGrid(outfile, word_alignments):
	# make the list of just phone alignments
	phons = []
	for wrd in word_alignments:
		phons.extend(wrd[1:])  # skip the word label

	# make the list of just word alignments
	# elements of the form: ["word", ["phone1", st, en], ...]
	wrds = []
	for wrd in word_alignments:
		if len(wrd) == 1:
			continue
		wrds.append([wrd[0], wrd[1][1], wrd[-1][2]])

	# write the phone interval tier
	with open(outfile, 'w') as fw:
		fw.write('File type = "ooTextFile short"\n')
		fw.write('"TextGrid"\n')
		fw.write('\n')
		fw.write(str(phons[0][1]) + '\n')
		fw.write(str(phons[-1][2]) + '\n')
		fw.write('<exists>\n')
		fw.write('2\n')
		fw.write('"IntervalTier"\n')
		fw.write('"phone"\n')
		fw.write(str(phons[0][1]) + '\n')
		fw.write(str(phons[-1][-1]) + '\n')
		fw.write(str(len(phons)) + '\n')
		for k in range(len(phons)):
			fw.write(str(phons[k][1]) + '\n')
			fw.write(str(phons[k][2]) + '\n')
			fw.write('"' + phons[k][0] + '"' + '\n')

		# write the word interval tier
		fw.write('"IntervalTier"\n')
		fw.write('"word"\n')
		fw.write(str(phons[0][1]) + '\n')
		fw.write(str(phons[-1][-1]) + '\n')
		fw.write(str(len(wrds)) + '\n')
		for k in range(len(wrds) - 1):
			fw.write(str(wrds[k][1]) + '\n')
			fw.write(str(wrds[k + 1][1]) + '\n')
			fw.write('"' + wrds[k][0] + '"' + '\n')

		fw.write(str(wrds[-1][1]) + '\n')
		fw.write(str(phons[-1][2]) + '\n')
		fw.write('"' + wrds[-1][0] + '"' + '\n')


def prep_working_directory():
	os.system("rm -r -f ./tmp")
	os.system("mkdir ./tmp")


def prep_scp(wavfile):
	with open('./tmp/codetr.scp', 'w') as fw:
		fw.write(wavfile + ' ./tmp/tmp.mfc\n')
	with open('./tmp/test.scp', 'w') as fw:
		fw.write('./tmp/tmp.mfc\n')


def create_plp(hcopy_config):
	os.system('HCopy -T 1 -C ' + hcopy_config + ' -S ./tmp/codetr.scp')


def viterbi(input_mlf, word_dictionary, output_mlf, phoneset, hmmdir):
	# MLF includes sil at boundaries, so no -b option needed
	# sp is in dictionary at end of each word
	os.system('HVite -T 1 -a -m -I ' + input_mlf + ' -H ' + hmmdir + '/macros -H ' + hmmdir + '/hmmdefs  -S ./tmp/test.scp -i ' + output_mlf + ' -p 0.0 -s 5.0 ' + word_dictionary + ' ' + phoneset + ' > ./tmp/aligned.results')


def getopt2(name, opts, default=None):
	value = [v for n, v in opts if n == name]
	if len(value) == 0:
		return default
	return value[0]


if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], "r:s:e:", ["model="])

		# get the three mandatory arguments
		if len(args) != 3:
			raise ValueError("Specify wavefile, a transcript file, and an output file!")

		wavfile, trsfile, outfile = args

		sr_override = getopt2("-r", opts, None)
		wave_start = getopt2("-s", opts, "0.0")
		wave_end = getopt2("-e", opts, None)
		# Dictionary includes 'sp' at end of each word
		# Do NOT insert sp in MLF to avoid tee-model conflicts
		surround_token = getopt2("-p", opts, 'sil')
		between_token = getopt2("-b", opts, None)

		if sr_override is not None:
			try:
				sr_override = int(sr_override)
			except ValueError:
				raise ValueError("-r must be an integer: one of 8000, 11025, or 16000")

		if surround_token is not None and surround_token.strip() == "":
			surround_token = None
		if between_token is not None and between_token.strip() == "":
			between_token = None

		mypath = getopt2("--model", opts, None)
	except Exception:
		print(__doc__)
		(_type, value, _traceback) = sys.exc_info()
		print(value)
		sys.exit(0)

	# If no model directory was said explicitly, get directory containing this script.
	hmmsubdir = ""
	sr_models = None
	if mypath is None:
		mypath = os.path.dirname(os.path.abspath(sys.argv[0])) + "/model"
		hmmsubdir = "FROM-SR"
		# sample rates for which there are acoustic models set up, otherwise
		# the signal must be resampled to one of these rates.
		sr_models = [8000, 11025, 16000]

	if sr_override is not None and sr_models is not None and sr_override not in sr_models:
		raise ValueError("invalid sample rate: not an acoustic model available")

	word_dictionary = "./tmp/dict"
	input_mlf = './tmp/tmp.mlf'
	output_mlf = './tmp/aligned.mlf'

	# create working directory
	prep_working_directory()

	# Helper: detect if transcript contains Hangul (try multiple encodings)
	def contains_hangul(path: str) -> bool:
		try:
			text = _read_text_any_encoding(path)
			for ch in text:
				code = ord(ch)
				if 0xAC00 <= code <= 0xD7A3:
					return True
			return False
		except Exception:
			return False

	# If transcript is in Hangul, convert it to romanized tokens and augment dictionary
	trsfile_for_mlf = trsfile
	if contains_hangul(trsfile):
		print("Detected Hangul transcript; converting and augmenting dictionary...")
		# Prepare temp input in ./tmp
		os.system('cp -f "' + trsfile + '" ./tmp/hangul.txt')
		# 1) Convert sentences to romanized word tokens into ./tmp/sentence_unicode.txt
		#    Note: convert_sentences_unicode.py expects UTF-8 input; our hangul.txt is copied as-is.
		os.system('cd ./tmp && python3 ../bin/convert_sentences_unicode.py hangul.txt')
		trsfile_for_mlf = './tmp/sentence_unicode.txt'
		# 2) Build kdict0/kdict1 in ./tmp from the same Hangul input
		os.system('cd ./tmp && python3 ../bin/han2uniconversion.py hangul.txt')
		os.system('cd ./tmp && python3 ../bin/make_kdict.py')
		# 3) Merge with model dict using add_dict.py inside bin (expects kdict1 in CWD)
		os.system('cp -f ./tmp/kdict1.txt ./bin/kdict1.txt')
		os.system('cd ./bin && python3 add_dict.py')
		# 4) Use the merged dict from bin for this run
		os.system('cp -f ./bin/dict ' + word_dictionary)
	else:
		# Default: start from model dict (+ optional local)
		if os.path.exists("dict.local"):
			os.system("cat " + mypath + "/dict dict.local > " + word_dictionary)
		else:
			os.system("cat " + mypath + "/dict > " + word_dictionary)

	# prepare wavefile: do a resampling if necessary
	tmpwav = "./tmp/sound.wav"
	SR = prep_wav(wavfile, tmpwav, sr_override, wave_start, wave_end)

	if hmmsubdir == "FROM-SR":
		hmmsubdir = "/" + str(SR)

	# prepare mlfile (use converted transcript if applicable)
	prep_mlf(trsfile_for_mlf, input_mlf, word_dictionary, surround_token, between_token)

	# prepare scp files
	prep_scp(tmpwav)

	# generate the plp file using a given configuration file for HCopy
	create_plp(mypath + hmmsubdir + '/config')

	# run Viterbi decoding
	print("Running HVite...")
	mpfile = mypath + '/monophones'
	if not os.path.exists(mpfile):
		mpfile = mypath + '/hmmnames'
	viterbi(input_mlf, word_dictionary, output_mlf, mpfile, mypath + hmmsubdir)

	# output the alignment as a Praat TextGrid
	writeTextGrid(outfile, readAlignedMLF(output_mlf, SR, float(wave_start)))


