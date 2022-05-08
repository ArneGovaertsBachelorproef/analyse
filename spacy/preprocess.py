import spacy, sqlite3, random, re, string, csv

from spacy.tokens import DocBin

nl = spacy.load('nl_core_news_lg')
stopwoorden = nl.Defaults.stop_words # verschil tussen tok2vec v2 en v3

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

# training data
training_data  = []

with open('./zinnen.elderspeak.txt') as f:
    while line := f.readline():
        line = preprocess_tekst(line)
        tdoc = (line, { 'normaal': 0.0, 'elderspeak': 1.0 })
        training_data.append(tdoc)

with open('./zinnen.normaal.txt') as f:
    while line := f.readline():
        line = preprocess_tekst(line)
        tdoc = (line, { 'normaal': 1.0, 'elderspeak': 0.0 })
        training_data.append(tdoc)

# to disk
nlp = spacy.blank('nl')

db = DocBin()
for tekst, cats in training_data:
    doc = nlp(tekst)
    doc.cats = cats
    db.add(doc)
db.to_disk('./train.spacy')

# test data
test_data = []

with open('test.csv', newline='') as csvfile:
    r = csv.reader(csvfile, delimiter=';', quotechar='"')
    for rij in r:
        line = preprocess_tekst(rij[0])
        
        if rij[1]:
            tdoc = (line, { 'normaal': 0.0, 'elderspeak': 1.0 })
        else:
            tdoc = (line, { 'normaal': 1.0, 'elderspeak': 0.0 })
        
        test_data.append(tdoc)

# to disk
nlp = spacy.blank('nl')

db = DocBin()
for tekst, cats in test_data:
    doc = nlp(tekst)
    doc.cats = cats
    db.add(doc)
db.to_disk('./test.spacy')