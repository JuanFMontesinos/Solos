import os
import sys
import tempfile

import fire

import numpy as np
from ffprobe import FFProbe
from tqdm import tqdm
import imageio

from torchtree import Directory_Tree
from flerken.utils import BaseDict
from flerken.video.utils import apply_single
import Solos

DB_PATH = '/media/jfm/SlaveEVO970/roch_cu_25'
VIDEOS_PATH = os.path.join(DB_PATH, 'videos')
DST_PATH = os.path.join(DB_PATH, 'videos_yuv420_cropped_upperbody_224')

"""
This script crop Solos videos taking as coords the maximum coordinates of the upperbody.

Warning:
This is an unstable code as it depends on a ffprobe wrapping. 
Some videos may fail if ffprobe returns exceptional metadata.
An alternative is provided via imageio, but it doesn't support webm videos. 

"""

special_cases = {
}


def get_size(path):
    reader = imageio.get_reader(path)
    metadata: dict = reader.get_meta_data()
    size = metadata.get('size')
    if size is None:
        size = metadata.get('source_size')
    if size is None:
        raise AttributeError(f'Imageio cannot retrieve size from {video_path}')
    return size


if __name__ == '__main__':
    RECOVER = False
    tree = Directory_Tree(VIDEOS_PATH)
    if not os.path.exists(DST_PATH):
        os.mkdir(DST_PATH)
    tree.clone_tree(DST_PATH)

    list_of_video_paths = list(tree.paths(root=VIDEOS_PATH))
    progress_bar = tqdm(list_of_video_paths)

    for video_path in progress_bar:
        dst_path = video_path.replace(VIDEOS_PATH, DST_PATH)
        key = video_path.split('/')[-1].split('.')[0]
        cat = video_path.split('/')[-2]

        input_options = ['-y']
        input_options = ['-y', '-hide_banner', '-loglevel', 'panic']
        output_options = ['-s', '256x256', '-pix_fmt', 'yuv420p']
        apply_single(video_path, dst_path, input_options, output_options, ext='.mp4')
        progress_bar.set_postfix_str(f'{cat}-->{key}')
