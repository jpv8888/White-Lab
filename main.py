# ------------------------------------------------------
# ---------------------- main.py -----------------------
# ------------------------------------------------------
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

import numpy as np
import xml.etree.ElementTree as ET

path = ("C:/Users/jpv88/OneDrive/Documents/GitHub/White-Lab-Data/" 
        "M184 Imaging and Behavior/Imaging/12-8-21/"
        "M184_Region1_Sample3_x2_Hz1stim/")

file = "C.csv"
C = np.genfromtxt(path + file, delimiter=',')

file = "S.csv"
S = np.genfromtxt(path + file, delimiter=',')

file = "YrA.csv"
YrA = np.genfromtxt(path + file, delimiter=',')

file = "Experiment.xml"
tree = ET.parse(path + file) 
root = tree.getroot() 
expInfo = {}

for child in root.findall('LSM'):
    expInfo['width'] = int(child.attrib['pixelX'])
    expInfo['height'] = int(child.attrib['pixelY'])
    expInfo['pixelSizeUM'] = np.double(child.attrib['pixelSizeUM'])
    expInfo['widthUM'] = np.double(child.attrib['widthUM'])
    expInfo['heightUM'] = np.double(child.attrib['heightUM'])
    if int(child.attrib['averageMode'])==0:
        expInfo['frameRate'] = np.double(child.attrib['frameRate'])
    elif int(child.attrib['averageMode'])==1:
        expInfo['frameRate'] = np.double(child.attrib['frameRate'])/np.double(child.attrib['averageNum'])

f = expInfo['frameRate'] # in Hz
T = 1/f # in seconds

num_ROI = C.shape[0] - 1
trace_len = C.shape[1] - 1

total_time = T*trace_len

t = np.linspace(0, total_time, trace_len)


# %%
     
class MatplotlibWidget(QMainWindow):
    
    def __init__(self):
        
        QMainWindow.__init__(self)

        loadUi("qt_designer.ui",self)

        self.setWindowTitle("CaImAn Spike Remover")

        self.verticalSlider_noise_percentile.setMinimum(1)
        self.verticalSlider_noise_percentile.setMaximum(99)
        self.verticalSlider_spike_percentile.setMinimum(1)
        self.verticalSlider_spike_percentile.setMaximum(99)
        self.horizontalSlider_ROI.setMinimum(1)
        self.horizontalSlider_ROI.setMaximum(num_ROI)
        
        self.label_ROI.setText('ROI: ' + str(self.horizontalSlider_ROI.value()))
        np_label = ('Noise \nPercentile:\n' + 
                    str(self.verticalSlider_noise_percentile.value()))
        self.label_noise_percentile.setText(np_label)
        
        sp_label = ('Spike \nPercentile:\n' + 
                    str(self.verticalSlider_spike_percentile.value()))
        self.label_spike_percentile.setText(sp_label)
            
        
        self.horizontalSlider_ROI.valueChanged.connect(self.update_label_ROI)
        self.horizontalSlider_ROI.valueChanged.connect(self.update_graph)
        
        self.verticalSlider_noise_percentile.valueChanged.connect(self.update_label_noise_percentile)
        self.verticalSlider_noise_percentile.valueChanged.connect(self.update_graph)
        self.verticalSlider_spike_percentile.valueChanged.connect(self.update_label_spike_percentile)
        self.verticalSlider_spike_percentile.valueChanged.connect(self.update_graph)

        self.update_graph()
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))
        

    def update_label_ROI(self):
        self.label_ROI.setText('ROI: ' + str(self.horizontalSlider_ROI.value()))
    
    def update_label_noise_percentile(self):
        np_label = ('Noise \nPercentile:\n' + 
                    str(self.verticalSlider_noise_percentile.value()))
        self.label_noise_percentile.setText(np_label)
    
    def update_label_spike_percentile(self):
        sp_label = ('Spike \nPercentile:\n' + 
                    str(self.verticalSlider_spike_percentile.value()))
        self.label_spike_percentile.setText(sp_label)
    
    # take a percentile of just the nonzero values, used for spike probabilities
    def nonzero_percentile(self, data, percentile):
        for i in reversed(range(len(data))):
            if data[i] == 0:
                data = np.delete(data,i)
        return np.percentile(data, percentile)
        
    def update_graph(self):

        ROI = self.horizontalSlider_ROI.value()
        noise_percentile = self.verticalSlider_noise_percentile.value()
        spike_percentile = self.verticalSlider_spike_percentile.value()
        
        spikes = np.zeros(trace_len, dtype=int)
        
        trace = C[ROI,1:]
        binary_mask = np.zeros(trace_len, dtype=int)
        threshold = np.percentile(np.absolute(YrA[ROI,1:]), noise_percentile)
        for i, val in enumerate(trace):
            if val >= threshold:
                binary_mask[i] = 1
            
        spike_threshold = self.nonzero_percentile(S[ROI,1:], spike_percentile)
        for i, val in enumerate(S[ROI,1:]):
            if val >= spike_threshold and binary_mask[i] == 1:
                spikes[i] = 1
        
        # clear axes
        self.MplWidget.canvas.ax1.clear()
        self.MplWidget.canvas.ax2.clear()
        self.MplWidget.canvas.ax3.clear()
        
        self.MplWidget.canvas.ax1.plot(t, C[ROI,1:], c='r')
        self.MplWidget.canvas.ax1.axhline(threshold, ls='--', c='k')
        self.MplWidget.canvas.ax2.plot(t, S[ROI,1:], c='g')
        self.MplWidget.canvas.ax2.axhline(spike_threshold, ls='--', c='k')
        self.MplWidget.canvas.ax3.plot(t, spikes, c='b')
        
        self.MplWidget.canvas.ax3.set_xlabel('t (s)')
        self.MplWidget.canvas.ax1.set_ylabel('arb. unit')
        self.MplWidget.canvas.ax2.set_ylabel('p')
        self.MplWidget.canvas.ax3.set_title('Filtered Spikes')
        self.MplWidget.canvas.ax2.set_title('Spike Probabilities')
        self.MplWidget.canvas.ax1.set_title('Fitted Trace')
        self.MplWidget.canvas.ax3.set_yticks([])

        self.MplWidget.canvas.draw()
        
        num_spikes = sum(spikes)
        self.label_total_spikes.setText('Total Spikes: ' + str(num_spikes))
        self.label_avg_firing_rate.setText('Average Firing Rate: ' + str(num_spikes/total_time) + ' Hz')
    
app = QApplication([])
window = MatplotlibWidget()
window.show()
app.exec_()
