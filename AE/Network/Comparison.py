import numpy as np
from scipy.optimize import linear_sum_assignment

import AE.Network.Network

def compare(NetA, NetB, weight_constraint=True, nIter=100):
  '''
  Comparison of two networks.

  The algorithm is identical to [1] but with the addition of a constraint
  of edge weight similarity. Set weight_constraint=False to recover the 
  original algorithm.

  [1] L.A. Zager and G.C. Verghese, "Graph similarity scoring and matching",
      Applied Mathematics Letters 21 (2008) 86–94, doi: 10.1016/j.aml.2007.01.006
  '''
  
  # --- Definitions

  # Number of nodes
  nA = len(NetA.node)
  nB = len(NetB.node)

  # Number of edges
  mA = len(NetA.edge)
  mB = len(NetB.edge)

  # --- Source-edge and terminus-edge matrices

  # Net A
  As = np.zeros((nA, mA))
  At = np.zeros((nA, mA))
  for k, e in enumerate(NetA.edge):
    As[e['i'], k] = 1
    At[e['j'], k] = 1

  # Net B
  Bs = np.zeros((nB, mB))
  Bt = np.zeros((nB, mB))
  for k, e in enumerate(NetB.edge):
    Bs[e['i'], k] = 1
    Bt[e['j'], k] = 1

  # --- Weight constraint

  if weight_constraint:

    # Edge weights
    W = np.zeros((mA, mB))
    for i, a in enumerate(NetA.edge):
      for j, b in enumerate(NetB.edge):
        W[i,j] = a['w'] - b['w']

    sigma2 = np.var(W)
    if sigma2>0:
      W = np.exp(-W**2/2/sigma2)
      yc = W.reshape(mA*mB)
    else:
      yc = np.ones(mA*mB)

  else:
    yc = np.ones(mA*mB)

  # --- Initialization

  x = np.ones(nA*nB)
  y = np.ones(mA*mB)

  # Structure matrix
  G = np.kron(As.T, Bs.T) + np.kron(At.T, Bt.T)

  for i in range(nIter):

    y_ = (G @ x) * yc
    x_ = G.T @ y

    # Normalization
    x = x_/np.sqrt(np.sum(x_**2))
    y = y_/np.sqrt(np.sum(y_**2))

  # Similarity matrices
  S_nodes = x.reshape((nA, nB))
  S_edges = y.reshape((mA, mB))

  return(S_nodes, S_edges)

def matching(NetA, NetB, threshold=None, **kwargs):

  # Get similarity measures
  Sim = compare(NetA, NetB, **kwargs)[0]

  # Threshold
  if threshold is not None:
    Sim[Sim<threshold] = -np.inf

  # Hungarian algorithm (Jonker-Volgenant)
  I, J = linear_sum_assignment(Sim, True)

  # Output
  M = [(I[k], J[k]) for k in range(len(I))]

  return M

# === MatchNet class ======================================================

class NetMatch(AE.Network.Network.Network):

  def __init__(self, verbose=False):

    super().__init__(verbose)

    