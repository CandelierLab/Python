
class time():
  """
  A class to manage time, especially the duality between steps and
  continuous time. 
  """

  def __init__(self, step, time):
    """
    `time` constructor

    Defines a time aobject that contains both a stepwise and continuous representation.

    Args:
      step (int): The current time step
      time (float): The current time.
    """

    self.step = step
    ''' The current time step.'''

    self.time = time
    '''The current time (continuous).'''