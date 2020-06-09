import numpy as np
import os

from .utils import BaseDict

__all__ = ['SKReader']


class SKReader(object):
    def __init__(self, download=True, in_ram=False):
        path = __path__[0]
        path = os.path.join(path, 'skeleton_files', 'skeleton.npy')
        self.json = BaseDict().load(path=os.path.join(path, 'skeleton_files', 'skeleton_dict.json'))
        N = self.json['_counter']
        self.npy = np.memmap(path, dtype=np.float32, mode='r', shape=(N, 3, 47))
        if in_ram:
            self.npy = self.npy.copy()

        if download:
            from google_drive_downloader import GoogleDriveDownloader as gdd

            gdd.download_file_from_google_drive(file_id='',
                                                dest_path=path,
                                                unzip=False)

    def __call__(self, path, offset, length):
        return self.npy[offset:offset + length]

    def __getitem__(self, item):
        if isinstance(item, str):
            start, stop = self.json[item]
            return self.npy[start:stop]
        else:
            return self.npy[item]

    def __len__(self):
        return len(self.json)
