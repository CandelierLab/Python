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

import numpy as np

from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QElapsedTimer, QPointF, QRectF
from PyQt5.QtGui import QKeySequence, QPalette, QColor, QPainter, QPen, QBrush, QPolygonF, QFont, QPainterPath
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut, QGridLayout, QPushButton, QGraphicsScene, QGraphicsView, QAbstractGraphicsShapeItem, QGraphicsItem, QGraphicsItemGroup, QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsRectItem, QGraphicsPathItem

# === ITEMS ================================================================

# --- Generic Item ---------------------------------------------------------

class item():
  """
  Item of the animation (generic class)

  Items are the elements displayed in the :py:attr:`Animation2d.Qscene`. 
  This class provides a common constructor, conversions of positions
  to scene coordinates and styling of ``QAbstractGraphicsShapeItem`` 
  children.

  Attr:

    animation (:class:`Animation2d`): Parent animation.

    name (str): Unique identifier of the item.

    parent (:class:`item` *subclass*): Parent item, if any.

    position ([float, float]): Position of the item. See each subclass for
      details.

    zvalue (float): Z-value (stack order).
  """

  def __init__(self, animation, name, **kwargs):
    """
    Generic item constructor

    Args:

      animation (:class:`Animaton2d`): The animation container.

      name (str): Name of the item. It should be unique, as it is used as an
        identifier in the :py:attr:`Animation2d.item` dict.

      parent (*QGraphicsItem*): The parent ``QGraphicsItem``.

      zvalue (float): Z-value (stack order).

      position ([float, float]): Position of the item. See each item's 
        documentation for a description.

      draggable (bool): If True, the element will be draggable. (default: ``False``)

      clickable (bool): *TO DO*
    """  

    # Call the other item's constructor, if any
    super().__init__()

    # --- Definitions

    # Reference animation
    self.animation = animation

    # Assign name
    self.name = name

    self._parent = None
    self._behindParent = None
    self._position = [0,0]
    self._shift = [0,0]
    self._orientation = None
    self._zvalue = None
    self._draggable = None
      
    # --- Initialization

    if 'parent' in kwargs: self.parent = kwargs['parent']
    if 'behindParent' in kwargs: self.behindParent = kwargs['behindParent']
    if 'position' in kwargs: self.position = kwargs['position']
    if 'orientation' in kwargs: self.orientation = kwargs['orientation']
    if 'zvalue' in kwargs: self.zvalue = kwargs['zvalue']
    if 'draggable' in kwargs: self.draggable = kwargs['draggable']

  def x2scene(self, x):
    """
    Convert the :math:`x` position in scene coordinates

    arg:
      x (float): The :math:`x` position.

    returns:
      The :math:`x` position in scene coordinates.
    """
    if self.parent is None:
      return (x-self.animation.boundaries['x'][0])*self.animation.factor
    else:
      return x*self.animation.factor

  def y2scene(self, y):
    """
    Convert the :math:`y` position in scene coordinates

    arg:
      y (float): The :math:`y` position.

    returns:
      The :math:`y` position in scene coordinates.
    """
    
    if self.parent is None:
      return (self.animation.boundaries['y'][0]-y)*self.animation.factor
    else:
      return -y*self.animation.factor

  def xy2scene(self, xy):
    """
    Convert the :math:`x` and :math:`y` positions in scene coordinates

    arg:
      xy ([float,float]): The :math:`x` and :math:`y` positions.

    returns:
      The :math:`x` and :math:`y` position in scene coordinates.
    """

    return self.x2scene(xy[0]), self.y2scene(xy[1])

  def d2scene(self, d):
    """
    Convert a distance in scene coordinates

    arg:
      d (float): Distance to convert.

    returns:
      The distance in scene coordinates.
    """

    return d*self.animation.factor

  def a2scene(self, a):
    """
    Convert an angle in scene coordinates (radian to degrees)

    arg:
      a (float): Angle to convert.

    returns:
      The angle in degrees.
    """

    return -a*180/np.pi
  
  def scene2x(self, u):
    """
    Convert horizontal scene coordinates into :math:`x` position

    arg:
      u (float): The horizontal coordinate.

    returns:
      The :math:`x` position.
    """

    if self._parent is None:
      return self.animation.boundaries['x'][0] + u/self.animation.factor
    else:
      return u/self.animation.factor

  def scene2y(self, v):
    """
    Convert vertical scene coordinates into :math:`y` position

    arg:
      v (float): The horizontal coordinate.

    returns:
      The :math:`y` position.
    """

    if self._parent is None:
      return self.animation.boundaries['y'][0] - v/self.animation.factor
    else:
      return - v/self.animation.factor

  def scene2xy(self, pos):
    """
    Convert scene coordinates into :math:`x` and :math:`y` positions

    arg:
      pos ([float,float]): The position in scene coordinates.

    returns:
      The :math:`x` and :math:`y` positions.
    """

    if isinstance(pos, QPointF):
      u = pos.x()
      v = pos.y()
    else:
      u = pos[0]
      v = pos[1]

    return self.scene2x(u), self.scene2y(v)

  def place(self):
    """
    Absolute positionning

    Places the item at an absolute position.
    
    Attributes:
      x (float): :math:`x`-coordinate of the new position. It can also be a 
        doublet [``x``,``y``], in this case the *y* argument is 
        overridden.
      y (float): :math:`y`-coordinate of the new position.
      z (float): A complex number :math:`z = x+jy`. Specifying ``z``
        overrides the ``x`` and ``y`` arguments.
    """

    # Set position
    self.setPos(self.x2scene(self._position[0])-self._shift[0], 
      self.y2scene(self._position[1])-self._shift[1])

  def move(self, dx=None, dy=None, z=None):
    """
    Relative displacement

    Displaces the item of relative amounts.
    
    Attributes:
      dx (float): :math:`x`-coordinate of the displacement. It can also be a 
        doublet [`dx`,`dy`], in this case the *dy* argument is overridden.
      dy (float): :math:`y`-coordinate of the displacement.
      z (float): A complex number :math:`z = dx+jdy`. Specifying ``z``
        overrides the ``x`` and ``y`` arguments.
    """

    # Doublet input
    if isinstance(dx, (tuple, list)):
      dy = dx[1]
      dx = dx[0]  

    # Convert from complex coordinates
    if z is not None:
      dx = np.real(z)
      dy = np.imag(z)

    # Store position
    if dx is not None: self._position[0] += dx
    if dy is not None: self._position[1] += dy

    self.place()

  def rotate(self, angle):
    """
    Relative rotation

    Rotates the item relatively to its current orientation.
    
    Attributes:
      angle (float): Orientational increment (rad)
    """

    self._orientation += angle
    self.setRotation(self.a2scene(self.orientation))

  def setStyle(self):
    """
    Item styling

    This function does not take any argument, instead it applies the changes
    defined by each item's styling attributes (*e.g.* color, stroke thickness).
    """

    # --- Fill

    if isinstance(self, QAbstractGraphicsShapeItem):

      if self._color['fill'] is not None:
        self.setBrush(QBrush(QColor(self._color['fill'])))

    # --- Stroke

    if isinstance(self, (QAbstractGraphicsShapeItem,QGraphicsLineItem)):

      Pen = QPen()

      #  Color
      if self._color['stroke'] is not None:
        Pen.setColor(QColor(self._color['stroke']))

      # Thickness
      if self._thickness is not None:
        Pen.setWidth(self._thickness)

      # Style
      match self._linestyle:
        case 'dash' | '--': Pen.setDashPattern([3,6])
        case 'dot' | ':' | '..': Pen.setStyle(Qt.DotLine)
        case 'dashdot' | '-.': Pen.setDashPattern([3,3,1,3])
      
      self.setPen(Pen)

  def mousePressEvent(self, event):
    """
    Simple click event

    For internal use only.

    args:
      event (QGraphicsSceneMouseEvent): The click event.
    """

    match event.button():
      case 1: type = 'leftclick'
      case 2: type = 'rightclick'
      case 4: type = 'middleclick'
      case 8: type = 'sideclick'

    self.animation.change(type, self)
    super().mousePressEvent(event)

  def mouseDoubleClickEvent(self, event):
    """
    Double click event

    For internal use only.

    args:
      event (QGraphicsSceneMouseEvent): The double click event.
    """

    self.animation.change('doubleclick', self)
    super().mousePressEvent(event)

  def itemChange(self, change, value):
    """
    Item change notification

    This method is triggered upon item change. The item's transformation
    matrix has changed either because setTransform is called, or one of the
    transformation properties is changed. This notification is sent if the 
    ``ItemSendsGeometryChanges`` flag is enabled (e.g. when an item is 
    :py:attr:`item.movable`), and after the item's local transformation 
    matrix has changed.

    args:

      change (QGraphicsItem constant): 

    """
    # -- Define type

    type = None

    match change:
      case QGraphicsItem.ItemPositionHasChanged:
        type = 'move'

    # Report to animation
    if type is not None:
      self.animation.change(type, self)

    # Propagate change
    return super().itemChange(change, value)

  # --- Parent -------------------------------------------------------------

  @property
  def parent(self): return self._parent

  @parent.setter
  def parent(self, pName):
    self._parent = pName
    self.setParentItem(self.animation.item[self._parent])

  # --- belowParent --------------------------------------------------------

  @property
  def behindParent(self): return self._behindParent

  @behindParent.setter
  def behindParent(self, b):
    self._behindParent = b
    self.setFlag(QGraphicsItem.ItemStacksBehindParent, b)

  # --- Position -------------------------------------------------------------

  @property
  def position(self): return self._position

  @position.setter
  def position(self, pos):
    
    if isinstance(pos, complex):

      # Convert from complex coordinates
      x = np.real(pos)
      y = np.imag(pos)

    else:

      # Doublet input
      x = pos[0]  
      y = pos[1]      

    # Store position
    self._position = [x,y]

    # Set position
    self.place()    

  # --- Orientation --------------------------------------------------------

  @property
  def orientation(self): return self._orientation

  @orientation.setter
  def orientation(self, angle):
    
    self._orientation = angle
    self.setRotation(self.a2scene(angle))

  # --- Z-value ------------------------------------------------------------

  @property
  def zvalue(self): return self._zvalue

  @zvalue.setter
  def zvalue(self, z):
    self._zvalue = z
    self.setZValue(self._zvalue)

  # --- Draggability -------------------------------------------------------

  @property
  def draggable(self): return self._draggable

  @draggable.setter
  def draggable(self, z):
    
    self._draggable = z
    
    self.setFlag(QGraphicsItem.ItemIsMovable, self._draggable)
    self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, self._draggable)
    if self._draggable:
      self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
    
