# @Time    : 8/20/21 18:00 PM
# @Author  : Yunqi Chen
# @Affiliation  : Nanyang Technological University
# @Email   : chenyunqi101@gmail.com
# @File    : mix_cleanaudio_with_rir_offline.py

"""
dataset:
rir dataset: BUT Speech@FIT Reverb Database

Usage:
python mix_cleanaudio_with_rir_offline.py \
    --data_root <absolute path to where the data should be stored> \
    --clean_data_list_path <the path of the folder in which 'training_list.txt', 'validation_list.txt', 'testing_list.txt' are stored in> \
"""
import argparse
import glob
import json
import logging
import os
import re
import tarfile
import urllib.request

import librosa
import numpy as np
import soundfile as sf
import shutil
import random
from scipy import signal

def __maybe_download_file(destination: str, source: str):
    """
    Downloads source to destination if it doesn't exist.
    If exists, skips download
    Args:
        destination: local filepath
        source: url of resource
    Returns:
    """
    if not os.path.exists(destination):
        logging.info(f"{destination} does not exist. Downloading ...")
        urllib.request.urlretrieve(source, filename=destination + '.tmp')
        os.rename(destination + '.tmp', destination)
        logging.info(f"Downloaded {destination}.")
    else:
        logging.info(f"Destination {destination} exists. Skipping.")
    return destination


def __extract_all_files(filepath: str, data_root: str, data_dir: str):
    if not os.path.exists(data_dir):
        extract_file(filepath, data_dir)
    else:
        logging.info(f'Skipping extracting. Data already there {data_dir}')


def extract_file(filepath: str, data_dir: str):
    try:
        tar = tarfile.open(filepath)
        tar.extractall(data_dir)
        tar.close()
    except Exception:
        logging.info('Not extracting. Maybe already there?')
def move_rir_file(destination: str, source: str):

    ReverDB_root = source
    Room_name = ['Hotel_SkalskyDvur_ConferenceRoom2', 'Hotel_SkalskyDvur_Room112', 'VUT_FIT_E112',
                 'VUT_FIT_L207',
                 'VUT_FIT_L212', 'VUT_FIT_L227', 'VUT_FIT_Q301', 'VUT_FIT_C236', 'VUT_FIT_D105']

    step = 1
    for i in range(9):
        print("Moving", Room_name[i])
        speaker_name = os.listdir(ReverDB_root + Room_name[i] + '/MicID01')

        for j in range(len(speaker_name)):
            position_name = []
            for lists in os.listdir(ReverDB_root + Room_name[i] + '/MicID01/' + speaker_name[j]):
                sub_path = os.path.join(ReverDB_root + Room_name[i] + '/MicID01/' + speaker_name[j], lists)

                if os.path.isdir(sub_path):
                    position_name.append(sub_path)

            for k in range(len(position_name)):
                selected_rir_path = position_name[k] + '/RIR/'
                rir_wav_path = selected_rir_path + os.listdir(selected_rir_path)[0]
                shutil.copyfile(rir_wav_path, destination + str(step) + '.wav')
                step = step + 1


def main():
    parser = argparse.ArgumentParser(description='Google Speech Command Data download')
    parser.add_argument("--data_root", required=True, default='/notebooks/data_processing', type=str)
    parser.add_argument("--clean_data_list_path", required=True, default='/notebooks/data_processing/', type=str)
    parser.add_argument('--log', required=False, action='store_true')

    args = parser.parse_args()
    
    if args.log:
        logging.basicConfig(level=logging.DEBUG)

    
    # download and extrat RIR files
    print('Downloading BUT_ReverbDB dataset')
    data_set = 'ReverDB_dataset'
    URL = 'http://merlin.fit.vutbr.cz/ReverbDB/BUT_ReverbDB_rel_19_06_RIR-Only.tgz'
    rir_data_folder = args.data_root + '/ReverDB_data/'
    
    file_path = os.path.join(args.data_root, data_set + ".tar.gz")
    logging.info(f"Getting {data_set}")
    __maybe_download_file(file_path, URL)
    logging.info(f"Extracting {data_set}")
    __extract_all_files(file_path, args.data_root, rir_data_folder)
    
    rir_data_mix_folder = args.data_root + '/ReverDB_mix/'
    if not os.path.exists(rir_data_mix_folder):
        os.mkdir(rir_data_mix_folder)
        move_rir_file(rir_data_mix_folder, rir_data_folder)

        
        
    # Generate far-field wav offline
    print('Generating far-field dataset, Maybe lasting several hours')
    
    list_path = args.clean_data_list_path
    
    random.seed(2000)
        
    for split in ['testing', 'validation', 'training']:
        with open(os.path.join(list_path, split+'_list.txt'), 'r') as f:
            filelist = f.readlines()
        for file in filelist:
            file_path = file.strip()
            
            if random.random() < 0.5:
                sig, sr = sf.read(file_path)
                seed = random.randint(1, 1674)
                rir_wav_path = rir_data_mix_folder + str(seed) + '.wav'
                rir, sr_rir = sf.read(rir_wav_path)

                h = np.array(rir)
                reverb_sig = signal.lfilter(h, 1, sig)
                sf.write(file_path, reverb_sig, sr)
                                
    
    logging.info('Done!')


if __name__ == "__main__":
    main()
