import numpy as np
import matplotlib.pyplot as plt


t = ['2022-02', '2022-03' , '2022-04', '2022-06', '2022-07', '2022-10', '2022-11', '2022-12', '2023-02', '2023-03']
data1 = [165, 438, 654, 434, 336, 869, 1248, 358, 834, 438]
data2 = [1.47, 3.82, 6.41, 10.17, 2.23, 8.38, 33.11, 10.87, 31.04, 3.82]

fig, ax1 = plt.subplots()

color = 'tab:red'
# ax1.set_xlabel('Experiment Month')
ax1.set_xticklabels(t, rotation=45, ha='right')
# ax1.xticks(rotation = 45)
# ax1.set_xticks(t)
ax1.set_ylabel('# of samples', color=color)
ax1.plot(t, data1, 'bo', color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('TB', color=color)  # we already handled the x-label with ax1
ax2.plot(t, data2, 'go', color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
# plt.xticks(rotation = 45) # Rotates X-Axis Ticks by 45-degrees
plt.show()
