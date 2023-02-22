from matplotlib import cm
from matplotlib.colors import Normalize
from PyQt5.QtGui import QColor

class Colormap():
    
  def __init__(self, name='jet'):
    
    self.ncolors = 64

    # Range
    self.norm = None
    self.range = [0,1]

    # Colormap
    self.cmap = None
    self.set(name)

  def set(self, name):

    self.cmap = cm.get_cmap(name, self.ncolors)

  def qcolor(self, value, scaled=False):

    if not scaled:

      # Scale value in range
      if value<self.range[0]:
        value = 0
      elif value>self.range[1]:
        value = 1
      else:
        value = (value - self.range[0])/(self.range[1] - self.range[0])
    
    c = self.cmap(value)

    return QColor(int(c[0]*255), int(c[1]*255), int(c[2]*255))

  def htmlcolor(self, value, scaled=False):

    if not scaled:

      # Scale value in range
      if value<self.range[0]:
        value = 0
      elif value>self.range[1]:
        value = 1
      else:
        value = (value - self.range[0])/(self.range[1] - self.range[0])
    
    c = self.cmap(value)

    return 'rgb({:d},{:d},{:d})'.format(int(c[0]*255), int(c[1]*255), int(c[2]*255))
