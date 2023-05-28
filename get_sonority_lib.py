import re
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from numpy import average, median
from pyasjp.api import ASJP
import geopandas
from shapely.geometry import Point

sonority_scales = [
    # 0: Parker's
    # 1: Fought's
    # 2: Clements'
    # 3: Obstruent-Sonorant
    # 4: C-V
    # Sonority index for clicks can be re-assigned in set_monophone2scale()
    # Duplicate ASJPcodes will be assigned the minimum index (e.g. p = 1 in Parker's Scale)
    #
    #  ASJPcode      sonority index      type of sounds
    #         scale: 0    1  2  3  4
    ('!        ', [1,     2, 1, 1, 1],           'click'),
    ('        7', [1,     2, 1, 1, 1],  'guttural plosive'),
    ('p  ttTkq ', [1,     2, 1, 1, 1], 'voiceless plosive'),
    ('b  dd gG ', [4,     2, 1, 1, 1],    'voiced plosive'),
    ('   cC    ', [2,     3, 1, 1, 1], 'voiceless affricate'),
    ('   cj    ', [5,   2.5, 1, 1, 1],    'voiced affricate'),
    ('pf8sS    ', [3,     4, 1, 1, 1], 'voiceless fricative'),
    ('bv8zZ    ', [6,     3, 1, 1, 1],    'voiced fricative'),
    ('      xXh', [4,     4, 1, 1, 1],  'guttural fricative'),
    ('m 4nn5N  ', [7,     9, 2, 2, 1],           'nasal'),
    ('   lLLL  ', [9,    17, 3, 2, 1],           'lateral'),
    ('   r     ', [10,   36, 3, 2, 1],           'rhotic'),
    ('w        ', [12,   27, 4, 2, 2],       'back semivowel'),
    ('     y   ', [12,   43, 4, 2, 2],      'front semivowel'),
    ('      3  ', [13,   55, 5, 2, 3],   'interior vowel'),
    ('     i   ', [15,   41, 5, 2, 3], 'high front vowel'),
    ('      u  ', [15,   65, 5, 2, 3],  'high back vowel'),
    ('     e   ', [16,   69, 5, 2, 3],        'mid vowel'),
    ('     Eo  ', [16.5, 75, 5, 2, 3],    'mid/low vowel'),
    ('     a   ', [17,  100, 5, 2, 3],        'low vowel'),
]

# phone: a phone presented in ASJPcode letter(s)
# monophone: a single-letter phone
# base: the base letter of a multi-letter phone (e.g. `t` in `thy`)
monophone2type = dict([(phone, e[2])
                       for e in reversed(sonority_scales)
                       for phone in e[0].replace(' ', '')])
monophone2index = {}
phone2index_cache = {}
phone2base_and_types_cache = {}
word2phones_cache = {}


def set_index_maps(scale_no, index_for_click):
    monophone2index.clear()
    phone2index_cache.clear()
    phone2base_and_types_cache.clear()
    word2phones_cache.clear()
    for e in sonority_scales:
        for phone in e[0].replace(' ', ''):
            if phone not in monophone2index:
                monophone2index[phone] = e[1][scale_no]
    if index_for_click:
        monophone2index['!'] = index_for_click


def phone2index(phone):
    if phone in phone2index_cache:
        return phone2index_cache[phone]

    base, types = phone2base_and_types(phone)
    indices = [monophone2index[i] for i in base]
    index = average(indices) if 'prenasalized' in types else min(indices)
    # Sonority index of devoiced sonorants will be treated equal to 'h'
    if 'aspirated' in types:
        index = min(index, monophone2index['h'])
    # Remaining types of secondary articulation will be ignored

    phone2index_cache[phone] = index
    return index


def phone2base_and_types(phone):
    if phone in phone2base_and_types_cache:
        return phone2base_and_types_cache[phone]

    tags = []
    if '*' in phone:
        tags.append('nasalized')
    if '"' in phone:
        tags.append('glottalized')
    suffix_tags = {
        'w': 'labialized',
        'y': 'palatalized',
        'h': 'aspirated',  # including devoiced
        'x': 'velarized',
        'X': 'pharyngealized',
    }
    base = phone.replace('*', '').replace('"', '')
    while len(base) > 1:
        if base[-1] in suffix_tags:
            tag = suffix_tags[base[-1]]
            if tag not in tags:
                tags.append(tag)
            base = base[:-1]
        else:
            break
    if len(base) > 1 \
            and monophone2type[base[0]] == 'nasal' \
            and re.search('click|plos|fric', monophone2type[base[1]]):
        # nasal + obstruent means prenasalized
        tags.append('prenasalized')
    tags.append(f'len-{len(base)}')
    tags.append('semivowel' if 'semivowel' in monophone2type[phone[0]]
                else 'vowel' if 'vowel' in monophone2type[phone[0]]
                else 'consonant')
    tags.reverse()
    result = (base, tags)
    phone2base_and_types_cache[phone] = result
    return result


