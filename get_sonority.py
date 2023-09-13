import get_sonority_lib as lib
from sys import argv

raw_path = argv[1]
doculects = lib.open_doculects(raw_path)
lib.validate(doculects)  # optional

words_to_include = [  # 40 words
    'I', 'you', 'we', 'one', 'two', 'person', 'fish', 'dog', 'louse', 'tree',
    'leaf', 'skin', 'blood', 'bone', 'horn', 'ear', 'eye', 'nose', 'tooth', 'tongue',
    'knee', 'hand', 'breast', 'liver', 'drink', 'see', 'hear', 'die', 'come', 'sun',
    'star', 'water', 'stone', 'fire', 'path', 'mountain', 'night', 'full', 'new', 'name',
]
doculects = lib.filter_doculects(doculects, words_to_include, 'data/temperatures.csv')
phone_counts = lib.get_phone_counts(doculects)  # optional
lib.write_classified_phones(lib.classify_phones(phone_counts), 'data/phones.csv')  # optional

all_sonority_indices = lib.get_all_sonority_indices(doculects, True, False)
all_sonority_indices.append(lib.get_sonority_indices_lingpy_model(doculects, True, False))
word_lengths = lib.get_word_lengths(doculects, True, False)
geometries = lib.get_geometries(doculects)
lib.write_geometries_and_indices(doculects, all_sonority_indices, word_lengths, geometries, 'data/sonorities.csv')

lib.write_word_structures(lib.get_word_structures(doculects), 'data/word_structures.csv', 'data/word_lengths.csv')
