import io, sqlite3

con = sqlite3.connect('../elderspeak_detect.db')
cur = con.cursor()

cur.execute('DROP TABLE IF EXISTS woordenlijst')
cur.execute('CREATE TABLE woordenlijst (woord TEXT NOT NULL PRIMARY KEY)')

def verwerk_lijst(lijst: str) -> bool:
    with io.open(lijst + '.txt', mode='r', encoding='utf-8') as lijst_bestand:
        while True:
            woord = lijst_bestand.readline()
            if not woord:
                break
            
            woord = str(woord.lstrip().rstrip())
            if woord != '' and woord[0] != '#':
                cur.execute('INSERT OR IGNORE INTO woordenlijst VALUES (?)', [ woord ])
                
        con.commit()
    return True   

lijsten = [
    'voornamen_m',
    'voornamen_v',
    'plaatsnamen',
    'woordenlijst_opentaal'
]

print(list(map(verwerk_lijst, lijsten)))

con.close()