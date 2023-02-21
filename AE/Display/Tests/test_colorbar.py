from AE.Display.Animation2d import *

# --- 2D Animation ---------------------------------------------------------

class Anim(Animation2d):

  def __init__(self):

    super().__init__(disp_time=True)

    self.add(colorbar, 'Cb',
      position = [0, 0.5],
      major = 0.005,
      minor = 0.005,
      colors = ('white', None),
    )

    

    # Display animation
    self.show()

# --- Main -----------------------------------------------------------------

A = Anim()
