import sqlite3

con = sqlite3.connect('../elderspeak_detect.db')
cur = con.cursor()

cur.execute('DROP TABLE IF EXISTS woordenlijst')
cur.execute('CREATE TABLE woordenlijst (woord TEXT NOT NULL PRIMARY KEY)')

def verwerk_lijst(lijst: str):
    with open(lijst + '.txt', 'r') as lijst_bestand:
        while True:
            woord = lijst_bestand.readline().lstrip().rstrip()
            if not woord:
                break

            woord = str(woord)
            if woord != '' and woord[0] != '#':
                cur.execute('INSERT OR IGNORE INTO woordenlijst VALUES (?)', [ woord ])

        con.commit()        

lijsten = [
    'voornamen_m',
    'voornamen_v',
    'plaatsnamen',
    'woordenlijst_opentaal',
]

con.close()