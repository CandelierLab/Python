"""Generic neural network tools

The class :class:`.Network` is a generic class for Neural Networks of the 
:py:mod:`AE.NN` package. It does not perform any processing though, so it
has to be subclassed to be useful.
"""

import AE.Display.Animation as Animation

# ==========================================================================

class Network():
  """
  Generic Neuronal Network

  Base class for all the NN of the :py:mod:`AE.NN` package.
  This class does not perform any processing and is intended to be subclassed.
  Subclasses should have the following methods:
  - add_node()
  - add_link()
  - process()
  
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
    Constructor

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

    anim = NetworkAnimation(window=Animation.Window())
    anim.window.title = 'Network'
    anim.window.show()

# ==========================================================================

class NetworkAnimation(Animation.Animation2d):

  def __init__(self, dt=None, disp_time=False, window=None):

    # Parent constructor
    super().__init__(dt, disp_time, window)

    # --- Elements

    # Node
    self.elm['n0'] = Animation.element('circle',
      position = (0.5,0.5),
      radius = 0.025,
      color = (None, 'white'),
      thickness = 2
    )