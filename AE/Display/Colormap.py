from matplotlib import cm
import matplotlib.pyplot as plt
from PyQt5.QtGui import QColor

class Colormap():
    
  def __init__(self, name='jet'):
    
    self.ncolors = 4

    # Range
    self.norm = None
    self._range = None
    self.range = [0,1]

    # Colormap
    self.cmap = None
    self.set(name)

  def set(self, name):

    self.cmap = cm.get_cmap(name, self.ncolors)

  def qcolor(self, value):

    # Reduced value
    if value<self.range[0]:
      value = self.range[0]
    elif value>self.range[1]:
      value = self.range[1]
    
    c = self.cmap(self.norm(value))

    return QColor(int(c[0]*255), int(c[1]*255), int(c[2]*255))
  
  # --- Range -------------------------------------------------------------

  @property
  def range(self): return self._range

  @range.setter
  def range(self, r):
    self.norm = plt.Normalize(r[0], r[1])
    self._range = r