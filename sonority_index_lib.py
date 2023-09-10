import re
from numpy import average

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
