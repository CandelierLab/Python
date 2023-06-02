import os

from AE.Display.time import *
from AE.Display.Animation.Information import *
from AE.Display.Animation.Animation_2d import *

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut, QGridLayout

class Window(QWidget):
  """
  Animation-specific window

  Creates a new window containing an animation.
  
  Attributes:
    title (str): Title of the window.
    app (``QApplication``): Underlying ``QApplication``.
    anim (:class:`Animation2d`): Animation to display.
  """

  # Generic event signal
  events = pyqtSignal(dict)

  # ========================================================================
  def __init__(self, title='Animation', display_information=True, dt=None):
    """
    Window constructor

    Defines the ``QApplication``, window title and animation to display.

    Args:
      title (str): Title of the window. Default is 'Animation'.
    """

    # Attributes
    self.title = title

    # Misc private properties
    self._nAnim = 0
    self._movieCounter = 0
    
    # Qapplication
    self.app = QApplication([])

    # Call widget parent's constructor
    # (otherwise no signal can be caught)
    super().__init__()

    # --- Main Layout

    self.layout = QGridLayout()
    self.setLayout(self.layout)

    # --- Information

    self.information = Information() if display_information else None

    if self.information is not None:
      self.layout.addWidget(self.information.view, 0, 0)
      self.events.connect(self.information.receive)
      self.information.updated.connect(self.capture)
      self._nAnim += 1

    # --- Style

    # Modified qdarkstyle
    with open(os.path.dirname(os.path.abspath(__file__))+'/Style/dark.css', 'r') as f:
      css = f.read()
      self.app.setStyleSheet(css)

    # --- Timing

    # Framerate
    self.fps = 25

    # Time
    self.step = 0
    self.dt = dt if dt is not None else 1/self.fps

    # Timer
    self.timer = QTimer()
    self.timer.timeout.connect(self.set_step)

    # Play
    self.autoplay = True
    self.allow_backward = False
    self.allow_negative_time = False

    self.play_forward = True

    # --- Output 

    # Movie
    self.movieFile = None
    self.movieWriter = None
    self.movieWidth = 1600     # Must be a multiple of 16
    self.moviefps = 25
    self.keep_every = 1
    
  # ========================================================================
  def add(self, panel, row=None, col=None):
    """ 
    Add a panel

    A panel can be a layout or an Animation2d object.
    """

    # --- Default row / column

    if row is None:
      pass
    if col is None:
      pass

    # --- Append animation or layout

    if isinstance(panel, Animation_2d):

      self.layout.addWidget(panel.view, row, col)
      self.events.connect(panel.receive)
      panel.updated.connect(self.capture)
      self._nAnim += 1

    else:

      self.layout.addLayout(panel, row, col)

  # ========================================================================
  def show(self):
    """
    Creates the animation window
    
    Create the window to display the animation, defines the shortcuts,
    initialize and start the animation.

    Args:
      size (float): Height of the ``QGraphicsView`` widget, defining the 
        height of the window.
    """

    # --- Settings ---------------------------------------------------------
    
    # Window title
    self.setWindowTitle(self.title)

    # --- Shortcuts

    self.shortcut = {}

    # Quit
    self.shortcut['esc'] = QShortcut(QKeySequence('Esc'), self)
    self.shortcut['esc'].activated.connect(self.close)

    # Play/pause
    self.shortcut['space'] = QShortcut(QKeySequence('Space'), self)
    self.shortcut['space'].activated.connect(self.play_pause)

    # Decrement
    self.shortcut['previous'] = QShortcut(QKeySequence.MoveToPreviousChar, self)
    self.shortcut['previous'].activated.connect(self.decrement)

    # Increment
    self.shortcut['next'] = QShortcut(QKeySequence.MoveToNextChar, self)
    self.shortcut['next'].activated.connect(self.increment)

    # --- Display animation ------------------------------------------------

    super().show()

    # --- Timing -----------------------------------------------------------

    # Timer settings
    self.timer.setInterval(int(1000*self.dt))

    # Autoplay
    if self.autoplay:
      self.play_pause()
    
    # --- Movie ------------------------------------------------------------

    if self.movieFile is not None:

      # Check directory
      dname = os.path.dirname(self.movieFile)
      if not os.path.isdir(dname):
        os.makedirs(dname)

      # Open video file
      self.movieWriter = imageio.get_writer(self.movieFile, fps=self.moviefps)

      # Capture first frame
      self.capture(force=True)

    self.app.exec()

 # ========================================================================
  def set_step(self, step=None):

    if step is None:
      self.step += 1 if self.play_forward else -1
    else:
      self.step = step

    # Check negative times
    if not self.allow_negative_time and self.step<0:
      self.step = 0

    # Emit event
    self.events.emit({'type': 'update', 'time': time(self.step, self.step*self.dt)})

  # ========================================================================
  def capture(self, force=False):

    if self.movieWriter is not None and not (self.step % self.keep_every):

      self._movieCounter += 1

      if force or self._movieCounter == self._nAnim:

        # Reset counter
        self._movieCounter = 0

        # Get image
        img = self.grab().toImage().scaledToWidth(self.movieWidth).convertToFormat(QImage.Format.Format_RGB888)

        # Create numpy array
        ptr = img.constBits()
        ptr.setsize(img.height()*img.width()*3)
        A = np.frombuffer(ptr, np.uint8).reshape((img.height(), img.width(), 3))

        # Add missing rows (to get a height multiple of 16)
        A = np.concatenate((A, np.zeros((16-img.height()%16, img.width(), 3), dtype=np.uint8)), 0)
        
        # Append array to movie
        self.movieWriter.append_data(A)

  # ========================================================================
  def play_pause(self, force=None):

    if self.timer.isActive():

      # Stop qtimer
      self.timer.stop()

      # Emit event
      self.events.emit({'type': 'pause'})

    else:

      # Start timer
      self.timer.start()
    
      # Emit event
      self.events.emit({'type': 'play'})

  # ========================================================================
  def increment(self):

    self.play_forward = True

    if not self.timer.isActive():
      self.set_step()

  # ========================================================================
  def decrement(self):

    if self.allow_backward:

      self.play_forward = False

      if not self.timer.isActive():
        self.set_step()

  # ========================================================================
  def close(self):
    """
    Stop the animation

    Stops the timer and close the window
    """

    # Stop the timer
    self.timer.stop()

    # Emit event
    self.events.emit({'type': 'stop'})

    # Movie
    if self.movieWriter is not None:
      self.movieWriter.close()

    self.app.quit()