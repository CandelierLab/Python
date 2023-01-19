"""Generic neural network tools

The class :class:`.Network` is a generic class for Neural Networks of the 
:py:mod:`AE.NN` package. It does not perform any processing though, so it
has to be subclassed to be useful.
"""

import AE.Display.Animation as Animation

class NetWidget(Animation.Window):

  def __init__(self, engine):

    # Parent's constructor
    super().__init__()
    
    # --- Definitions

    self.engine = engine
    self.engine.trigger = self
    self.n = self.engine.n

    # Arms lengths
    self.D = 0.95
    s = np.sum(self.engine.length)
    L = [self.D*l/s for l in self.engine.length]

    # --- Display

    # Window title
    self.view.setWindowTitle('Snake 2')

    # Limits
    self.view.sceneLimits['x'] = (-1,1)
    self.view.sceneLimits['y'] = (-1,1)

    # --- Elements

    # Midline
    self.view.elm['midline'] = Anim.element('line',
      position = (0,-1),
      width = 0,
      height = 2,
      color = (None, 'grey')
    )

    # Anchor
    self.view.elm['anchor'] = Anim.element('circle',
      position = (0,0),
      radius = 0.015,
      color = ('grey', None)
    )

    parent = 'anchor'

    for i,a in enumerate(self.engine.alpha):

      bar_name = 'bar_{:d}'.format(i)
      joint_name = 'joint_{:d}'.format(i)

      # bar
      self.view.elm[bar_name] = Anim.element('line', parent=parent, behindParent=True,
        position = (0,0),
        width = 0,
        height = L[i],
        thickness = 5,
        color = (None, 'darkCyan')
      )

      # Elbow
      self.view.elm[joint_name] = Anim.element('circle', parent=bar_name,
        position = (0,L[i]),
        radius = 0.01,
        color = ('lightgrey', None)
      )

      parent = joint_name

    # Center of mass
    self.view.elm['barycenter'] = Anim.element('circle',
      position = (0,self.D/2),
      radius = 0.01,
      color = ('red', None)
    )

  def update(self):

    # Update timer display
    super().update()

    # Time (sec)
    t = self.view.timer.elapsed()/1000

    # Computations
    self.engine.update(t)    

    # Update angles
    for i,a in enumerate(self.engine.alpha):
      self.view.elm['bar_{:d}'.format(i)].rotate(a)

    # Update barycenter position
    x = -self.engine.r*np.sin(self.engine.gamma)*self.D/self.n
    y = self.engine.r*np.cos(self.engine.gamma)*self.D/self.n
    self.view.elm['barycenter'].setPosition(x, y)
    

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
    Node ([dict]]): All the nodes, including input, hidden and output nodes.
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