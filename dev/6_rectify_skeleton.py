from torchtree import Tree
import torch
from flerken.utils import BaseDict
import numpy as np
from torchtree import Tree
import torch
import numpy as np
from flerken.utils import BaseDict
import sys

sys.path.append('/home/jfm/GitHub/OpenposeWrapper/openpose_wrapper')
from skeleton import Skeleton


def get_disordered_graph():
    num_node = 7 + 20 * 2
    self_link = [(i, i) for i in range(num_node)]
    neighbor_link_body = [(3, 2), (2, 1), (1, 0),
                          (6, 5), (5, 4), (4, 0)]
    neighbor_link_hand1 = [(4, 3), (3, 2), (2, 1), (1, -3),
                           (8, 7), (7, 6), (6, 5), (5, -3),
                           (12, 11), (11, 10), (10, 9), (9, -3),
                           (16, 15), (15, 14), (14, 13), (13, -3),
                           (20, 19), (19, 18), (18, 17), (17, -3)]
    neighbor_link_hand1 = [(x[0] + 6, x[1] + 6) for x in neighbor_link_hand1]
    neighbor_link_hand2 = [(4, 3), (3, 2), (2, 1), (1, -20),
                           (8, 7), (7, 6), (6, 5), (5, -20),
                           (12, 11), (11, 10), (10, 9), (9, -20),
                           (16, 15), (15, 14), (14, 13), (13, -20),
                           (20, 19), (19, 18), (18, 17), (17, -20)]
    neighbor_link_hand2 = [(x[0] + 6 + 20, x[1] + 6 + 20) for x in neighbor_link_hand2]
    edge = self_link + neighbor_link_body + neighbor_link_hand1 + neighbor_link_hand2
    return edge


def skeleton_mean(data_numpy: np.ndarray):
    coords = data_numpy[:, :2, :]
    #
    mask = data_numpy[:, 2, :][:, None, :].repeat(2, axis=1) == 0  # Shape T,2,J
    mean = np.zeros(coords.shape[1:])
    # mean = coords.new_zeros(2, data_numpy.shape[-1])
    for c in range(2):
        for j in range(data_numpy.shape[-1]):
            mean[c, j] = data_numpy[:, c, j][~mask[:, c, j]].mean()
    mean[np.isnan(mean)] = 0

    return mean


class Graph(object):
    def __init__(self, graph):
        self.graph = sorted([sorted(x) for x in graph])
        self.tree = Tree()
        self.build_tree(self.tree, 0)

    def iter_graph(self, c):
        triggered = False
        for edge in self.graph:
            if edge[0] == c and edge[1] != c:
                triggered = True
                yield edge
        if not triggered:
            yield (c, None)

    def build_tree(self, tree, c):
        for edge in self.iter_graph(c):
            x, y = str(edge[0]), edge[1]
            if y is None:
                tree.add_module(x, Tree())
            else:
                if x not in tree._modules and int(x) != y:

                    new_tree = Tree()
                    tree.add_module(x, new_tree)
                    self.build_tree(new_tree, y)
                else:
                    self.build_tree(new_tree, y)

    def get_ordered_graph(self):
        x = []
        self.iter_ordered_graph(self.tree, -1, x)
        del x[0]
        return tuple(x)

    def iter_ordered_graph(self, tree, prev, lista):
        for el, mod in self.iter_children(tree, prev):
            lista.append(el)
            self.iter_ordered_graph(mod, el[1], lista)

    def iter_children(self, tree, prev):
        for name, mod in tree.named_children():
            yield (prev, int(name)), mod


def lin_interp_mask(skeleton, th=0):
    T = skeleton.shape[0]
    mask = (skeleton[:, 2, :] <= th).astype(np.int8)
    dist_fwd = np.zeros_like(mask).astype(np.int16)
    index_fwd = np.zeros_like(mask).astype(np.int32)
    dist_bwd = np.zeros_like(mask).astype(np.int16)
    index_bwd = np.zeros_like(mask.astype(np.int32))

    dist_fwd[0] = mask[0]
    index_fwd[0] = 0 - dist_fwd[0]
    dist_bwd[T - 1] = mask[T - 1]
    index_bwd[T - 1] = T - 1 + dist_bwd[T - 1]

    for t in range(T - 2, -1, -1):
        dist_bwd[t] = (dist_bwd[t + 1] + mask[t]) * mask[t]
        index_bwd[t] = t + dist_bwd[t]
    for t in range(1, T):
        dist_fwd[t] = (dist_fwd[t - 1] + mask[t]) * mask[t]
        index_fwd[t] = t - dist_fwd[t]

    return index_fwd, index_bwd, dist_fwd, dist_bwd


