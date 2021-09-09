#!/bin/bash
DATA_DIR="/media/m/F439-FA9D/workshop/callhome/callhome_data/data"

python3 preprocess.py "$DATA_DIR/wav" "$DATA_DIR/adapt" "config.conf"
chmod +x make_distorted_wavs.sh
./make_distorted_wavs.sh
rm make_distorted_wavs.sh