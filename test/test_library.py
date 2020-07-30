import unittest

import Solos
import numpy as np
import os

from . import TEST_PATH

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