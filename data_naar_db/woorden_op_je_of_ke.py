import io
import sqlite3

con = sqlite3.connect('../elderspeak_detect.db')
cur = con.cursor()

def setup_tabel(lijst: str) -> str:
    cur.execute('DROP TABLE IF EXISTS woorden_op_je_of_ke_' + lijst + ';')
    cur.execute('CREATE TABLE woorden_op_je_of_ke_' + lijst + ''' (
        woord    TEXT NOT NULL PRIMARY KEY
    );''')
    cur.execute('DROP TABLE IF EXISTS woorden_niet_op_je_of_ke_' + lijst + ';')
    cur.execute('CREATE TABLE woorden_niet_op_je_of_ke_' + lijst + ''' (
        woord    TEXT NOT NULL PRIMARY KEY
    );''')

    return lijst + ' oké'

def verwerk_lijst(lijst: str) -> str:
    with io.open(lijst + '.txt', mode='r', encoding='utf-8') as lijst_bestand:
        while True:
            woord = lijst_bestand.readline()
            if not woord:
                break
            
            woord = str(woord.lstrip().rstrip())
            
            if woord != '' and woord[0] != '#':
                if (woord[-2:] == 'je' or woord[-3:] == 'jes' or woord[-2:] == 'ke' or woord[-3:] == 'ken'):
                    print(woord)
                    try:
                        cur.execute('INSERT INTO woorden_op_je_of_ke_' + lijst + ' VALUES (:woord)', {
                        'woord': woord
                        })
                    except sqlite3.IntegrityError as ie:
                        pass
                else:
                    print(woord)
                    try:
                        cur.execute('INSERT INTO woorden_niet_op_je_of_ke_' + lijst + ' VALUES (:woord)', {
                        'woord': woord
                        })
                    except sqlite3.IntegrityError as ie:
                        pass
    con.commit()

    return lijst + ' oké'

def filteren(lijst: str) -> str:
    # woorden die als deel voorkomen filteren behalve bij namen
    cur.execute('DELETE FROM woorden_op_je_of_ke_' + lijst + '''
    where substr(woord,1,length(woord)-2) not in (
        select woord from woorden_niet_op_je_of_ke_''' + lijst + '''
    )
    and substr(woord,1,length(woord)-3) not in (
        select woord from woorden_niet_op_je_of_ke_''' + lijst + '''
    );''')

    con.commit()

    return lijst + ' oké'

# setup tables
lijsten = [
    'voornamen_m',
    'voornamen_v',
    'woordenlijst_opentaal'
]
# plaatsnamen, zie: https://docs.google.com/spreadsheets/d/16GJ69B7Q3023pPwaEoH3R_InkzS65lExeKp-r5IxNR4/edit#gid=0

vereist_filteren = ['woordenlijst_opentaal']

print(list(map(setup_tabel, lijsten)))
print(list(map(verwerk_lijst, lijsten)))
print(list(map(filteren, vereist_filteren)))

con.close()


# misschien ook interessant: https://languagemachines.github.io/frog/