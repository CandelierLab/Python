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
from collections import defaultdict

from PyQt5.QtCore import Qt, QTimer, QElapsedTimer, QPointF, QRectF
from PyQt5.QtGui import QKeySequence, QPalette, QColor, QPainter, QPen, QBrush, QPolygonF, QFont
from PyQt5.QtWidgets import QApplication, QShortcut, QGraphicsScene, QGraphicsView, QAbstractGraphicsShapeItem, QGraphicsItem, QGraphicsItemGroup, QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsRectItem

# === ELEMENTS =============================================================

# class element():
#   """
#   Elements of the animation

#   Elements are the items displayed in the ``QGraphicsScene`` of the :class:`Animation2d`.
#   A ``group`` element groups other elements for easier manipulation. Some elements like 
#   ``arrow`` are groups of items.
  
#   Supported types are:
#     * ``group``
#     * ``crew``: similar to ``group``, but interactions are reported to the 
#       :py:meth:`Animation2d.change`: method.
#     * ``text``
#     * ``line``
#     * ``arrow``
#     * *TO DO*: ``path``
#     * ``circle``
#     * *TO DO*: ``ellipse``
#     * ``rectangle``
#     * ``polygon``

#   During animation, attributes can be modified with the methods:
#     * :py:meth:`element.rotate`: relative rotation
#     * *TO DO* :py:meth:`element.translate`: relative translation
#     * *TO DO* s:py:meth:`element.setOrientation`: Set absolute orientation
#     * :py:meth:`element.setPosition`: Set absolute position
#     * *TO DO* :py:meth:`element.setColors`: Set fill and stroke colors
#     * *TO DO* :py:meth:`element.setFill`: Set fill color
#     * *TO DO* :py:meth:`element.setStroke`: Set stroke color

#   .. note:: The :py:meth:`element.convert` method is for internal use upon
#     view initialization. It is normaly not called by a user.
  
#   Attributes:
#     elm ({:class:`element`}): All elements in the scene
#     Qitem (*QGraphicsItem*): The underlying ``QGraphicsItem`` belonging to
#       the ``QGraphicsScene`` of the view.
#   """

#   def __init__(self, type, **kwargs):
#     """
#     Element constructor

#     An element should be fully determined upon definition, so the constructor has many options
#     for the different types of elements.

#     Args:

#       type (str): Type of element, among ``group``, ``text``, ``line``, 
#         ``circle``, ``polygon`` or ``rectangle``.

#       parent (*QGraphicsItem*): The parent ``QGraphicsItem``

#       belowParent (bool): Determine if the element should be placed above
#         the parent (``False``, default) or below (``True``).

#       zvalue (float): Z-value of the element in the stack.

#       rotation (float): Rotation of the element (rad)

#       position ([float,float]): Position of the ``group``, ``text``, 
#         ``circle``, and ``rectangle`` elements (scene units).

#       points ([[float,float]]): Positions of the points of ``line``, 
#         ``arrow`` or ``polygon`` elements (scene units).
                
#       radius (float): Radius of the circle (for ``circle`` only).
      
#       width (float): Width of the ``rectangle``.

#       height (float): Height of the ``rectangle``.

#       thickness (float): Stroke thickness (pix). For ``line``, ``circle``, 
#         ``ellipse``, ``rectangle`` or ``polygon`` elements. (Default: 0)

#       locus (float): Position of the tip of arrowhead on the normalized 
#         curvilinear coordinates of the ``arrow`` element. This value should 
#         be between 0 and 1 (default: 1).

#       shape (str): Shape of the arrowhead of ``arrow`` elements. Can be
#         ``dart`` (default) or ``disk``.

#       size (float): Size of the arrowhead of ``arrow`` elements, in scene 
#         units. (default: 0.02)

#       string (str): String of a ``text`` element. Rich HTML text is supported.

#       fontname (str): Font of a ``text`` element. Default: ``Arial``

#       fontsize (int): Default font size of a ``text`` element, corresponding to 
#         the pointSize property of ``QFont``. Default value: 10

