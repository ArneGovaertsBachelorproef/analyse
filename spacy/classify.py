import spacy, sqlite3, csv, re, string

def preprocess_text(text): # verschil tussen tok2vec v1 en v2
    text = text.lower().strip()
    text = re.compile('<.*?>').sub('', text)
    text = re.compile('[%s]' % re.escape(string.punctuation)).sub(' ', text)
    text = re.sub('\s+', ' ', text)
    text = re.sub(r'\[[0-9]*\]',' ',text)
    text = re.sub(r'[^\w\s]', '', str(text).lower().strip())
    text = re.sub(r'\d',' ',text)
    text = re.sub(r'\s+',' ',text)

    return text

nlp = spacy.load('output/model-best')

db_file = '../elderspeak_detect.db'

con = sqlite3.connect(db_file)
cur = con.cursor()

cur.execute('''SELECT t.tekst, a.audio_bestand
FROM teksten t
JOIN audio a
ON t.audio_id = a.audio_id
WHERE t.methode = 'GOOGLE_ENKEL_NL_BE'
AND t.tekst <> '';''')
rijen = cur.fetchall()

with open('resultaat.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(['tekst', 'gericht aan', 'score'])

    for rij in rijen:
        doc = nlp(preprocess_text(rij[0]))
        if 'leeftijdsgenoot' in rij[1]:
            csvwriter.writerow([rij[0], 'leeftijdsgenoot', round(doc.cats['elderspeak'], 3)])
        else:
            csvwriter.writerow([rij[0], 'oudere', round(doc.cats['elderspeak'], 3)])

'''
text = ''
print('type : "quit" to exit')
while text != 'quit':
    text = input('Please enter example input: ')
    doc = nlp(text)
    print('elderspeak score : ' + str(doc.cats['elderspeak']))
'''