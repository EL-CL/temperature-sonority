import os.path
from sonority_index_lib import *
from pyasjp.api import ASJP
from lingpy.sequence.sound_classes import tokens2class
from lingpy.settings import rc

rc(schema="asjp")

doculects_to_exclude = [
    # Having no vowels
    'Middle Egyptian',
    'Christian Palestinian',
    'Phoenician',
    'Sabean',

    # Having very few vowels
    'Ugaritic',
]


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


def filter_doculects(doculects, words_to_include=None, temperature_data=''):
    print_doculects_info(doculects)
    if words_to_include:
        for d in doculects:
            d.synsets = [s for s in d.synsets if s.meaning in words_to_include]
        print(f'After intersection with {len(words_to_include)}:')
        print_doculects_info(doculects)
    doculects = [d for d in doculects if
                 'Oth' not in d.classification_wals and  # Artificial/Creoles/Pidgins
                 d.code_iso and  # Proto languages
                 not d.long_extinct and  # Ancient languages
                 d.name not in doculects_to_exclude and
                 len(d.synsets) >= 20 and
                 d.latitude is not None]
    print('After filtering:')
    print_doculects_info(doculects)

    if os.path.exists(temperature_data):
        with open(temperature_data, 'r') as f:
            next(f)
            lines = [line for line in f if '--' not in line]
        names = [line.split(',')[0] for line in lines]
        doculects = [d for d in doculects if d.name in names]
        print('After removing doculects without temperature data:')
        print_doculects_info(doculects)
    return doculects


def validate(doculects):
    for doculect in doculects:
        for synset in doculect.synsets:
            for word in synset.words:
                for phone in word2phones(word.form):
                    base = phone2base_and_tags(phone)[0]
                    if len(phone) == 0 or \
                            len(base) == 0 or \
                            [i for i in base if i not in token2type]:
                        print(doculect.name, 'has invalid word:', word)
        tags = [i
                for synset in doculect.synsets
                for word in synset.words
                for phone in word2phones(word.form)
                for i in phone2base_and_tags(phone)[1]]
        tags = list(set(tags))
        if 'vowel' not in tags:
            print(doculect.name, 'has no vowel! Tags:', tags)
        if 'consonant' not in tags:
            print(doculect.name, 'has no consonant! Tags:', tags)


def get_phone_counts(doculects):
    result = {}
    for doculect in doculects:
        for synset in doculect.synsets:
            for word in synset.words:
                for phone in word2phones(word.form):
                    result[phone] = result.get(phone, 0) + 1
    print('Total types of phones:', len(result.keys()))
    print('Counts of all phones:', sum(result.values()))
    print()
    return result


def get_word_structures(doculects):
    set_token2index(0, 1)  # Use C-V map
    result = {}
    for doculect in doculects:
        for synset in doculect.synsets:
            for word in synset.words:
                word = ''.join(['V' if phone2index(i) > 6 else 'C'
                                for i in word2phones(word.form)])
                result[word] = result.get(word, 0) + 1
    print('Total types of word structures:', len(result))
    print('Counts of all words:', sum(result.values()))
    print()
    return result


def write_word_structures(structures, word_structures_filename, word_lengths_filename):
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
    with open(word_structures_filename, 'w') as f:
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
    with open(word_lengths_filename, 'w') as f:
        f.writelines([','.join(line) + '\n' for line in result])


def doculect2index(doculect, average_by_meaning, with_loan, is_word_length=False, use_lingpy_model=False):
    def word2value(word):
        if is_word_length:
            return len(word2phones(word))
        if use_lingpy_model:
            return average([int(i) for i in tokens2class(word2phones(word), 'art')])
        return word2index(word)
    if average_by_meaning:
        indices = []
        for synset in doculect.synsets:
            synset_indices = [word2value(word.form) for word in synset.words
                              if with_loan or not word.loan]
            if synset_indices:
                indices.append(average(synset_indices))
    else:
        indices = [word2value(word.form) for synset in doculect.synsets
                   for word in synset.words if with_loan or not word.loan]
    return average(indices)


def get_sonority_indices(doculects, average_by_meaning, with_loan, scale_no, index_for_click, use_lingpy_model=False):
    set_token2index(scale_no, index_for_click)
    return [doculect2index(d, average_by_meaning, with_loan) for d in doculects]


def get_sonority_indices_lingpy_model(doculects, average_by_meaning, with_loan):
    return [doculect2index(d, average_by_meaning, with_loan, use_lingpy_model=True) for d in doculects]


def get_word_lengths(doculects, average_by_meaning, with_loan):
    return [doculect2index(d, average_by_meaning, with_loan, is_word_length=True) for d in doculects]


def get_all_sonority_indices(doculects, average_by_meaning, with_loan, indices_for_click):
    scale_nos = range(len(sonority_scales[0][1]))
    if not indices_for_click:
        indices_for_click = [None for _ in scale_nos]
    return [get_sonority_indices(doculects, average_by_meaning, with_loan,
                                 scale_no, indices_for_click[scale_no])
            for scale_no in scale_nos]


def get_geometries(doculects):
    return [(d.longitude, d.latitude) for d in doculects]


def write_geometries_and_indices(doculects, all_sonority_indices, word_lengths, geometries, csv_filename):
    result = [['doculect name', 'longitude', 'latitude', 'classification', 'meaning count', 'word count', 'mean word length'] +
              ['index' + str(i) for i in range(len(all_sonority_indices))]]
    result += [
        [
            doculects[i].name,
            str(geometries[i][0]),
            str(geometries[i][1]),
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
