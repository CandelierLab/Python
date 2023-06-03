import numpy as np

from PyQt5.QtGui import QLinearGradient

from AE.Display.Animation.Items_2d import *
from AE.Display.Colormap import *

# === COMPOSITE ELEMENTS ===================================================

# --- Composite ------------------------------------------------------------

class composite():
  """
  Composite element

  A composite element defines a group item containing other items.
  """

  def __init__(self, animation, name, **kwargs):

    # Definition
    self.animation = animation
    self.name = name

    # Position
    self._position = None
    self.position = kwargs['position'] if 'position' in kwargs else (0,0)

    # Main item
    self.animation.add(group, self.name, **kwargs)

  # --- Points -------------------------------------------------------------

  @property
  def position(self): return self._position

  @position.setter
  def position(self, position):
    self._position = position
    if self.name in self.animation.item:
      self.animation.item[self.name].position = self._position

# --- Arrow ----------------------------------------------------------------

class arrow(composite):
  """
  Arrow composite element
  """

  def __init__(self, animation, name, **kwargs):
    """
    Arrow element constructor
    """ 

    self.fontsize = kwargs['fontsize'] if 'fontsize' in kwargs else 9

    super().__init__(animation, name, **kwargs)

    # Names
    self.line = self.name + '_line'
    self.head = self.name + '_head'
    self.text = self.name + '_text'

    # Items
    self.animation.add(line, self.line,
      parent = self.name, 
      points = [[0,0],[0,0]]
    )

    self.animation.add(text, self.text,
      parent = self.name,
      position = (0,0),
      fontsize = self.fontsize,
      center = (False, False),
      string = ''
    )
    # NB: arrowhead is created later on, when the 'shape' attribute is assigned.

    # Protected attributes

    self._points = None
    self._zvalue = None
    self._size = None
    self._locus = 1
    self._shape = None
    self._color = None
    self._string = None

    # --- Arguments

    self.size = kwargs['size'] if 'size' in kwargs else 0.015
    self.shape = kwargs['shape'] if 'shape' in kwargs else 'dart'

    if 'points' in kwargs:        
      self.points = kwargs['points']
    else:
      raise AttributeError("The 'points' argument is necessary for an arrow element.")

    if 'locus' in kwargs: self.locus = kwargs['locus']
    if 'thickness' in kwargs: self.thickness = kwargs['thickness']
    if 'zvalue' in kwargs: self.zvalue = kwargs['zvalue']
    self.color = kwargs['color'] if 'color' in kwargs else 'white'
    if 'string' in kwargs: self.string = kwargs['string']

  # --- Arrowhead size -----------------------------------------------------

  @property
  def size(self): return self._size

  @size.setter
  def size(self, s):

    self._size = s

    if self.head in self.animation.item:

      match self._shape:

        case 'dart':

          self.animation.item[self.head].points = [[0,0], 
            [-self._size*3/2, self._size/2], [-self._size, 0],
            [-self._size*3/2, -self._size/2], [0,0]]

        case 'disk':

          self.animation.item[self.head].radius = self._size/2

  # --- Shape --------------------------------------------------------------

  @property
  def shape(self): return self._shape

  @shape.setter
  def shape(self, s):

    # Same shape: do nothing
    if self._shape==s: return

    self._shape = s

    if self.head in self.animation.item:

      # Remove previous arrowhead
      self.animation.scene.removeItem(self.animation.item[self.head])

      match self._shape:

        case 'dart':
          
          self.animation.item[self.head] = polygon(self.animation, self.head,
            parent = self.name,
            position = [np.abs(self._z)*self._locus,0],
            points = [[0,0]])

        case 'disk':

          self.animation.item[self.head] = circle(self.animation, self.head,
            parent = self.name,
            position = [np.abs(self._z)*self._locus,0],
            radius = 0)

    else:

      # Initial shape
      match self._shape:

        case 'dart':

          self.animation.item[self.head] = polygon(self.animation, self.head,
            parent = self.name,
            position = [0,0],
            points = [[0,0]])

        case 'disk':

          self.animation.item[self.head] = circle(self.animation, self.head,
            parent = self.name,
            position = [0,0],
            radius = 0)

    # Adjust size
    self.size = self._size
  
  # --- Points -------------------------------------------------------------

  @property
  def points(self): return self._points

  @points.setter
  def points(self, points):

    self._points = points
    self._z = (points[1][0]-points[0][0]) + 1j*(points[1][1]-points[0][1])
    
    # --- Application

    # Group
    self.animation.item[self.name].position = self._points[0]
    self.animation.item[self.name].orientation = np.angle(self._z)

    # Line
    self.animation.item[self.line].points = [[0,0],[np.abs(self._z)-self._size/2,0]]

    # Arrowhead and text positions
    self.pos_ahat()

  # --- Locus --------------------------------------------------------------

  @property
  def locus(self): return self._locus

  @locus.setter
  def locus(self, k):

    self._locus = k

    # Arrowhead and text positions
    self.pos_ahat()

  def pos_ahat(self):
    '''Set arrowhead and text positions'''

    z = np.abs(self._z)
    a = np.angle(self._z)

    # Arrowhead
    self.animation.item[self.head].position = [z*self._locus,0]

    # Text (adapt position to arrow angle)
    rect = self.animation.item[self.text].boundingRect()
    
    if np.abs(a)<np.pi/2:
      self.animation.item[self.text].orientation = 0
      dx = -rect.width()/4
      dy = 0
    else:
      self.animation.item[self.text].orientation = np.pi
      dx = 3*rect.width()/4
      dy = -rect.height()

    self.animation.item[self.text].position = [z*self._locus+dx/self.animation.factor, dy/self.animation.factor]

  # --- Thickness ----------------------------------------------------------

  @property
  def thickness(self): return self._thickness

  @thickness.setter
  def thickness(self, t):

    self._thickness = t
    self.animation.item[self.line].thickness = self._thickness

  # --- Z-value ------------------------------------------------------------

  @property
  def zvalue(self): return self._zvalue

  @zvalue.setter
  def zvalue(self, z):

    self._zvalue = z
    self.animation.item[self.line].zvalue = self._zvalue
    self.animation.item[self.head].zvalue = self._zvalue
    self.animation.item[self.text].zvalue = self._zvalue

  # --- Color --------------------------------------------------------------

  @property
  def color(self): return self._color

  @color.setter
  def color(self, C):

    self._color = C
    self.animation.item[self.line].color = self._color
    self.animation.item[self.head].colors = [self._color, self._color]
    self.animation.item[self.text].color = self._color

  # --- String -------------------------------------------------------------

  @property
  def string(self): return self._string

  @string.setter
  def string(self, s):

    self._string = str(s)
    self.animation.item[self.text].string = self._string

