#!/bin/bash
clear
DATA_DIR="/media/m/F439-FA9D/workshop/callhome/callhome_data/data"

rm make_distorted_wavs.sh
python3 preprocess.py "$DATA_DIR/wav" "$DATA_DIR/adapt" "config.conf" --verbose
chmod +x make_distorted_wavs.sh
./make_distorted_wavs.sh
rm make_distorted_wavs.sh