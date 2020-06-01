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