# --- Colorbar -------------------------------------------------------------

class colorbar(composite):
  """
  Colorbar composite element
  """

  def __init__(self, animation, name, **kwargs):
    """
    Colorbar constructor
    """  

    super().__init__(animation, name, **kwargs)

    # --- Arguments

    self.cm = kwargs['colormap']
    self.width = kwargs['width'] if 'width' in kwargs else 0.025
    self.height = kwargs['height'] if 'height' in kwargs else 0.5
    self.nticks = kwargs['nticks'] if 'nticks' in kwargs else 2

    # --- Items

    self.rect = self.name + '_rect'

    # Items
    self.animation.add(rectangle, self.rect, parent = self.name,
      width = self.width,
      height = self.height,
      center = False,
      colors = [None, None]
    )

    # --- Set gradient

    g = QLinearGradient(self.animation.item[self.rect].boundingRect().topLeft(),
      self.animation.item[self.rect].boundingRect().bottomLeft())
    
    for z in np.linspace(0, 1, self.cm.ncolors):      
      g.setColorAt(z, self.cm.qcolor(z, scaled=True))
  
    self.animation.item[self.rect].setBrush(g)

    # --- Ticks

    for z in np.linspace(0, 1, self.nticks):

      v = self.cm.range[0] + z*(self.cm.range[1]-self.cm.range[0])
      y = z*self.height

      self.animation.add(text, 'tick_0', parent = self.name,
        position = [self.width, y],
        string = '<span style="color: ' + self.cm.htmlcolor(z, scaled=True) + ';">◄</span> <span style="color: #AAA;">{:.02f}</span>'.format(v),
        color = 'white',
        fontsize = 10,
        center = (False, True))
  