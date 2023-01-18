class Network():
  """
  Abstract class for Artificial neuron networks

  :param kind: Optional "kind" of ingredients.
  :type kind: list[str] or None
  :raise lumache.InvalidKindError: If the kind is invalid.
  :return: The ingredients list.
  :rtype: list[str]

  """

  def __init__(self):
    """
    Constructor

    :param kind: Optional "kind" of ingredients.
    :type kind: list[str] or None
    :raise lumache.InvalidKindError: If the kind is invalid.
    :return: The ingredients list.
    :rtype: list[str]

    """
    
    # --- Nodes
    # Array of dict.
    self.Node

    # 