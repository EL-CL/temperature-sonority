import get_sonority_lib as lib
import os
from sys import argv

raw_path = argv[1]
doculects = lib.open_doculects(raw_path)

lib.validate(doculects)  # optional
phone_counts = lib.get_phone_counts(doculects)
lib.write_classified_phones(lib.classify_phones(phone_counts), 'phones.csv')  # optional

words_to_include = [  # 40 words
    'I', 'you', 'we', 'one', 'two', 'person', 'fish', 'dog', 'louse', 'tree',
    'leaf', 'skin', 'blood', 'bone', 'horn', 'ear', 'eye', 'nose', 'tooth', 'tongue',
    'knee', 'hand', 'breast', 'liver', 'drink', 'see', 'hear', 'die', 'come', 'sun',
    'star', 'water', 'stone', 'fire', 'path', 'mountain', 'night', 'full', 'new', 'name',
]
doculects = lib.filter_doculects(doculects, words_to_include)
if os.path.exists('temperatures.csv'):
    with open('temperatures.csv', 'r') as f:
        next(f)
        names = [line.strip().split(',')[0] for line in f if '--' not in line]
    print('After removing doculects without temperature data:')
    _ = lib.filter_doculects([d for d in doculects if d.name in names])

all_sonority_indices = lib.get_all_sonority_indices(doculects, True, False, None)
word_lengths = lib.get_word_lengths(doculects, True, False)
geometries = lib.get_geometries(doculects)
lib.write_geometries_and_indices(doculects, all_sonority_indices, word_lengths, geometries, 'sonorities.csv')

lib.write_word_structures(lib.get_word_structures(doculects), 'word_structures.csv')
