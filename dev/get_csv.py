import csv
import sys

from tqdm import tqdm

import Solos

if __name__ == '__main__':
    # Expected format
    # id, frame_n, j0_x, j0_y, j0_c, ... , j46_x, j46_y, j46_c
    # https://www.juanmontesinos.com/Solos/csv/

    DST = '/home/jfm/solos_csv.csv'

    assert DST.endswith(('.csv'))


    reader = Solos.SKReader(download=True, in_ram=True)
    with open(DST, 'w', newline='') as file:
        writer = csv.writer(file)
        timer = tqdm(total=len(reader.npy))
        for key in reader.keys():
            sk = reader[key]
            for i,sk_i in enumerate(sk):
                coords = sk_i.T.flatten()
                row = [key,str(i),*['%.4f'%x for x in coords]]
                writer.writerow(row)
                timer.update()