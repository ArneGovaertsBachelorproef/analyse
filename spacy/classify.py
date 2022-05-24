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

with open('test.csv', newline='', encoding='utf-8') as csvfile1:
    with open('resultaat.csv', 'w', newline='', encoding='utf-8') as csvfile2:
        csvreader = csv.reader(csvfile1, delimiter=';', quotechar='"')

        csvwriter = csv.writer(csvfile2, delimiter=';', quoting=csv.QUOTE_MINIMAL, quotechar='"')
        csvwriter.writerow(['tekst', 'elderspeak', 'echte_waarde'])

        totaal_TP = 0
        totaal_TN = 0
        totaal_FP = 0
        totaal_FN = 0
        totaal    = 0
        precisie  = 0
        recall    = 0
        f_measure = 0

        for rij in csvreader:
            doc = nlp(preprocess_text(rij[0]))

            echte_waarde = int(rij[1]) == 1
            waarde = doc.cats['elderspeak'] > 0.5
            csvwriter.writerow([rij[0], int(waarde), int(echte_waarde)])

            totaal += 1

            if waarde == True and echte_waarde == True:
                totaal_TP += 1
            else:
                if waarde == False and echte_waarde == False:
                    totaal_TN += 1
                else:
                    if waarde == True and echte_waarde == False:
                        totaal_FP += 1
                    else:
                        totaal_FN += 1

        csvwriter.writerow([])
        csvwriter.writerow(['totaal_TP', totaal_TP])
        csvwriter.writerow(['totaal_TN', totaal_TN])
        csvwriter.writerow(['totaal_FP', totaal_FP])
        csvwriter.writerow(['totaal_FN', totaal_FN])
        csvwriter.writerow(['totaal', totaal])
        csvwriter.writerow([])

        if (totaal_TP + totaal_FP) != 0:
            precisie  = totaal_TP * 1.0 / (totaal_TP + totaal_FP)
            csvwriter.writerow(['precisie', precisie])

        if (totaal_TP + totaal_FN) != 0:
            recall    = totaal_TP * 1.0 / (totaal_TP + totaal_FN)
            csvwriter.writerow(['recall', recall])
        
        if (precisie + recall) != 0:
            f_measure = (2 * precisie * recall) / (precisie + recall)
            csvwriter.writerow(['F measure', f_measure])


# db_file = '../elderspeak_detect.db'
# con = sqlite3.connect(db_file)
# cur = con.cursor()
# cur.execute('''SELECT t.tekst, a.audio_bestand
# FROM teksten t
# JOIN audio a
# ON t.audio_id = a.audio_id
# WHERE t.methode = 'GOOGLE_ENKEL_NL_BE'
# AND t.tekst <> '';''')
# rijen = cur.fetchall()
# with open('resultaat.csv', 'w', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
#     csvwriter.writerow(['tekst', 'gericht aan', 'score'])
#     for rij in rijen:
#         doc = nlp(preprocess_text(rij[0]))
#         if 'leeftijdsgenoot' in rij[1]:
#            csvwriter.writerow([rij[0], 'leeftijdsgenoot', round(doc.cats['elderspeak'], 3)])
#         else:
#            csvwriter.writerow([rij[0], 'oudere', round(doc.cats['elderspeak'], 3)])











        