def word2phones(word):
    if type(word) is not str:
        word = word.form
    word = word.replace(' ', '')

    if word in word2phones_cache:
        return word2phones_cache[word]

    # Fix invalid spellings
    patches = {
        '""': '"',
        'a*g~': 'a*g',
        'i*7~': 'i*7',
        'a*d~': 'a*d',
        'a*7~': 'a*7',
        'i*dy$': 'i*dy~',
        'eq"X$': 'eq"X~',
    }
    for k in patches:
        if k in word:
            word = word.replace(k, patches[k])
    if word == '~E':
        word = 'E'
    if len(word) > 2 and word[1] == '~':
        word = word[0] + word[2:]

    word = '│' + re.sub('(.)', r'\1│', word)

    unit = '([^│]*)│'
    word = re.sub('│' + unit * 1 + '\*', r'│\1*', word)
    word = re.sub('│' + unit * 1 + '"', r'│\1"', word)
    word = re.sub('│' + unit * 2 + '~', r'│\1\2', word)
    word = re.sub('│' + unit * 2 + '~', r'│\1\2', word)
    word = re.sub('│' + unit * 3 + '\$', r'│\1\2\3', word)

    word = word.strip('│')
    phones = word.split('│')
    word2phones_cache[word] = phones
    return phones


def word2index(word, word2index_cache, is_word_length=False):
    if type(word) is not str:
        word = word.form
    if word not in word2index_cache:
        word2index_cache[word] = \
            average([phone2index(i) for i in word2phones(word)]) \
            if not is_word_length else len(word2phones(word))
    return word2index_cache[word]


def doculect2index(doculect, average_by_meaning, with_loan, word2index_cache, is_word_length=False):
    if average_by_meaning:
        indices = []
        for synset in doculect.synsets:
            synset_indices = [word2index(i, word2index_cache, is_word_length)
                              for i in synset.words if with_loan or not i.loan]
            if synset_indices:
                indices.append(average(synset_indices))
    else:
        indices = [word2index(i, word2index_cache, is_word_length)
                   for synset in doculect.synsets
                   for i in synset.words if with_loan or not i.loan]
    return average(indices)


def classify_phones(phone_counts):
    result = {}
    for phone in phone_counts:
        tags = '; '.join(phone2base_and_types(phone)[1])
        if tags not in result.keys():
            result[tags] = {}
        result[tags][phone] = phone_counts[phone]
    return result


def write_classified_phones(classified, csv_filename):
    result = [['phone', 'base', 'count', 'tags']]
    for tags in sorted(classified.keys()):
        lines = [[
            phone,
            phone2base_and_types(phone)[0],
            classified[tags][phone],
            tags,
        ] for phone in classified[tags]]
        lines = sorted(lines, key=lambda l: l[1])
        lines = sorted(lines, key=lambda l: l[2], reverse=True)
        lines = [[str(i) for i in line] for line in lines]
        result += lines
    with open(csv_filename, 'w') as f:
        f.writelines([','.join(line) + '\n' for line in result])


# ============


def open_doculects(raw_dir):
    asjp = ASJP(raw_dir)
    doculects = list(asjp.iter_doculects())
    return doculects


def print_doculects_info(doculects):
    print(
        'Total:', len(doculects), 'doculects, having',
        sum([len(doculect.synsets)
            for doculect in doculects]), 'meanings and',
        sum([sum([len(synset.words) for synset in doculect.synsets])
            for doculect in doculects]), 'words',
    )
    names = [(
        d.code_iso,
        (d.classification_wals or '').split('.')[0],
        (d.classification_ethnologue or '').split(',')[0],
        (d.classification_glottolog or '').split(',')[0],
    ) for d in doculects]
    counts = [len(set([c[i] for c in names if c[i]]))
              for i in range(len(names[0]))]
    # Null language/family names are excluded
    print(
        'Corresponding to:',
        counts[0], 'languages,',
        counts[1], 'families (WALS),',
        counts[2], 'families (Ethnologue),',
        counts[3], 'families (Glottolog)',
    )
    print()


