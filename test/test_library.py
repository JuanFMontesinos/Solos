import unittest
import os


import numpy as np
from flerken.utils import BaseDict
from flerken.video.utils import get_duration_fps
from torchtree import Directory_Tree

import Solos

from . import TEST_PATH

_VIDEOS_PATH = '/media/jfm/Slave/Solos/videos'

class TestSolos(unittest.TestCase):
    def test_skreader(self):
        reader = Solos.skeleton.SKReader(download=True,in_ram=False)
        sk = reader['OqH9szlahwU']
        gt = np.load(os.path.join(TEST_PATH,'data/skeleton_npy_test.npy'))
        self.assertTrue((gt==sk).all())
        reader = Solos.skeleton.SKReader(download=True, in_ram=True)
    def test_import_json_files(self):
        Solos.get_solos_ids()
        Solos.get_solos_timestamps()

    @unittest.skipIf(not os.path.exists(_VIDEOS_PATH), 'Path to dataset not found')
    def test_solos_timestamps(self):
        sk_dict = BaseDict().load(path=os.path.join(Solos.PATH, 'skeleton_files', 'skeleton_dict.json'))
        tree = Directory_Tree(_VIDEOS_PATH)
        for path in list(tree.paths(_VIDEOS_PATH)):
            key = path.split('/')[-1].split('.')[0]
            duration, fps = get_duration_fps(path, display=False)
            vdur = int((duration[1] * 60 + duration[2] + duration[3] / 1000) * 25)
            if abs(vdur - sk_dict[key][1] + sk_dict[key][0]) > 50 or fps != 25:
                raise Exception(f'sk_dict.json for file {path} is wrong')