# --- Group ----------------------------------------------------------------

class group(item, QGraphicsItemGroup):
  """
  Group item

  A group item has no representation upon display but serves as a parent for
  multiple other items in order to create and manipulate composed objects.  
  """

  def __init__(self, animation, name, **kwargs):
    """
    Group item constructor

    Defines a group, which inherits both from ``QGraphicsItemGroup`` and
    :class:`item`.

    Args:

      animation (:class:`Animaton2d`): The animation container.

      name (str): The item's identifier, which should be unique. It is used as a
        reference by :class:`Animation2d`. This is the only mandatory argument.

      parent (*QGraphicsItem*): The parent ``QGraphicsItem`` in the ``QGraphicsScene``.
        Default is ``None``, which means the parent is the ``QGraphicsScene`` itself.

      zvalue (float): Z-value (stack order) of the item.

      position ([float,float]): Position of the ``group``, ``text``, 
        ``circle``, and ``rectangle`` elements (scene units).

      orientation (float): Orientation of the item (rad)

      clickable (bool): *TO DO*

      movable (bool): If True, the element will be draggable. (default: ``False``)
    """  

    # Generic item constructor
    super().__init__(animation, name, **kwargs)
   
# --- Text -----------------------------------------------------------------

class text(item, QGraphicsTextItem):
  """
  Text item

  The ellipse is defined by it's :py:attr:`ellipse.major` and :py:attr:`ellipse.minor`
  axis lenghts, and by its position and orientation. The position of the 
  center is set by :py:attr:`item.position` and the orientation ... *TO WRITE*.
  
  Attributes:

    major (float): Length of the major axis.

    minor (float): Length of the minor axis.
  """

  def __init__(self, animation, name, **kwargs):
    """
    Text item constructor

    Defines a textbox, which inherits both from ``QGraphicsEllipseItem`` and
    :class:`item`.

    Args:

      animation (:class:`Animaton2d`): The animation container.

      name (str): The item's identifier, which should be unique. It is used as a
        reference by :class:`Animation2d`. This is the only mandatory argument.

      parent (*QGraphicsItem*): The parent ``QGraphicsItem`` in the ``QGraphicsScene``.
        Default is ``None``, which means the parent is the ``QGraphicsScene`` itself.

      zvalue (float): Z-value (stack order) of the item.

      orientation (float): Orientation of the item (rad)

      position ([float,float]): Position of the ``group``, ``text``, 
        ``circle``, and ``rectangle`` elements (scene units).

      colors ([*color*, *color*]): Fill and stroke colors for ``circle``, 
        ``ellipse``, ``rectangle`` or ``polygon`` elements.  Colors can be 
        whatever input of ``QColor`` (*e.g*: ``darkCyan``, ``#ff112233`` or 
        (255, 0, 0, 127))

      linestyle (str): Stroke style (for ``circle``, ``ellipse``, ``rectangle``
        or ``p    
      clickable (bool): *TO DO*

      movable (bool): If True, the element will be draggable. (default: ``False``)
    """  

    # Generic item constructor
    super().__init__(animation, name, **kwargs)
    
    # --- Definitions
  
    self._string = None
    self._color = None
    self._fontname = 'Arial'
    self._fontsize = 10
    self._center = (True, True)
    
    # --- Initialization

    self.string = kwargs['string'] if 'string' in kwargs else '-'
    self.color = kwargs['color'] if 'color' in kwargs else 'white'
    if 'fontname' in kwargs: self.fontname = kwargs['fontname']
    if 'fontsize' in kwargs: self.fontsize = kwargs['fontsize']
    if 'center' in kwargs: self.center = kwargs['center'] 

  # --- String -------------------------------------------------------------

  @property
  def string(self): return self._string

  @string.setter
  def string(self, s):
    self._string = s
    self.setHtml(s)

  # --- Color --------------------------------------------------------------

  @property
  def color(self): return self._color

  @color.setter
  def color(self, c):
    self._color = c
    self.setDefaultTextColor(QColor(self._color))

  # --- Fontname -----------------------------------------------------------

  @property
  def fontname(self): return self._fontname

  @fontname.setter
  def fontname(self, name):
    self._fontname = name
    self.setFont((QFont(self._fontname, self._fontsize)))

  # --- Font size ----------------------------------------------------------

  @property
  def fontsize(self): return self._fontsize

  @fontsize.setter
  def fontsize(self, name):
    self._fontsize = name
    self.setFont((QFont(self._fontname, self._fontsize)))

  # --- Center -------------------------------------------------------------

  @property
  def center(self): return self._center

  @center.setter
  def center(self, C):

    if isinstance(C, bool):
      self._center = (C,C)

    self._shift = [0,0]
    if self._center[0] or self._center[1]:
      
      bb = self.boundingRect()

      if self.center[0]:
        self._shift[0] = bb.width()/2
      if self._center[0]:
        self._shift[1] = bb.height()/2

    self.place()