def lin_interp(skeleton: np.ndarray, graph, th):
    skeleton_rel = skeleton.copy()
    T = skeleton.shape[0]
    # Obtain relative coords
    for prev, pos in graph:
        skeleton_rel[:, :2, pos] = skeleton[:, :2, pos] - skeleton[:, :2, prev]
    sk_avg = skeleton_mean(skeleton_rel)  # shape 2,J
    sk_avg = np.concatenate([sk_avg, np.zeros((1, sk_avg.shape[-1]))], axis=0)[
        None, ...]  # Expanding sk_avg to fit (1,3,J)
    index_fwd, index_bwd, dist_fwd, dist_bwd = lin_interp_mask(skeleton_rel, th)
    skeleton_rel = np.concatenate([skeleton_rel, sk_avg], axis=0)  # Padding skeleton_rel
    elements = []
    for i in range(T):
        indices_fwd = skeleton_rel[index_fwd[i], :2, range(47)]
        indices_bwd = skeleton_rel[index_bwd[i], :2, range(47)]
        element = (indices_fwd * dist_bwd[i][:, None] + indices_bwd * dist_fwd[i][:, None]) / (
                dist_fwd[i][:, None] + dist_bwd[i][:, None])
        element[np.isnan(element)] = indices_fwd[np.isnan(element)]
        elements.append(element.transpose())
    skeleton[:, :2, :] = np.stack(elements)
    # Moving back to absolute coords
    skeleton_out = skeleton.copy()
    for prev, pos in graph:
        skeleton_out[:, :2, pos] = skeleton[:, :2, pos] + skeleton_out[:, :2, prev]
    return skeleton_out


# def test():
#     json = BaseDict().load('/media/jfm/Slave/SkDataset/skeleton_npy/skeleton_dict.json')
#     N = json['_counter']
#     numpy_mmap = np.memmap('/media/jfm/Slave/SkDataset/skeleton_npy/skeleton_nonpadded.npy', dtype=np.float32,
#                            mode='r',
#                            shape=(N, 3, 47))
#
#     edge = get_disordered_graph()
#     elements = json['TiqUpTAwWgY']
#     elements = json['XAQBStul-PU']
#     # elements = json['uj9q1jBICTQ']
#     path = '/media/jfm/SlaveSSD/test_video_folder'
#     tensor = numpy_mmap[elements[0]:elements[1]]
#
#     from overlay_sk import Skeleton_Plotter
#
#     graph = Graph(edge).get_ordered_graph()
#     skeleton = lin_interp(tensor.copy(), graph, 0.2)
#     sk = Skeleton_Plotter(graph=Graph(edge).get_ordered_graph(), th=0)
#     w = sk(torch.from_numpy(skeleton))


def run():
    json_path = '/media/jfm/Slave/Solos/skeleton_npy/skeleton_dict.json'
    mmap_path = '/media/jfm/Slave/Solos/skeleton_npy/skeleton_npy.npy'
    dst_path = '/media/jfm/Slave/Solos/skeleton_npy/skeleton_npy_padded.npy'

    json = BaseDict().load(json_path)
    N = json['_counter']
    numpy_mmap = np.memmap(mmap_path, dtype=np.float32, mode='r',
                           shape=(N, 3, 47))
    dst_mmap = np.memmap(dst_path, dtype=np.float32, mode='w+',
                         shape=(N, 3, 47))
    N = json['_counter']
    edge = get_disordered_graph()
    for key in json:
        elements = json[key]
        tensor = numpy_mmap[elements[0]:elements[1]]
        dst_mmap[elements[0]:elements[1]] = lin_interp(tensor.copy(), Graph(edge).get_ordered_graph(), 0.2)


if __name__ == '__main__':
    run()
