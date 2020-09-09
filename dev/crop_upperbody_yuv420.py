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

DB_PATH = '/media/jfm/Slave/Solos'
VIDEOS_PATH = os.path.join(DB_PATH, 'videos')
DST_PATH = os.path.join(DB_PATH, 'videos_yuv420_cropped_upperbody_256')

"""
This script crop Solos videos taking as coords the maximum coordinates of the upperbody.

Warning:
This is an unstable code as it depends on a ffprobe wrapping. 
Some videos may fail if ffprobe returns exceptional metadata.
An alternative is provided via imageio, but it doesn't support webm videos. 

"""


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

    sk_reader = Solos.SKReader(in_ram=True, download=True)
    solos_ids = Solos.get_solos_ids()
    tree = Directory_Tree(VIDEOS_PATH)
    tmp = tempfile.gettempdir()
    tmp = os.path.join(tmp, 'yuv420_conversor.json')

    if not os.path.exists(DST_PATH):
        os.mkdir(DST_PATH)
    tree.clone_tree(DST_PATH)
    if RECOVER:
        list_of_video_paths = BaseDict().load(tmp)['paths']
    else:
        list_of_video_paths = list(tree.paths(root=VIDEOS_PATH))
    failure = []
    progress_bar = tqdm(list_of_video_paths)

    for video_path in progress_bar:
        dst_path = video_path.replace(VIDEOS_PATH, DST_PATH)
        key = video_path.split('/')[-1].split('.')[0]
        cat = video_path.split('/')[-2]
        try:
            metadata = FFProbe(video_path)
            vw = int(metadata.video[0].width)
            vh = int(metadata.video[0].height)
        except Exception:
            try:
                vw, vh = get_size(video_path)
            except Exception as ex:
                failure.append(video_path)
                print(f'Metadata exception at:'
                      f'{video_path}')
                continue
        skeleton = sk_reader[key]
        # Interpolation may point out of the img
        # Cropping out of the image leads to errors in ffmpeg
        x_max = min(skeleton[:, 0, :].max(), vw)
        x_min = max(skeleton[:, 0, :].min(), 0)
        y_max = min(skeleton[:, 1, :].max(), vh)
        y_min = max(skeleton[:, 1, :].min(), 0)
        w = int(x_max - x_min)
        h = int(y_max - y_min)

        input_options = ['-y']
        input_options = ['-y', '-hide_banner', '-loglevel', 'panic']
        output_options = ['-vf', f"crop={w}:{h}:{int(x_min)}:{int(y_min)}", '-s', '256x256', '-pix_fmt', 'yuv420p']
        apply_single(video_path, dst_path, input_options, output_options, ext='.mp4')
        progress_bar.set_postfix_str(f'{cat}-->{key}')
    json = BaseDict()
    json['paths'] = failure
    json.write(tmp)
    print('Wrong videos:')
    for s in failure:
        print(s)
