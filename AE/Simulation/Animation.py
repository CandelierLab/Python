import numpy as np
from collections import defaultdict

from PyQt5.QtCore import Qt, QTimer, QElapsedTimer, QPointF
from PyQt5.QtGui import QKeySequence, QPalette, QColor, QPainter, QPen, QBrush, QPolygonF
from PyQt5.QtWidgets import QApplication, QShortcut, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsItemGroup, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsRectItem

# === ELEMENTS =============================================================

class element():

  def __init__(self, type, **kwargs):
    
    # Common properties
    self.type = type
    self.Qelm = None
    self.rotation = kwargs['rotation'] if 'rotation' in kwargs else 0
    self.parent = kwargs['parent'] if 'parent' in kwargs else None
    self.behindParent = kwargs['behindParent'] if 'behindParent' in kwargs else False
    self.zvalue = kwargs['zvalue'] if 'zvalue' in kwargs else None

    # Element-dependent properties
    match type:

      case 'line':
        self.position = kwargs['position'] if 'position' in kwargs else (0,0)
        self.width = kwargs['width'] if 'width' in kwargs else 0
        self.height = kwargs['height'] if 'height' in kwargs else 0
        
      case 'circle':
        self.position = kwargs['position'] if 'position' in kwargs else (0,0)
        self.radius = kwargs['radius'] if 'radius' in kwargs else 0

      case 'polygon':
        self.position = kwargs['position'] if 'position' in kwargs else (0,0)
        self.points = kwargs['points'] if 'points' in kwargs else None

      case 'rectangle':
        self.position = kwargs['position'] if 'position' in kwargs else (0,0)
        self.width = kwargs['width'] if 'width' in kwargs else 0
        self.height = kwargs['height'] if 'height' in kwargs else 0
        
    # --- Style

    # Stroke thickness
    self.thickness = kwargs['thickness'] if 'thickness' in kwargs else 0

    # Colors
    self.color = {}
    self.color['fill'] = kwargs['color'][0] if 'color' in kwargs else 'gray'
    self.color['stroke'] = kwargs['color'][1] if 'color' in kwargs else 'white'

  def convert(self, view):

    # --- Definition

    match self.type:

      case 'group':

        self.Qelm = QGraphicsItemGroup()

      case 'line':

        self.Qelm = QGraphicsLineItem(0,0,
          self.width*view.factor,
          -self.height*view.factor)

      case 'circle':

        self.Qelm = QGraphicsEllipseItem(
          -self.radius*view.factor,
          self.radius*view.factor,
          2*self.radius*view.factor,
          -2*self.radius*view.factor)

      case 'polygon':

        poly = []
        for p in self.points:
          poly.append(QPointF(p[0]*view.factor, -p[1]*view.factor))

        self.Qelm = QGraphicsPolygonItem(QPolygonF(poly))
        
      case 'rectangle':

        self.Qelm = QGraphicsRectItem(0,0,
          self.width*view.factor,
          -self.height*view.factor)


    # --- Position

    if type != 'group':
      if self.parent is None:
        self.Qelm.setPos(
          (self.position[0]-view.sceneLimits['x'][0])*view.factor, 
          -(self.position[1]-view.sceneLimits['y'][0])*view.factor)
      else:
        self.Qelm.setPos(
          self.position[0]*view.factor, 
          -self.position[1]*view.factor)

    # Rotation
    self.rotate(self.rotation)

    # --- Parent

    if self.parent is not None:
      self.Qelm.setParentItem(view.elm[self.parent].Qelm)

    # --- Stack order

    if self.behindParent:
      self.Qelm.setFlags(self.Qelm.flags() | QGraphicsItem.ItemStacksBehindParent)

    if self.zvalue is not None:
      self.Qelm.setZValue(self.zvalue)

    # --- Colors

    if self.type!='line' and self.color['fill'] is not None:
      self.Qelm.setBrush(QBrush(QColor(self.color['fill'])))

    if self.color['stroke'] is not None:
      self.Qelm.setPen(QPen(QColor(self.color['stroke']), self.thickness))

  def rotate(self, angle):
    self.Qelm.setRotation(-angle*180/np.pi)

# === GRAPHICS VIEW ========================================================

class AnimatedView(QGraphicsView):

  def __init__(self, window=None):

    # Parent constructor
    super().__init__()
    
    # Window
    self.window = window

    # --- Shortcuts

    self.shortcut = defaultdict()

    # Quit
    self.shortcut['esc'] = QShortcut(QKeySequence('Esc'), self)
    self.shortcut['esc'].activated.connect(QApplication.instance().quit)

    # -- Settings

    # self.scale(1,-1)

    # Sizes
    self.sceneLimits = {'x':(0,1), 'y':(0,1), 'width':None, 'height':None}
    self.margin = 25
    self.timeHeight = 30

    # --- Scene

    # Scene
    self.scene = QGraphicsScene()
    self.setScene(self.scene)

    self.elm = defaultdict()

    # --- Display

    # Dark background
    self.setBackgroundBrush(Qt.black)
    pal = self.palette()
    pal.setColor(QPalette.Window, Qt.black)
    self.setPalette(pal)

    # Antialiasing
    self.setRenderHints(QPainter.Antialiasing)

    # --- Animation
  
    self.qtimer = QTimer()
    if self.window is None:
      self.qtimer.timeout.connect(self.update)
    else:
      self.qtimer.timeout.connect(self.window.update)

    self.timer = QElapsedTimer()
  
  def init(self, size=None):

    # Scene width and height
    self.sceneLimits['width'] = self.sceneLimits['x'][1]-self.sceneLimits['x'][0]
    self.sceneLimits['height'] = self.sceneLimits['y'][1]-self.sceneLimits['y'][0]

    # --- Scale factor and margin

    if size is None:
      self.factor = QApplication.desktop().screenGeometry().height()/self.sceneLimits['height']*0.6

    else:
      self.factor = size/self.sceneLimits['height']

    # Scene boundaries
    self.boundaries = QGraphicsRectItem(0,0,
      self.factor*self.sceneLimits['width'],
      -self.factor*self.sceneLimits['height'])
    self.boundaries.setPen(QPen(Qt.lightGray, 0)) 
    self.scene.addItem((self.boundaries))

    # Time display
    self.timeDisp = self.scene.addText("Hello World")
    self.timeDisp.setDefaultTextColor(QColor('white'))
    self.timeDisp.setPos(0, -self.timeHeight-self.factor*self.sceneLimits['height'])

    # Elements
    for k,elm in self.elm.items():
      elm.convert(self)
      if elm.parent is None:
        self.scene.addItem(elm.Qelm)

  def startAnimation(self):
    self.qtimer.setInterval(int(1000/self.window.fps))
    self.qtimer.start()
    self.timer.start()

  def update(self):

    # Update timer display
    t = self.timer.elapsed()
    self.timeDisp.setPlainText('{:06.02f} sec'.format(t/1000))
    

# === WINDOW ===============================================================

class Window():

  def __init__(self):

    # Qapplication
    self.app = QApplication([])

    # QgraphicsView
    self.view = AnimatedView(window=self)

    # Misc settings
    self.fps = 25
    
  def show(self, size=None):

    # Initialize view
    self.view.init(size=size)

    # Window size
    self.view.resize(
      int(self.view.factor*self.view.sceneLimits['width']+2*self.view.margin), 
      int(self.view.factor*self.view.sceneLimits['height']+2*self.view.margin+self.view.timeHeight))

    self.view.show()
    self.view.startAnimation()
    self.app.exec()

  def update(self):

    # Update timer display
    self.view.update()

  def close(self):
    self.app.quit()