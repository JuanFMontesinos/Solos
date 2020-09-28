import Solos
from torchtree import Directory_Tree

PATH = '/media/jfm/Slave/Solos/videos'

tree = Directory_Tree(path=PATH)

dic = Solos.get_solos_ids()

dic_real = {}

for path in tree.paths(root=PATH):
    feats = path.split('/')
    cat = feats[-2]

    key = feats[-1].split('.')[0]
    if cat not in dic_real:
        dic_real[cat] = []

    dic_real[cat].append(key)

for cat in dic:
    for key in dic[cat]:
        if key not in dic_real[cat]:
            print(cat,key)
