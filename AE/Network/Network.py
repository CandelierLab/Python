"""
Generic neural network tools

The class :class:`.Network` is a generic class for Neural Networks of the 
:py:mod:`AE.NN` package. It does not perform any processing though, so it
has to be subclassed to be useful.
"""

import pprint

from AE.Display.Animation.Window import Window
from AE.Network.Visu_2d import Visu2d

class Network():
  """
  Generic Neuronal Network

  Base class for all the Neural Networks of the :py:mod:`AE.NN` package.
  This class does not perform any processing and is intended to be subclassed.
  
  Subclasses should have the following methods:
    * ``add_node()``: Adding nodes
    * ``add_link()``: Adding links
    * ``process()``: Processing inputs to generate outputs.
  
  It is also recommended to have an ``initialize()`` method to compile the 
  network and improve ease of coding and speed of exection.
  
  Nodes should have the fields:
    * ``IN``
    * ``OUT``
    * ``name``

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
    self.edge = []

    # Inputs and outputs
    self.IN = []
    self.OUT = []

    # Display settings
    self.nodeRadius = 0.03
    self.nodeFontSize = 12
    self.edgeFontSize = 9
    self.nodeColor = '#fff'
    self.nodeTextColor = '#000'
    self.nodeStroke = None
    self.IOnodeStroke = '#ccc'
    self.edgeColor = '#ccc'

    # Misc
    self.verbose = verbose

  def __str__(self):

    print('\n--- Generic network')

    # Nodes
    if len(self.node):
      print('\n* Nodes:')
      for i, N in enumerate(self.node):
        print('[{:d}]'.format(i), N)
    else:
      print('\n* No node defined.')

    # Links
    if len(self.edge):
      print('\n* Edges:')
      for i,L in enumerate(self.edge):
        print('[{:d}]'.format(i), L)
    else:
      print('\n* No edge defined.')

    return ''

  def print(self):

    pp = pprint.PrettyPrinter(depth=4)
    pp.pprint(self.__dict__)

  def show(self, isolate_output=True, viewHeight=None):

    W = Window('Simple network', display_information=False)
    W.add(Visu2d(self, isolate_output=isolate_output, viewHeight=viewHeight))
    W.show()

