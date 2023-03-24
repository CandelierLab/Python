"""
Simple tools for displaying 2D animations

Animation2d
-----------

The :class:`Animation2d` wraps a  ``QGraphicsView`` and ``QGraphicsScene``
as well as all necessary tools for display (scene limits, antialiasing, etc.)
Groups of elements can be formed for easier manipulation, and user interaction 
is possible (drag, click, etc.). It contains a timer triggering the 
:py:meth:`Animation2d.update` method at a regular pace. In subclasses, this 
allows to change elements' positions or features (color, size, etc.) to create
animations.

Items
--------

The items are the elements displayed in the scene (*e.g.* circles, lines, ...).
They derive both from the generic class :class:`item` and from their corresponding 
``QGraphicsItem``. They are incorporaeted in the animation *via* 
:py:meth:`Animation2d.add`.

Simple animation window
-----------------------

The :class:`Window` class creates a simple window containing the 
:py:meth:`Animation2d.Qview` widget. It manages the ``QApplication``, size 
on screen, shortcuts and timer trig. If an :class:`Animation2d` object is
created without parent (``QWidget`` or :class:`Window`), the default 
:class:`Window` is automatically created.

"""

from matplotlib import cm
from matplotlib.colors import Normalize
from PyQt5.QtGui import QColor

class Colormap():
  
  

  def __init__(self, name='jet'):
    """
    Colormap constructor

    Defines the basic attributes of a colormap, namely the number of colors 
    (:py:attr:`ncolors`, default 64) and value range (:py:attr:`range`, 
    default = [0,1]). 
    
    The name of the colormap is either provided to the constructor or set 
    later on with the :py:meth:`set` method.

    Args:

      name (string): The name of the colormap. Default: 'jet'
    """

    self.ncolors = 64

    # Range
    self.norm = None
    self.range = [0,1]

    # Colormap
    self.cmap = None
    self.set(name)

  def set(self, name):
    """
    Set colormap name

    Args:

      name (string): The name of the colormap, to be chosen among all valid 
        colormap names in matplotlib. The default colormap is 'jet'.
    """

    self.cmap = cm.get_cmap(name, self.ncolors)

  def qcolor(self, value, scaled=False):
    """
    Get Qt color (QColor)

    Args:

      name (string): The name of the colormap, to be chosen among all valid 
        colormap names in matplotlib. The default colormap is 'jet'.

    Re
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
