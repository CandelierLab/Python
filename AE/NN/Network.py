"""
Generic neural network tools

The class :class:`.Network` is a generic class for Neural Networks of the 
:py:mod:`AE.NN` package. It does not perform any processing though, so it
has to be subclassed to be useful.
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

import AE.Display.Animation as Animation

# ==========================================================================

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
    if len(self.edge):
      print('\n* Links:')
      for i,L in enumerate(self.edge):
        print('[{:d}]'.format(i), L)
    else:
      print('\n* No link defined.')

    return ''

  def show(self, isolate_output=True):

    anim = Visu2d(self, isolate_output=isolate_output, window=Animation.Window())
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

  def __init__(self, Net, isolate_output=True, dt=None, disp_time=False, window=None):
    """
    Network 2D visualization constructor

    Each node and link is converted to an :class:`AE.Display.Animation.element`.

    It also defines all the necessary attributes for animations.

    Args:
      Net (:class:`Network`): Network to visualize.
      dt (float): Animation time increment (s) between two updates.
      disp_time (bool): If true, the animation time is overlaid to the animation.
      window (:class:`.Window`): If not None, a simple window containing the 
        visualization.
    """

    # Parent constructor
    super().__init__(dt=dt, disp_time=disp_time, disp_boundaries=False, window=window)

    # Network
    self.Net = Net

    # Output isolation
    self.isolate_output = isolate_output

    # --- Computation ------------------------------------------------------

    G = nx.Graph()

    # --- Nodes

    # Vertical spacing
    hIN = 2/(len(self.Net.IN)+1)
    if self.isolate_output:
      hOUT = 2/(len(self.Net.OUT)+1)

    # Input nodes
    for i,node in enumerate(self.Net.IN):
      G.add_node(node, pos=[0, 1-hIN*(i+1)])

    # Other nodes
    if self.isolate_output:
      
      # Hidden nodes
      I_hidden = set(range(len(self.Net.node))) - set(self.Net.IN) - set(self.Net.OUT)
      G.add_nodes_from(I_hidden)

      # Output nodes
      for i,node in enumerate(self.Net.OUT):
        G.add_node(node, pos=[1, 1-hOUT*(i+1)])

      # Fixed nodes
      I_fixed = self.Net.IN + self.Net.OUT

      # Optimal distance between nodes
      k = 1/np.sqrt(len(I_hidden))

    else:

      # Define hidden and output nodes
      notIN = set(range(len(self.Net.node))) - set(self.Net.IN)
      G.add_nodes_from(notIN)

      # Fixed nodes
      I_fixed = self.Net.IN

      # Optimal distance between nodes
      k = 1/np.sqrt(len(notIN))
     
    # --- Edges

    G.add_edges_from([(edge['i'], edge['j']) for edge in self.Net.edge])

    # --- Positions
    # Position nodes using the Fruchterman-Reingold force-directed algorithm.

    pos = nx.spring_layout(G, k=k, pos=nx.get_node_attributes(G,'pos'), fixed=I_fixed)

    # # Matplotlib draw
    # nx.draw(G, pos=pos, with_labels=True, font_weight='bold')
    # plt.show()  
    
    # --- Boundaries
    P = np.array(list(pos.values()))
    xym = np.amin(P, axis=0)
    xyM = np.amax(P, axis=0)

    # --- Scene settings ---------------------------------------------------

    self.r = 0.025

    self.sceneLimits['x'] = [xym[0]-self.r, xyM[0]+self.r]
    self.sceneLimits['y'] = [xym[1]-self.r, xyM[1]+self.r]

    # --- Nodes ------------------------------------------------------------

    for i,node in enumerate(self.Net.node):
      
      # --- Group

      # Name
      if isinstance(node['name'], int):
        gname = 'node_{:d}'.format(i)
      else:
        gname = 'node_' + self.Net.node[i]['name']

      self.elm[gname] = Animation.element('group', position=pos[i])

      # --- Circle

      self.elm[gname+'_circle'] = Animation.element('circle',
        parent = gname,
        position = (0, 0),
        radius = self.r,
        color = ('#444', '#ccc'),
        thickness = 2
      )

      # --- Name

     

      # --- INPUT Nodes

      if node['IN']:
        pass

      # --- OUTPUT Nodes

      if node['OUT']:
        pass
       


    # h = 1/len(self.Net.IN)

    # for k,i in enumerate(self.Net.IN):

    #   # Element's name
    #   if isinstance(self.Net.node[i]['name'], int):
    #     ename = 'node_{:d}'.format(i)
    #   else:
    #     ename = 'node_' + self.Net.node[i]['name']

    #   self.elm[ename] = Animation.element('circle',
    #     position = (-0.1, h*(k+0.5)),
    #     radius = 0.025,
    #     color = (None, 'white'),
    #     thickness = 2
    #   )

    # for i, node in enumerate(self.Net.node):

    #   # Element's name
    #   if isinstance(node['name'], int):
    #     ename = 'node_{:d}'.format(i)
    #   else:
    #     ename = 'node_' + node['name']

    #   self.elm[ename] = Animation.element('circle',
    #     position = self.pos[i],
    #     radius = 0.025,
    #     color = (None, 'white'),
    #     thickness = 2
    #   )