"""
Colormaps tools
"""

from matplotlib import cm
from PyQt5.QtGui import QColor

class Colormap():
  """
  A class to manage colormaps
  It is mainly used to convert scaler values to colors.
  """
  
  def __init__(self, name='turbo', range=[0,1], ncolors=64):
    """
    `Colormap` constructor

    Defines the basic attributes of a colormap, namely the number of colors 
    `ncolors` and value range `range`.
    
    The name of the colormap is either provided to the constructor or set 
    later on with the `set` method.

    Args:
      name (string): The name of the colormap. All the names from Matplotlib 
        are accepted. Default: 'turbo'
      range (list): The range of the colormap. Default: [0,1]
      ncolors (int): The number of colors in the colormap. Default: 64
    """

    self.ncolors = ncolors

    # Range
    self.norm = None
    self.range = range

    # Colormap
    self.cmap = None
    self.set(name)

  def set(self, name):
    """
    Set colormap's name.

    Args:
      name (string): The name of the colormap, to be chosen among all valid 
        colormap names in Matplotlib. The default colormap is 'turbo'.
    """

    self.cmap = cm.get_cmap(name, self.ncolors)

  def qcolor(self, value, scaled=False):
    """
    Convert a scalar value in a Qt color (QColor).

    Args:
      value (float): A value in `range` that determines the desired color.
        If `value` is not `range`, the closest value in the range is used.

    Returns:
      Color (QColor): The QColor object corresponding to `value`in the colormap. 
    """
    if not scaled:

      # Scale value in range
      if value<self.range[0]:
        value = 0.0
      elif value>self.range[1]:
        value = 1.0
      else:
        value = (value - self.range[0])/(self.range[1] - self.range[0])

    c = self.cmap(value)

    return QColor(int(c[0]*255), int(c[1]*255), int(c[2]*255))

  def htmlcolor(self, value, scaled=False):
    """
    Convert a scalar value in an html color (string).

    Args:
      value (float): A value in `range` that determines the desired color.
        If `value` is not `range`, the closest value in the range is used.

    Returns:
      Color (string): A html string corresponding to `value`in the colormap.
        The output string is formated as 'rgb(x,y,z)'. 
    """

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