def filter_doculects(doculects, words_to_include=None):
    print_doculects_info(doculects)
    if words_to_include:
        for d in doculects:
            d.synsets = [s for s in d.synsets if s.meaning in words_to_include]
        print(f'After intersection with {len(words_to_include)}:')
        print_doculects_info(doculects)
    doculects = [d for d in doculects if
                 'Oth' not in d.classification_wals and
                 d.code_iso and  # proto languages
                 not d.long_extinct and  # ancient languages
                 d.name not in [
                     # having no vowels
                     'Middle Egyptian',
                     'Christian Palestinian',
                     'Phoenician',
                     'Sabean',
                     # having very few vowels
                     'Ugaritic',
                 ] and
                 len(d.synsets) >= 20 and
                 d.latitude is not None]
    print(f'After filtering:')
    print_doculects_info(doculects)
    return doculects


def validate(doculects):
    for doculect in doculects:
        for synset in doculect.synsets:
            for word in synset.words:
                for phone in word2phones(word):
                    base = phone2base_and_types(phone)[0]
                    if len(phone) == 0 or \
                            len(base) == 0 or \
                            [i for i in base if i not in monophone2type]:
                        print(doculect.name, 'has invalid word:', word)
        types = [i
                 for synset in doculect.synsets
                 for word in synset.words
                 for phone in word2phones(word)
                 for i in phone2base_and_types(phone)[1]]
        types = list(set(types))
        if 'vowel' not in types:
            print(doculect.name, 'has no vowel! Types:', types)
        if 'consonant' not in types:
            print(doculect.name, 'has no consonant! Types:', types)


def get_phone_counts(doculects):
    result = {}
    for doculect in doculects:
        for synset in doculect.synsets:
            for word in synset.words:
                for phone in word2phones(word):
                    result[phone] = result.get(phone, 0) + 1
    print('Total types of phones:', len(result.keys()))
    print('Counts of all phones:', sum(result.values()))
    print()
    return result


def get_word_structures(doculects):
    set_index_maps(0, 1)  # Use C-V map
    result = {}
    for doculect in doculects:
        for synset in doculect.synsets:
            for word in synset.words:
                word = ''.join(['V' if phone2index(i) > 6 else 'C'
                                for i in word2phones(word)])
                result[word] = result.get(word, 0) + 1
    print('Total types of word structures:', len(result))
    print('Counts of all words:', sum(result.values()))
    print()
    return result


def write_word_structures(structures, csv_filename):
    def get_ratio(cs, vs):
        return '%.2f' % (cs / vs) if vs else 'C-only'

    result = [['structure', 'length', 'C-V ratio', 'count']]
    lines = [[
        s,
        len(s),
        get_ratio(s.count('C'), s.count('V')),
        structures[s],
    ] for s in structures]
    lines = sorted(lines, key=lambda l: l[0])
    lines = sorted(lines, key=lambda l: l[1])
    lines = sorted(lines, key=lambda l: l[3], reverse=True)
    lines = [[str(i) for i in line] for line in lines]
    result += lines
    with open(csv_filename, 'w') as f:
        f.writelines([','.join(line) + '\n' for line in result])

    grouped = {}
    for s in structures:
        l = len(s)
        if l not in grouped:
            grouped[l] = [0, 0, 0]  # count, Cs, Vs
        grouped[l][0] += structures[s]
        grouped[l][1] += s.count('C') * structures[s]
        grouped[l][2] += s.count('V') * structures[s]
    result = [['length', 'C-V ratio', 'count']]
    lines = [[
        k,
        get_ratio(v[1], v[2]),
        v[0],
    ] for k, v in grouped.items()]
    lines = sorted(lines, key=lambda l: l[0])
    lines = [[str(i) for i in line] for line in lines]
    result += lines
    with open(csv_filename.replace('.csv', '_grouped.csv'), 'w') as f:
        f.writelines([','.join(line) + '\n' for line in result])


def get_sonority_indices(doculects, average_by_meaning, with_loan, scale_no, index_for_click):
    word2index_cache = {}
    set_index_maps(scale_no, index_for_click)
    return [doculect2index(d, average_by_meaning, with_loan, word2index_cache) for d in doculects]


