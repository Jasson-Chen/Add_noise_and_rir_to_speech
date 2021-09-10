import os
from mix_cleanaudio_with_rir_offline import move_rir_file

dest_dir = "/media/m/F439-FA9D/workshop/reverbdbmix"
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
move_rir_file(dest_dir, "/media/m/F439-FA9D/workshop/reverbdb/")