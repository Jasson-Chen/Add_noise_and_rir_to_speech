def add_rir(rir_data_mix_folder, src_file, dest_file=None):
    import os, random, numpy as np
    import soundfile as sf
    from scipy import signal
    
    reverb_sig = None
    if os.path.exists(src_file):
        sig, sr = sf.read(src_file)
        seed = random.randint(1, 1674)
        rir_wav_path = rir_data_mix_folder + str(seed) + '.wav'
        rir, sr_rir = sf.read(rir_wav_path)

        h = np.array(rir)
        reverb_sig = signal.lfilter(h, 1, sig)

        try:
            if isinstance(dest_file, (bool)):
                dest_file = src_file

            if dest_file is not None:
                sf.write(dest_file, reverb_sig, sr)
        except:
            print("Error writing to destination file", dest_file)
    else:
        print("File not exists:", src_file)

    return reverb_sig

def resample_change_tempo_add_codecs(src_dir, dest_dir, codecs, scheme=(1., 1), verbose=False):
    from glob import glob
    import random, os
    
    commands = []
    if isinstance(src_dir, str):
        src_dir = glob(f"{src_dir}/*.wav")

    for wav_fn in src_dir:
        fname = "".join(os.path.basename(wav_fn).split(".")[:-1])
        path = os.path.join(dest_dir, f"{fname}.wav")
        num_codecs = len(codecs)
        
        if num_codecs > 0:
            sampled_codecs = codecs.copy()
            speed_perturbation = min(100.0, max(0.5, scheme[0]))
            mixed_codecs_left = max(1, min(num_codecs, scheme[1]))
            num_mixed_codecs = mixed_codecs_left
            command = None
            last_format = None
            while mixed_codecs_left > 0 and len(sampled_codecs) > 0:
                codec = random.sample(sampled_codecs, 1)[0]
                sampled_codecs.remove(codec)
                if not codec.startswith("#"):
                    codec = codec.split(",")
                    # Pipe commands to follow Kaldi style
                    if len(codec) == 5:
                        if command is None:
                            command = f"ffmpeg -i {wav_fn if mixed_codecs_left == num_mixed_codecs else path} -c:a {codec[1]} -b:a {codec[2]} -ac 1 -ar {codec[3]} -f {codec[0]} - | "
                        else:
                            command += f"ffmpeg -f {last_format} -i - -c:a {codec[1]} -b:a {codec[2]} -ac 1 -ar {codec[3]} -f {codec[0]} - | "
                        last_format = codec[0]
                        mixed_codecs_left -= 1
                    else:
                        print("Unknown codec specification:", ",".join(codec))

            if command is None or last_format is None:
                command = f"cp \"{wav_fn}\" \"{path}\""
            else:
                command += f"ffmpeg -y -f {last_format} -i - -c:a pcm_mulaw -b:a 16k -ac 1 -af \"atempo={speed_perturbation}\" -ar {codec[4]} {path}"
            commands.append(command)
        else:
            command = f"ffmpeg -y -i {wav_fn} -c:a pcm_mulaw -ac 1 -af \"atempo={speed_perturbation}\" -ar 8000 \"{path}\""
            commands.append(command)

    if verbose:
        print(f"Generated {len(commands)} commands")
    return commands

def mix_codecs(dataset, dest_dir, config, scheme=(0.2, 0.2, 0.2, 1., 1), verbose=False):
    import os, random

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
    clean_set = dataset[:int(data_length * (1 - sum(scheme[:3])))]
    clean_set = [f"cp \"{src}\" \"{os.path.join(dest_dir, os.path.basename(src))}\"" for src in clean_set]
    distorted_sets = []
    for category, percent in zip(categories, scheme[:3]):
        if percent > 0:
            distorted_sets.append(resample_change_tempo_add_codecs(dataset[:int(data_length * percent)],
                                                                   dest_dir,
                                                                   codecs[category],
                                                                   scheme=(scheme[3], scheme[4]), verbose=verbose))
        else:
            distorted_sets.append([])

    distorted_sets.insert(0, clean_set)
    return distorted_sets