def get_word_lengths(doculects, average_by_meaning, with_loan):
    word2index_cache = {}
    return [doculect2index(d, average_by_meaning, with_loan, word2index_cache, True) for d in doculects]


def get_all_sonority_indices(doculects, average_by_meaning, with_loan, indices_for_click):
    scale_nos = range(len(sonority_scales[0][1]))
    if not indices_for_click:
        indices_for_click = [None for _ in scale_nos]
    return [get_sonority_indices(doculects, average_by_meaning, with_loan,
                                 scale_no, indices_for_click[scale_no])
            for scale_no in scale_nos]


def get_geometries(doculects):
    return [Point((d.longitude, d.latitude)) for d in doculects]


def write_geometries_and_indices(doculects, all_sonority_indices, word_lengths, geometries, csv_filename):
    result = [['doculect name', 'longitude', 'latitude', 'classification', 'meaning count', 'word count', 'mean word length'] +
              ['index' + str(i) for i in range(len(all_sonority_indices))]]
    result += [
        [
            doculects[i].name,
            str(geometries[i].x),
            str(geometries[i].y),
            doculects[i].classification_wals,
            str(len(doculects[i].synsets)),
            str(sum([len(synset.words) for synset in doculects[i].synsets])),
            '%.4f' % word_lengths[i],
        ] +
        ['%.4f' % sonority_indices[i]
            for sonority_indices in all_sonority_indices]
        for i, _ in enumerate(doculects)]
    with open(csv_filename, 'w') as f:
        f.writelines([','.join(line) + '\n' for line in result])


def plot(geometry, indices, sects_count, save_to='', save_only=False):
    world_path = geopandas.datasets.get_path('naturalearth_lowres')
    world = geopandas.read_file(world_path)
    ax = world.boundary.plot(linewidth=0.3)

    index_min = min(indices)
    index_max = max(indices)
    print('index_min =', index_min)
    print('index_max =', index_max)
    print('index_avr =', average(indices))
    print('index_med =', median(indices))

    indices_sorted = sorted(indices)
    plot_min = int(index_min)
    plot_max = int(index_max) + 1
    step = 0.5

    stops = int((plot_max - plot_min) / step + 1)
    geometry_added = [Point(((i - stops / 2) * 5, -50)) for i in range(stops)]
    indices_added = [i * step + plot_min for i in range(stops)]

    sects_in = []
    sects_out = []
    for i in range(sects_count + 1):
        k = i / sects_count
        sects_in.append(indices_sorted[int((len(indices_sorted) - 1) * k)])
        sects_out.append(k)

    def mapp(index):
        if index < sects_in[0]:
            return 0
        if index >= sects_in[-1]:
            return 1
        for i in range(len(sects_in) - 1):
            start = sects_out[i]
            width = sects_out[i + 1] - sects_out[i]
            if index < sects_in[i + 1]:
                return (index - sects_in[i]) / (sects_in[i + 1] - sects_in[i]) * width + start

    gdf = geopandas.GeoDataFrame(geometry=geometry + geometry_added)
    gdf.plot(ax=ax,
             color=cm.cool([mapp(i) for i in indices + indices_added]),
             markersize=0.8,
             legend=True)
    for i in range(stops):
        if i % 2:
            continue
        plt.text(
            geometry_added[i].x - 1.5,
            geometry_added[i].y - 5,
            int(indices_added[i]),
        )
    plt.xlim([-179.8, 179.8])
    plt.ylim([-89.8, 89.8])
    plt.rcParams["figure.figsize"] = (19.2, 10)
    plt.rcParams['font.serif'] = ['SimHei']
    plt.text(geometry_added[0].x - 18, geometry_added[0].y - 2,
             '平均响度', fontdict={'family': 'serif'})

    rect = Rectangle((geometry_added[0].x - 20, geometry_added[0].y - 7.5),
                     geometry_added[-1].x - geometry_added[0].x + 24,
                     12, linewidth=0.5, edgecolor='black', facecolor='none')

    # Add the patch to the Axes
    ax.add_patch(rect)
    ax.set_axis_off()

    if save_to:
        plt.savefig(save_to, bbox_inches='tight',
                    pad_inches=0.3, dpi=150)
    if not save_only:
        plt.show()
    return plt