# --- Ellipse --------------------------------------------------------------

class ellipse(item, QGraphicsEllipseItem):
  """
  Ellipse item

  The ellipse is defined by it's :py:attr:`ellipse.major` and :py:attr:`ellipse.minor`
  axis lenghts, and by its position and orientation. The position of the 
  center is set by :py:attr:`item.position` and the orientation ... *TO WRITE*.
  
  Attributes:

    major (float): Length of the major axis.

    minor (float): Length of the minor axis.
  """

  def __init__(self, animation, name, **kwargs):
    """
    Ellipse item constructor

    Defines an ellipse, which inherits both from ``QGraphicsEllipseItem`` and
    :class:`item`.

    Args:

      animation (:class:`Animaton2d`): The animation container.

      name (str): The item's identifier, which should be unique. It is used as a
        reference by :class:`Animation2d`. This is the only mandatory argument.

      parent (*QGraphicsItem*): The parent ``QGraphicsItem`` in the ``QGraphicsScene``.
        Default is ``None``, which means the parent is the ``QGraphicsScene`` itself.

      zvalue (float): Z-value (stack order) of the item.

      orientation (float): Orientation of the item (rad)

      position ([float,float]): Position of the ``group``, ``text``, 
        ``circle``, and ``rectangle`` elements (scene units).

      colors ([*color*, *color*]): Fill and stroke colors for ``circle``, 
        ``ellipse``, ``rectangle`` or ``polygon`` elements.  Colors can be 
        whatever input of ``QColor`` (*e.g*: ``darkCyan``, ``#ff112233`` or 
        (255, 0, 0, 127))

      linestyle (str): Stroke style (for ``circle``, ``ellipse``, ``rectangle``
        or ``polygon``). Can have any value among ``solid`` (default), ``dash``
        or ``--``, ``dot`` or ``..`` or ``:``, ``dashdot`` or ``-.``.

      clickable (bool): *TO DO*

      movable (bool): If True, the element will be draggable. (default: ``False``)
    """  

    # Generic item constructor
    super().__init__(animation, name, **kwargs)
    
    # --- Definitions

    self._major = None
    self._minor = None
    self._color = (None, None)
    self._thickness = None
    self._linestyle = None

    # --- Initialization

    if 'major' not in kwargs or 'minor' not in kwargs:
      raise AttributeError("'major' and 'minor' must be specified for ellipse items.")
    else:
      self.major = kwargs['major']
      self.minor = kwargs['minor']

    self.colors = kwargs['colors'] if 'colors' in kwargs else ['gray','white']
    self.linestyle = kwargs['linestyle'] if 'linestyle' in kwargs else None
    self.thickness = kwargs['thickness'] if 'thickness' in kwargs else 0   

  # --- Major axis length --------------------------------------------------

  @property
  def major(self): return self._major

  @major.setter
  def major(self, major):

    self._major = major

    if self._minor is not None:

      # Conversion
      M = self.d2scene(self._major)
      m = self.d2scene(self._minor)

      # Set geometry
      self.setRect(QRectF(-M/2, -m/2, M, m))

  # --- Minor axis length --------------------------------------------------

  @property
  def minor(self): return self._minor

  @minor.setter
  def minor(self, minor):

    self._minor = minor

    # Conversion
    M = self.d2scene(self._major)
    m = self.d2scene(self._minor)

    # Set geometry
    self.setRect(QRectF(-M/2, -m/2, M, m))

  # --- Colors -------------------------------------------------------------

  @property
  def colors(self): return self._color

  @colors.setter
  def colors(self, C):
    self._color = {'fill': C[0], 'stroke': C[1]}
    self.setStyle()

  # --- Thickness ----------------------------------------------------------

  @property
  def thickness(self): return self._thickness

  @thickness.setter
  def thickness(self, t):
    self._thickness = t
    self.setStyle()

  # --- Linestyle ----------------------------------------------------------

  @property
  def linestyle(self): return self._linestyle

  @linestyle.setter
  def linestyle(self, s):
    self._linestyle = s
    self.setStyle()      

