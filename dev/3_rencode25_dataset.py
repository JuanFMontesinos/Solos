from flerken.video.utils import apply_tree, reencode_25_interpolate

from multiprocessing import cpu_count


def main(root, dst):
    apply_tree(root, dst, multiprocessing=cpu_count(), fn=reencode_25_interpolate)


if __name__ == '__main__':
    import sys

    root = sys.argv[1]
    dst = sys.argv[2]
    main(root, dst)
    # Reencode dataset at 25 fps