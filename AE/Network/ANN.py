import numpy as np

from AE.Network.Network import Network

# === ACTIVATION FUNCTIONS =================================================

def activate(afun, x):

  match afun:

    case 'identity':
      '''
      Identity activation

      NB: in practice this case is never executed since the nodes with
      identity activation are removed from the activation groups beforehand.
      '''

      y = x

    case 'sigmoid':
      '''
      The standard sigmoid function
      '''

      y = 1/(1+np.exp(-x))

    case 'rectified_sigmoid':
      '''
      Rectified sigmoid function.
      It has been used in the original NEAT paper (doi: 10.1162/106365602320169811)
      with the justification: 
        "The steepened sigmoid allows more fine-tuning at extreme 
        activations. It is optimized to be close to linear during its 
        steepest ascent between activations -0.5 and 0.5."
      '''

      y = 1/(1+np.exp(-4.9*x))
    
    case 'fast_rectified_sigmoid':
      '''
      A faster approximation of the rectified sigmoid, using np.abs() instead 
      of np.exp().
      '''

      a = 4.9
      y = (1+x*a/(1+np.abs(x*a)))/2

    case 'tanh':
      '''
      Hyperbolic tangent
      '''

      y = np.tanh(x)

    case 'negative_tanh':
      '''
      Hyperbolic tangent with opposite output
      To implement inhibitor neurons
      '''

      y = -np.tanh(x)


    case 'rectified_tanh':
      '''
      Rectified tanh function, as used in the neat-python package.
      '''

      y = np.tanh(2.5*x)

    case _:
      raise AttributeError(f"Unknown activation type '{afun}'.")#"Unknown activation type '{:s}'.".format(afun))

  return y    

# === NETWORK ==============================================================

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
    
    self.BULK = []

    # Defined during initialization
    self._isInitialized = False
    self.nNd = None
    self.nIn = None
    self.nBk = None
    self._W = None
    self._bias = None
    self._value = None
    self._activation_group = None

  def add_node(self, n=1, IN=False, OUT=False, bias=0., activation=None, initial_value=0., name=None, html=None, response = 1.0):

    # --- Checks

    if IN and OUT:
      raise RuntimeError('A node cannot be both an input and an output.')

    if n<1:
      raise ValueError('At least one node should be added')

    if not isinstance(n,int):
      raise ValueError('Only an integer number of nodes can be added.')

    # --- Default activation
    '''
    NB: The default activation for input nodes is None (equivalent to 'identity'),
    but it is still possible to explicitely assign another activation.
    '''
    
    if not IN and activation is None:

      activation = self.default_activation

    # --- Add node

    for i in range(n):

      # Index inputs
      if IN:
        self.IN.append(len(self.node))
      else:
        self.BULK.append(len(self.node))

      # Index outputs
      if OUT:
        self.OUT.append(len(self.node))

      self.node.append({'IN':IN, 'OUT':OUT, 'bias':bias, 'response':response, 'activation':activation, 
        'initial_value':initial_value, 'name': len(self.node) if name is None else name,
        'html': html})

  def add_edge(self, i, j, w=0., d=0):

    # --- Conversion

    # Emitting node
    if isinstance(i, str):
      try:
        i = [n['name'] for n in self.node].index(i)
      except ValueError:
        raise ValueError("Cannot find the node '{:s}'.".format(i))

    # Receiving node
    if isinstance(j, str):
      try:
        j = [n['name'] for n in self.node].index(j)
      except ValueError:
        raise ValueError("Cannot find the node '{:s}'.".format(j))

    # --- Checks

    # TODO: Check that edge does not already exist

    # --- Add edge

    self.edge.append({'i':i, 'j':j, 'w':w, 'd':d})
    
  def initialize(self):

    # --- Numbers

    self.nNd = len(self.node)
    self.nIn = len(self.IN)
    self.nBk = len(self.BULK)

    # --- Weights

    self._W = np.zeros((self.nNd, self.nBk))
    for e in self.edge:
      try:
        self._W[e['i'], e['j']-sum([i<e['j'] for i in self.IN])] = e['w']
      except:
        print(self.nNd, self.nIn, self.nBk)
        print(self._W)
        print(self.edge)
        print(self.IN)


        raise      
    # --- Biases

    self._bias = np.array([self.node[i]['bias'] for i in self.BULK])

    # --- Responses

    self._response = np.array([self.node[i]['response'] for i in self.BULK])


    # --- Activation groups

    self._activation_group = {}
    
    for k, node in enumerate(self.node):

      a = node['activation']

      # Skip None or 'identity'
      if a is None or a=='identity': continue

      if a in self._activation_group:
        self._activation_group[a].append(k)
      else:
        self._activation_group[a] = [k]

    # --- Values

    self._value = np.zeros(len(self.node))

    # Update initialization state
    self._isInitialized = True

  def process(self, input):

    if self.propagation_mode=='synchronous':

      # Initialize
      if not self._isInitialized:
        self.initialize()

      # Update input
      self._value[self.IN] = input

      # Compute new values
      self.step()

    return self._value[self.OUT]

  def step(self):
    
    # Weighted sum, bias and response
    self._value[self.BULK] = self._response * (np.matmul(self._value, self._W) + self._bias)

    ''' 
    Note:
      Input nodes are set to zero during this operation, but this is not 
      important for the rest of the computation since they are not used
      afterward. They will be then reset during the initialization of the
      next step.
    '''

    # Activation
    for g in self._activation_group:
      self._value[self._activation_group[g]] = activate(g, self._value[self._activation_group[g]])
