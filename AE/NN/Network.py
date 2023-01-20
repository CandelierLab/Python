"""
Generic neural network tools

The class :class:`.Network` is a generic class for Neural Networks of the 
:py:mod:`AE.NN` package. It does not perform any processing though, so it
has to be subclassed to be useful.
"""

import AE.Display.Animation as Animation

# ==========================================================================

class Network():
  """
  Generic Neuronal Network

  Base class for all the Neural Networks of the :py:mod:`AE.NN` package.
  This class does not perform any processing and is intended to be subclassed.
  
  Subclasses should have the following methods:
    * ``add_node()``
    * ``add_link()``
    * ``process()``
  
  Attributes:
    Node ([dict]): All the nodes, including input, hidden and output nodes.
    W (np.Array): Weights matrix. Each element :math:`w_{ij}` contains the weight of the 
      link :math:`i \\rightarrow j`.
    IN ([int]): Indices of the input nodes.
    OUT ([int]): Indices of the output nodes.
    verbose (*boolean*): If True, informative messages are displayed.
  """

  def __init__(self, verbose=False):
    """
    Generic network constructor

    Args:
      verbose (boolean): If True, informative messages are displayed.
    """
    
    # Nodes and links
    self.node = []
    self.link = []

    # Inputs and outputs
    self.IN = []
    self.OUT = []

    # Misc
    self.verbose = verbose

  def __repr__(self):

    print('\n--- Generic network')

    # Nodes
    if len(self.node):
      print('\n* Nodes:')
      for i, N in enumerate(self.node):
        print('[{:d}]'.format(i), N)
    else:
      print('\n* No node defined.')

    # Links
    if len(self.link):
      print('\n* Links:')
      for i,L in enumerate(self.link):
        print('[{:d}]'.format(i), L)
    else:
      print('\n* No link defined.')

    return ''

  def show(self):

    anim = Visu2d(window=Animation.Window())
    anim.window.title = 'Network'
    anim.window.show()

# ==========================================================================

class Visu2d(Animation.Animation2d):
  """
  2D network visualisation and animation tool

  Generates a 2D representation of a network. As it derives from
  :class:`AE.Display.Animation.Animation2d`, it can also be used to 
  implement animations, like color-changing nodes to represent their
  values through time.
  """

  def __init__(self, dt=None, disp_time=False, window=None):
    """
    Network 2D visualization constructor

    Each node and link is converted to an :class:`AE.Display.Animation.element`.

    It also defines all the necessary attributes for animations.

    Args:
      dt (float): Animation time increment (s) between two updates.
      disp_time (bool): If true, the animation time is overlaid to the animation.
      window (:class:`.Window`): If not None, a simple window containing the 
        visualization.
    """
    # Parent constructor
    super().__init__(dt=dt, disp_time=disp_time, disp_boundaries=False, window=window)

    # --- Elements

    # Node
    self.elm['n0'] = Animation.element('circle',
      position = (0.5,0.5),
      radius = 0.025,
      color = (None, 'white'),
      thickness = 2
    )