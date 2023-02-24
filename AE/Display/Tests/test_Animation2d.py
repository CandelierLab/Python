from AE.Display.Animation2d import *

# --- 2D Animation ---------------------------------------------------------

class Anim(Animation2d):

  def __init__(self):

    super().__init__(disp_time=True)

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
    #   points = [[0.9,0.7],[0.85,0.8],[0.85,0.1]],
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


    # Allow backward
    self.allow_backward = True
    self.allow_negative_time = False

    # Add listener
    self.event.connect(receive)

    # Display animation
    self.show()

  def update(self):
    
    # Update timer display
    super().update()

    # Update position
    x = self.x0 + self.R*np.cos(self.step*self.dt)
    y = self.y0 + self.R*np.sin(self.step*self.dt)
    self.item['C'].position = [x, y]

# --- Event listener -------------------------------------------------------

def receive(event):

    match event['type']:
      case 'update':
        pass
      case _:
        print(event['type'])

# --- Main -----------------------------------------------------------------

A = Anim()