# --- Circle ---------------------------------------------------------------

class circle(item, QGraphicsEllipseItem):
  """
  Circle item

  The ellipse is defined by it's :py:attr:`ellipse.major` and :py:attr:`ellipse.minor`
  axis lenghts, and by its position and orientation. The position of the 
  center is set by :py:attr:`item.position` and the orientation ... *TO WRITE*.
  
  Attributes:

    major (float): Length of the major axis.

    minor (float): Length of the minor axis.
  """

  def __init__(self, animation, name, **kwargs):
    """
    Circle item constructor

    Defines an ellipse, which inherits both from ``QGraphicsEllipseItem`` and
    :class:`item`.

    Args:

      animation (:class:`Animaton2d`): The animation container.

      name (str): The item's identifier, which should be unique. It is used as a
        reference by :class:`Animation2d`. This is the only mandatory argument.

      parent (*QGraphicsItem*): The parent ``QGraphicsItem`` in the ``QGraphicsScene``.
        Default is ``None``, which means the parent is the ``QGraphicsScene`` itself.

      zvalue (float): Z-value (stack order) of the item.

      orientation (float): Orientation of the item (rad)

      position ([float,float]): Position of the ``group``, ``text``, 
        ``circle``, and ``rectangle`` elements (scene units).

      colors ([*color*, *color*]): Fill and stroke colors for ``circle``, 
        ``ellipse``, ``rectangle`` or ``polygon`` elements.  Colors can be 
        whatever input of ``QColor`` (*e.g*: ``darkCyan``, ``#ff112233`` or 
        (255, 0, 0, 127))

      linestyle (str): Stroke style (for ``circle``, ``ellipse``, ``rectangle``
        or ``polygon``). Can have any value among ``solid`` (default), ``dash``
        or ``--``, ``dot`` or ``..`` or ``:``, ``dashdot`` or ``-.``.

      clickable (bool): *TO DO*

      movable (bool): If True, the element will be draggable. (default: ``False``)
    """  

    # Generic item constructor
    super().__init__(animation, name, **kwargs)
    
    # --- Definitions

    self._radius = None
    self._color = (None, None)
    self._thickness = None
    self._linestyle = None

    # --- Initialization

    if 'radius' not in kwargs:
      raise AttributeError("'radius' must be specified for circle items.")
    else:
      self.radius = kwargs['radius']

    self.colors = kwargs['colors'] if 'colors' in kwargs else ['gray','white']
    self.linestyle = kwargs['linestyle'] if 'linestyle' in kwargs else None
    self.thickness = kwargs['thickness'] if 'thickness' in kwargs else 0   

  # --- Radius -------------------------------------------------------------

  @property
  def radius(self): return self._radius

  @radius.setter
  def radius(self, r):

    self._radius = r
    R = self.d2scene(r)
    self.setRect(QRectF(-R, -R, 2*R, 2*R))

  # --- Colors -------------------------------------------------------------

  @property
  def colors(self): return self._color

  @colors.setter
  def colors(self, C):
    self._color = {'fill': C[0], 'stroke': C[1]}
    self.setStyle()

  # --- Thickness ----------------------------------------------------------

  @property
  def thickness(self): return self._thickness

  @thickness.setter
  def thickness(self, t):
    self._thickness = t
    self.setStyle()

  # --- Linestyle ----------------------------------------------------------

  @property
  def linestyle(self): return self._linestyle

  @linestyle.setter
  def linestyle(self, s):
    self._linestyle = s
    self.setStyle()      

# --- Rectangle ------------------------------------------------------------

