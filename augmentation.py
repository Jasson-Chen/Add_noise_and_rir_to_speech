def mix_rir_package(destination: str, source: str):
    import os, shutil

    ReverDB_root = source
    Room_name = ['Hotel_SkalskyDvur_ConferenceRoom2', 'Hotel_SkalskyDvur_Room112', 'VUT_FIT_E112',
                 'VUT_FIT_L207',
                 'VUT_FIT_L212', 'VUT_FIT_L227', 'VUT_FIT_Q301', 'VUT_FIT_C236', 'VUT_FIT_D105']

    step = 1
    for i in range(9):
        print("Moving", Room_name[i])
        speaker_name = os.listdir(os.path.join(ReverDB_root, Room_name[i], 'MicID01'))

        for j in range(len(speaker_name)):
            position_name = []
            for lists in os.listdir(os.path.join(ReverDB_root, Room_name[i], 'MicID01', speaker_name[j])):
                sub_path = os.path.join(ReverDB_root, Room_name[i], 'MicID01', speaker_name[j], lists)

                if os.path.isdir(sub_path):
                    position_name.append(sub_path)

            for k in range(len(position_name)):
                selected_rir_path = os.path.join(position_name[k], 'RIR')
                rir_wav_path = os.path.join(selected_rir_path, os.listdir(selected_rir_path)[0])
                basis = rir_wav_path[len(source):].replace("/", "_").replace("\\", "_").split(".")[0]
                dest_path = os.path.join(destination, str(step) + "_" + basis + '.wav')
                print(f"Copy from {rir_wav_path} to {dest_path}")
                shutil.copyfile(rir_wav_path, dest_path)
                step = step + 1

def add_rir(src_file, wav_info, info=None, rir_id=None, rir_data_mix_folder="reverdb"):
    import os, random
    #import numpy as np
    #import soundfile as sf
    #from scipy import signal
    from glob import glob
    
    command = None
    #reverb_sig = None
    if os.path.exists(src_file):
        #sig, sr = sf.read(src_file)
        rir_wav_path = None
        print("rir_data_mix_folder", rir_data_mix_folder)
        while rir_wav_path is None or not os.path.exists(rir_wav_path):
            try:
                if rir_wav_path is None:
                    if rir_id is None or rir_id < 1 or rir_id > 1674:
                        rir_id = str(random.randint(1, 1674))

                    rir_wav_path = glob(os.path.join(rir_data_mix_folder, rir_id + '_*.wav'))[0]
                else:
                    rir_wav_path = random.sample(glob(os.path.join(rir_data_mix_folder, '*.wav')), 1)[0]
            except:
                print("Error loading rir", rir_wav_path)
                rir_wav_path = None

        if rir_wav_path is not None:
            #rir, sr_rir = sf.read(rir_wav_path)

            #h = np.array(rir)
            basis = '_'.join(os.path.basename(rir_wav_path)[:-4].split('_')[1:])
            print(f"Adding RIR {basis} to", os.path.basename(src_file))
            #command = f"ffmpeg -i {src_file} -i \"{rir_wav_path}\" -filter_complex '[0] [1] afir=dry=10:wet=10 [reverb]; [0] [reverb] amix=inputs=2:weights=3 1' -c:a {wav_info.codec} -b:a {wav_info.bitrate} -ac {wav_info.channels} -ar {wav_info.samplerate} -f {wav_info.format.lower()} - | "
            command = f"ffmpeg -i {src_file} -i \"{rir_wav_path}\" -filter_complex '[0] [1] afir=dry=10:wet=10' -c:a {wav_info.codec} -b:a {wav_info.bitrate} -ac {wav_info.channels} -ar {wav_info.samplerate} -f {wav_info.format.lower()} - | "
            info["RIR"] = basis
            #reverb_sig = signal.lfilter(h, 1, sig)

            #try:
            #    if isinstance(dest_file, (bool)):
            #        dest_file = src_file

            #    if dest_file is not None:
            #        sf.write(dest_file, reverb_sig, sr)
            #        if info is not None:
            #            info["RIR"] = basis
            #except:
            #    print("Error writing to destination file", dest_file)
    else:
        print("File not exists:", src_file)

    #return reverb_sig
    return command

def get_audio_info(wav_fn, verbose=False):
    import soundfile as sf
    wav_info = sf.info(wav_fn)

    codecs = {}
    with open("codecs.info", "r") as f:
        lines = f.readlines()
        for line in lines:
            [key, value] = line.strip().split("=")
            codecs[key] = value

    wav_info.codec = codecs[wav_info.subtype_info]
    bitrate_header = "bytes/sec"
    bitrate_header_pos = wav_info.extra_info.lower().index(bitrate_header)
    bitrate_header_pos = wav_info.extra_info.lower().index(":", bitrate_header_pos)
    wav_info.bitrate = float(wav_info.extra_info[bitrate_header_pos+1:wav_info.extra_info.lower().index('\n', bitrate_header_pos)].strip()) / 1000
    wav_info.bitrate = f"{wav_info.bitrate}k"

    if verbose:
        print("Audio:", wav_fn)
        print("Sample Rate:", wav_info.samplerate)
        print("Channels:", wav_info.channels)
        print("Format:", wav_info.format)
        print("Format Info", wav_info.format_info)
        print("Subtype:", wav_info.subtype_info)
        print("Codec:", wav_info.codec)
        print("Bitrate:", wav_info.bitrate)
        print("Endian:", wav_info.endian)
        print("Check:", sf.check_format(wav_info.format, wav_info.subtype, wav_info.endian))
        print("Extra:", wav_info.extra_info)

    return wav_info

