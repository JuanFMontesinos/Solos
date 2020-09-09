from flerken.video.utils import apply_tree, apply_single

import os
import subprocess

if __name__ == '__main__':
    OR_PATH = '/media/jfm/Slave/Solos/videos'
    DST_PATH = '/media/jfm/Slave/Solos/audio_vk'

    rep = apply_tree(OR_PATH, DST_PATH,
                     output_options=['-ac', '1', '-ar', '16000'],
                     multiprocessing=0,
                     ext='.wav',
                     fn=apply_single)
