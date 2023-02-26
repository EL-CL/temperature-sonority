import get_temperature_lib as lib
from sys import argv

path = argv[1]

names, geometries = lib.read_names_and_geometries('sonorities.csv')
temperatures = lib.get_temperatures_by_geometries(path, geometries, True)
lib.write_temperatures_by_doculects(names, geometries, temperatures, 'temperatures.csv')
