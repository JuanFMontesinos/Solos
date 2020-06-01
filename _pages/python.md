---
permalink: /python/
title: "Solos Python library"
excerpt: "Python library to easily work with Solos."
author_profile: true
redirect_from: 
  - "/python.html"
---

# Quickstart  
Clone the repository in your local: 
```
git clone https://github.com/JuanFMontesinos/Solos-dataset
```
Install the requirements:
```
pip install -r requirements.txt
```
Call the downloader:
```
python youtubesaver.py from_csv_per_instrument /path_to_your_dst
```
If some video fails to be downloaded, a backup copy with the remaining videos is created at:
```
/path_to_your_dst/backup.json
```
So that you can resume from:
```
python youtubesaver.py from_csv_per_instrument /path_to_your_dst /path_to_your_dst/backup.json
```
# Skeletons and Numpy  
Skeletons are provided as a numpy memory map file in order to have a versatile scalable way of reading them.  
The class `solos.SkReader` automatically downloads the refined skeletons and exposes a `np.mmap` instance. You can query `SkReader` with 
video keys to obtain a `np.mmap` array with the skeletons of the chosen video. Besides you can slice the original array which cointains all the skeletons.  

```
import solos
sk_npy = solos.SkReader(download=True,in_ram=False)
sk = sk_npy[youtube_id] # This is a np.mmap if in_ram = False or np.ndarray if in_ram=True
#sk shape is Nx3x47 --> N,[x,y,c],47  where N is the total amount of frames
```

# Downloading the data  
The numpy array should be automatically downloaded. In case anything fails the `.npy` file can be downloaded here. 
To open it in reading mode:  
`npy = np.memmap(path, dtype=np.float32, mode='r', shape=(N, 3, 47))`  
For extra info check `np.mmap` [docs](https://het.as.utexas.edu/HET/Software/Numpy/reference/generated/numpy.memmap.html)