class rectangle(item, QGraphicsRectItem):
  """
  Rectangle item

  The ellipse is defined by it's :py:attr:`ellipse.major` and :py:attr:`ellipse.minor`
  axis lenghts, and by its position and orientation. The position of the 
  center is set by :py:attr:`item.position` and the orientation ... *TO WRITE*.
  
  Attributes:

    major (float): Length of the major axis.

    minor (float): Length of the minor axis.
  """

  def __init__(self, animation, name, **kwargs):
    """
    Rectangle item constructor

    Defines an ellipse, which inherits both from ``QGraphicsEllipseItem`` and
    :class:`item`.

    Args:

      animation (:class:`Animaton2d`): The animation container.

      name (str): The item's identifier, which should be unique. It is used as a
        reference by :class:`Animation2d`. This is the only mandatory argument.

      parent (*QGraphicsItem*): The parent ``QGraphicsItem`` in the ``QGraphicsScene``.
        Default is ``None``, which means the parent is the ``QGraphicsScene`` itself.

      zvalue (float): Z-value (stack order) of the item.

      orientation (float): Orientation of the item (rad)

      position ([float,float]): Position of the ``group``, ``text``, 
        ``circle``, and ``rectangle`` elements (scene units).

      colors ([*color*, *color*]): Fill and stroke colors for ``circle``, 
        ``ellipse``, ``rectangle`` or ``polygon`` elements.  Colors can be 
        whatever input of ``QColor`` (*e.g*: ``darkCyan``, ``#ff112233`` or 
        (255, 0, 0, 127))

      linestyle (str): Stroke style (for ``circle``, ``ellipse``, ``rectangle``
        or ``polygon``). Can have any value among ``solid`` (default), ``dash``
        or ``--``, ``dot`` or ``..`` or ``:``, ``dashdot`` or ``-.``.

      clickable (bool): *TO DO*

      movable (bool): If True, the element will be draggable. (default: ``False``)
    """  

    # Generic item constructor
    super().__init__(animation, name, **kwargs)
    
    # --- Definitions

    self._width = None
    self._height = None
    self._center = (True, True)
    self._color = (None, None)
    self._thickness = None
    self._linestyle = None

    # --- Initialization

    if 'width' not in kwargs or 'height' not in kwargs:
      raise AttributeError("'width' and 'height' must be specified for rectangle items.")
    else:
      self.width = kwargs['width']
      self.height = kwargs['height']

    if 'center' in kwargs: self.center = kwargs['center']
    self.colors = kwargs['colors'] if 'colors' in kwargs else ['gray','white']
    self.linestyle = kwargs['linestyle'] if 'linestyle' in kwargs else None
    self.thickness = kwargs['thickness'] if 'thickness' in kwargs else 0   

  def setGeometry(self):

    # Conversion
    W = self.d2scene(self._width)
    H = self.d2scene(self._height)

    dx = 0
    dy = 0
    if self._center[0] or self._center[1]:
      
      bb = self.boundingRect()
      if self.center[0]: dx = -W/2
      if self._center[1]: dy = H/2

    # Set geometry
    self.setRect(QRectF(dx, dy, W, -H))

  # --- Width --------------------------------------------------------------

  @property
  def width(self): return self._width

  @width.setter
  def width(self, w):

    self._width = w
    if self._height is not None: self.setGeometry()
      

  # --- Height -------------------------------------------------------------

  @property
  def height(self): return self._height

  @height.setter
  def height(self, h):

    self._height = h
    self.setGeometry()    

  # --- Center -------------------------------------------------------------

  @property
  def center(self): return self._center

  @center.setter
  def center(self, C):

    if isinstance(C, bool):
      self._center = (C,C)

    self.setGeometry()

  # --- Colors -------------------------------------------------------------

  @property
  def colors(self): return self._color

  @colors.setter
  def colors(self, C):
    self._color = {'fill': C[0], 'stroke': C[1]}
    self.setStyle()

  # --- Thickness ----------------------------------------------------------

  @property
  def thickness(self): return self._thickness

  @thickness.setter
  def thickness(self, t):
    self._thickness = t
    self.setStyle()

  # --- Linestyle ----------------------------------------------------------

  @property
  def linestyle(self): return self._linestyle

  @linestyle.setter
  def linestyle(self, s):
    self._linestyle = s
    self.setStyle()      

# --- Line -----------------------------------------------------------------

class line(item, QGraphicsLineItem):
  """
  Line item

  The ellipse is defined by it's :py:attr:`ellipse.major` and :py:attr:`ellipse.minor`
  axis lenghts, and by its position and orientation. The position of the 
  center is set by :py:attr:`item.position` and the orientation ... *TO WRITE*.
  
  Attributes:

    major (float): Length of the major axis.

    minor (float): Length of the minor axis.
  """

  def __init__(self, animation, name, **kwargs):
    """
    Line item constructor

    Defines an ellipse, which inherits both from ``QGraphicsEllipseItem`` and
    :class:`item`.

    Args:

      animation (:class:`Animaton2d`): The animation container.

      name (str): The item's identifier, which should be unique. It is used as a
        reference by :class:`Animation2d`. This is the only mandatory argument.

      parent (*QGraphicsItem*): The parent ``QGraphicsItem`` in the ``QGraphicsScene``.
        Default is ``None``, which means the parent is the ``QGraphicsScene`` itself.

      zvalue (float): Z-value (stack order) of the item.

      orientation (float): Orientation of the item (rad)

      position ([float,float]): Position of the ``group``, ``text``, 
        ``circle``, and ``rectangle`` elements (scene units).

      colors ([*color*, *color*]): Fill and stroke colors for ``circle``, 
        ``ellipse``, ``rectangle`` or ``polygon`` elements.  Colors can be 
        whatever input of ``QColor`` (*e.g*: ``darkCyan``, ``#ff112233`` or 
        (255, 0, 0, 127))

      linestyle (str): Stroke style (for ``circle``, ``ellipse``, ``rectangle``
        or ``polygon``). Can have any value among ``solid`` (default), ``dash``
        or ``--``, ``dot`` or ``..`` or ``:``, ``dashdot`` or ``-.``.

      clickable (bool): *TO DO*

      movable (bool): If True, the element will be draggable. (default: ``False``)
    """  

    # Generic item constructor
    super().__init__(animation, name, **kwargs)
    
    # --- Definitions

    self._points = None
    self._color = (None, None)
    self._thickness = None
    self._linestyle = None

    # --- Initialization

    if 'points' not in kwargs:
      raise AttributeError("'points' must be specified for line items.")
    else:
      self.points = kwargs['points']

    self.color = kwargs['color'] if 'color' in kwargs else 'white'
    self.linestyle = kwargs['linestyle'] if 'linestyle' in kwargs else None
    self.thickness = kwargs['thickness'] if 'thickness' in kwargs else 0   

  # --- Points -------------------------------------------------------------

  @property
  def points(self): return self._points

  @points.setter
  def points(self, p):

    self._points = p

    x1 = self.x2scene(p[0][0])
    y1 = self.y2scene(p[0][1])
    x2 = self.x2scene(p[1][0])
    y2 = self.y2scene(p[1][1])
    self.setLine(x1, y1, x2, y2)
  
  # --- Color --------------------------------------------------------------

  @property
  def color(self): return self._color

  @color.setter
  def color(self, C):
    self._color = {'fill': None, 'stroke': C}
    self.setStyle()

  # --- Thickness ----------------------------------------------------------

  @property
  def thickness(self): return self._thickness

  @thickness.setter
  def thickness(self, t):
    self._thickness = t
    self.setStyle()

  # --- Linestyle ----------------------------------------------------------

  @property
  def linestyle(self): return self._linestyle

  @linestyle.setter
  def linestyle(self, s):
    self._linestyle = s
    self.setStyle()      

