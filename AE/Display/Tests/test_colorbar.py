from AE.Display.Animation2d import *

# --- 2D Animation ---------------------------------------------------------

class Anim(Animation2d):

  def __init__(self):

    super().__init__(disp_time=True)

    self.add(colorbar, 'Cb',
      position = [0.5, 0.25],      
    )

    

    # Display animation
    self.show()

# --- Main -----------------------------------------------------------------

A = Anim()
