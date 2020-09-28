from ffprobe import FFProbe
import imageio

path = '/media/jfm/Slave/Solos/videos/Trombone/gv5kQw-jlMs.mkv'


def get_size(path):
    reader = imageio.get_reader(path)
    metadata: dict = reader.get_meta_data()
    size = metadata.get('size')
    if size is None:
        size = metadata.get('source_size')
    if size is None:
        raise AttributeError(f'Imageio cannot retrieve size from:'
                             f' {path}')
    return size


size = get_size(path)
metadata = FFProbe(path)
