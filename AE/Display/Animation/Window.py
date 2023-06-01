import os
from AE.Display.Animation.Information import *
from AE.Display.Animation.Animation_2d import *

from PyQt5.QtGui import QKeySequence
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

  def __init__(self, title='Animation', display_information=True):
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

    # --- Style

    # Modified qdarkstyle
    with open(os.path.dirname(os.path.abspath(__file__))+'/Style/dark.css', 'r') as f:
      css = f.read()
      self.app.setStyleSheet(css)
    
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

    # --- Append widget or layout

    if isinstance(panel, Animation_2d):
      self.layout.addWidget(panel.view, row, col)
    else:
      self.layout.addLayout(panel, row, col)

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
    # self.shortcut['space'] = QShortcut(QKeySequence('Space'), self)
    # self.shortcut['space'].activated.connect(self.animation.play_pause)

    # Decrement
    # self.shortcut['previous'] = QShortcut(QKeySequence.MoveToPreviousChar, self)
    # self.shortcut['previous'].activated.connect(self.animation.decrement)

    # Increment
    # self.shortcut['next'] = QShortcut(QKeySequence.MoveToNextChar, self)
    # self.shortcut['next'].activated.connect(self.animation.increment)

    # --- Display animation ------------------------------------------------

    super().show()

    # if self.animation.autoplay:
    #   self.animation.play_pause()
    
    self.app.exec()

  def close(self):

    # self.animation.stop()
    self.app.quit()