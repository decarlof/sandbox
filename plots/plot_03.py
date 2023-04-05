import numpy as np
import matplotlib.pyplot as plt


dates = ('2022-02', '2022-03' , '2022-04', '2022-06', '2022-07', '2022-10', '2022-11', '2022-12', '2023-02', '2023-03')
y_pos = np.arange(len(dates))
number_of_samples = [165, 438, 654, 434, 336, 869, 1248, 358, 834, 2185]
# tera_bytes = np.random.rand(len(dates))
tera_bytes = [1.47, 3.82, 6.41, 10.17, 2.23, 8.38, 33.11, 10.87, 31.04, 37.36]

fig, ax = plt.subplots()

hbars = ax.barh(y_pos, number_of_samples, xerr=tera_bytes, align='center')
ax.set_yticks(y_pos, labels=dates)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Number of Samples')
ax.set_title('Tomography data at beamline 2-BM')

# Label with given captions, custom padding and annotate options
ax.bar_label(hbars, labels=['%.2f TB' % tb for tb in tera_bytes], padding=8, color='b', fontsize=14)
ax.set_xlim(right=1600)

plt.show()
