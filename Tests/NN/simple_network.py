import os
import numpy as np
from AE.NN.ANN import ANN

os.system('clear')

Net = ANN()

Net.add_node(3, IN=True)
Net.add_node(1, name='ok1')
Net.add_node(1, name='ok2')
Net.add_node(1, name='ok3')
Net.add_node(1, name='ok4')
Net.add_node(1, name='ok5')
Net.add_node(OUT=True)

N = len(Net.node)
for i in range(15):
  Net.add_edge(np.random.randint(N), np.random.randint(N), w=i)

Net.add_edge(3, 3, w=1)

# print(Net)

Net.show()