def mix_cocktail(src_dir, dest_dir, codecs, info={}, scheme=(True, .5, 1), reverdb_dir="reverdb", verbose=False):
    from glob import glob
    import random, os
    import shutil
    
    commands = []
    if isinstance(src_dir, str):
        src_dir = glob(f"{src_dir}/*.wav")

    for wav_fn in src_dir:
        fname = "".join(os.path.basename(wav_fn).split(".")[:-1])
        wav_info = get_audio_info(wav_fn, verbose)
        last_format = wav_info.format.lower()
        path = os.path.join(dest_dir, f"{fname}.wav")
        info[fname] = {"codecs": []}

        command = None
        if scheme[0]:
            command = add_rir(wav_fn, wav_info, 
                              info=info[fname], 
                              rir_id=None if isinstance(scheme[0], (bool)) else scheme[0], rir_data_mix_folder=reverdb_dir)

        num_codecs = len(codecs)
        
        if num_codecs > 0:
            sampled_codecs = codecs.copy()
            speed_perturbation = min(100.0, max(0.5, scheme[1]))
            mixed_codecs_left = max(1, min(num_codecs, scheme[2]))
            while mixed_codecs_left > 0 and len(sampled_codecs) > 0:
                codec = random.sample(sampled_codecs, 1)[0]
                sampled_codecs.remove(codec)
                if not codec.startswith("#"):
                    codec = codec.split(",")
                    # Pipe commands to follow Kaldi style
                    if len(codec) == 4:
                        info[fname]["codecs"].append(codec)
                        if command is None:
                            command = f"ffmpeg -i \"{wav_fn}\" -c:a {codec[1]} -b:a {codec[2]} -ac 1 -ar {codec[3]} -f {codec[0]} - | "
                        else:
                            command += f"ffmpeg -f {last_format} -i - -c:a {codec[1]} -b:a {codec[2]} -ac 1 -ar {codec[3]} -f {codec[0]} - | "
                        last_format = codec[0]
                        mixed_codecs_left -= 1
                    else:
                        print("Unknown codec specification:", ",".join(codec))

            if command is None or last_format is None:
                command = f"cp \"{wav_fn}\" \"{path}\""
            else:
                command += f"ffmpeg -y -f {last_format} -i - -c:a {wav_info.codec} -b:a {wav_info.bitrate} -ac {wav_info.channels} -af \"atempo={speed_perturbation}\" -ar {wav_info.samplerate} \"{path}\""
            commands.append(command)
        else:
            command = f"ffmpeg -y -i {wav_fn} -c:a {wav_info.codec} -b:a {wav_info.bitrate} -ac {wav_info.channels} -af \"atempo={speed_perturbation}\" -ar {wav_info.samplerate} -f {wav_info.format} \"{path}\""
            commands.append(command)

    if verbose:
        print(f"Generated {len(commands)} commands")
    return commands

def augment(dataset, dest_dir, config, scheme=(True, 0.2, 0.2, 0.2, 1., 1), reverdb_dir="reverdb", verbose=False):
    import os, random
    import json

    from pathlib import Path
    parent_dir = Path(dest_dir).parents[1]
    dest_info_fn = os.path.join(parent_dir, "cocktail.json")

    info = {}
    with open(dest_info_fn, "w+") as f:
        json.dump(info, f)

    categories = ["[MINOR DISTORTION CODECS]",
                  "[MEDIUM DISTORTION CODECS]",
                  "[HIGH DISTORTION CODECS]"]
    codecs = {category:[] for category in categories}
    codec = None
    with open(config, "r") as f:
        lines = f.readlines()
        for line in lines:
            config = line.strip()
            if len(config) > 0:
                if config in codecs:
                    codec = config
                    codecs[codec] = []
                elif codec is None:
                    print("Codec Category not found", config)
                else:
                    codecs[codec].append(config)
            config = f.readline()

    random.shuffle(dataset)
    data_length = len(dataset)
    end_index = int(data_length * (1 - sum(scheme[1:4])))
    clean_set = dataset[:end_index]
    clean_set = [f"cp \"{src}\" \"{os.path.join(dest_dir, os.path.basename(src))}\"" for src in clean_set]
    distorted_sets = []
    for category, percent in zip(categories, scheme[1:4]):
        if percent > 0:
            delta = min(data_length, end_index + int(data_length * percent))
            distorted_sets.append(mix_cocktail(dataset[end_index:delta],
                                               dest_dir,
                                               codecs[category], info,
                                               reverdb_dir=reverdb_dir,
                                               scheme=(scheme[0], scheme[4], scheme[5]), verbose=verbose))
            end_index = delta
        else:
            distorted_sets.append([])

    distorted_sets.insert(0, clean_set)

    with open(dest_info_fn, "w+") as f:
        json.dump(info, f)

    return distorted_sets