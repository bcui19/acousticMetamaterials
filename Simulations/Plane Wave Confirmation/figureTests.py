import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


N = 2
x = [1, 2]
y = [2, 1]
colors = [(0, 1, 1), (1, 1, 0)]
# area = np.pi * (15 * np.random.rand(N))**2  # 0 to 15 point radiuses
area = np.pi * (15)**2

plt.scatter(x, y, s=area, c=colors, alpha=0.5)
print colors
plt.show()