#       center ((bool,bool)): Center a ``text`` element horizontally and/or
#         vertically. Default is (``False``, ``False``).

#       color (*color*): Color for ``text``, ``line`` or ``arrow`` elements. 
#         Colors can be whatever input of ``QColor`` (*e.g*: ``darkCyan``, ``#ff112233`` or 
#         (255, 0, 0, 127)).

#       colors ([*color*, *color*]): Fill and stroke colors for ``circle``, 
#         ``ellipse``, ``rectangle`` or ``polygon`` elements.  Colors can be 
#         whatever input of ``QColor`` (*e.g*: ``darkCyan``, ``#ff112233`` or 
#         (255, 0, 0, 127))

#       linestyle (str): Stroke style (for ``circle``, ``ellipse``, ``rectangle``
#         or ``polygon``). Can have any value among ``solid`` (default), ``dash``
#         or ``--``, ``dot`` or ``..`` or ``:``, ``dashdot`` or ``-.``.

#       clickable (bool): *TO DO*

#       movable (bool): If True, the element will be draggable. (default: ``False``)
#     """  

#     # Common properties
#     self.name = None
#     self.type = type
#     self.view = None
#     self.QitemRef = None
#     self.rotation = kwargs['rotation'] if 'rotation' in kwargs else 0
#     self.parent = kwargs['parent'] if 'parent' in kwargs else None
#     self.belowParent = kwargs['belowParent'] if 'belowParent' in kwargs else False
#     self.zvalue = kwargs['zvalue'] if 'zvalue' in kwargs else None
#     self.position = kwargs['position'] if 'position' in kwargs else [0,0]
#     self.movable = kwargs['movable'] if 'movable' in kwargs else False
#     self.clickable = kwargs['clickable'] if 'clickable' in kwargs else False
#     self.color = {}

#     # Element-dependent properties
#     match type:

#       case 'text':
#         self.string = kwargs['string'] if 'string' in kwargs else '-'
#         self.color['fill'] = kwargs['color'] if 'color' in kwargs else 'white'
#         self.center = {}
#         self.center['horizontal'] = kwargs['center'][0] if 'center' in kwargs else False   
#         self.center['vertical'] = kwargs['center'][1] if 'center' in kwargs else False
#         self.fontname = kwargs['fontname'] if 'fontname' in kwargs else 'Arial'
#         self.fontsize = kwargs['fontsize'] if 'fontsize' in kwargs else 10
        
#       case 'line':

#         if 'points' in kwargs:           
#           self.points = kwargs['points']
#         else:
#           raise AttributeError("The 'points' argument is necessary for a line element.")

#         self.color['fill'] = None  
#         self.color['stroke'] = kwargs['color'] if 'color' in kwargs else 'white'
        
#       case 'arrow':

#         # Items of the arrow group
#         self.Qitems = []

#         if 'points' in kwargs:           
#           self.points = kwargs['points']
#         else:
#           raise AttributeError("The 'points' argument is necessary for an arrow element.")
          
#         self.color['stroke'] = kwargs['color'] if 'color' in kwargs else 'white'

#         # Arrow-specific properties
#         self.arrow = {
#           'locus': kwargs['locus'] if 'locus' in kwargs else 1,
#           'size': kwargs['size'] if 'size' in kwargs else 0.02,
#           'shape': kwargs['shape'] if 'shape' in kwargs else 'dart'
#         }

#         if self.arrow['locus']<0 or self.arrow['locus']>1:
#           raise ValueError("Arrowhead position should be in [0;1] (value: {:f})".format(self.arrow['pos']))
        
#       case 'circle':
#         self.radius = kwargs['radius'] if 'radius' in kwargs else 0
#         self.color['fill'] = kwargs['colors'][0] if 'colors' in kwargs else 'gray'
#         self.color['stroke'] = kwargs['colors'][1] if 'colors' in kwargs else 'white'

#       case 'polygon':
        
#         if 'points' in kwargs:           
#           self.points = kwargs['points']
#         else:
#           raise AttributeError("The 'points' argument is necessary for a polygon element.")

