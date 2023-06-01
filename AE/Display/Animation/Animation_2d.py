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

import os
import numpy as np
import re
import imageio

from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QPoint, QPointF, QRectF
from PyQt5.QtGui import QPalette, QColor, QPainter, QPen, QBrush, QPolygonF, QFont, QPainterPath, QLinearGradient, QTransform, QImage
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QGraphicsScene, QGraphicsView, QAbstractGraphicsShapeItem, QGraphicsItem, QGraphicsItemGroup, QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsRectItem, QGraphicsPathItem

from AE.Display.Animation.Items_2d import *
from AE.Display.Animation.Composites_2d import *

# ==========================================================================

class view(QGraphicsView):
  
  def __init__(self, scene, *args, **kwargs):

    super().__init__(*args, *kwargs)
    self.setScene(scene)
    self.padding = 0
    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

  def fit(self):
    
    rect = self.scene().itemsBoundingRect()
    rect.setLeft(rect.left() - self.padding)
    rect.setTop(rect.top() - self.padding)
    rect.setBottom(rect.bottom() + self.padding)
    self.fitInView(rect, Qt.KeepAspectRatio)

  def showEvent(self, E):

    self.fit()    
    super().showEvent(E)

  def resizeEvent(self, E):
    
    self.fit()
    super().resizeEvent(E)

# ==========================================================================

