import os

import imageio
  
try:
  import imageio
except:
  # The try-except structure is for pdoc, which may have trouble to find imageio
  pass

from AE.Display.time import *
from AE.Display.Animation.Information import *
from AE.Display.Animation.Animation_2d import *

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut, QGridLayout

class Window(QWidget):
  """
  Window for animations.

  It is a subclass of Qwidget, which creates a window containing:
  * an information widget
  * one or several animation widgets.
  """

  # Generic event signal
  events = pyqtSignal(dict)
  ''' A pyqtSignal object to manage internal events to propagate to the information and animation(s) panels. Emitted events have a `type` entry (`str`) which can be:
  * `'show'`: to signal that the window is shown.
  * `'update'`: to signal that time has changed and that animations should be updated. This signal also has a `time` entry to specify the current time in the form of a `AE.Display.time` object.
  * `'play'`: to signal that the animation is now playing.
  * `'pause'`: to signal that the animation is now in pause.
  * `'stop'`: to signal that the window is closing.
  '''

  # ========================================================================
  def __init__(self, title='Animation', display_information=True, autoplay=True, dt=None, style='dark'):
    """
    Window constructor.
   
    The dark style is automatically applied if the corresponding stylesheet is found.

    Args:
      `title` (`str`): Window title. Default: `'Animation'`.
      `display_information` (`bool`): Determines if the extra information have to be displayed. Default: `True`.
      `autoplay` (`bool`): Indicating if autoplay is on or off. Default: `True`.
      `dt` (`float`): time increment between two frames (seconds). Default: `None`.
      `style` (`str`): The window style name. It can be `'bright'` or `'dark'` (default).
    """

    # Qapplication
    self.app = QApplication([])
    '''The underlying `QApplication`.'''

    # Attributes
    self.title = title
    '''The window title (`str`).'''
    
    # Call widget parent's constructor (otherwise no signal can be caught)
    super().__init__()

    # Misc private properties
    self._nAnim = 0
    self._movieCounter = 0

    # --- Main Layout

    self.layout = QGridLayout()
    '''The underlying `QGridLayout` (main layout).'''

    self.setLayout(self.layout)

    # --- Information

    self.information = None
    '''The object controlling the extra information displayed. If `display_information` is set to `False` then it is set to `None` and no information if displayed during the animation. Otherwise it is an `AE.Display.Animation.Information` object (subclass of `AE.Display.Animation.Animation_2d`) displayed on the left side of the window.
    '''

    if display_information:

      self.information = Information()
    
      self.layout.addWidget(self.information.view, 0, 0)
      self.events.connect(self.information.receive)
      self.information.updated.connect(self.capture)
      self._nAnim += 1

    
    # --- Default size

    self.height = None
    '''Window height (pixels). If not set, it is temporarily set to `None` and transformed in `show` to 0.6 times the screen height.'''

    self.width = None
    '''Window width (pixels). If not set, it is temporarily set to `None` and later converted in `show` into a proper value based on `height`. 
    
    > It is not recommended to specify `width` but not `height`. In this case the height is computed with the default procedure and the width is fixed, which may result in discrepencies from screen to screen.'''

    # --- Style

    self.style = style
    '''The window style. It is a `str` with values `'bright'` or `'dark'`(default).'''

    # Modified qdarkstyle
    if self.style is 'dark':
      with open(os.path.dirname(os.path.abspath(__file__))+'/Style/dark.css', 'r') as f:
        css = f.read()
        self.app.setStyleSheet(css)

    # --- Timing

    # Framerate
    self.fps = 25
    '''Refreshing animation rate (1/seconds).'''

    # Time
    self.step = 0
    '''Current animation step (`int`)'''

    self.dt = dt if dt is not None else 1/self.fps
    '''Time interval between two frames (seconds). if `dt`is None, it is automatically set to 1/`fps`.'''

    # Timer
    self.timer = QTimer()
    '''`QTimer` object controlling the animation timing.'''

    self.timer.timeout.connect(self.set_step)

    # Play
    self.autoplay = autoplay
    '''`bool` indicating if the animation should start automatically upon window creation. Default: `True`'''

    self.allow_backward = False
    '''`bool` indicating if backward animation is authorized. Default: `False`.'''

    self.allow_negative_time = False
    '''Boolean indicating if negative times are authorized. Only useful when `allow_backward` is `True`. Default: `False`.'''

    self.play_forward = True
    '''`bool` indicating the default time direction. Only useful when `allow_backward` is `True`. Default: `True`.'''

    # --- Output 

    # Movie
    self.movieFile = None
    '''Path to a movie to be created. By default it is `None` and no movie is created. If it is a `str` with a valid filename, the movie file is created when the window is displayed (in `show`). If the containing folder does not exist, it is readily created with `os.makedirs`.
    
    > &#9888; *Warning: If the movie already exists, it is erased without confirmation dialog.*'''

    self.movieWriter = None
    '''Internal `imageio` writer object for movie creation. Only useful when `movieFile`is not `None`.'''

    self.movieWidth = 1600     # Must be a multiple of 16
    '''Width of the movie (pixels). *It must be a multiple of 16*. Only useful when `movieFile`is not `None`.'''

    self.moviefps = 25
    '''Movie framerate (1/seconds). Default: 25. Only useful when `movieFile`is not `None`.'''

    self.keep_every = 1
    '''Defines the ratio of frames to keep. A value of 2 will skip one every 2 frames, resulting in a x2 speedup display. Only useful when `movieFile`is not `None`.'''
    
  # ========================================================================
  def add(self, panel, row=None, col=None):
    """ 
    Add a panel, which can be a `QLayout` or an `AE.Display.Animation.Animation_2d` object.

    Args:
      panel (*misc*): The panel to add
      row (`int`): The row where the panel should be inserted. Default: last row.
      col (`int`): The column where the panel should be inserted. Default: last column. 

    """

    # --- Default row / column

    if row is None:
      row = self.layout.rowCount()-1

    if col is None:
      col = self.layout.columnCount()

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
    This method performs many differents tasks, in this order:
    
    * Set the window title
    * Define the shortcuts
    * Create the window, and emit the `'show'` event
    * Resize the window. The height of the `QGraphicsView` widget, defining the height of the window (pixels) is set by the `height`property. If `height` is `None`, it is automatically replaced by 0.6 times the height of the screen. The width, if unset, is then calculated automatically.
    * Initialize the animation timer
    * Manage `autoplay`
    * If `moviefile` is defined, create the movie dir if necessary and the movie writer object. 
    * Run the `exec()` method of the Qt `app` (GUI loop).

    > *Note*: This method has to be called, otherwise the window is never created. All the parameters of the window and animations (`autoplay`, `movieFile`, etc.) have to be defined before `show` is called.
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
    self.events.emit({'type': 'show'})

    # --- Sizing

    # Default size
    if self.height is None:
      self.height = int(QApplication.desktop().screenGeometry().height()*0.6)

    if self.width is None:
      if self.information is None:
        self.width = int(self.height*(self._nAnim))
      else:
        self.width = int(self.height*(self._nAnim-0.75))

    # Set window size
    self.resize(self.width, self.height)

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
    '''
    Sets the current step and emits an update event.

    Args:
      `step` (`int`): The step to go to. If `None`, then the current step is incremented by 1 if `play_forward` is `True`, and decremented by 1 otherwise.
    '''

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
    '''
    Captures the current frame (for inserting in a movie). 

    Args:
      `force` (`bool`): If `True`, overrides the `keep_every` directive. Default: `False`.
    '''

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
  def play_pause(self):
    '''
    Method to toggle the animation play/pause status.

    An event of type `'play'` or `'pause'` is emited, depending on the new status.
    '''

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
    '''
    Increments the animation by one step.
    '''

    self.play_forward = True

    if not self.timer.isActive():
      self.set_step()

  # ========================================================================
  def decrement(self):
    '''
    Decrements the animation by one step.
    '''

    if self.allow_backward:

      self.play_forward = False

      if not self.timer.isActive():
        self.set_step()

  # ========================================================================
  def close(self):
    """
    Stops the animation timer and close the window.

    An event of type `'stop'` is emited.
    """

    # Stop the timer
    self.timer.stop()

    # Emit event
    self.events.emit({'type': 'stop'})

    # Movie
    if self.movieWriter is not None:
      self.movieWriter.close()

    self.app.quit()
