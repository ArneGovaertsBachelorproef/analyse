import sqlite3, numpy

from statistics import mean
from jiwer import wer as calc_wer

db_file = '../elderspeak_detect.db'
con = sqlite3.connect(db_file)
cur = con.cursor()

def my_wer(r, h):
    """
    Calculation of WER with Levenshtein distance.

    Works only for iterables up to 254 elements (uint8).
    O(nm) time ans space complexity.

    Parameters
    ----------
    r : list
    h : list

    Returns
    -------
    int

    Examples
    --------
    >>> wer("who is there".split(), "is there".split())
    1
    >>> wer("who is there".split(), "".split())
    3
    >>> wer("".split(), "who is there".split())
    3
    """
    # initialisation
    d = numpy.zeros((len(r) + 1) * (len(h) + 1), dtype=numpy.uint8)
    d = d.reshape((len(r) + 1, len(h) + 1))
    for i in range(len(r) + 1):
        for j in range(len(h) + 1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i

    # computation
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                substitution = d[i - 1][j - 1] + 1
                insertion = d[i][j - 1] + 1
                deletion = d[i - 1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)

    return d[len(r)][len(h)] / len(r)

def verwerk(bestandsnaam: str) -> dict:
    res = {}
    
    print()
    print('===================================================')
    print()
    print('Opname : ' + bestandsnaam.replace('txt', 'flac'))
    print()

    gold_standard = ''
    with open(bestandsnaam, mode='r', encoding='utf-8') as bestand:
        gold_standard = str(bestand.readline())
    print('Gold standard:')
    print(gold_standard)
    print()
    print()

    cur.execute('''select tekst, methode
    from teksten t
    join audio a on a.audio_id = t.audio_id
    where audio_bestand = ? ''', [bestandsnaam.replace('txt', 'flac')])
    rijen = cur.fetchall()

    for rij in rijen:
        error = calc_wer(gold_standard, rij[0])
        res[rij[1]] = error

        print(rij[1] + ':')
        print(rij[0])
        print()
        print('WER =\t\t' + str(error))
        print('MY_WER =\t' + str(my_wer(gold_standard.split(), rij[0].split())))
        print()
        print()

    return res

print('BEREKEN WER WAARDES (lager is beter)')

bestanden = [
    'oudere_opname_2022-04-14_94329e2190bf3d02a64de0f777d6625e.txt',
    'oudere_opname_2022-02-11_8bb4506fd302006d224e9c1584d0a5da.txt',
    'leeftijdsgenoot_opname_2022-03-17_97af73e3939320f945ec67a090e4dc18.txt',
    'leeftijdsgenoot_opname_2022-02-28_9bd65c7d1a54b84b8815e4347a36eb9e.txt'
]

resultaten = list(map(verwerk, bestanden))
print('===================================================')
per_cat = {}

for el in resultaten:
    for item in el.items():
        if item[0] not in per_cat:
            per_cat[item[0]] = []
        per_cat[item[0]].append(item[1])

for item in per_cat.items():
    print(item[0] + ':\t\t' + str(mean(item[1])))