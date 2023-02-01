import numpy as np
from AE.NN.ANN import ANN

Net = ANN()

Net.add_node(3, IN=True)
Net.add_node(5)
Net.add_node(1, OUT=True)

N = len(Net.node)
for i in range(15):
  Net.add_edge(np.random.randint(N), np.random.randint(N))

# print(Net)

Net.show()