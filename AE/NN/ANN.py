from collections import defaultdict
import numpy as np
from AE.NN.Network import Network

class ANN(Network):

  def __init__(self, default_activation='sigmoid', propagation_mode='synchronous'):
    
    # Parent constructor
    super().__init__(self)

    # --- Default behavior

    self.default_activation = default_activation

    # --- Propagation

    self.propagation_mode = propagation_mode

    #  --- Convenience arrays

    self.notIN = []
    self.bias = []
    self.value = []
    self.activation_group = defaultdict

  def add_node(self, n=1, IN=False, OUT=False, bias=0, activation=None, initial_value=0, name=None):
    """
    Fetches rows from a Smalltable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle.  String keys will be UTF-8 encoded.

    Args:
      table_handle (int): An open smalltable.Table instance.
      keys:
        A sequence of strings representing the key of each table row to
        fetch.  String keys will be UTF-8 encoded.
      require_all_keys:
        If True only rows with values set for all keys will be returned.

    Returns:
      A dict mapping keys to the corresponding table row data
      fetched. Each row is represented as a tuple of strings. For
      example:

      {b'Serak': ('Rigel VII', 'Preparer'),
       b'Zim': ('Irk', 'Invader'),
       b'Lrrr': ('Omicron Persei 8', 'Emperor')}

      Returned keys are always bytes.  If a key from the keys argument is
      missing from the dictionary, then that row was not found in the
      table (and require_all_keys must have been False).

    Raises:
      IOError: An error occurred accessing the smalltable.
    """

    # --- Checks

    if IN and OUT:
      raise RuntimeError('A node cannot be both an input and an output.')

    if n<1:
      raise ValueError('At least one node should be added')

    if not isinstance(n,int):
      raise ValueError('Only an integer number of nodes can be added.')

    # --- Default values

    if IN:

      if activation is not None and activation!='identity':
        raise Warning("Activation has been changes to 'identity' for an input node")

      # Override activation
      activation = 'identity'
    
    if activation is None:
      activation = self.default_activation

    # --- Add node

    for i in range(n):

      self.node.append({'IN':IN, 'OUT':OUT, 'bias':bias, 'activation':activation, 
        'initial_value':initial_value, 'name':len(self.node) if name is None else name})

  def add_link(self, i, j, w=0, d=0, name=None):

    # --- Checks

    # TODO: Check that link does not already exist

    # --- Add link

    self.link.append({'i':i, 'j':j, 'w':w, 'd':d, 'name':name})
    