# --- Polygon --------------------------------------------------------------

class polygon(item, QGraphicsPolygonItem):
  """
  Polygon item

  The ellipse is defined by it's :py:attr:`ellipse.major` and :py:attr:`ellipse.minor`
  axis lenghts, and by its position and orientation. The position of the 
  center is set by :py:attr:`item.position` and the orientation ... *TO WRITE*.
  
  Attributes:

    major (float): Length of the major axis.

    minor (float): Length of the minor axis.
  """

  def __init__(self, animation, name, **kwargs):
    """
    Polygon item constructor

    Defines an ellipse, which inherits both from ``QGraphicsEllipseItem`` and
    :class:`item`.

    Args:

      animation (:class:`Animaton2d`): The animation container.

      name (str): The item's identifier, which should be unique. It is used as a
        reference by :class:`Animation2d`. This is the only mandatory argument.

      parent (*QGraphicsItem*): The parent ``QGraphicsItem`` in the ``QGraphicsScene``.
        Default is ``None``, which means the parent is the ``QGraphicsScene`` itself.

      zvalue (float): Z-value (stack order) of the item.

      orientation (float): Orientation of the item (rad)

      position ([float,float]): Position of the ``group``, ``text``, 
        ``circle``, and ``rectangle`` elements (scene units).

      colors ([*color*, *color*]): Fill and stroke colors for ``circle``, 
        ``ellipse``, ``rectangle`` or ``polygon`` elements.  Colors can be 
        whatever input of ``QColor`` (*e.g*: ``darkCyan``, ``#ff112233`` or 
        (255, 0, 0, 127))

      linestyle (str): Stroke style (for ``circle``, ``ellipse``, ``rectangle``
        or ``polygon``). Can have any value among ``solid`` (default), ``dash``
        or ``--``, ``dot`` or ``..`` or ``:``, ``dashdot`` or ``-.``.

      clickable (bool): *TO DO*

      movable (bool): If True, the element will be draggable. (default: ``False``)
    """  

    # Generic item constructor
    super().__init__(animation, name, **kwargs)
    
    # --- Definitions

    self._points = None
    self._color = (None, None)
    self._thickness = None
    self._linestyle = None

    # --- Initialization

    if 'points' not in kwargs:
      raise AttributeError("'points' must be specified for polygon items.")
    else:
      self.points = kwargs['points']

    self.colors = kwargs['colors'] if 'colors' in kwargs else ['gray','white']
    self.linestyle = kwargs['linestyle'] if 'linestyle' in kwargs else None
    self.thickness = kwargs['thickness'] if 'thickness' in kwargs else 0   

  # --- Points -------------------------------------------------------------

  @property
  def points(self): return self._points

  @points.setter
  def points(self, points):

    self._points = points

    poly = []
    for p in self._points:
      poly.append(QPointF(self.x2scene(p[0]), self.y2scene(p[1])))
    self.setPolygon(QPolygonF(poly))
  
  # --- Color --------------------------------------------------------------

  @property
  def colors(self): return self._color

  @colors.setter
  def colors(self, C):
    self._color = {'fill': C[0], 'stroke': C[1]}
    self.setStyle()

  # --- Thickness ----------------------------------------------------------

  @property
  def thickness(self): return self._thickness

  @thickness.setter
  def thickness(self, t):
    self._thickness = t
    self.setStyle()

  # --- Linestyle ----------------------------------------------------------

  @property
  def linestyle(self): return self._linestyle

  @linestyle.setter
  def linestyle(self, s):
    self._linestyle = s
    self.setStyle()      

# --- Path -----------------------------------------------------------------

