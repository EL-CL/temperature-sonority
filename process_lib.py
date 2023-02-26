from time import time
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import geopandas
from shapely.geometry import Point
import matplotlib.cm as cm
from sklearn.preprocessing import PowerTransformer


def coord_2_macroarea(coord):  # coord: (lon, lat)
    x, y = coord

    def below(x1, y1, x2, y2):
        return (x2 - x1) * (y - y1) <= (y2 - y1) * (x - x1)
    if \
            x <= -168 or \
            x <= -98 and below(-168, 40, -98, 5) or \
            x <= -98 and y <= 5:
        return 'Pacific'
    if \
            x <= -28 and below(-94, 86, -28, 46) or \
            x <= -28 and y <= 46:
        if \
                y <= 5 or \
                -80 < x and x <= -66 and y <= 13 or \
                -66 < x and y <= 11:
            return 'SouthAmerica'
        return 'NorthAmerica'
    if x <= 62:
        if \
                x <= -3 and y <= 36 or \
                -3 < x and x <= 3 and below(-3, 36, 3, 38) or \
                3 < x and x <= 11 and y <= 38 or \
                11 < x and x <= 13 and below(11, 38, 13, 34) or \
                13 < x and x <= 30 and y <= 34 or \
                30 < x and x <= 44 and below(30, 34, 44, 11) or \
                44 < x and below(44, 11, 62, 17):
            return 'Africa'
        return 'Eurasia'
    if \
            x <= 127 and y <= -13 or \
            127 < x and x <= 145 and y <= -10 or \
            145 < x and x <= 162 and below(145, -10, 162, -30):
        return 'Australia'
    if \
            x <= 97 and below(62, 0, 97, 6) or \
            97 < x and x <= 104 and below(97, 6, 104, 0) or \
            104 < x and x <= 120 and below(104, 0, 120, 22) or \
            120 < x and x <= 123 and y <= 26 or \
            123 < x and y <= 22:
        return 'Pacific'
    return 'Eurasia'


def transform(lst, title='', print_message=False, do_plot=False):
    lst = np.array(lst, dtype=float).reshape(-1, 1)
    bc = PowerTransformer(method='box-cox')
    yj = PowerTransformer(method='yeo-johnson')

    offset = (-lst.min() + 0.1) if (lst.min() < 0) else 0
    lst_bc = bc.fit(lst + offset).transform(lst + offset).flatten()
    lst_yj = yj.fit(lst).transform(lst).flatten()
    lambda_bc = round(bc.lambdas_[0], 2)
    lambda_yj = round(yj.lambdas_[0], 2)

    message = '\n'.join([
        title,
        '',
        'Box-Cox',
        'Min:  %.2f → %.2f' % (lst.min(), lst_bc.min()),
        'Aver: %.2f → %.2f' % (lst.mean(), lst_bc.mean()),
        'Max:  %.2f → %.2f' % (lst.max(), lst_bc.max()),
        'Yeo-Johnson',
        'Min:  %.2f → %.2f' % (lst.min(), lst_yj.min()),
        'Aver: %.2f → %.2f' % (lst.mean(), lst_yj.mean()),
        'Max:  %.2f → %.2f' % (lst.max(), lst_yj.max()),
    ])
    if print_message:
        print(message)
    if do_plot:
        is_sonority = lst.max() < 20
        _, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 7))
        axes = axes.flatten()

        axes[1].axis('off')
        axes[1].text(0, 0, message, fontsize=12)
        axes[0].hist(lst, bins=30)
        axes[2].hist(lst_bc, bins=30)
        axes[3].hist(lst_yj, bins=30)
        axes[0].set_title('Original')
        axes[2].set_title('Box-Cox' + r'  $\lambda$ = {}'.format(lambda_bc))
        axes[3].set_title(
            'Yeo-Johnson' + r'  $\lambda$ = {}'.format(lambda_yj))
        if not is_sonority:
            axes[0].set_xlim([-20.5, 40.5])
            axes[2].set_xlim([-2.5, 3.2])
            axes[3].set_xlim([-2.5, 3.2])

        plt.tight_layout()
        plt.subplots_adjust(left=0.117, right=0.926, wspace=0.367)
        plt.show()
    return lst_bc, lst_yj, lambda_bc, lambda_yj


def read_data(temperatures_filename, sonorities_filename):
    with open(temperatures_filename, 'r') as f:
        next(f)
        temperatures = [line.strip('\n').split(',') for line in f]
    temperatures = [(line[0], [float(i) for i in line[1:]])
                    for line in temperatures if line[1] != '--']
    temperatures = dict(temperatures)

    with open(sonorities_filename, 'r') as f:
        next(f)
        data = [line.strip('\n').split(',') for line in f]
    data = [dict(
        [
            ('Name', line[0]),
            ('Lon', float(line[1])),
            ('Lat', float(line[2])),
            ('Macroarea', coord_2_macroarea((float(line[1]), float(line[2])))),
            # ('Classification', line[3]),
            ('Family', line[3].split('.')[0]),
        ] + [(f'Index{i}', float(v)) for i, v in enumerate(line[6:])] +
        list(process_temperature(temperatures[line[0]]).items())
    ) for line in data if line[0] in temperatures]
    print('Doculects count:', len(data))
    return data


def process_temperature(temperatures):
    mean_monthly = np.average(np.array(temperatures).reshape(-1, 12), 0)
    result = {
        'T': np.average(temperatures),
        'T_max': max(mean_monthly),
        'T_min': min(mean_monthly),
        'T_sd': np.std(temperatures)
    }
    result['T_diff'] = result['T_max'] - result['T_min']
    return result


def grouped_by(data, key):
    num_keys = [k for k in data[0].keys() if 'Index' in k or 'T' in k]
    names = set([d[key] for d in data])
    return [dict([(key, name)] +
                 [(k, func([i[k] for i in data if i[key] == name]))
                  for k in num_keys] +
                 [('Method', method)]
                 ) for name in names for (method, func) in [('mean', np.average), ('median', np.median)]]


def transform_data(data, do_plot=False):
    def transform_key(key):
        transformed = transform([d[key] for d in data], key, do_plot)[0]
        for i, d in enumerate(data):
            d[key + '_trans'] = transformed[i]
    num_keys = [k for k in data[0].keys() if 'Index' in k or 'T' in k]
    for k in num_keys:
        transform_key(k)


def write_data(data, csv_filename):
    # Do not write longitude and latitude
    keys = [k for k in data[0].keys() if 'L' not in k]
    result = [list(keys)]
    result += [[str(i[k]) for k in keys] for i in data]
    with open(csv_filename, 'w') as f:
        f.writelines([','.join([str(i) for i in line]) + '\n'
                      for line in result])


def plot_macroareas(data):
    world_path = geopandas.datasets.get_path('naturalearth_lowres')
    world = geopandas.read_file(world_path)
    ax = world.boundary.plot(linewidth=0.3)

    geometry = [Point((d['Lon'], d['Lat'])) for d in data]
    gdf = geopandas.GeoDataFrame(geometry=geometry)
    macroarea_order = ['Pacific', 'SouthAmerica', 'NorthAmerica',
                       'Africa', 'Eurasia', 'Australia']
    values = [macroarea_order.index(d['Macroarea']) / len(macroarea_order)
              for d in data]
    gdf.plot(ax=ax,
             color=cm.gist_rainbow(values),
             markersize=0.8,
             legend=True)
    ax.set_axis_off()
    plt.show()
