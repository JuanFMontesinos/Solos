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
git clone https://github.com/JuanFMontesinos/Solos
```
Install the requirements:
```
pip install -r requirements.txt
```
Call the downloader:
```
python youtubesaver.py from_json /path_to_your_dst
```
If some video fails to be downloaded, a backup copy with the remaining videos is created at:
```
/path_to_your_dst/backup.json
```
So that you can resume from:
```
python youtubesaver.py from_json /path_to_your_dst /path_to_your_dst/backup.json
```   
You can directly import Solos from appending that folder to pythonpaths or installing via pip
# PIP
For simplicity solos can be installed via pip. (Realize youtube script to download videos is not part of the package)  
**Until the release of version 0.4 we encourage you to use the version 0.3 which can be found in GitHub** 
```
pip install solos
```

# Skeletons and Numpy  
Skeletons are provided as a numpy memory map file in order to have a versatile scalable way of reading them.  
The class `Solos.SkReader` automatically downloads the refined skeletons and exposes a `np.mmap` instance. You can query `SkReader` with 
video keys to obtain a `np.mmap` array with the skeletons of the chosen video. Besides you can slice the original array which cointains all the skeletons.  

```
import solos
sk_npy = solos.SkReader(download=True,in_ram=False)
sk = sk_npy[youtube_id] # This is a np.mmap if in_ram = False or np.ndarray if in_ram=True
#sk shape is Nx3x47 --> N,[x,y,c],47  where N is the total amount of frames
```
# YouTube IDs  
YouTube IDs are exposed by calling `Solos.get_solos_ids()` as a dictionary whose keys are the categories (instruments) present in the dataset and its values are lists of YouTube IDs (corresponding to the key category).  
Dataset timestamps are exposed by calling `Solos.get_solos_timestamps()`.  
Corresponding paths to the files can be found at `Solos.SOLOS_IDS_PATH` and `Solos.SOLOS_TIMESTAMPS_PATH`.  
# Downloading the data (Optional)  
The numpy array should be automatically downloaded. In case anything fails the `.npy` file can be downloaded from [GDrive 3Gb](https://drive.google.com/file/d/1QRn7KMoJVD342VjpxsQh_uyQPhH2859B/view?usp=sharing) and the index mapping [here](https://drive.google.com/file/d/1vkVDWDcChYaiVjp0PmOgQgZdLIYbWeaV/view?usp=sharing). Index json file is already included in the python package. 
To open it in reading mode:  
`npy = np.memmap(path, dtype=np.float32, mode='r', shape=(N, 3, 47))`  
For extra info check `np.mmap` [docs](https://het.as.utexas.edu/HET/Software/Numpy/reference/generated/numpy.memmap.html)
