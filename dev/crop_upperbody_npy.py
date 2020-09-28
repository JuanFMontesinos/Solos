import os
import sys
from shutil import rmtree
import subprocess
import tempfile

import numpy as np
from ffprobe import FFProbe
from tqdm import tqdm
import imageio

from flerken.video.utils import apply_single
from torchtree import Directory_Tree
from flerken.utils import BaseDict
import Solos

DB_PATH = '/media/jfm/Slave/Solos'
VIDEOS_PATH = os.path.join(DB_PATH, 'videos')
DST_PATH = os.path.join('/media/jfm/SlaveEVO970/Solos', 'frames')

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


class FFMPEGFrameExtractor:
    def __init__(self, path):
        self.path = path
        tmp = tempfile.gettempdir()
        self.dst = os.path.join(tmp, 'frame_extraction')

    def __enter__(self):
        self.make_folder()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        rmtree(self.dst)

    def make_folder(self):
        if os.path.exists(self.dst):
            rmtree(self.dst)
        os.mkdir(self.dst)

    def read_frames(self):
        files = sorted(os.listdir(self.dst))
        paths = [os.path.join(self.dst, f) for f in files]

        frames = [imageio.imread(p) for p in paths]
        frames = np.stack(frames)
        return frames


if __name__ == '__main__':
    VERBOSE = False
    sk_reader = Solos.SKReader(in_ram=True, download=True)
    solos_ids = Solos.get_solos_ids()
    tree = Directory_Tree(VIDEOS_PATH)

    if not os.path.exists(DST_PATH):
        os.mkdir(DST_PATH)
    tree.clone_tree(DST_PATH)

    list_of_video_paths = list(tree.paths(root=VIDEOS_PATH))
    failure = []
    progress_bar = tqdm(list_of_video_paths)

    for video_path in progress_bar:
        dst_path = video_path.replace(VIDEOS_PATH, DST_PATH).split('.')[0] + '.npy'
        with FFMPEGFrameExtractor(video_path) as extractor:

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

            path = os.path.join(extractor.dst, 'frame_%05d.png')
            input_options = ['-y', '-hide_banner', '-loglevel', 'panic']
            output_options = ['-vf', f"crop={w}:{h}:{int(x_min)}:{int(y_min)}", '-s', '256x256']

            result = subprocess.Popen(["ffmpeg", *input_options, '-i', video_path, *output_options, path],
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            stdout = result.stdout.read()
            stderr = result.stderr
            if stdout != '' and VERBOSE:
                print(stdout.decode("utf-8"))
            if stderr is not None and VERBOSE:
                print(stderr.read().decode("utf-8"))
            frames = extractor.read_frames()
            np.save(dst_path, frames)
            progress_bar.set_postfix_str(f'{cat}-->{key}')
    print('Wrong videos:')
    for s in failure:
        print(s)
