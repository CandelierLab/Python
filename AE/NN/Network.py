"""
Generic neural network tools

The class :class:`.Network` is a generic class for Neural Networks of the 
:py:mod:`AE.NN` package. It does not perform any processing though, so it
has to be subclassed to be useful.
"""

import numpy as np
import networkx as nx

from PyQt5.QtCore import Qt
import AE.Display.Animation as Animation

# === Network ==============================================================

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
      print('\n* Edges:')
      for i,L in enumerate(self.edge):
        print('[{:d}]'.format(i), L)
    else:
      print('\n* No edge defined.')

    return ''

  def show(self, isolate_output=True, size=None):

    anim = Visu2d(self, isolate_output=isolate_output, size=size)
    anim.parent.title = 'Network'
    anim.show()

# === Visualisation ========================================================

class Visu2d(Animation.Animation2d):
  """
  2D network visualisation and animation tool

  Generates a 2D representation of a network. As it derives from
  :class:`AE.Display.Animation.Animation2d`, it can also be used to 
  implement animations, like color-changing nodes to represent their
  values through time.
  """

  def __init__(self, Net, isolate_output=True, dt=None, disp_time=False, size=None):
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
    super().__init__(dt=dt, disp_time=disp_time, disp_boundaries=False, size=size)

    # Network
    self.Net = Net

    # Output isolation
    self.isolate_output = isolate_output

    # --- Computation ------------------------------------------------------

    G = nx.Graph()

    # --- Nodes

    # Vertical spacing
    hIN = 1/len(self.Net.IN)
    if self.isolate_output:
      hOUT = 1/len(self.Net.OUT)

    # Input nodes
    for i,node in enumerate(self.Net.IN):
      G.add_node(node, pos=[0, 1-hIN*(i+1/2)])

    # Other nodes
    if self.isolate_output:
      
      # Hidden nodes
      I_hidden = set(range(len(self.Net.node))) - set(self.Net.IN) - set(self.Net.OUT)
      G.add_nodes_from(I_hidden)

      # Output nodes
      for i,node in enumerate(self.Net.OUT):
        G.add_node(node, pos=[1, 1-hOUT*(i+1/2)])

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

    # --- Corners (for bounding))
    
    I_corners = len(self.Net.node) + np.arange(4)
    G.add_node(I_corners[0], pos=[0,0])
    G.add_node(I_corners[1], pos=[0,1])
    G.add_node(I_corners[2], pos=[1,0])
    G.add_node(I_corners[3], pos=[1,1])
    I_fixed += I_corners.tolist()

    # --- Edges

    Edges = [(edge['i'], edge['j']) for edge in self.Net.edge]

    # Corner bindings for confinment
    for i in range(len(self.Net.node)):
      Edges += [[i, I_corners[0]], [i, I_corners[1]], [i, I_corners[2]], [i, I_corners[3]]]

    G.add_edges_from(Edges)

    # --- Positions
    # Position nodes using the Fruchterman-Reingold force-directed algorithm.

    pos = nx.spring_layout(G, k=k, pos=nx.get_node_attributes(G,'pos'), fixed=I_fixed)
   
    # --- Boundaries
    P = np.array(list(pos.values()))
    xym = np.amin(P, axis=0)
    xyM = np.amax(P, axis=0)

    # --- Scene settings ---------------------------------------------------

    # self.r = 0.025
    self.r = 0.05
    self.fontsize = int(np.floor(self.r*self.size/4.5))

    # self.sceneLimits['x'] = [xym[0]-self.r, xyM[0]+self.r]
    # self.sceneLimits['y'] = [xym[1]-self.r, xyM[1]+self.r]

    # --- Edges ------------------------------------------------------------

    for i,edge in enumerate(self.Net.edge):

      # Name
      name = str(edge['i']) + '→' +  str(edge['j'])

      if name not in self.item:

        self.add(Animation.arrow, name,
          points = [pos[edge['i']], pos[edge['j']]],
          thickness = 2,
          locus = 0.5
        )

    # --- Nodes ------------------------------------------------------------

    for i,node in enumerate(self.Net.node):
      
      # --- Group

      # Name
      if isinstance(node['name'], int):
        gname = 'node_{:d}'.format(i)
      else:
        gname = 'node_' + self.Net.node[i]['name']

      self.add(Animation.group, gname,
        position = pos[i], 
        draggable = not (node['IN'] or node['OUT']))

      # --- Circle

      # Double circle for OUTPUT Nodes
      if node['OUT']:
        self.add(Animation.circle, gname + '_outercircle',
          parent = gname,
          position = (0,0),
          radius = self.r*1.2,
          colors = ('black', '#ccc'),
          thickness = 2
        )

      self.add(Animation.circle, gname + '_circle',
        parent = gname,
        position = (0,0),
        radius = self.r,
        colors = ('#555', '#ccc'),
        thickness = 2,
        linestyle = '--' if node['IN'] else None
      )

      # --- Name

      name = str(node['name'])
      if len(name)>3:
        name = name[0:3]  # TODO: make this html friendly ...

      self.add(Animation.text, gname + '_text',
        parent = gname,
        position = (0,0),
        string = name,
        color = 'white',
        center = True,
        fontsize = self.fontsize
      )

  def change(self, type, item):
    """
    Drag callback

    Reimplements :py:meth:`AE.Display.Animation.Animation2d.change`.

    args:

      type (str): type of change (``move``).

      elm (:class:`AE.Display.Animation.element`): Element that has changed.
    """

    if type=='move':

      # Moved node
      k = int(item.name[5:])

      # Get new position
      pos = item.scene2xy(item.pos())
    
      # Edges
      for edge in self.Net.edge:

          # Name
          name = str(edge['i']) + '→' +  str(edge['j'])

          # Afferent nodes
          if edge['j']==k:        
            p1 = item.scene2xy(self.item['node_{:d}'.format(edge['i'])].pos())          
            self.composite[name].points = [p1, pos]

          # Efferent nodes
          if edge['i']==k:        
            p2 = item.scene2xy(self.item['node_{:d}'.format(edge['j'])].pos())
            self.composite[name].points = [pos, p2]
