import io
import sqlite3

con = sqlite3.connect('../elderspeak_detect.db')
cur = con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS woorden_op_je_of_ke (
    woord    TEXT NOT NULL PRIMARY KEY
);''')

toegevoegd_woord = []

# voornamen op -je of -ke moeten er steeds uit, dus integraal overnemen
with io.open('voornamen_m.txt', mode='r', encoding='utf-8') as voornamen_file:
    while True:
        woord = voornamen_file.readline()
        if not woord:
            break
        woord = str(woord.lstrip().rstrip())
        if woord != '' and woord[0] != '#' and (woord[-2:] == 'je' or woord[-3:] == 'jes' or woord[-2:] == 'ke' or woord[-3:] == 'ken'):
            print(woord)
            try:
                cur.execute('INSERT INTO woorden_op_je_of_ke VALUES (:woord)', {
                    'woord': woord
                })
            except sqlite3.IntegrityError as ie:
                pass
con.commit()

with io.open('voornamen_v.txt', mode='r', encoding='utf-8') as voornamen_file:
    while True:
        woord = voornamen_file.readline()
        if not woord:
            break
        woord = str(woord.lstrip().rstrip())
        if woord != '' and woord[0] != '#' and (woord[-2:] == 'je' or woord[-3:] == 'jes' or woord[-2:] == 'ke' or woord[-3:] == 'ken'):
            print(woord)
            try:
                cur.execute('INSERT INTO woorden_op_je_of_ke VALUES (:woord)', {
                    'woord': woord
                })
            except sqlite3.IntegrityError as ie:
                pass
con.commit()

# idem voor plaatsnamen

# de woordenlijst van opentaal -> oké?
with io.open('woordenlijst_opentaal.txt', mode='r', encoding='utf-8') as voornamen_file:
    while True:
        woord = voornamen_file.readline()
        if not woord:
            break
        woord = str(woord.lstrip().rstrip())
        if woord != '' and woord[0] != '#' and (woord[-2:] == 'je' or woord[-3:] == 'jes' or woord[-2:] == 'ke' or woord[-3:] == 'ken'):
            print(woord)
            try:
                cur.execute('INSERT INTO woorden_op_je_of_ke VALUES (:woord)', {
                    'woord': woord
                })
            except sqlite3.IntegrityError as ie:
                pass
con.commit()



con.close()


# misschien ook interessant: https://languagemachines.github.io/frog/