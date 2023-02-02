import numpy as np
import time
from AE.NN.ANN import *

import matplotlib.pyplot as plt

x = np.linspace(-10,10,10000)

start = time.time()
y0 = activate('tanh', x)
end = time.time()
print(end - start)

start = time.time()
y1 = activate('fast_tanh', x)
end = time.time()
print(end - start)

fig, ax = plt.subplots()

ax.plot(x, y0, 'k')
ax.plot(x, y1, 'r')

ax.grid(True)

plt.show()