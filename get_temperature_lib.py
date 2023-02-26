from time import time
import numpy as np
from netCDF4 import Dataset

BUF_SIZE = 20 * 1024 * 1024  # 20 MB


class Temperatures:
    def __init__(self, year_months, points, values):
        self.year_months = year_months
        self.points = points
        self.values = values


def coord_2_point(coord):  # coord: (lon, lat)
    def round_value(fl):
        fl *= 10
        if fl < 0:
            fl -= 1
        return round(0.05 + int(fl) / 10, 2)
    lon = round_value(coord[0])
    lat = round_value(coord[1])
    return round((lon + 179.95) * 10), round((lat + 59.95) * 10)


def read_names_and_geometries(csv_filename):
    with open(csv_filename, 'r') as f:
        next(f)
        data = [line.strip('\n').split(',') for line in f]
        return [line[0] for line in data], [(float(line[1]), float(line[2])) for line in data]


def get_temperatures_by_geometries(path, geometries, use_neighbors=True, year_range=range(1982, 2022), month_range=range(1, 13), param='Tair_f_tavg'):
    points = set([coord_2_point(i) for i in geometries])
    return get_temperatures_by_points(path, points,
                                      use_neighbors, year_range, month_range, param)


def get_temperatures_by_points(path, points, use_neighbors=True, year_range=range(1982, 2022), month_range=range(1, 13), param='Tair_f_tavg'):
    condition = np.full((1500, 3600), False)
    for point in points:
        condition[point[1]][point[0]] = True
    return get_temperatures_by_condition(path, condition,
                                         use_neighbors, year_range, month_range, param)


def get_temperatures_by_condition(path, condition, use_neighbors=True, year_range=range(1982, 2022), month_range=range(1, 13), param='Tair_f_tavg'):
    # Rebuild list of points from condition matrix
    points = np.where(condition)
    points = np.array([points[1], points[0]]).T

    dct = {}
    for year in year_range:
        for month in month_range:
            ym = (year, month)
            filename = path \
                / ('%d' % year) \
                / ('FLDAS_NOAH01_C_GL_M.A%d%02d.001.nc' % (year, month))
            with open(filename, 'rb') as f:
                b = f.read()
            nc = Dataset('/', memory=b)
            data = nc[param][0]
            nc.close()
            dct[ym] = np.extract(condition, data)

            # For points without climate data, try neighbors
            if use_neighbors:
                idxs = np.where(dct[ym] == np.ma.masked)[0]
                for i in idxs:
                    x, y = points[i][0], points[i][1]
                    for offset in range(1, 6):
                        neighbors = [[
                            (x - offset, y + d),
                            (x + d, y - offset),
                            (x + offset, y + d),
                            (x + d, y + offset),
                        ] for d in range(-offset, offset + 1)]
                        neighbors = set([p for l in neighbors for p in l])
                        for p in neighbors:
                            v = data[p[1] % 1500][p[0] % 3600]
                            if not np.ma.is_masked(v):
                                break
                        if not np.ma.is_masked(v):
                            dct[ym][i] = v
                            break
            dct[ym] = np.round(dct[ym] - 273.15, 3)
            print('%d/%d' % (year, month), 'done')
    return Temperatures(list(dct.keys()), points, np.ma.array(list(dct.values())).T)


def comma_join(lst):
    return ','.join([str(i) for i in lst]) + '\n'


def write_temperatures_by_points(temperatures: Temperatures, csv_filename):
    with open(csv_filename, 'w', BUF_SIZE) as f:
        f.write(comma_join(
            ['point x', 'point y'] + ['%d/%d' % i for i in temperatures.year_months]))
        for i, v in enumerate(temperatures.values):
            f.write(comma_join(list(temperatures.points[i]) + list(v)))


def write_temperatures_by_doculects(names, geometries, temperatures: Temperatures, csv_filename):
    with open(csv_filename, 'w', BUF_SIZE) as f:
        f.write(comma_join(
            ['doculect name'] + ['%d/%d' % i for i in temperatures.year_months]))

        def point_2_key(point):
            return int(point[0] * 10000 + point[1])
        index_dict = dict([(point_2_key(v), i)
                           for i, v in enumerate(temperatures.points)])
        for j, name in enumerate(names):
            f.write(comma_join([name] +
                               list(temperatures.values[
                                   index_dict[
                                       point_2_key(
                                           coord_2_point(geometries[j]))
                                   ]
                               ])))
