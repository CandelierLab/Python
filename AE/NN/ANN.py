from collections import defaultdict
import numpy as np
from AE.NN.Network import Network

class ANN(Network):

  def __init__(self, default_activation='sigmoid', propagation_mode='synchronous'):
    
    # Parent constructor
    super().__init__(self)

    # --- Default attributes

    # Activation
    self.default_activation = default_activation

    # Propagation
    self.propagation_mode = propagation_mode

    #  --- Convenience attributes

    self._isInitialized = False
    self.notIN = None
    self.nNode = None
    self.nIN = None
    self.nNotIn = None
    self._W = None
    self._bias = None
    self._value = None
    self._activation_group = {}

  def add_node(self, n=1, IN=False, OUT=False, bias=0, activation=None, initial_value=0, name=None):

    # --- Checks

    if IN and OUT:
      raise RuntimeError('A node cannot be both an input and an output.')

    if n<1:
      raise ValueError('At least one node should be added')

    if not isinstance(n,int):
      raise ValueError('Only an integer number of nodes can be added.')

    # --- Default values

    if IN:

      if activation is not None:
        raise Warning("Activation has been removed for an input node.")

      # Override activation
      activation = None

    elif activation is None:

      activation = self.default_activation

    # --- Add node

    for i in range(n):

      # Count inputs
      if IN:
        self.IN.append(len(self.node))

      # Count outputs
      if OUT:
        self.OUT.append(len(self.node))

      self.node.append({'IN':IN, 'OUT':OUT, 'bias':bias, 'activation':activation, 
        'initial_value':initial_value, 'name':len(self.node) if name is None else name})

  def add_edge(self, i, j, w=0, d=0):

    # --- Checks

    # TODO: Check that edge does not already exist

    # --- Add edge

    self.edge.append({'i':i, 'j':j, 'w':w, 'd':d})
    
  def initialize(self):

    # --- Numbers

    self.nNode = len(self.node)
    self.nIN = len(self.IN)
    self.nNotIn = self.nNode-self.nIN

    # --- Weights

    self._W = np.zeros((self.nNode, self.nNotIn))
    print(self._W)
    
    # --- Biases
    
    self._bias = np.array([node['bias'] for node in self.node])

    # --- Activation groups

    for k, node in enumerate(self.node):

      a = node['activation']

      if a is None: continue

      if a in self._activation_group:
        self._activation_group[a].append(k)
      else:
        self._activation_group[a] = [k]

    # --- Values

    self._value = np.zeros(len(self.node))

  def process(self, input):

    if self.propagation_mode=='synchronous':

      # Initialize
      if not self._isInitialized: self.initialize()

      # Update input
      self._value[self.IN] = input

      # Compute new values
      self.step()

    return self._value[self.OUT]

  def step(self):
    
    # Weighted sum and bias
    self._value[self._notIN] = self._value*self._W + self._bias

    ''' 
    Note:
      Input nodes are set to zero during this operation, but this is not 
      important for the rest of the computation since they are not used
      afterward. They will be then reset during the initialization of the
      next step.
    '''

    # --- Activation

# f = fieldnames(this.activationGroup);
# for k = 1:numel(f)

#     % Group indices
#     I = this.activationGroup.(f{k});

#     % Compute activated values
#     this.value(I) = this.activate(this.value(I), f{k});

# end