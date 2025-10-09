#!/bin/sh
if [ "$#" -ne "1" ]; then
    echo "Usage: ./make_dict.sh flist.txt"
    echo "     flist.txt contains sentences in Korean."
    exit
fi
  
echo "We will make a new dictionary"
echo "based on Korean text in Unicode"
python ./bin/han2uniconversion.py $1
python ./bin/make_kdict.py
rm -f kdict0.txt
mv -f kdict1.txt ./bin/
python ./bin/convert_sentences_unicode.py $1
cd ./bin/
python ./add_dict.py
cd ..
mv ./bin/dict ./model/
