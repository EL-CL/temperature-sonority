import get_sonority_lib as lib
import os
from sys import argv

raw_path = argv[1]

doculects = lib.open_doculects(raw_path)
lib.validate(doculects)  # optional
doculects = lib.filter_doculects(doculects)
if os.path.exists('temperatures.csv'):
    with open('temperatures.csv', 'r') as f:
        next(f)
        names = [line.strip().split(',')[0] for line in f if '--' not in line]
    print('After removing doculects without temperature data:')
    _ = lib.filter_doculects([d for d in doculects if d.name in names])


phone_counts = lib.get_phone_counts(doculects)
lib.write_classified_phones(lib.classify_phones(phone_counts), 'phones.csv')  # optional
phones = list(phone_counts.keys())
geometries = lib.get_geometries(doculects)
all_sonority_indices = lib.get_all_sonority_indices(doculects, True, False, phones, None)
lib.write_geometries_and_indices(doculects, all_sonority_indices, geometries, 'sonorities.csv')