#         self.color['fill'] = kwargs['colors'][0] if 'colors' in kwargs else 'gray'
#         self.color['stroke'] = kwargs['colors'][1] if 'colors' in kwargs else 'white'

#       case 'rectangle':
#         self.width = kwargs['width'] if 'width' in kwargs else 0
#         self.height = kwargs['height'] if 'height' in kwargs else 0
#         self.color['fill'] = kwargs['colors'][0] if 'colors' in kwargs else 'gray'
#         self.color['stroke'] = kwargs['colors'][1] if 'colors' in kwargs else 'white'
        
#     # --- Style

#     # Stroke thickness
#     self.thickness = kwargs['thickness'] if 'thickness' in kwargs else 0   

#     # Stroke style
#     self.linestyle = kwargs['linestyle'] if 'linestyle' in kwargs else None

#   def convert(self, anim,  name):
#     """
#     Conversion to ``QGraphicsItem``

#     For internal use only.

#     Attributes:
#       anim (:class:`Animation2d`): Animation
#     """

#     self.anim = anim
#     self.name = name

#     # --- Definition

#     match self.type:

#       case 'group':

#         self.QitemRef = QGraphicsItemGroup()

#       case 'crew':

#         self.QitemRef = Crew(self)
          
#       case 'text':

#         self.QitemRef = QGraphicsTextItem()
#         self.QitemRef.setHtml(self.string)
#         self.QitemRef.setFont((QFont(self.fontname, self.fontsize)))

#         bb = self.QitemRef.boundingRect()
#         if self.center['horizontal']:
#           self.position[0] -= bb.width()/2/anim.factor
#         if self.center['vertical']:
#           self.position[1] += bb.height()/2/anim.factor

#       case 'line':

#         self.QitemRef = QGraphicsLineItem()
#         self.setPoints()

#       case 'arrow':

#         self.QitemRef = QGraphicsItemGroup()

#         # Arrow line
#         self.Qitems.append(QGraphicsLineItem(0,0,0,0))

#         # Arrowhead
#         match self.arrow['shape']:

#           case 'dart':
#             head = [QPointF(0,0),
#               QPointF(-self.arrow['size']*anim.factor*3/2, self.arrow['size']*anim.factor/2),
#               QPointF(-self.arrow['size']*anim.factor, 0),
#               QPointF(-self.arrow['size']*anim.factor*3/2, -self.arrow['size']*anim.factor/2),
#               QPointF(0,0)]
#             self.Qitems.append(QGraphicsPolygonItem(QPolygonF(head)))

#           case 'disk':
#             self.Qitems.append(QGraphicsEllipseItem(
#               -self.arrow['size']*anim.factor,
#               self.arrow['size']/2*anim.factor,
#               self.arrow['size']*anim.factor,
#               -self.arrow['size']*anim.factor))

#         self.setPoints()
        
#       case 'circle':

#         self.QitemRef = QGraphicsEllipseItem(
#           -self.radius*anim.factor,
#           self.radius*anim.factor,
#           2*self.radius*anim.factor,
#           -2*self.radius*anim.factor)
        
#       case 'polygon':

#         self.QitemRef = QGraphicsPolygonItem(QPolygonF([]))
#         self.setPoints()

#       case 'rectangle':

#         self.QitemRef = QGraphicsRectItem(0,0,
#           self.width*anim.factor,
#           -self.height*anim.factor)

#     # --- Position

#     if self.parent is None:
#       self.QitemRef.setPos(
#         (self.position[0]-anim.sceneLimits['x'][0])*anim.factor, 
#         -(self.position[1]-anim.sceneLimits['y'][0])*anim.factor)
#     else:
#       self.QitemRef.setPos(
#         self.position[0]*anim.factor, 
#         -self.position[1]*anim.factor)

#     if self.movable:
#       self.QitemRef.setFlag(QGraphicsItem.ItemIsMovable, True)
#       self.QitemRef.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
#       self.QitemRef.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

