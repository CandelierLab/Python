from AE.Display.Animation2d import *

# --- 2D Animation ---------------------------------------------------------

class Anim(Animation2d):

  def __init__(self):

    super().__init__(disp_time=True)

    # --- Colorbar

    self.colormap.range = [-1,1]

    self.add(colorbar, 'Cb',
      insight = True,
      height = 'fill',
      nticks = 5
    )

    # --- Animation

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
      colors = (None, None),
      thickness = 5
    )

    # Display animation
    self.show()

  def update(self):
    
    # Update timer display
    super().update()

    x_ = np.cos(self.step*self.dt)
    y_ = np.sin(self.step*self.dt)

    # Update position
    x = self.x0 + self.R*x_
    y = self.y0 + self.R*y_
    self.item['C'].position = [x, y]

    # Update color
    self.item['C'].colors = (self.colormap.qcolor(x_), self.colormap.qcolor(y_))


# --- Main -----------------------------------------------------------------

A = Anim()
