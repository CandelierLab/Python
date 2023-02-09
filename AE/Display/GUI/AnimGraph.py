'''
Animation and graph viewer
'''

from AE.Display.Viewer import Viewer

class AnimGraph(Viewer):

  def __init__(self, animation):

    # Prent's contructor
    super().__init__()

    # Define animation
    self.animation = animation()