#     # Rotation
#     if self.type not in ['arrow']:
#       self.rotate(self.rotation)

#     # --- Parent

#     if self.parent is not None:
#       self.QitemRef.setParentItem(anim.elm[self.parent].QitemRef)

#     if hasattr(self, 'Qitems'):
#       for item in self.Qitems:
#         item.setParentItem(self.QitemRef)

#     # --- Stack order

#     if self.belowParent:
#       self.QitemRef.setFlags(self.QitemRef.flags() | QGraphicsItem.ItemStacksbelowParent)

#     if self.zvalue is not None:
#       self.QitemRef.setZValue(self.zvalue)

#     # --- Style

#     match self.type:

#       case 'text':

#         self.QitemRef.setDefaultTextColor(QColor(self.color['fill']))

#       case 'line' | 'path' | 'polygon' | 'circle' | 'ellipse' | 'rectangle':
      
#         # Fill
#         if self.color['fill'] is not None:
#           self.QitemRef.setBrush(QBrush(QColor(self.color['fill'])))

#         # Stroke
#         self.QitemRef.setPen(self.strokePen())

#       case 'arrow':

#         strokePen = self.strokePen()

#         # Line stroke
#         self.Qitems[0].setPen(strokePen)

#         # Arrowhead
#         self.Qitems[1].setPen(strokePen)
#         self.Qitems[1].setBrush(QBrush(QColor(self.color['stroke'])))

#   def convertPoints(self, points):
#     """
#     Element position and relative points positions 
    
#     For path-style elements (``line``, ``arrow`` and ``polygon``), it sets
#     the element's position to the first point's absolute position in the 
#     scene (self.position) and the relative position of all the points 
#     (self.points). The first point in self.points is thus always [0,0].

#     For internal use only.

#     args:
#       points ([[float,float]]): Positions of the points of ``line``, 
#         ``arrow`` or ``polygon`` elements (absolute, scene units).
#     """

#     self.position = [points[0][0],points[0][1]]
#     self.points = [[p[0]-points[0][0], p[1]-points[0][1]] for p in points]

#   def strokePen(self):
#     """
#     Define stroke pen for compatible items

#     For internal use only.

#     Returns:
#       A QPen defining the stroke style and color of the item based on the 
#       self.linestyle and self.color properties.    
#     """

#     Pen = QPen()

#     # Stroke color
#     if self.color['stroke'] is not None:
#       Pen.setColor(QColor(self.color['stroke']))
#       Pen.setWidth(self.thickness)

#     # Stroke style
#     if self.linestyle is not None:
      
#       match self.linestyle:
#         case 'dash' | '--':
#           Pen.setDashPattern([3,6])
#         case 'dot' | ':' | '..':
#           Pen.setStyle(Qt.DotLine)
#         case 'dashdot' | '-.':
#           Pen.setDashPattern([3,3,1,3])

#     return Pen

#   def rotate(self, angle):
#     """
#     Relative rotation

#     Rotates the element relatively to its current orientation.
    
#     Attributes:
#       angle (float): Orientational increment (rad)
#     """

#     self.QitemRef.setRotation(-angle*180/np.pi)

#   def setPosition(self, x=None, y=None, z=None):
#     """
#     Absolute positionning

#     Places the element's referenceitem to an absolute position.
    
#     Attributes:
#       x (float): :math:`x`-coordinate of the new position
#       y (float): :math:`y`-coordinate of the new position
#       z (float): A complex number :math:`z = x+jy`. Specifying ``z``
#         overrides the ``x`` and ``y`` arguments.
#     """

#     # Convert from complex coordinates
#     if z is not None:
#       x = np.real(z)
#       y = np.imag(z)

#     self.QitemRef.setPos((x-self.anim.sceneLimits['x'][0])*self.anim.factor,
#       -(y-self.anim.sceneLimits['y'][0])*self.anim.factor)

#   def setPoints(self, points=None):
#     """
#     Set the points of ``line``, ``arrow`` or ``polygon`` elements

