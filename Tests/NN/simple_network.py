import os
import numpy as np
from AE.NN.ANN import ANN

os.system('clear')

Net = ANN()

Net.add_node(3, IN=True)
for i in range(5):
  Net.add_node(1, name='hn{:d}'.format(i))
Net.add_node(OUT=True)

N = len(Net.node)
for i in range(15):
  Net.add_edge(np.random.randint(N), np.random.randint(N), w=i*np.pi/10)

Net.add_edge(3, 3, w=1)

Net.show()
