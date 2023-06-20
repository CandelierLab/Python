"""
Generic neural network tools

The class :class:`.Network` is a generic class for Neural Networks of the 
:py:mod:`AE.NN` package. It does not perform any processing though, so it
has to be subclassed to be useful.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment

def compare(NetA, NetB, C_nodes=None, C_edges=None):
  '''
  Comparison of two networks.

  The algorithm is similar to [1] but with the addition of inner constraints
  on nodes (C_nodes) and edges (C_edges). Typically C_edges is the weighted
  adjacency matrix and C_nodes is the correlation matrix. By default these 
  matrices are filled with ones.

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

  # --- Constraint vectors

  # Nodes
  xc = np.ones(nA*nB) if C_nodes is None else C_nodes.reshape(nA*nB)

  # Edges
  yc = np.ones(mA*mB) if C_edges is None else C_edges.reshape(mA*mB)

  # --- Initialization

  x = np.ones(nA*nB)
  y = np.ones(mA*mB)

  # Structure matrix
  G = np.kron(As.T, Bs.T) + np.kron(At.T, Bt.T)

  for i in range(10):

    y_ = G @ x
    x_ = G.T @ y

    # Contraints
    x_ = x_ * xc
    y_ = y_ * yc

    # Normalization
    x = x_/np.sqrt(np.sum(x_**2))
    y = y_/np.sqrt(np.sum(y_**2))

  # Similarity matrices
  S_nodes = x.reshape((nA, nB))
  S_edges = y.reshape((mA, mB))

  return(S_nodes, S_edges)

def matching(NetA, NetB, C_edges=None, C_nodes=None):

  # Get similarity measures
  S_nodes = compare(NetA, NetB, C_edges=C_edges, C_nodes=C_nodes)[0]

  # Hungarian algorithm (Jonker-Volgenant)
  I, J = linear_sum_assignment(S_nodes, True)

  # Output
  M = [(I[k], J[k]) for k in range(len(I))]

  return M

