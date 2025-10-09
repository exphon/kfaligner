# check_alignment.praat
# A script is designed to help you to check the force-aligned files 
# with wave files
# Tae-Jin Yoon
# tjyoon@mcmaster.ca
# 6/30/2011
# Praat version: 5.0.35

form Configuration for Check_alignment
    sentence Snddir ./test/
    sentence Tgdir ./test/
    sentence Sound .wav
endform

clearinfo

Create Strings as file list... filelist 'snddir$'*'sound$'
num_files = Get number of strings

for j from 1 to num_files
    select Strings filelist
    fname$ = Get string... 'j'
    basename$ = fname$-sound$
    wavname$ = basename$+"sound$"
    tgname$ = basename$ + ".TextGrid"

    printline We will label 'fname$'

    if fileReadable("'tgdir$''tgname$'")
	printline 'tgname$' exists!

	Read from file... 'snddir$''fname$'
        Read from file... 'tgdir$''tgname$'

        btime = Get start time
	etime = Get end time

	select Sound 'basename$'
   	plus TextGrid 'basename$'

	View & Edit
		editor TextGrid 'basename$'
		        pause Click to play 'basename$'
			Play... btime etime
			pause Click to close 'basename$'

			Close
		endeditor
    else

	 printline 'tgname$' does not exists!
	
    endif
endfor

select Strings filelist
Remove