class Animation_2d(QObject):
  """
  2D Animation

  Base class for two-dimensional animations.

  The :py:attr:`Animation2d.Qview` attribute is a ``QGraphicsView`` and can thus
  be used directly as a QWidget in any Qt application. For rapid display, the
  companion class :class:`Window` allows to easily create a new window for
  the animation.

  .. note:: Two times are at play in an animation: the *display* time, whose 
    increments are approximately the inverse of the :py:attr:`Animation2d.fps`
    attribute, and the *animation* time, which is a virtual quantity unrelated 
    to the actual time. This way, slow motion or fast-forward animations can
    be displayed. The :py:attr:`Animation2d.dt` attibute controls the increment
    of animation time between two display updates.
  
  Attributes:
    
    item ({:class:`item` *subclass*}): All items in the scene.

    boundaries ({'x', 'y', 'width', 'height'}): Limits of the scene.

    margin (float): Margin around the scene (pix).

    timeHeight (float): Position of the time display relative to the top of the
      scene (pix).

    fps (float): Display framerate (1/s). Default is 25.

    t (float): Current animation time (s).

    dt (float): Animation time increment (s) between two updates.

    disp_time (bool): If true, the animation time is overlaid to the animation.

    disp_boundaries (bool): If true, a thin grey rectanle is overlaid to 
      indicate the boundaries.

    parent (``QWidget`` or :class:`Window`): If not None (default), a simple
      window containing the animation is created.

    Qscene (``QGraphicsScene``): ``QGraphicsScene`` containing the elements.

    Qview (``QGraphicsView``): ``QGraphicsView`` widget representing the scene.

    timer (``QElapsedTimer``): Timer storing the display time since the 
      animation start.

    Qtimer (``QTimer``): Timer managing the display updates.
  """

  # Generic event signal
  event = pyqtSignal(dict)

  def __init__(self, size=None, boundaries=None, disp_boundaries=True, boundaries_color=Qt.lightGray, dt=None):
    """
    Animation constructor

    Defines all the attributes of the animation, especially the ``QGraphicsScene``
    and ``QGraphicsView`` necessary for rendering.

    Args:

      size (float): Height of the ``QGraphicsView``.

      boundaries ([[float,float],[float,float]]): Limits of the scene to display.
        The first element sets the *x*-limits and the second the *y*-limits. 
        Default is [[0,1],[0,1]].

      disp_boundaries (bool): If true, a thin grey rectanle is overlaid to 
        indicate the boundaries.

      disp_time (bool): If true, the animation time is overlaid to the animation.

      dt (float): Animation time increment (s) between two updates. Default: 0.04.
    """

    super().__init__()

    # --- Size settings

    self.size = size if size is not None else QApplication.desktop().screenGeometry().height()*0.6
    
     # --- Scene & view

    # Scene limits
    self.boundaries = {'x':[0,1], 'y':[0,1], 'width':None, 'height':None}
    if boundaries is not None:
      self.boundaries['x'] = list(boundaries[0])
      self.boundaries['y'] = list(boundaries[1])
    self.boundaries['width'] = self.boundaries['x'][1]-self.boundaries['x'][0]
    self.boundaries['height'] = self.boundaries['y'][1]-self.boundaries['y'][0]

    # Scale factor
    self.factor = self.size/self.boundaries['height']

    # Scene
    self.scene = QGraphicsScene()
    self.view = view(self.scene)

    # --- Items and composite elements

    self.item = {}
    self.composite = {}

    # --- Display

    # Dark background
    self.view.setBackgroundBrush(Qt.black)
    pal = self.view.palette()
    pal.setColor(QPalette.Window, Qt.black)
    self.view.setPalette(pal)

    # Antialiasing
    self.view.setRenderHints(QPainter.Antialiasing)

    # Optional display
    self.disp_boundaries = disp_boundaries

    # Stack
    self.stack = {'vpos': self.boundaries['y'][1], 
                  'vmin': self.boundaries['y'][0],
                  'hpadding': self.boundaries['width']/50,
                  'vpadding': 0}
    
    # --- Animation

    # Framerate
    self.fps = 25

    # Time
    self.step = 0
    self.dt = dt if dt is not None else 1/self.fps

    # Timer
    self.timer = QTimer()
    self.timer.timeout.connect(self.set_time)

    # Play
    self.autoplay = True
    self.allow_backward = False
    self.allow_negative_time = False

    self.play_forward = True
    
    # Scene boundaries
    if self.disp_boundaries:
      self.box = QGraphicsRectItem(0,0,
        self.factor*self.boundaries['width'],
        -self.factor*self.boundaries['height'])
      self.box.setPen(QPen(boundaries_color, 2))
      self.scene.addItem((self.box))

    # Output movie
    self.movieFile = None
    self.movieWriter = None
    self.movieWidth = 1600     # Must be a multiple of 16
    self.moviefps = 25
    self.keep_every = 1

  def add(self, type, name, **kwargs):
    """
    Add an item to the scene.

    args:
      item (:class:`item` *subclass*): The item to add.
    """

    # Stack
    if 'stack' in kwargs:
      stack = kwargs['stack']
      del kwargs['stack']
    else:
      stack = False

    height = kwargs['height'] if 'height' in kwargs else None

    if height=='fill':
      height = self.stack['vpos']-self.boundaries['y'][0]
      kwargs['height'] = height
      
    # Add items
    if issubclass(type, composite):

      # Let composite elements create items
      self.composite[name] = type(self, name, **kwargs)

    else:

      # Create item
      self.item[name] = type(self, name, **kwargs)

      # Add item to the scene
      if self.item[name].parent is None:
        self.scene.addItem(self.item[name])
    
    # --- Stack

    if stack:

      x = self.stack['hpadding']
      y = self.stack['vpos']

      if height is None:
        self.stack['vpos'] -= self.item[name].height()
      else:
        self.stack['vpos'] -= height
        y -= height

      # Set position
      self.item[name].position = [x, y]

      # Bottom padding
      self.stack['vpos'] -= self.stack['vpadding']

  def setPadding(self, padding):

    self.view.padding = padding*self.factor

  def show(self):
    """
    Display animation window

    If the animation's parent is a :class:`Window` object, the 
    :py:meth:`Window.show` method is called. Otherwise nothing is done.
    """

    # Timing options
    # self.timer.setInterval(int(1000/self.fps))
    self.timer.setInterval(int(1000*self.dt))
    
    # Movie
    if self.movieFile is not None:

      # Check directory
      dname = os.path.dirname(self.movieFile)
      if not os.path.isdir(dname):
        os.makedirs(dname)

      # Open video file
      self.movieWriter = imageio.get_writer(self.movieFile, fps=self.moviefps)

  def stop(self):
    """
    Stop the animation

    Stops the timer and close the window, if any.
    """

    # Stop the timer
    self.timer.stop()

    # Emit event
    self.event.emit({'type': 'stop'})

    # Movie
    if self.movieWriter is not None:
      self.movieWriter.close()
      
  def set_time(self, step=None):

    if step is None:
      if self.play_forward:
        self.step += 1
      else:
        self.step -= 1
    else:
      self.step = step

    # Check negative times
    if not self.allow_negative_time and self.step<0:
      self.step = 0

    self.update()

  def update(self):
    """
    Update animation state

    Update the animation time :py:attr:`Animation.t`. Subclass this method
    to implement the animation, *e.g.* moving elements or changing color.
    """

    # Emit event
    self.event.emit({'type': 'update', 'step': self.step})

    # Timer display
    if self.disp_time:
      self.item['Time'].string = self.time_str()

    # Repaint
    self.view.viewport().repaint()

    # Movie
    if self.movieWriter is not None and not (self.step % self.keep_every):

      # Get image
      img = self.view.grab().toImage().scaledToWidth(self.movieWidth).convertToFormat(QImage.Format.Format_RGB888)

      # Create numpy array
      ptr = img.constBits()
      ptr.setsize(img.height()*img.width()*3)
      A = np.frombuffer(ptr, np.uint8).reshape((img.height(), img.width(), 3))

      # Add missing rows (to get a height multiple of 16)
      A = np.concatenate((A, np.zeros((16-img.height()%16, img.width(), 3), dtype=np.uint8)), 0)
      
      # Append array to movie
      self.movieWriter.append_data(A)

  

  def change(self, type, item):
    """
    Change notification

    This method is triggered whenever an item is changed.
    It does nothing and has to be reimplemented in subclasses.

    .. Note::
      To catch motion an item has to be declared as ``movable``,
      which is not the default.

    args:
      type (str): Type of change (``move``).
      item (:class:`item` *subclass*): The changed item.
    """

    pass

  def play_pause(self, force=None):

    if self.timer.isActive():

      # Stop qtimer
      self.timer.stop()

      # Emit event
      self.event.emit({'type': 'pause'})

    else:

      # Start timer
      self.timer.start()
    
      # Emit event
      self.event.emit({'type': 'play'})

  def increment(self):

    self.play_forward = True

    if not self.timer.isActive():
      self.set_time()

  def decrement(self):

    if self.allow_backward:

      self.play_forward = False

      if not self.timer.isActive():
        self.set_time()
