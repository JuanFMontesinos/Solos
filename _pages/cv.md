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
Sourcecode used to produce the csv file can be found   [here](https://github.com/JuanFMontesinos/Solos/blob/master/dev/get_csv.py)  
CSV files in [GDrive](https://drive.google.com/file/d/1QbYX-9souLwVyfhgz371xEQWA9TQuqt-/view?usp=sharing)  
The CSV file is ~6Gb. Float numbers are 4 decimals only. 
