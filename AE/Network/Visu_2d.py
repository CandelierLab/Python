"""
Generic neural network tools

The class :class:`.Network` is a generic class for Neural Networks of the 
:py:mod:`AE.NN` package. It does not perform any processing though, so it
has to be subclassed to be useful.
"""

import numpy as np
import networkx as nx

# import project
from Animation.Animation_2d import *
from Animation.Items_2d import *
from Animation.Composites_2d import *

# from AE.Display.Animation.Animation_2d import *
# from AE.Display.Animation.Items_2d import *
# from AE.Display.Animation.Composites_2d import *

class Visu2d(Animation_2d):
  """
  2D network visualisation and animation tool

  Generates a 2D representation of a network. As it derives from
  :class:`AE.Display.Animation.Animation2d`, it can also be used to 
  implement animations, like color-changing nodes to represent their
  values through time.
  """

  def __init__(self, Net, W, isolate_output=True, viewHeight=None):
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
    Animation_2d.__init__(self, W, disp_boundaries=False, viewHeight=viewHeight)

    # Network
    self.Net = Net

    # Output isolation
    self.isolate_output = isolate_output

    # --- Computation ------------------------------------------------------

    G = nx.Graph()

    # --- Nodes

    # Vertical spacing
    hIN = 1/len(self.Net.IN) if len(self.Net.IN) else 0.5
    if self.isolate_output:
      hOUT = 1/len(self.Net.OUT) if len(self.Net.OUT) else 0.5

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
      if len(I_hidden):
        k = 1/np.sqrt(len(I_hidden))
      else:
        k = 1

    else:

      # Define hidden and output nodes
      notIN = set(range(len(self.Net.node))) - set(self.Net.IN)
      G.add_nodes_from(notIN)

      # Fixed nodes
      I_fixed = self.Net.IN.copy()

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

    self.r = Net.nodeRadius
    self.nodeFontSize = Net.nodeFontSize if Net.nodeFontSize is not None else int(np.floor(self.r*self.viewHeight/2))

    # self.sceneLimits['x'] = [xym[0]-self.r, xyM[0]+self.r]
    # self.sceneLimits['y'] = [xym[1]-self.r, xyM[1]+self.r]

    # --- Edges ------------------------------------------------------------

    for edge in self.Net.edge:

      # Name
      name = str(edge['i']) + '→' +  str(edge['j'])

      if name not in self.item and edge['i']!=edge['j']:
          
        self.add(arrow, name,
          points = [pos[edge['i']], pos[edge['j']]],
          locus = 0.45,
          string = '{:.02f}'.format(edge['w']),
          fontsize = Net.edgeFontSize
        )

    # --- Nodes ------------------------------------------------------------
    
    for i, node in enumerate(self.Net.node):
      
      # --- Group

      # Name
      gname = 'node_' + str(node['name'])

      self.add(group, i,
        position = pos[i], 
        draggable = not (node['IN'] or node['OUT']))

      # --- Self-edge

      for edge in self.Net.edge:

        # Name
        name = str(edge['i']) + '→' +  str(edge['j'])

        if name not in self.item and edge['i']==i and edge['j']==i:
          
          self.add(circle, name,
            parent = i,
            position = (0, self.r),
            radius = self.r,
            colors = (None, Net.edgeColor),
          )

          self.add(arrow, name + '_arrowhead',
            parent = i,
            points = [(-0.005, 2*self.r), (-0.02, 2*self.r)],
            locus = 0.5,
            string = '{:.02f}'.format(edge['w']),
            fontsize = Net.edgeFontSize,
            color = Net.edgeColor
          )

      # --- Circle

      # Double circle for INPUT/OUTPUT Nodes
      if node['IN'] or node['OUT']:
        self.add(circle, str(gname) + '_outercircle',
          parent = i,
          position = (0,0),
          radius = self.r*1.2,
          colors = (None, Net.IOnodeStroke),
          thickness = 2,
          linestyle = ':' if node['IN'] else None
        )

      self.add(circle, str(gname) + '_circle',
        parent = i,
        position = (0,0),
        radius = self.r,
        colors = (Net.nodeColor, Net.nodeStroke),
        thickness = 2,
      )

      # --- Name

      if node['html'] is None:
        name = str(node['name'])
        if len(name)>3: name = name[0:3]
      else:
        name = node['html']

      # --- Text

      self.add(text, str(gname) + '_text',
        parent = i,
        position = (0,0),
        string = name,
        color = Net.nodeTextColor,
        center = True,
        fontsize = self.nodeFontSize,
        fontname = 'Serif'
      )

  # ========================================================================
  def change(self, type, item):
    """
    Drag callback

    Reimplements :py:meth:`AE.Display.Animation.Animation2d.change`.

    args:

      type (str): type of change (``move``).

      elm (:class:`AE.Display.Animation.element`): Element that has changed.
    """

    if type=='move':

      k = item.name

      # Get new position
      pos = item.scene2xy(item.pos())
    
      # Edges
      for edge in self.Net.edge:

          # Name
          name = str(edge['i']) + '→' +  str(edge['j'])

          if edge['i']==edge['j']:
            pass

          else:

            # Afferent nodes
            if edge['j']==k:        
              p1 = item.scene2xy(self.item[edge['i']].pos())
              self.composite[name].points = [p1, pos]

            # Efferent nodes
            if edge['i']==k:
              p2 = item.scene2xy(self.item[edge['j']].pos())
              self.composite[name].points = [pos, p2]

