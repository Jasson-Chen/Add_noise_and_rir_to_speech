# Add_noise_and_rir_to_speech
The purpose of this code base is to add a specified signal-to-noise ratio noise from MUSAN dataset to a pure speech signal and to generate far-field speech data using room impulse response data from BUT Speech@FIT Reverb Database. 
## Noise and RIR dataset description:

- ### [BUT Speech@FIT Reverb Database](https://speech.fit.vutbr.cz/software/but-speech-fit-reverb-database ):

  The database is being built with respect to collect a large number of various Room Impulse Responses, Room environmental noises (or "silences"), Retransmitted speech (for ASR and SID testing), and meta-data (positions of microphones, speakers etc.).

  The goal is to provide speech community with a dataset for data enhancement and distant microphone or microphone array experiments in ASR and SID.

  In this codebase, we only use the RIR data, which is used to synthesize far-field speech, the composition of the RIR dataset and citation details are as follows.

  | Room Name |    Room Type    | Size (length, depth, height) (m) | (microphone_num x   loudspeaker_num) |
  | :-------: | :-------------: | :------------------------------: | :----------------------------------: |
  |   Q301    |     Office      |           10.7x6.9x2.6           |                31 x 3                |
  |   L207    |     Office      |           4.6x6.9x3.1            |                31 x 6                |
  |   L212    |     Office      |           7.5x4.6x3.1            |                31 x 5                |
  |   L227    |     Stairs      |           6.2x2.6x14.2           |                31 x 5                |
  |   R112    |   Hotel room    |           4.4x2.8x2.6            |                31 x 5                |
  |    CR2    | Conference room |          28.2x11.1x3.3           |                31 x 4                |
  |   E112    |  Lecture room   |          11.5x20.1x4.8           |                31 x 2                |
  |   D105    |  Lecture room   |          17.2x22.8x6.9           |                31 x 6                |
  |   C236    |  Meeting room   |           7.0x4.1x3.6            |               31 x 10                |

  ```
  @ARTICLE{8717722,
           author={Szöke, Igor and Skácel, Miroslav and Mošner, Ladislav and Paliesek, Jakub and Černocký, Jan},
           journal={IEEE Journal of Selected Topics in Signal Processing}, 
           title={Building and evaluation of a real room impulse response dataset}, 
           year={2019},
           volume={13},
           number={4},
           pages={863-876},
           doi={10.1109/JSTSP.2019.2917582}
   }
  ```

- ### [MUSAN database](https://arxiv.org/pdf/1510.08484):

  The database consists of music from several genres, speech from twelve languages, and a wide assortment of technical and non-technical noises and we only use the noise data in this database. Citation details are as follows.

  ```
  @misc{snyder2015musan,
        title={MUSAN: A Music, Speech, and Noise Corpus}, 
        author={David Snyder and Guoguo Chen and Daniel Povey},
        year={2015},
        eprint={1510.08484},
        archivePrefix={arXiv},
        primaryClass={cs.SD}
  }
  ```

  

## Before using the data-processing code:

- **If you do not want the original dataset to be overwritten**, please download the dataset again for use

- You need to create three files: **'training_list.txt', 'validation_list.txt', 'testing_list.txt'**, based on your training, validation and test data **file paths** respectively, and ensure the audio in the file paths can be read and written. 

- The content of the aforementioned **'*_list.txt'** files are in the following form:

  ```
  *_list.txt
  	/../...../*.wav
  	/../...../*.wav
  	/../...../*.wav
  ```

  

## Instruction for using the following data-processing code:

1. **mix_cleanaudio_with_rir_offline.py**: Generate far-field speech offline

   - two parameters are needed: 
     - **--data_root**: the data path which you want to download and store the RIR dataset in.
     - **--clean_data_list_path:** the path of the folder in which  **'training_list.txt', 'validation_list.txt', 'testing_list.txt'** are stored in

   - 2 folders will be created in data_root: 'ReverDB_data (Removable if needed)', 'ReverDB_mix'

     

2. **download_and_extract_noise_file.py**: Generate musan noise file

   - one parameters are needed: 
     - **--data_root**: the data path which you want to download and store the noise dataset in.
   - 2 folder will be created in data_root: 'musan (Removable if needed)', 'noise'

   

3. **vad_torch.py**: Voice activity detection when adding noise to the speech

   **The noise data is usually added online according to the SNR requirements, several pieces of code are provided below, please add them in the appropriate places according to your needs!**

   ```python
   import torchaudio
   import numpy as np
   import torch
   import random
   from vad_torch import VoiceActivityDetector
   
   
   def _add_noise(speech_sig, vad_duration, noise_sig, snr):
       """add noise to the audio.
       :param speech_sig: The input audio signal (Tensor).
       :param vad_duration: The length of the human voice (int).
       :param noise_sig: The input noise signal (Tensor).
       :param snr: the SNR you want to add (int).
       :returns: noisy speech sig with specific snr.
       """
       if vad_duration != 0:
           snr = 10**(snr/10.0)
           speech_power = torch.sum(speech_sig**2)/vad_duration
           noise_power = torch.sum(noise_sig**2)/noise_sig.shape[1]
           noise_update = noise_sig / torch.sqrt(snr * noise_power/speech_power)
   
           if speech_sig.shape[1] > noise_update.shape[1]:
               # padding
               temp_wav = torch.zeros(1, speech_sig.shape[1])
               temp_wav[0, 0:noise_update.shape[1]] = noise_update
               noise_update = temp_wav
           else:
               # cutting
               noise_update = noise_update[0, 0:speech_sig.shape[1]]
   
           return noise_update + speech_sig
       
       else:
           return speech_sig
       
   def main():
       # loading speech file
       speech_file = './speech.wav'
   	waveform, sr = torchaudio.load(speech_file)
   	waveform = waveform - waveform.mean()
   	
       # loading noise file and set snr
   	snr = 0       
   	noise_file = random.randint(1, 930)
   	
       # Voice activity detection
   	v = VoiceActivityDetector(waveform, sr)
   	raw_detection = v.detect_speech()
   	speech_labels = v.convert_windows_to_readible_labels(raw_detection)
   	vad_duration = 0
       if not len(speech_labels) == 0:
           for i in range(len(speech_labels)):
               start = speech_labels[i]['speech_begin']
               end = speech_labels[i]['speech_end']
               vad_duration = vad_duration + end-start
               
   	# adding noise
       noise, _ = torchaudio.load('/notebooks/noise/' + str(noise_file) + '.wav')
       waveform = _add_noise(waveform, vad_duration, noise, snr)
   
   if __name__ == '__main__':
       main()
   ```