#     Use this function to update the points of ``line``, ``arrow`` 
#     or ``polygon`` elements.

#     args:
#       points ([[float,float]]): Positions of the points of ``line``, 
#         ``arrow`` or ``polygon`` elements (absolute, scene units). If 
#         set as ``None`` (default) then ``self.point`` is used.
#     """

#     if points is None:
#       points = self.points

#     self.position = [points[0][0], points[0][1]]
#     self.points = [[p[0]-self.position[0], p[1]-self.position[1]] for p in points]

#     match self.type:

#       case 'line':

#         self.QitemRef = QGraphicsLineItem(0,0,
#           self.points[1][0]*self.anim.factor,
#           -self.points[1][1]*self.anim.factor)

#       case 'arrow':

#         # Remove previous rotation
#         self.QitemRef.setRotation(self.rotation*180/np.pi)

#         z = self.points[1][0] + 1j*self.points[1][1]
        
#         # Group
#         self.QitemRef.setPos(self.position[0]*self.anim.factor, 
#           -self.position[1]*self.anim.factor)

#         # Arrow line
#         self.Qitems[0].setLine(0,0,np.abs(z)*self.anim.factor, 0)

#         # Arrow head
#         self.Qitems[1].setPos(np.abs(z)*self.arrow['locus']*self.anim.factor,0)

#         # Rotation
#         self.rotation = np.angle(z)
#         self.QitemRef.setRotation(-self.rotation*180/np.pi)

#       case 'polygon':
        
#         poly = []
#         for p in self.points:
#           poly.append(QPointF(p[0]*self.anim.factor, -p[1]*self.anim.factor))

#         self.QitemRef.setPolygon(QPolygonF(poly))

class item():
  """
  Item of the animation (generic class)

  Items are the elements displayed in the :py:attr:`Animation2d.Qscene`. 
  This class provides a common constructor, conversions of positions
  to scene coordinates and styling of ``QAbstractGraphicsShapeItem`` 
  children.
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

      movable (bool): If True, the element will be draggable. (default: ``False``)

      clickable (bool): *TO DO*
    """  

    # Call the other item's constructor, if any
    super().__init__()

    # Parent animation
    self.animation = animation

    # Assign name
    self.name = name

    # Parent
    self.parent = kwargs['parent'] if 'parent' in kwargs else None

    # Stack order
    if 'zvalue' in kwargs:
      self.setZValue(kwargs['zvalue'])
    
    # Position
    self.position = kwargs['position'] if 'position' in kwargs else [0,0]

    # -- Actions

    # Movable
    if 'movable' in kwargs and kwargs['movable']:
      self.setFlag(QGraphicsItem.ItemIsMovable, True)
      self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
      self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    self.clickable = kwargs['clickable'] if 'clickable' in kwargs else False

  def x2scene(self, x):
    return (x-self.animation.sceneLimits['x'][0])*self.animation.factor

  def y2scene(self, y):
    return (self.animation.sceneLimits['y'][0]-y)*self.animation.factor

  def xy2scene(self, xy):
    return self.x2scene(xy[0]), self.y2scene(xy[1])

  def d2scene(self, x):
    return x*self.animation.factor

  def a2scene(self, a):
    return a*180/np.pi

  def itemChange(self, change, value):
    
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

  def setStyle(self):

    if isinstance(self, QAbstractGraphicsShapeItem):

      # --- Fill

      if self.color['fill'] is not None:
        self.setBrush(QBrush(QColor(self.color['fill'])))

      # --- Stroke

      Pen = QPen()

      #  Color
      if self.color['fill'] is not None:
        Pen.setColor(QColor(self.color['stroke']))

      # Thickness
      Pen.setWidth(self.thickness)

      # Style
      match self.linestyle:
        case 'dash' | '--': Pen.setDashPattern([3,6])
        case 'dot' | ':' | '..': Pen.setStyle(Qt.DotLine)
        case 'dashdot' | '-.': Pen.setDashPattern([3,3,1,3])
      
      self.setPen(Pen)

