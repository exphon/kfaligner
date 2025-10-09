# This script will resample the signal at 11,025Hz

# Tae-Jin Yoon
# McMaster University
# Dec, 2011

form Configuration for downstep_resampling
    comment Don't forget / at the end
    sentence Snddir ./KevinMin/
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
    Read from file... 'snddir$''fname$'
    Resample... 16000 50
    Rename... 'basename'
    Save as WAV file... 'snddir$''fname$'
    printline The file ''basename$'' is resampled to 16000Hz and saved...
    select Sound 'basename$'
    Remove
    endif
endfor
select all
Remove







