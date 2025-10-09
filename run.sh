#!/bin/sh
source ~/.bashrc
speaker=fv01
file=01
./align.py test/${speaker}_t01_s${file}.wav test/${speaker}_t01_s${file}.lab test/${speaker}_t01_s${file}.TextGrid

