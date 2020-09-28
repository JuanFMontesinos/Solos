import numpy as np
import torch
from scipy.signal import resample
from scipy.io.wavfile import read as read_audio, write
from tqdm import tqdm

from torchtree import Directory_Tree
from flerken.utils import BaseDict
import os
import sys
import fire

sys.path.append('/home/jfm/GitHub/OpenposeWrapper/openpose_wrapper')
from skeleton import Skeleton
from Solos import get_solos_ids, PATH

OR_PATH = '/media/jfm/Slave/Solos'


# OR_PATH = '/media/jfm/SlaveSSD/test_dataset'


def openpose25toupperbody(data_numpy):
    if torch.is_tensor(data_numpy):
        new_data = torch.zeros(data_numpy.shape[0], 3, 7)
    else:
        new_data = np.zeros((data_numpy.shape[0], 3, 7))
    new_data[..., 0] = data_numpy[..., 1]
    new_data[..., 1:] = data_numpy[..., 2:8]
    return new_data


def uperbodyhands(skeleton, hands):
    if torch.is_tensor(skeleton):
        data_numpy = torch.zeros(skeleton.shape[0], 3, 7 + 20 * 2)
    else:
        data_numpy = np.zeros((skeleton.shape[0], 3, 7 + 20 * 2))
    data_numpy[..., :7] = openpose25toupperbody(skeleton)
    data_numpy[..., 7:7 + 20] = hands[:, 0, :, 1:21]
    data_numpy[..., 7 + 20:7 + 20 * 2] = hands[:, 1, :, 1:21]
    return data_numpy


def skeleton2stamps(skeleton, min_frames, max_error):
    def prune_idx(idx_list, min_frames, max_error):
        mod = True
        i = 0
        while mod:
            result = []
            mod = False

            for i in range(i, len(idx_list) - 1):
                # fake_idx = i if i > 0 else 0
                result = idx_list[:i]
                stamp_t = idx_list[i]
                stamp_t1 = idx_list[i + 1]
                error = stamp_t1[0] - stamp_t[1]
                if error < max_error:
                    result.append([stamp_t[0], stamp_t1[1]])
                    result.extend(idx_list[i + 2:])
                    idx_list = result
                    mod = True

                    break

        return [x for x in idx_list if x[1] - x[0] > min_frames]

    ids = []
    idx = []
    for i, tensor in enumerate(skeleton):
        if tensor[2, 4] != 0 or tensor[2, 7] != 0:
            idx.append(i)
        else:
            # if len(idx) > min_frames: Replaced at prune_idx
            if len(idx) > 1:
                ids.append([min(idx), max(idx)])
            idx = []
    if idx:
        ids.append([min(idx), max(idx)])

    return prune_idx(ids, min_frames, max_error)


def yield_modules(tree, solos_ids, prefix):
    for n, m in tree.skeleton.named_modules(prefix=os.path.join(prefix, 'skeleton')):
        if m.level() == 3:
            ID = n.split('/')[-1]
            assert ID in solos_ids
            yield n, ID, m


SSK = ['VdFnyZWJAgo',
       '1u3yHICR_BU',
       'I0LedcEaPL0',
       '1X2l_1za1g0',
       'PCicM6i59_I',
       'VlIcqDWmPkw',
       'XlPvAkLT3Yw',
       'tar_TGXQ59g',
       'QAiwlq3aP2U',
       'aGXm9SGCVT8',
       'FBbaE4ytj8E',
       'tfcNUo8qjrA',
       'X0T6KysSejQ',
       'cZoWhKTZTYY',
       'eHbxLcoLWYY',
       'eCQO6k5Qrmg',
       'lR8RrUBhCQg',
       'STKXyBGSGyE',
       'YcXK-dWMxC0',
       '3bpD1lZsTsM',
       'ufsSRKgUb6g',
       'aGk1zIDQQjQ',
       'nZ4HNz9xvSw',
       'HQveyGmUBSs',
       'P_lSgczU2Sk',
       'u6Mr13lHQVs',
       'JRPtROMynA8',
       '4-hZDt0Vr5I',
       'C952gmBlkIU',
       'sgyhfvTIMmw',
       '-kUCgRjtwPY',
       'fC6p0MRp-s4',
       'dTApdk9eCVU']