class path(item, QGraphicsPathItem):
  """
  Path item

  The ellipse is defined by it's :py:attr:`ellipse.major` and :py:attr:`ellipse.minor`
  axis lenghts, and by its position and orientation. The position of the 
  center is set by :py:attr:`item.position` and the orientation ... *TO WRITE*.
  
  Attributes:

    major (float): Length of the major axis.

    minor (float): Length of the minor axis.
  """

  def __init__(self, animation, name, **kwargs):
    """
    Path item constructor

    Defines an ellipse, which inherits both from ``QGraphicsEllipseItem`` and
    :class:`item`.

    Args:

      animation (:class:`Animaton2d`): The animation container.

      name (str): The item's identifier, which should be unique. It is used as a
        reference by :class:`Animation2d`. This is the only mandatory argument.

      parent (*QGraphicsItem*): The parent ``QGraphicsItem`` in the ``QGraphicsScene``.
        Default is ``None``, which means the parent is the ``QGraphicsScene`` itself.

      zvalue (float): Z-value (stack order) of the item.

      orientation (float): Orientation of the item (rad)

      position ([float,float]): Position of the ``group``, ``text``, 
        ``circle``, and ``rectangle`` elements (scene units).

      colors ([*color*, *color*]): Fill and stroke colors for ``circle``, 
        ``ellipse``, ``rectangle`` or ``polygon`` elements.  Colors can be 
        whatever input of ``QColor`` (*e.g*: ``darkCyan``, ``#ff112233`` or 
        (255, 0, 0, 127))

      linestyle (str): Stroke style (for ``circle``, ``ellipse``, ``rectangle``
        or ``polygon``). Can have any value among ``solid`` (default), ``dash``
        or ``--``, ``dot`` or ``..`` or ``:``, ``dashdot`` or ``-.``.

      clickable (bool): *TO DO*

      movable (bool): If True, the element will be draggable. (default: ``False``)
    """  

    # Generic item constructor
    super().__init__(animation, name, **kwargs)
    
    # --- Definitions

    self._points = None
    self._color = (None, None)
    self._thickness = None
    self._linestyle = None

    # --- Initialization

    if 'points' not in kwargs:
      raise AttributeError("'points' must be specified for path items.")
    else:
      self.points = kwargs['points']

    self.colors = kwargs['colors'] if 'colors' in kwargs else ['gray','white']
    self.linestyle = kwargs['linestyle'] if 'linestyle' in kwargs else None
    self.thickness = kwargs['thickness'] if 'thickness' in kwargs else 0   

  # --- Points -------------------------------------------------------------

  @property
  def points(self): return self._points

  @points.setter
  def points(self, points):

    self._points = points

    P = QPainterPath()
    for k,p in enumerate(points):
      if k:
        P.lineTo(self.x2scene(p[0]), self.y2scene(p[1]))
      else:
        P.moveTo(self.x2scene(p[0]), self.y2scene(p[1]))

    self.setPath(P)
  
  # --- Color --------------------------------------------------------------

  @property
  def colors(self): return self._color

  @colors.setter
  def colors(self, C):
    self._color = {'fill': C[0], 'stroke': C[1]}
    self.setStyle()

  # --- Thickness ----------------------------------------------------------

  @property
  def thickness(self): return self._thickness

  @thickness.setter
  def thickness(self, t):
    self._thickness = t
    self.setStyle()

  # --- Linestyle ----------------------------------------------------------

  @property
  def linestyle(self): return self._linestyle

  @linestyle.setter
  def linestyle(self, s):
    self._linestyle = s
    self.setStyle()      

# === COMPOSITE ELEMENTS ===================================================

# --- Composite ------------------------------------------------------------

class composite():
  """
  Composite element

  A composite element defines a group item containing other items.
  """

  def __init__(self):
    pass

# --- Arrow ----------------------------------------------------------------

class arrow(composite):
  """
  Arrow composite element
  """

  def __init__(self, animation, name, **kwargs):
    """
    Arrow element constructor
    """  

    # --- Definitions

    self.animation = animation

    # Names
    self.name = name
    self.line = self.name + '_line'
    self.head = self.name + '_head'

    # Items
    self.animation.add(group, self.name, **kwargs)
    self.animation.add(line, self.line, parent = self.name, points = [[0,0],[0,0]])
    # NB: arrowhead is created later on, when the 'shape' attibute is assigned.

    # Protected attributes

    self._points = None
    self._z = None
    self._size = None
    self._locus = 1
    self._shape = None
    self._color = None

    # --- Arguments

    self.size = kwargs['size'] if 'size' in kwargs else 0.015
    self.shape = kwargs['shape'] if 'shape' in kwargs else 'dart'

    if 'points' in kwargs:        
      self.points = kwargs['points']
    else:
      raise AttributeError("The 'points' argument is necessary for an arrow element.")

    if 'locus' in kwargs: self.locus = kwargs['locus']
    if 'thickness' in kwargs: self.thickness = kwargs['thickness']
    self.color = kwargs['color'] if 'color' in kwargs else 'white'

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

    # Arrowhead 
    self.animation.item[self.head].position = [np.abs(self._z)*self._locus,0]

  # --- Locus --------------------------------------------------------------

  @property
  def locus(self): return self._locus

  @locus.setter
  def locus(self, k):

    self._locus = k

    self.animation.item[self.head].position = [np.abs(self._z)*self._locus, 0]

  # --- Thickness ----------------------------------------------------------

  @property
  def thickness(self): return self._thickness

  @thickness.setter
  def thickness(self, t):

    self._thickness = t
    self.animation.item[self.line].thickness = self._thickness

  # --- Color --------------------------------------------------------------

  @property
  def color(self): return self._color

  @color.setter
  def color(self, C):

    self._color = C
    self.animation.item[self.line].color = self._color
    self.animation.item[self.head].colors = [self._color, self._color]

# === ANIMATION ============================================================

class view(QGraphicsView):
  
  def __init__(self, scene, *args, **kwargs):

    super().__init__(*args, *kwargs)
    self.setScene(scene)

  def showEvent(self, E):
    
    self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
    super().showEvent(E)

  def resizeEvent(self, E):
    
    self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
    super().resizeEvent(E)

