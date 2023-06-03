import os

from AE.Display.Animation.Window import *
from AE.Display.Animation.Animation_2d import *

os.system('clear')

# --- 2D Animation ---------------------------------------------------------

class Anim(Animation_2d):

  def __init__(self):

    super().__init__()

    self.padding=0.01

    self.x0 = 0.5
    self.y0 = 0.5
    self.R = 0.25
    self.r = 0.01

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

    # self.add(group, 'G',
    #   position = [0.5,0.5],
    #   orientation = 0.5,
    #   draggable = True
    # )

    # self.add(ellipse, 'E1',
    #   parent = 'G',
    #   position = [0,0],
    #   major = 0.2,
    #   minor = 0.1,
    #   colors = (None, 'white'),
    #   thickness = 2,
    #   linestyle = '--',
    # )

    # self.add(text, 'T',
    #   parent = 'G',
    #   position = [0,0],
    #   string = 'a&#946;c',
    #   color = 'white',
    #   fontsize = 12,
    #   center = True
    # )

    # self.add(line, 'L',
    #   parent = 'E0',
    #   points = [[0,0],[0.2,0.15]],
    #   color = 'yellow',
    #   thickness = 2,
    #   draggable = True
    # )

    # self.add(polygon, 'P',
    #   points = [[0.5,0.5],[0.5,0.75],[0.75,0.5]],
    #   colors = ['green','red'],
    #   thickness = 3,
    #   draggable = True
    # )

    # self.add(path, 'P',
    #   points = [[0.85,0.65],[0.80,0.80],[0.80,0.15]],
    #   colors = ['yellow','white'],
    #   thickness = 3,
    #   draggable = True
    # )

    # self.add(arrow, 'A', 
    #   points = [[0.1,0.1],[0.2,0.15]],
    #   color = 'darkcyan',
    #   thickness = 5,
    #   draggable = True
    # )

    # self.composite['A'].points = [[0.1,0.1],[0.3,0.35]]
    # self.composite['A'].locus = 0.5
    # self.composite['A'].shape = 'disk'

  def update(self, t):
    
    # Update timer display
    super().update(t)

    # Update position
    x = self.x0 + self.R*np.cos(t.time)
    y = self.y0 + self.R*np.sin(t.time)
    self.item['C'].position = [x, y]

# --- Main -----------------------------------------------------------------

W = Window('Simple animation')
W.add(Anim())

# Allow backward animation
W.allow_backward = True
W.allow_negative_time = False

# W.movieFile = '~/test.mp4'

W.show()