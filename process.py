import process_lib as lib

data = lib.read_data('data/temperatures.csv', 'data/sonorities.csv')
data_macroarea = lib.grouped_by(data, 'Macroarea')
data_family = lib.grouped_by(data, 'Family')
data_genus = lib.grouped_by(data, 'Genus')
lib.transform_data(data)
lib.transform_data(data_family)
lib.transform_data(data_genus)
lib.write_data(data, 'data/data.csv')
lib.write_data(data_macroarea, 'data/data_macroarea.csv')
lib.write_data(data_family, 'data/data_family.csv')
lib.write_data(data_genus, 'data/data_genus.csv')

lib.plot_macroareas(data)
