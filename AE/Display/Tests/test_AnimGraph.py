from AE.Display.Animation2d import * 
from AE.Display.GUI.AnimGraph import AnimGraph

# --- Simple 2D Animation --------------------------------------------------

class Anim(Animation2d):

  def __init__(self):

    super().__init__(disp_time=True)

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

    self.show()

  def update(self):
    
    # Update timer display
      super().update()

      # Time (sec)
      t = self.timer.elapsed()/1000

      # Update position
      x = self.x0 + self.R*np.cos(t)
      y = self.y0 + self.R*np.sin(t)
      self.item['C'].position = [x, y]

# --- AnimGraph Viewer------------------------------------------------------

class GUI(AnimGraph):

  def __init__(self, animation):

    # Parent's constructor
    super().__init__(animation)




# --- Start ----------------------------------------------------------------

GUI(Anim)


# Anim()
# Anim.start()
