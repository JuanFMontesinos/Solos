---
title: "CSV"
permalink: /csv/
author_profile: false
redirect_from:
  - /csv.html
---
Apart from `.json` files we provide skeleton data in a `.csv` format.  
CSV header:
Each row consist of id,3x47 + 1 numbers which indicate
The frame number, then, for each joint from 0 to 46 the coords X,Y and the confidence C.
```
id, frame_n, j0_x, j0_y, j0_c, ... , j46_x, j46_y, j46_c
```
CSV files in [GDrive](https://drive.google.com/file/d/1eWB6J1T2MKzl-c8-ylik9O2CWLJyUpjx/view?usp=sharing)
