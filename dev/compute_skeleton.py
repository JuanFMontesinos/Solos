from flerken.video.utils import apply_single
from flerken.utils import BaseDict
from torchtree import Directory_Tree
from tqdm import tqdm
from scipy.io.wavfile import read

import sys
from collections import deque
import threading

sys.path.append('/home/jfm/GitHub/OpenposeWrapper')
from openpose_wrapper.core import OPose

import fire


import time
import os
from shutil import rmtree


class FakeThread():
    def is_alive(self):
        return True


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result

    return timed


def main(root, gpu_ids=[0, 1], use_threading=False, verbose=True, ignore=[]):
    def full_path(paths, root):
        for path in paths:
            yield os.path.join(root, path)

    def gen_named_modules(module):
        for n, m in module.named_modules():
            yield n

    tree = Directory_Tree(root, ignore=ignore)  # Set of videos in a nutshell

    audio_dir = os.path.join(root, 'audio')  # Abs path to audio folder
    frame_dir = os.path.join(root, 'frames')  # Abs path to frames folder
    skeleton_dir = os.path.join(root, 'skeleton')  # Abs path to skeleton folder
    info_dir = os.path.join(root, 'info')  # Abs path to info folder
    for folder in gen_named_modules(tree.videos):
        path = os.path.join(info_dir, folder)
        if not os.path.exists(path):
            os.makedirs(path)
    paths = tuple(x for x, y in tree.videos.named_parameters())  # Rel path class1/video_1...classN/videoM
    # Folder making
    if verbose:
        print('Relative paths:')
        tuple(print(p) for p in paths)
        print('Absolute paths:')
    for root_ in (audio_dir, frame_dir, skeleton_dir):
        for path in full_path(paths, root_):
            if not os.path.exists(path):
                os.makedirs(path)
                if verbose:
                    print('Path: %s. Exist: %r' % (path, False))
            else:
                if verbose:
                    print('Path: %s. Exist: %r' % (path, True))

    # OpenPose instances
    # gpus = {idx: OPose({'num_gpu_start': 0, 'num_gpu': 2}) for idx in gpu_ids}

    gpus_available = deque(gpu_ids)
    print('Available gpus: %r' % gpu_ids)
    if hasattr(tree, 'info'):
        videos_available = dict({x: None for x in tree.videos.paths(root + '/videos')})
        videos_available_keys = tuple(videos_available.keys())
        for already_done in tree.info.paths():
            already_done = already_done.split('.')[0]
            for key in videos_available_keys:
                if already_done in key:
                    videos_available.pop(key)
        videos_available = deque(videos_available.keys())
    else:
        videos_available = deque(tree.videos.paths(root + '/videos'))
    if verbose:
        print('Available videos:')
        for v in videos_available:
            print(v)
    # threads
    threads = {}
    N = len(videos_available)
    t = tqdm(total=N)
    while videos_available:
        if gpus_available:

            gpu_id = gpus_available.pop()

            video_path = videos_available.pop()
            if verbose:
                print('Video --> %s' % video_path)
                print('Still available:')
                print('%r' % videos_available)
            frame_path = video_path.split('.')[0].replace('videos', 'frames')
            sk_path = frame_path.replace('frames', 'skeleton')
            audio_path = frame_path.replace('frames', 'audio')
            info_path = frame_path.replace('frames', 'info')
            t.update()
            t.set_postfix(remaining_time=len(videos_available) * 1.2 / 5)
            if use_threading:

                print('Threading with GPU %d' % gpu_id)
                x = threading.Thread(target=process_folder,
                                     args=(video_path, frame_path, sk_path, audio_path, info_path, gpu_id),
                                     daemon=True)
                x.start()
                threads[x.ident] = [gpu_id, x]

            else:
                x = process_folder(video_path, frame_path, sk_path, audio_path, info_path, gpu_id)
                gpus_available.append(gpu_id)
        if use_threading:
            for idx, thread in list(threads.items()):
                if not thread[1].is_alive():
                    gpus_available.append(thread[0])
                    threads.pop(idx)
        time.sleep(0.5)
    t.close()
    while 1:
        m = []
        for idx, thread in threads.items():
            m.append(thread[1].is_alive())
        time.sleep(5)
        if max(m) == 0:
            break


def process_folder(video_path, frames_path, skeleton_path, audio_path, info_path, op, ):
    info = BaseDict()
    audio_path = None
    print('Starting the thread for video %s' % video_path)
    print('Getting frames at  %s' % frames_path)
    audio_opts = []
    video_opts = []
    # Uncomment to deal with audio too
    if audio_path is not None:
        audio_opts += ['-ac', '1', '-ab', '16000', '-ar', '16384', audio_path]
    apply_single(video_path, frames_path + '/%05d.png', ['-y', '-hide_banner'], audio_opts, ext=None)
    # apply_single(video_path, frames_path + '/%05d.png', [], audio_opts)
    print('Getting skeleton at  %s' % skeleton_path)
    info['video_frames'] = len(os.listdir(frames_path))
    if audio_path is not None:
        info['audio_frames'] = read(audio_path)[1].shape[0]

    op = OPose({'num_gpu_start': op, 'num_gpu': 1})
    op.config_essential(number_people_max=1, face=True, hand=True, write_json=skeleton_path)
    imgs = op.process_images(frames_path, display=False, keep_in_ram=False)
    rmtree(frames_path)
    info.write(info_path)
    return imgs


if __name__ == '__main__':
    # fire.Fire(main)
    root = '/media/jfm/Slave/SolosPff'
    ignore=[]
    # path = '/media/jfm/Slave/Solos/redo.json'
    # dic = BaseDict().load(path)
    # ignore = [x.split('/')[1].split('.')[0] for x in dic['not_redo']]
    # do = [x.split('/')[1].split('.')[0] for x in dic['redo']]
    # print(len(do))
    main(root, gpu_ids=[1, 1], use_threading=False, verbose=False,
         ignore=['cf', 'clc', 'clf', 'clt', 'cltu', 'clv', 'ct', 'ec', 'ef', 'tf', 'tf', 'tut', 'tuv', 'vc', 'vf', 'vt',
                 'xf', 'skeleton'] + ignore)
    # main(root, gpu_ids=[0, 0, 0, 1, 1], use_threading=False, verbose=True,
    #      ignore=['cf', 'clc', 'clf', 'clt', 'cltu', 'clv', 'ct', 'ec', 'ef', 'tf', 'tf', 'tut', 'tuv', 'vc', 'vf', 'vt',
    #              'xf'])
