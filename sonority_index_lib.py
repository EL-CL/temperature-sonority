import re
from numpy import average
from lingpy.sequence.sound_classes import asjp2tokens

sonority_scales = [
    # Scale no:
    # 0: Parker's
    # 1: Fought's
    # 2: List's
    # 3: Clements's
    # 4: Obstruent-Sonorant
    # 5: C-V
    # Sonority index for clicks can be re-assigned in set_token2index()
    #
    # ASJPcode     Sonority index      Type of sounds
    #     scale no: 0   1  2  3  4  5
    ('!      ', [1,     2, 1, 1, 1, 1],           'click'),
    ('      7', [1,     2, 1, 1, 1, 1],  'guttural plosive'),
    ('p tTkq ', [1,     2, 1, 1, 1, 1], 'voiceless plosive'),
    ('b d gG ', [4,     2, 1, 1, 1, 1],    'voiced plosive'),
    ('  cC   ', [2,     3, 2, 1, 1, 1], 'voiceless affricate'),
    ('   j   ', [5,   2.5, 2, 1, 1, 1],    'voiced affricate'),
    ('f8sS   ', [3,     4, 3, 1, 1, 1], 'voiceless fricative'),
    ('v zZ   ', [6,     3, 3, 1, 1, 1],    'voiced fricative'),
    ('    xXh', [4,     4, 3, 1, 1, 1],  'guttural fricative'),
    ('m4n5N  ', [7,     9, 4, 2, 2, 1],           'nasal'),
    ('  lL   ', [9,    17, 5, 3, 2, 1],           'lateral'),
    ('  r    ', [10,   36, 5, 3, 2, 1],           'rhotic'),
    ('    w  ', [12,   27, 6, 4, 2, 2],       'back semivowel'),
    ('   y   ', [12,   43, 6, 4, 2, 2],      'front semivowel'),
    ('    3  ', [13,   55, 7, 5, 2, 3],   'interior vowel'),
    ('   i   ', [15,   41, 7, 5, 2, 3], 'high front vowel'),
    ('    u  ', [15,   65, 7, 5, 2, 3],  'high back vowel'),
    ('   e   ', [16,   69, 7, 5, 2, 3],        'mid vowel'),
    ('   Eo  ', [16.5, 75, 7, 5, 2, 3],    'mid/low vowel'),
    ('   a   ', [17,  100, 7, 5, 2, 3],        'low vowel'),
]

token2type = dict([(token, line[2]) for line in sonority_scales
                   for token in line[0].replace(' ', '')])
token2index = {}

asjp2tokens_patch = {
    # Both combination orders are actually correct, but asjp2tokens() currently recognizes only one of them
    '*$': '$*',
    '*~': '~*',
    '"$': '$"',
    '"~': '~"',
}

suffix_tags = {
    'w': 'labialized',
    'y': 'palatalized',
    'h': 'aspirated/devoiced',
    'x': 'velarized',
    'X': 'pharyngealized',
    '"': 'glottalized',
    '*': 'nasalized',
}


def set_token2index(scale_no, index_for_clicks):
    token2index.clear()
    for line in sonority_scales:
        for token in line[0].replace(' ', ''):
            token2index[token] = line[1][scale_no]
    if index_for_clicks:
        token2index['!'] = index_for_clicks


# Phone: a phone (segment) presented in one or multiple ASJPcode tokens
# Base: the base token(s) of a multi-token phone (e.g. 'thy' has the base 't' and suffixes 'h', 'y')
def phone2index(phone):
    base, tags = phone2base_and_tags(phone)
    indices = [token2index[i] for i in base]
    index = average(indices) if 'prenasalized' in tags else min(indices)
    if 'aspirated/devoiced' in tags:
        # Sonority index of devoiced sonorants will be treated equal to 'h'
        index = min(index, token2index['h'])
    # Other tags of secondary articulation will be ignored when calculating the index
    return index


def phone2base_and_tags(phone):
    tags = set()
    phone = list(phone)
    for i in range(1, len(phone)):
        if phone[i] in suffix_tags:
            tags.add(suffix_tags[phone[i]])
            phone[i] = ''
    phone = ''.join(phone)
    tags = sorted(list(tags))
    if len(phone) > 1 \
            and token2type[phone[0]] == 'nasal' \
            and re.search('click|plos|fric', token2type[phone[1]]):
        # nasal + obstruent means prenasalized
        tags.insert(0, 'prenasalized')
    tags.insert(0, f'len-{len(phone)}')
    tags.insert(0, 'semivowel' if 'semivowel' in token2type[phone[0]]
                else 'vowel' if 'vowel' in token2type[phone[0]]
                else 'consonant')
    return (phone, tags)


def split_geminate_tokens(tokens):
    i = 0
    while i < len(tokens):
        if tokens[i] == 'q""':  # Appears in Tsez 2; actually means [qʼˤ]
            tokens[i] = 'q"'
        token = tokens[i]
        # e.g. 'uu' -> 'u|u'; 'tt' -> 't|t'; 'tth' -> 't|th'
        if (len(token) == 2 or len(token) == 3) and token[0] == token[1]:
            tokens = tokens[:i] + [token[:1], token[1:]] + tokens[i + 1:]
            continue
        # e.g. 'u*u*' -> 'u*|u*'; 't"t"' -> 't"|t"'
        if len(token) == 4 and token[:2] == token[2:]:
            tokens = tokens[:i] + [token[:2], token[2:]] + tokens[i + 1:]
            continue
        i += 1
    return tokens


def word2phones(word, merge_vowels=False):
    word = word.replace(' ', '')
    for pair in asjp2tokens_patch.items():
        word = word.replace(*pair)
    phones = asjp2tokens(word, merge_vowels)
    phones = [phone.replace('~', '').replace('$', '') for phone in phones]
    phones = split_geminate_tokens(phones)
    return phones


def word2index(word, merge_vowels=False):
    return average([phone2index(i) for i in word2phones(word, merge_vowels)])


def classify_phones(phone_counts):
    result = {}
    for phone in phone_counts:
        tags = '; '.join(phone2base_and_tags(phone)[1])
        if tags not in result.keys():
            result[tags] = {}
        result[tags][phone] = phone_counts[phone]
    return result


def write_classified_phones(classified, csv_filename):
    result = [['phone', 'base', 'count', 'tags']]
    for tags in sorted(classified.keys()):
        lines = [[
            phone,
            phone2base_and_tags(phone)[0],
            classified[tags][phone],
            tags,
        ] for phone in classified[tags]]
        lines = sorted(lines, key=lambda l: l[1])
        lines = sorted(lines, key=lambda l: l[2], reverse=True)
        lines = [[str(i) for i in line] for line in lines]
        result += lines
    with open(csv_filename, 'w') as f:
        f.writelines([','.join(line) + '\n' for line in result])
