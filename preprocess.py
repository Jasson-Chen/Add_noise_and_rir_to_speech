if __name__ == "__main__":
    import os, shutil
    import argparse
    from glob import glob
    from augmentation import augment

    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="source wave files")
    parser.add_argument("dest", help="destination wave folder")
    parser.add_argument("config", help="configuration file")
    parser.add_argument("-v", "--verbose", default=False, action="store_true", help="show debug info", required=False)
    args = parser.parse_args()

    reverdb_dir = "reverdb"
    distortion_config = "distortion_codecs.conf"
    scheme = [False, .2, .2, .2, 1., 1]
    if os.path.exists(args.config):
        with open(args.config, "r") as f:
            lines = f.readlines()
            for line in lines:
                [key, value] = line.strip().split("=")
                if key == "ADD_REVERB":
                    scheme[0] = bool(value) if value == "True" or value == "False" or len(value) == 0 else value
                if key == "MINOR_DISTORTION_PERCENTAGE":
                    scheme[1] = float(value)
                elif key == "MEDIUM_DISTORTION_PERCENTAGE":
                    scheme[2] = float(value)
                elif key == "HIGH_DISTORTION_PERCENTAGE":
                    scheme[3] = float(value)
                elif key == "SPEED_PERTURBATION":
                    scheme[4] = float(value)
                elif key == "MIXED_CODECS_PER_CATEGORY":
                    scheme[5] = float(value)
                elif key == "DISTORTION_CONFIG_FILE":
                    distortion_config = value
                elif key == "REVERDB_DIR":
                    reverdb_dir = value
    else:
        parser.print_help()
        exit(1)
    
    if os.path.exists(args.src):
        src = os.path.abspath(args.src)
    else:
        parser.print_help()
        exit(1)

    if os.path.exists(args.dest):
        dest = os.path.abspath(args.dest)
    else:
        parser.print_help()
        exit(1)


    #(minor distortion percentage, 
    # medium distortion percentage, 
    # highly distortion percentage,
    # speed perturbation from 0.5 to 100.0
    # number of additive codecs per recording)
    scheme_dir = "_".join([str(s) for s in scheme])

    #src = os.path.join("/media/m/F439-FA9D/", "workshop", "callhome", "callhome_data", "data", "wav")
    #meta_src = os.path.join("/media/m/F439-FA9D/", "workshop", "callhome", "callhome_data", "data", "eval")
    #meta_dest = os.path.join("/media/m/F439-FA9D/", "workshop", "callhome", "callhome_data", "data", "adapt")
    
    dest = os.path.join(dest, scheme_dir, "wav")
    if not os.path.exists(dest):
        os.makedirs(dest)
    sets = augment(glob(os.path.join(src, "*.wav")), dest, distortion_config, scheme=scheme, reverdb_dir=reverdb_dir, verbose=args.verbose)

    with open(f"make_distorted_wavs.sh", "w+") as f:
        f.write("#!/bin/bash -x\n")
        f.write(f"if ! [ -f \"{dest}\" ]; then\n")
        f.write(f"\tmkdir -p \"{dest}\"\nfi")

        f.write("\n\n")
        for commands in sets:
            for command in commands:
                #f.write(f"echo \"{command}\n\n\"\n")
                f.write(f"{command}\n")

        f.write("\n\n")
        for fn in glob(os.path.join(src, "*")):
            f.write(f"cp \"{fn}\" \"{os.path.join(dest, os.path.basename(fn))}\"\n")

        #f.write("\n\n")
        #f.write(f"cp -R \"{meta_src}\" \"{meta_dest}\"\n")

        f.write("\n\n")
        f.write("echo \"Completed!\"")

    print("Preprocessing completed!")