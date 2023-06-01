import os

from AE.Display.Animation.Window import *
from AE.Display.Animation.Animation_2d import *

os.system('clear')

# === First Animation ======================================================

class Anim_1(Animation_2d):

  def __init__(self):

    super().__init__(boundaries=[[-0.5, 1.5],[-0.5, 1.5]])

    self.padding = 0.01

    self.x0 = 0.5
    self.y0 = 0.5
    self.R = 0.25
    self.r = 0.02

    self.add(ellipse, 'E0',
      position = [self.x0, self.y0],
      major = 0.005,
      minor = 0.005,
      colors = ('white', None),
    )

    self.add(circle, 'C0',
      position = [self.x0, self.y0],
      radius = self.R,
      colors = (None, 'grey'),
      thickness = 2,
      linestyle = '--'
    )

    self.add(circle, 'C',
      position = [self.x0 + self.R, self.y0],
      radius = self.r,
      colors = ('red', None),
    )

    # Allow backward
    self.allow_backward = True
    self.allow_negative_time = False

  def update(self, t):
    
    # Update timer display
    super().update(t)

    # Update position
    x = self.x0 + self.R*np.cos(t.time)
    y = self.y0 + self.R*np.sin(t.time)
    self.item['C'].position = [x, y]

# === Second Animation ======================================================

class Anim_2(Animation_2d):

  def __init__(self):

    super().__init__(boundaries=[[-0.5, 1.5],[-0.5, 1.5]])

    self.padding = 0.01

    self.x0 = 0.5
    self.y0 = 0.5
    self.R = 0.25
    self.r = 0.02

    self.add(ellipse, 'E0',
      position = [self.x0, self.y0],
      major = 0.005,
      minor = 0.005,
      colors = ('white', None),
    )

    self.add(circle, 'C0',
      position = [self.x0, self.y0],
      radius = self.R,
      colors = (None, 'grey'),
      thickness = 2,
      linestyle = '--'
    )

    self.add(circle, 'C',
      position = [self.x0 + self.R, self.y0],
      radius = self.r,
      colors = ('green', None),
    )

    # Allow backward
    self.allow_backward = True
    self.allow_negative_time = False

  def update(self, t):
    
    # Update timer display
    super().update(t)

    # Update position
    x = self.x0 + self.R*np.cos(t.time)
    y = self.y0 + self.R*np.sin(t.time)
    self.item['C'].position = [x, y]

# === Main =================================================================

W = Window()

W.add(Anim_1(), 0, 1)
W.add(Anim_2(), 0, 2)

# W.events.connect(W.receive)

W.show()