SSKD = {}
for key in SSK:
    for cat in get_solos_ids():
        if key in get_solos_ids()[cat]:
            SSKD[key] = cat
            break

print(SSKD)

def main(OR_PATH, ignore=['videos', 'info_backup', 'spectrograms_npy', 'sax', 'xylophone'], minumum_frames=150,
         max_error=5):
    solos_ids = get_solos_ids()
    hands_on_json = BaseDict().load(path=os.path.join(PATH, 'skeleton_files', 'skeleton_dict.json'))
    solos_ids = []
    for values in get_solos_ids().values():
        solos_ids.extend(values)

    for key in hands_on_json:
        if key not in solos_ids:
            ignore.append(key)
    print('Creating directory tree... (it may take a long time)')
    tree = Directory_Tree(OR_PATH, ignore=ignore)
    if not os.path.exists(os.path.join(OR_PATH, 'skeleton_npy')):
        os.mkdir(os.path.join(OR_PATH, 'skeleton_npy'))
    tree.skeleton.clone_tree(os.path.join(OR_PATH, 'skeleton_npy'))
    print('Done!')
    c = 0
    npy_dict = BaseDict()
    # for path in tree.info.paths(OR_PATH + '/info'):
    for name, key, m in yield_modules(tree, solos_ids, OR_PATH):
        n_sk = len(os.listdir(name))
        npy_dict[key] = [c, c + n_sk]
        c += n_sk
    # THIS PART IS APPENDED TO FIX THE PROBLEM
    ########
    fixd = BaseDict().load(path=os.path.join('/media/jfm/Slave/SkDataset/skeleton_npy', 'skeleton_dict.json'))
    for key in SSK:
        idx0, idx1 = fixd[key]
        n_sk = idx1 - idx0
        npy_dict[key] = [c, c + n_sk]
        c += n_sk
    ########
    npy_big = np.memmap(os.path.join(OR_PATH, 'skeleton_npy', 'skeleton_npy.npy'), dtype=np.float32, mode='w+',
                        shape=(c, 3, 47))
    npy_dict['_counter'] = c
    t = tqdm(total=len(SSK)+len(list(yield_modules(tree, solos_ids, OR_PATH))))
    # for name, module in tree.skeleton.named_modules(prefix=os.path.join(OR_PATH, 'skeleton')):
    solos_stamps = BaseDict()

    for name, key, module in yield_modules(tree, solos_ids, OR_PATH):
        # if module.level() == 3:
        cat = name.split('/')[-2]
        if cat not in solos_stamps:
            solos_stamps[cat] = {}
        sk = Skeleton(1, path=name)
        npy = uperbodyhands(sk.skeleton[:, 0, ...], sk.hands[:, 0, ...])
        stamps = skeleton2stamps(npy, minumum_frames, max_error)
        solos_stamps[cat][key]=stamps
        idx0, idx1 = npy_dict[key]
        npy_big[idx0:idx1] = npy
        t.update()
    # THIS PART IS APPENDED TO FIX THE PROBLEM
    ########
    fixd = BaseDict().load(path=os.path.join('/media/jfm/Slave/SkDataset/skeleton_npy', 'skeleton_dict.json'))
    npy_sk = np.memmap(os.path.join('/media/jfm/Slave/SkDataset/skeleton_npy', 'skeleton_npy.npy'),
                       dtype=np.float32,
                       mode='r',
                       shape=(fixd['_counter'], 3, 47))
    for key in SSK:
        json = BaseDict().load(os.path.join('/media/jfm/Slave/SkDataset/info',SSKD[key].lower(),key+'.json'))
        solos_stamps[SSKD[key]][key] = json['stamps']
        idx0, idx1 = npy_dict[key]
        idx0_sk, idx1_sk = fixd[key]
        npy_big[idx0:idx1] = npy_sk[idx0_sk:idx1_sk]
        t.update()
    ########
    npy_dict.write(os.path.join(OR_PATH, 'skeleton_npy', 'skeleton_dict'))
    solos_stamps.write(os.path.join(OR_PATH, 'skeleton_npy', 'solos_ids_new'))


if __name__ == '__main__':
    # fire.Fire(main)
    rep = main(OR_PATH, ignore=[])
