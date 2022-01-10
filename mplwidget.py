# ------------------------------------------------------
# -------------------- mplwidget.py --------------------
# ------------------------------------------------------
from PyQt5.QtWidgets import*

from matplotlib.backends.backend_qt5agg import FigureCanvas

from matplotlib.figure import Figure

    
class MplWidget(QWidget):
    
    def __init__(self, parent = None):

        QWidget.__init__(self, parent)
        
        self.canvas = FigureCanvas(Figure())
        
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        
        self.canvas.ax1 = self.canvas.figure.add_subplot(311)
        self.canvas.ax2 = self.canvas.figure.add_subplot(312)
        self.canvas.ax3 = self.canvas.figure.add_subplot(313)
        
        
        
        
        self.canvas.ax1.get_xaxis().set_visible(False)
        self.canvas.ax2.get_xaxis().set_visible(False)
        
        
        self.setLayout(vertical_layout)