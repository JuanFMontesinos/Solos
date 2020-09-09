PATH = __path__[0]
MEAN = [0.42814959, 0.36149122, 0.32985465]
STD = [0.24243268, 0.23360587, 0.22158483]

from .json_files import *

from .skeleton import SKReader


def dataset_statistics(dataset_path):
    from imageio import get_reader
    from random import choice, randint, seed
    import os
    import numpy as np
    from tqdm import tqdm

    seed(666)
    json = get_solos_timestamps()
    mean = []
    std = []
    c = 0
    progress_bar = tqdm(total=754)
    for cat in json:
        for key in json[cat]:
            if not json[cat][key]:
                continue
            stamps = choice(json[cat][key])
            frame_indices = [randint(*stamps) for _ in range(10)]
            path = os.path.join(dataset_path, cat, key + '.mp4')
            assert os.path.exists(path)
            try:
                reader = get_reader(path)
            except OSError:
                print(f'OSError in {cat}-->{key}')
                continue
            frames = [reader.get_data(x) / 255. for x in frame_indices]
            m = [x.reshape(-1, 3).mean(axis=0) for x in frames]
            s = [x.reshape(-1, 3).var(axis=0) for x in frames]
            mean.extend(m)
            std.extend(s)
            progress_bar.set_postfix_str(s=f'{cat}-->{key}')
            progress_bar.update()
    mean = np.stack(mean).mean(axis=0)
    std = np.stack(std).mean(axis=0) ** 0.5
    print(f'Mean: {mean}, std:{std}')
    return mean, std