class Animation2d(QObject):
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

  def __init__(self, parent=None, size=None, boundaries=None, disp_boundaries=True, disp_time=False, dt=None):
    """
    Animation constructor

    Defines all the attributes of the animation, especially the ``QGraphicsScene``
    and ``QGraphicsView`` necessary for rendering.

    Args:

      parent (*Qwidget* or :class:`Window`): Parent container. It can be a ``QWidget``
        or a :class:`Window` object. If not set, a new :class:`Window` object is 
        created and assigned as a parent.

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

    # --- Parent

    self.parent = parent if parent is not None else Window(animation=self)

    # --- Scene & view

    # Scene
    self.scene = QGraphicsScene()
    self.view = view(self.scene)
    self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # Items and composite elements
    self.item = {}
    self.composite = {}

    # --- Layout

    self.layout = QGridLayout()

    self.layout.addWidget(self.view, 0,0)

    button = QPushButton('ok')
    self.layout.addWidget(button, 1,0)

    # --- Time

    self.t = 0
    self.dt = dt
    self.disp_time = disp_time
    self.disp_boundaries = disp_boundaries

    # Framerate
    self.fps = 25

    # -- Size settings

    self.size = size if size is not None else QApplication.desktop().screenGeometry().height()*0.6
    self.margin = 25
    self.timeHeight = QApplication.desktop().screenGeometry().height()*0.02

    # Scene limits
    self.boundaries = {'x':[0,1], 'y':[0,1], 'width':None, 'height':None}
    if boundaries is not None:
      self.boundaries['x'] = list(boundaries[0])
      self.boundaries['y'] = list(boundaries[1])
    self.boundaries['width'] = self.boundaries['x'][1]-self.boundaries['x'][0]
    self.boundaries['height'] = self.boundaries['y'][1]-self.boundaries['y'][0]

    # Scale factor
    self.factor = self.size/self.boundaries['height']

    # --- Display

    # Dark background
    self.view.setBackgroundBrush(Qt.black)
    pal = self.view.palette()
    pal.setColor(QPalette.Window, Qt.black)
    self.view.setPalette(pal)

    # Antialiasing
    self.view.setRenderHints(QPainter.Antialiasing)

    # --- Animation
  
    self.qtimer = QTimer()
    self.qtimer.timeout.connect(self.update)
    self.timer = QElapsedTimer()
    
    # Scene boundaries
    if self.disp_boundaries:
      self.box = QGraphicsRectItem(0,0,
        self.factor*self.boundaries['width'],
        -self.factor*self.boundaries['height'])
      self.box.setPen(QPen(Qt.lightGray, 0)) 
      self.scene.addItem((self.box))

    # Time display
    if self.disp_time:
      self.timeDisp = self.scene.addText("---")
      self.timeDisp.setDefaultTextColor(QColor('white'))
      self.timeDisp.setPos(0, -self.timeHeight-self.factor*self.boundaries['height'])

  def add(self, type, name, **kwargs):
    """
    Add an item to the scene.

    args:
      item (:class:`item` *subclass*): The item to add.
    """

    if issubclass(type, composite):

      # Let composite elements create items
      self.composite[name] = type(self, name, **kwargs)

    else:

      # Create item
      self.item[name] = type(self, name, **kwargs)

      # Add item to the scene
      if self.item[name].parent is None:
        self.scene.addItem(self.item[name])
    
  def show(self):
    """
    Display animation window

    If the animation's parent is a :class:`Window` object, the 
    :py:meth:`Window.show` method is called. Otherwise nothing is done.
    """

    if isinstance(self.parent, Window):
      self.parent.show()

  def startAnimation(self):
    """
    Start the animation

    Trigs the animation :py:attr:`Animation.Qtimer` ``QTimer``, which starts
    the animation.
    """

    self.qtimer.setInterval(int(1000/self.fps))
    self.qtimer.start()
    self.timer.start()

    # Emit event
    self.event.emit({'type': 'start'})

  def stopAnimation(self):
    """
    Stop the animation

    Stops the timer and close the window, if any.
    """

    # Stop the timer
    self.qtimer.stop()

    # Emit event
    self.event.emit({'type': 'stop'})

    # Close the window, if any
    if isinstance(self.parent, Window):
      self.parent.close()
      
  def update(self):
    """
    Update animation state

    Update the animation time :py:attr:`Animation.t`. Subclass this method
    to implement the animation, *e.g.* moving elements or changing color.
    """

    # Update time
    if self.dt is None:
      self.t = self.timer.elapsed()/1000 
    else: 
      self.t += self.dt

    # Emit event
    self.event.emit({'type': 'update', 't': self.t})

    # Timer display
    if self.disp_time:
      self.timeDisp.setPlainText('{:06.02f} sec'.format(self.t))

  def change(self, type, item):
    """
    Change notification

    This method is triggered whenever an item is changed.
    It does nothing and has to be reimplemented in subclasses.

    .. Note::
      To catch motion the item has to be declared as ``movable``,
      which is not the default.

    args:
      type (str): Type of change (``move``).
      item (:class:`item` *subclass*): The changed item.
    """

    pass
    
# === WINDOW ===============================================================

class Window(QWidget):
  """
  Animation-specific window

  Creates a new window containing an animation.
  
  Attributes:
    title (str): Title of the window.
    app (``QApplication``): Underlying ``QApplication``.
    anim (:class:`Animation2d`): Animation to display.
  """

  def __init__(self, title='Animation', animation = None):
    """
    Window constructor

    Defines the ``QApplication``, window title and animation to display.

    Args:
      title (str): Title of the window. Default is 'Animation'.
    """

    # Attributes
    self.title = title
    
    # Qapplication
    self.app = QApplication([])

    # Animation
    self.animation = animation
    
  def show(self):
    """
    Creates the animation window
    
    Create the window to display the animation, defines the shortcuts,
    initialize and start the animation.

    Args:
      size (float): Height of the ``QGraphicsView`` widget, defining the 
        height of the window.
    """

    # --- Animation

    if self.animation is None:
      self.animation = Animation2d(parent=self)

    # --- Layout -----------------------------------------------------------

    self.widget = QWidget()
    self.widget.setLayout(self.animation.layout)

    # --- Settings ---------------------------------------------------------
    
    # Window title
    self.widget.setWindowTitle(self.title)

    # Window size
    # self.animation.view.resize(
    #   int(self.animation.factor*self.animation.boundaries['width']+2*self.animation.margin), 
    #   int(self.animation.factor*self.animation.boundaries['height']+2*self.animation.margin+self.animation.timeHeight))

    # --- Shortcuts

    self.shortcut = {}

    # Quit
    self.shortcut['esc'] = QShortcut(QKeySequence('Esc'), self.widget)
    self.shortcut['esc'].activated.connect(self.app.quit)

    # --- Display animation ------------------------------------------------

    self.widget.show()
    # self.animation.view.show()
    # self.animation.startAnimation()
    
    self.app.exec()

  def close(self):

    # self.animation.stopAnimation()
    self.app.quit()