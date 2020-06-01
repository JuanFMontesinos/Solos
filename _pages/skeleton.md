---
permalink: /data/
title: "Examples"
author_profile: true
redirect_from: 
  - /data-format/
  - /data.html
---
# Video Format
Using in-the-wild videos implies non-uniform video formats.  
Recordings are resampled to 25.0 FPS via ffmpeg in order to ensure homogeneus frame rate (desiderable for ML models).
Skeletons are computed for those resampled recordings.  

# Skeleton postprocessing  
Openpose provides independent skeleton predictions for each frame.  As there is no temporal coherence you may find flickering, misspredictions or other artifacts.  

We found empirically that this produces unstability in training pipes. That is why we apply the following postprocessing to OpenPose results:
* **Linear interpolation in missing frames**: Misspredicted joints are interpolated linearlly taking into account the distance to the previous and post detected frames. This prediction is based on the relative position of the joints wrt the precedent joint. This ensures estability in the absolute position. For example, if a finger is missing for lot of frames, an absolute interpolation wouldn't consider arm position and would generate bad coarse interpolation. Relative interpolation just takes into acount finger movement.  
* **Savgol filtering** We didn't apply but suggest to use savgol filters to deal with flickering.  

# Skeleton format  
Each video consist of `Nx3x47` joints where N is the number of frames.  
Not all the joints of openpose are provided but the relevants ones for playing an instrument. namely, hands and upperbody.  
Hands distribution are the following:  
<img src="https://raw.githubusercontent.com/CMU-Perceptual-Computing-Lab/openpose/master/doc/media/keypoints_hand.png" alt="Open P ose Hand" width="400" title="Open Pose Hand"/>

