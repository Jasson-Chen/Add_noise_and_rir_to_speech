# @Time    : 8/20/21 18:00 PM
# @Author  : Yunqi Chen
# @Affiliation  : Nanyang Technological University
# @Email   : chenyunqi101@gmail.com
# @File    : download_and_extract_noise_file.py

"""
dataset:
MUSAN noise subdataset

Usage:
python download_and_extract_noise_file.py \
    --data_root <absolute path to where the data should be stored> 
"""

import os
import shutil
import argparse
import logging
import re
import tarfile
import urllib.request

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
    extract_file(filepath, data_dir)



def extract_file(filepath: str, data_dir: str):
    try:
        tar = tarfile.open(filepath)
        tar.extractall(data_dir)
        tar.close()
    except Exception:
        logging.info('Not extracting. Maybe already there?')

def main():
    parser = argparse.ArgumentParser(description='MUSAN noise download')
    parser.add_argument("--data_root", required=True, default='/notebooks/data_processing', type=str)
    args = parser.parse_args()
    
    data_root = args.data_root

    data_set = 'MUSAN'
    URL = 'https://www.openslr.org/resources/17/musan.tar.gz'
    
    # Download noise dataset
    file_path = os.path.join(data_root, data_set + ".tar.gz")
    __maybe_download_file(file_path, URL)
    
    # Extract all the noise file
    if not os.path.exists(data_root + '/musan'):
        __extract_all_files(file_path, data_root, data_root)
    
    download_musan_noise_dir = data_root + '/musan/noise/'
    noise_dir = data_root + '/noise/'
    if not os.path.exists(noise_dir):
        os.mkdir(noise_dir)
    os.chdir(download_musan_noise_dir)
    
    file_path = './free-sound/'
    wavelist=[]
    filenames=os.listdir(file_path)
    for filename in filenames:
        name,category=os.path.splitext(file_path+filename)
        if category=='.wav':  
            wavelist.append(filename)

    for file in wavelist:
        f_src = './free-sound/' + file
        f_dst = noise_dir + file
        shutil.copyfile(f_src, f_dst)

        
    file_path = './sound-bible/'
    wavelist=[]
    filenames=os.listdir(file_path)
    for filename in filenames:
        name,category=os.path.splitext(file_path+filename)
        if category=='.wav':  
            wavelist.append(filename)

    for file in wavelist:
        f_src = './sound-bible/' + file
        f_dst = noise_dir + file
        shutil.copyfile(f_src, f_dst)
        
    os.chdir(noise_dir)
    g = os.walk(r"./")
    step = 1
    for path,dir_list,file_list in g:
        for file in file_list:
            os.rename('./'+file, './'+str(step)+'.wav')
            step = step + 1
        
if __name__ == "__main__":
    main()
