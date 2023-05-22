import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import colorsys


def read_global_temperature(filename):
    return np.genfromtxt(filename, delimiter=',', usemask=True)

def read_sonorities(filename, temperatures_filename):
    with open(filename, 'r') as f:
        next(f)
        data = [line.strip('\n').split(',') for line in f]
    with open(temperatures_filename, 'r') as f:
        next(f)
        names = [line.strip().split(',')[0] for line in f if '--' not in line]
    data = [line for line in data if line[0] in names]
    # return [(lon, lat, sonority index)]
    return [[float(line[i]) for line in data] for i in (1, 2, 6)]


def new_cmap(cm_object, saturation_factor, lightness_factor):
    my_cmap = cm_object(np.arange(cm_object.N))
    my_cmap = np.array([colorsys.rgb_to_hls(*i) for i in my_cmap[:, 0:3]])
    my_cmap[:, 1] *= lightness_factor
    my_cmap[:, 2] *= saturation_factor
    my_cmap = np.minimum(my_cmap, 1)
    my_cmap = np.array([colorsys.hls_to_rgb(*i) for i in my_cmap])
    my_cmap = ListedColormap(my_cmap)
    return my_cmap


t = read_global_temperature('temperature_global.csv')
sx, sy, sv = read_sonorities('sonorities.csv', 'temperatures.csv')

# plt.hist(t.flatten(), bins=30), plt.show()
t = np.power(t - np.nanmin(t) + 0.1, 1.6)
t = t / np.nanmax(t)
# plt.hist(t.flatten(), bins=30), plt.show()

plt.rcParams['figure.figsize'] = (20, 10)
fig = plt.figure()
ax_t = fig.add_subplot(111)
ax_s = fig.add_subplot(111, frame_on=False)

cm_t = new_cmap(plt.cm.inferno, 0.65, 0.65)
cm_s = new_cmap(plt.cm.coolwarm, 1, 0.9)
ax_t.imshow(t, origin='lower', aspect='auto', cmap=cm_t, vmin=-0.5, vmax=1.5)
ax_s.scatter(sx, sy, c=sv, cmap=cm_s, s=2)

ax_s.set_xlim(-180, 180)
ax_s.set_ylim(-60, 90)
ax_t.axis('off')
ax_s.axis('off')

plt.savefig('global.png', bbox_inches='tight', pad_inches=0.3, dpi=150)
# plt.savefig('global.pdf', bbox_inches='tight', pad_inches=0.3, dpi=150)
plt.show()
