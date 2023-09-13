import get_sonority_lib as lib
from sys import argv

raw_path = argv[1]
doculects = lib.open_doculects(raw_path)
words_to_include = [  # 40 words
    'I', 'you', 'we', 'one', 'two', 'person', 'fish', 'dog', 'louse', 'tree',
    'leaf', 'skin', 'blood', 'bone', 'horn', 'ear', 'eye', 'nose', 'tooth', 'tongue',
    'knee', 'hand', 'breast', 'liver', 'drink', 'see', 'hear', 'die', 'come', 'sun',
    'star', 'water', 'stone', 'fire', 'path', 'mountain', 'night', 'full', 'new', 'name',
]
doculects = lib.filter_doculects(doculects, words_to_include, 'data/temperatures.csv')

current = lib.get_sonority_indices(doculects, True, False, 0)
merge_vowels = lib.get_sonority_indices(doculects, True, False, 0, merge_vowels=True)
VOWELS = '3iueEoa'


def double_monophthongs(word):
    # Nasalization does not affect calculation
    word = word.replace('*', '')
    i = 0
    while i < len(word):
        if word[i] in VOWELS:
            if i == len(word) - 1 or word[i + 1] not in VOWELS:
                word = word[:i] + word[i] * 2 + word[i + 1:]
            while i < len(word) - 1 and word[i + 1] in VOWELS:
                i += 1
        i += 1
    return word


for doculect in doculects:
    for synset in doculect.synsets:
        for word in synset.words:
            word.form = double_monophthongs(word.form)
double_monophthongs = lib.get_sonority_indices(doculects, True, False, 0)

result = [[
    'doculect_name',
    'current',
    'merge_vowels',
    'double_monophthongs',
]]
result += [[
    doculects[i].name,
    '%.4f' % current[i],
    '%.4f' % merge_vowels[i],
    '%.4f' % double_monophthongs[i],
] for i, _ in enumerate(doculects)]
with open('data/vowel_solutions.csv', 'w') as f:
    f.writelines([','.join(line) + '\n' for line in result])
