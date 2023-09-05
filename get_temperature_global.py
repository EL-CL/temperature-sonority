from time import time
import get_temperature_lib as lib
import numpy as np
from sys import argv

path = argv[1]

# Get data of 1982 Jan to see filter points without temperature
condition = np.full((1500, 3600), True)
temperatures = lib.get_temperatures_by_condition(path, condition, False, range(1982, 1983), range(1, 2))
# Lines with temperature
idxs = ~temperatures.values.mask.flatten()
points = np.extract(np.stack((idxs, idxs), axis=-1), temperatures.points).reshape(-1, 2)

for i in range(41):
    s = time()
    year = 1982 + i
    temperatures_i = lib.get_temperatures_by_points(path, points, False, range(year, year + 1))
    if i == 0:
        temperatures = temperatures_i
    else:
        temperatures.values += temperatures_i.values
    print(f'Read {year} done,', round(time() - s, 2), 's')
    print()

temperatures.values /= 41
s = time()
lib.write_temperatures_by_points_global(temperatures, 'data/temperature_global.csv')
print(f'Write done,', round(time() - s, 2), 's')
