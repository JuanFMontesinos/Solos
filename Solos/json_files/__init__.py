import os

from ..utils import BaseDict

__all__ = ['SOLOS_IDS_PATH', 'get_solos_ids']


SOLOS_IDS_PATH = os.path.join(__path__[0], 'solos_ids.json')


def get_solos_ids():
    return BaseDict().load(SOLOS_IDS_PATH)
