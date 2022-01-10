# -*- coding: utf-8 -*-
"""
Created on Mon Jan  3 12:40:50 2022

@author: jpv88
"""

import matplotlib.pyplot as plt
import numpy as np

path = ("C:/Users/jpv88/OneDrive/Documents/GitHub/White-Lab-Data/" 
        "M184 Imaging and Behavior/Imaging/12-8-21/"
        "M184_Region1_Sample3_x2_Hz1stim/")

file = "C.csv"
C = np.genfromtxt(path + file, delimiter=',')

file = "S.csv"
S = np.genfromtxt(path + file, delimiter=',')

file = "YrA.csv"
YrA = np.genfromtxt(path + file, delimiter=',')


# %%

# takes same percentile in both directions and averages them, used for 
# residuals, which we assume to be zero centered
def zero_percentile(data, percentile):
    top = np.percentile(data, percentile)
    bottom = np.percentile(data, 100-percentile)
    avg = (abs(top) + abs(bottom))/2
    return avg

# take a percentile of just the nonzero values, used for spike probabilities
def nonzero_percentile(data, percentile):
    for i in reversed(range(len(data))):
        if data[i] == 0:
            data = np.delete(data,i)
    return np.percentile(data, percentile)


# %%

num_ROI = C.shape[0] - 1
trace_len = C.shape[1] - 1

# smooth_probabilities = False
# N = 3

# if smooth_probabilities == True:
#     for ROI_idx in range(num_ROI):
#         S[ROI_idx+1,1:] = uniform_filter1d(S[ROI_idx+1,1:], size=N)
        
noise_percentile = 90
spike_percentile = 90

spikes = np.zeros((num_ROI, trace_len), dtype=int)

for ROI_idx in range(num_ROI):

    trace = C[ROI_idx+1,1:]
    binary_mask = np.zeros(trace_len, dtype=int)
    threshold = zero_percentile(YrA[ROI_idx+1,1:], noise_percentile)
    for i, val in enumerate(trace):
        if val >= threshold:
            binary_mask[i] = 1
            
    spike_threshold = nonzero_percentile(S[ROI_idx+1,1:], spike_percentile)
    for i, val in enumerate(S[ROI_idx+1,1:]):
        if val >= spike_threshold and binary_mask[i] == 1:
            spikes[ROI_idx, i] = 1
        
# %%

ROI = 110
f, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
ax1.plot(C[ROI,1:], c='r')
ax2.plot(S[ROI,1:], c='g')
ax3.plot(spikes[ROI-1,1:], c='b')
ax1.set_title('Fitted Trace')
ax2.set_title('Spike Probabilities')
ax3.set_title('Filtered Spikes')

# %%

