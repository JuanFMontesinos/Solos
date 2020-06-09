import os

from ..utils import BaseDict

__all__ = ['SOLOS_IDS_PATH','SOLOS_TIMESTAMPS_PATH', 'get_solos_ids','get_solos_timestamps']

from .. import PATH
SOLOS_IDS_PATH = os.path.join(PATH,'json_files', 'solos_ids.json')
SOLOS_TIMESTAMPS_PATH = os.path.join(PATH,'json_files', 'solos_timestamps.json')


def get_solos_ids():
    return BaseDict().load(SOLOS_IDS_PATH)
def get_solos_timestamps():
    return BaseDict().load(SOLOS_TIMESTAMPS_PATH)