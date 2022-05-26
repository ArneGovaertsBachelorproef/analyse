import spacy, sqlite3, random, re, string

from spacy.tokens import DocBin

nl = spacy.load('nl_core_news_lg')
stopwoorden = nl.Defaults.stop_words

def preprocess_tekst(tekst):
    tekst = tekst.lower().strip()
    tekst = re.compile('<.*?>').sub('', tekst)
    tekst = re.compile('[%s]' % re.escape(string.punctuation)).sub(' ', tekst)
    tekst = re.sub('\s+', ' ', tekst)
    tekst = re.sub(r'\[[0-9]*\]',' ',tekst)
    tekst = re.sub(r'[^\w\s]', '', str(tekst).lower().strip())
    tekst = re.sub(r'\d',' ',tekst)
    tekst = re.sub(r'\s+',' ',tekst)

    lst = []
    for token in tekst.split():
        if token.lower() not in stopwoorden:
            lst.append(token)

    return ' '.join(lst)

db_file = '../elderspeak_detect.db'
con = sqlite3.connect(db_file)
cur = con.cursor()

cur.execute('''select t.audio_id, t.tekst, td.elderspeak
from teksten t
join test_data td on td.audio_id = t.audio_id
where t.methode = 'GOOGLE_ENKEL_NL_BE';''')
data = cur.fetchall()

nlp = spacy.blank('nl')
db = DocBin()

for rij in data:
    tekst = preprocess_tekst(rij[1])
    cats = { 'normaal': 1.0 - rij[2], 'elderspeak': rij[2] * 1.0 }

    print([tekst, cats])

    doc = nlp(tekst)
    doc.cats = cats
    db.add(doc)

db.to_disk('./train.spacy')