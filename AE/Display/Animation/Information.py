import re

from AE.Display.time import *
from AE.Display.Animation.Animation_2d import *
from AE.Display.Animation.Items_2d import *

class Information(Animation_2d):
    
  # ========================================================================
  def __init__(self, disp_time=True):
    
    # Parent contructor
    super().__init__(boundaries=[[0, 0.01], [0, 1]], disp_boundaries=True, boundaries_color=Qt.black)

    # --- Optional display

    # Time string
    self.disp_time = disp_time

    if self.disp_time:
      self.add(text, 'Time',
        stack = True,
        string = self.time_str(time(0,0)),
        color = 'white',
        fontsize = 12,
      )

  # ========================================================================
  def time_str(self, t):
    '''
    Format time string for display
    '''

    s = '<p>step {:06d}</p><font size=2> {:06.02f} sec</font>'.format(t.step, t.time)

    # Grey zeros
    s = re.sub(r'( )([0]+)', r'\1<span style="color:grey;">\2</span>', s)

    return s
  
  # ========================================================================
  def update(self, t):

    if self.disp_time:
      self.item['Time'].string = self.time_str(t) 

    # Repaint & confirm
    super().update(t)