class ellipse(item, QGraphicsEllipseItem):
  """
  Ellipse item

  
  Attributes:
    Qitem (QGraphicsEllipseItem): The underlying ``QGraphicsEllipseItem`` belonging to
      the ``QGraphicsScene``.
  """

  def __init__(self, animation, name, **kwargs):
    """
    Ellipse item constructor

    Defines an ``ellipse`` item, which inherits both from ``QGraphicsEllipseItem`` and
    :class:`item`.

    Args:

      name (str): The item's identifier, which should be unique. It is used as a
        reference by :class:`Animation2d`. This is the only mandatory argument.

      parent (*QGraphicsItem*): The parent ``QGraphicsItem`` in the ``QGraphicsScene``.
        Default is ``None``, which means the parent is the ``QGraphicsScene`` itself.

      belowParent (bool): Determine if the element should be placed above
        the parent (``False``, default) or below (``True``).

      zvalue (float): Z-value (stack order) of the item.

      rotation (float): Rotation of the item (rad)

      position ([float,float]): Position of the ``group``, ``text``, 
        ``circle``, and ``rectangle`` elements (scene units).

      points ([[float,float]]): Positions of the points of ``line``, 
        ``arrow`` or ``polygon`` elements (scene units).
                
      radius (float): Radius of the circle (for ``circle`` only).
      
      width (float): Width of the ``rectangle``.

      height (float): Height of the ``rectangle``.

      thickness (float): Stroke thickness (pix). For ``line``, ``circle``, 
        ``ellipse``, ``rectangle`` or ``polygon`` elements. (Default: 0)

      locus (float): Position of the tip of arrowhead on the normalized 
        curvilinear coordinates of the ``arrow`` element. This value should 
        be between 0 and 1 (default: 1).

      shape (str): Shape of the arrowhead of ``arrow`` elements. Can be
        ``dart`` (default) or ``disk``.

      size (float): Size of the arrowhead of ``arrow`` elements, in scene 
        units. (default: 0.02)

      string (str): String of a ``text`` element. Rich HTML text is supported.

      fontname (str): Font of a ``text`` element. Default: ``Arial``

      fontsize (int): Default font size of a ``text`` element, corresponding to 
        the pointSize property of ``QFont``. Default value: 10

      center ((bool,bool)): Center a ``text`` element horizontally and/or
        vertically. Default is (``False``, ``False``).

      color (*color*): Color for ``text``, ``line`` or ``arrow`` elements. 
        Colors can be whatever input of ``QColor`` (*e.g*: ``darkCyan``, ``#ff112233`` or 
        (255, 0, 0, 127)).

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
    
    # --- Geometry

    if 'major' not in kwargs or 'minor' not in kwargs:
      raise AttributeError("'major' and 'minor' must be specified for ellipse items.")
    else:
      self.major = kwargs['major']
      self.minor = kwargs['minor']

    self.setGeometry()

    # --- Styling

    # Colors
    self.color = {'fill': kwargs['colors'][0] if 'colors' in kwargs else 'gray',
      'stroke': kwargs['colors'][1] if 'colors' in kwargs else 'white'}
    
    # Stroke style
    self.linestyle = kwargs['linestyle'] if 'linestyle' in kwargs else None

    # Stroke thickness
    self.thickness = kwargs['thickness'] if 'thickness' in kwargs else 0   

    self.setStyle()

  def setGeometry(self, position=None, major=None, minor=None):
    """
    Set ellipse geometry
    """

    if position is not None: self.position = position
    if major is not None: self.major = major
    if minor is not None: self.minor = minor

    # Conversion
    x, y = self.xy2scene(self.position)
    M = self.d2scene(self.major)
    m = self.d2scene(self.minor)

    # Modification
    self.setRect(QRectF(x-M/2, y-m/2, M, m))

# === Animation ============================================================

class Animation2d():
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

    sceneLimits ({'x', 'y', 'width', 'height'}): Limits of the scene.

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

  def __init__(self, parent=None, size=None, sceneLimits=None, disp_boundaries=True, disp_time=False, dt=None):
    """
    Animation constructor

    Defines all the attributes of the animation, especially the ``QGraphicsScene``
    and ``QGraphicsView`` necessary for rendering.

    Args:

      parent (*Qwidget* or :class:`Window`): Parent container. It can be a ``QWidget``
        or a :class:`Window` object. If not set, a new :class:`Window` object is 
        created and assigned as a parent.

      size (float): Height of the ``QGraphicsView``.

      sceneLimits ([[float,float],[float,float]]): Limits of the scene to display.
        The first element sets the *x*-limits and the second the *y*-limits. 
        Default is [[0,1],[0,1]].

      disp_boundaries (bool): If true, a thin grey rectanle is overlaid to 
        indicate the boundaries.

      disp_time (bool): If true, the animation time is overlaid to the animation.

      dt (float): Animation time increment (s) between two updates. Default: 0.04.
    """

     # --- Parent

    self.parent = parent
    if self.parent is None:
      self.parent = Window(animation=self)

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
    self.sceneLimits = {'x':[0,1], 'y':[0,1], 'width':None, 'height':None}
    if sceneLimits is not None:
      self.sceneLimits['x'] = list(sceneLimits[0])
      self.sceneLimits['y'] = list(sceneLimits[1])
    self.sceneLimits['width'] = self.sceneLimits['x'][1]-self.sceneLimits['x'][0]
    self.sceneLimits['height'] = self.sceneLimits['y'][1]-self.sceneLimits['y'][0]

    # Scale factor
    self.factor = self.size/self.sceneLimits['height']

    # --- Scene & view

    # Scene
    self.Qscene = QGraphicsScene()
    self.Qview = QGraphicsView()
    self.Qview.setScene(self.Qscene)
    self.Qview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.Qview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    self.item = defaultdict()

    # --- Display

    # Dark background
    self.Qview.setBackgroundBrush(Qt.black)
    pal = self.Qview.palette()
    pal.setColor(QPalette.Window, Qt.black)
    self.Qview.setPalette(pal)

    # Antialiasing
    self.Qview.setRenderHints(QPainter.Antialiasing)

    # --- Animation
  
    self.qtimer = QTimer()
    self.qtimer.timeout.connect(self.update)
    self.timer = QElapsedTimer()
  
    
    # Scene boundaries
    if self.disp_boundaries:
      self.boundaries = QGraphicsRectItem(0,0,
        self.factor*self.sceneLimits['width'],
        -self.factor*self.sceneLimits['height'])
      self.boundaries.setPen(QPen(Qt.lightGray, 0)) 
      self.Qscene.addItem((self.boundaries))

    # Time display
    if self.disp_time:
      self.timeDisp = self.Qscene.addText("---")
      self.timeDisp.setDefaultTextColor(QColor('white'))
      self.timeDisp.setPos(0, -self.timeHeight-self.factor*self.sceneLimits['height'])

  def add(self, type, name, **kwargs):
    """
    Add an item to the scene.

    args:
      item (:class:`item` *subclass*): The item to add.
    """

    # Create item
    self.item[name] = type(self, name, **kwargs)

    # Add item to the scene
    if self.item[name].parent is None:
        self.Qscene.addItem(self.item[name])

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

class Window():
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

    # Window title
    self.animation.Qview.setWindowTitle(self.title)

    # --- Shortcuts

    self.shortcut = defaultdict()

    # Quit
    self.shortcut['esc'] = QShortcut(QKeySequence('Esc'), self.animation.Qview)
    self.shortcut['esc'].activated.connect(self.app.quit)

    # --- Initialization

    # Window size
    self.animation.Qview.resize(
      int(self.animation.factor*self.animation.sceneLimits['width']+2*self.animation.margin), 
      int(self.animation.factor*self.animation.sceneLimits['height']+2*self.animation.margin+self.animation.timeHeight))

    self.animation.Qview.show()
    self.animation.startAnimation()
    self.app.exec()

  def close(self):
    self.app.quit()