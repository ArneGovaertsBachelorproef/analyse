# see: https://chriskiehl.com/article/parallelism-in-one-line

# ========================================================================= #
#  Imports                                                                  #
# ========================================================================= #
import os
import csv
import time
import sqlite3
import logging
import datetime

from multiprocessing.dummy import Pool as ThreadPool
from TextBased import TextBased
from PraatBased import PraatBased
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

# ========================================================================= #
#  Global variables                                                         #
# ========================================================================= #
database        = 'elderspeak_detect.db'
input_data_file = '_dataverza.csv'
output_dir      = 'output'
aantal_pools    = 1

# fase 0 = inlezen data
# fase 1 = praat
# fase 2 = speech to text
# fase 3 = analyse tekst
# fase 4 = output data als csv
fase = 1

# ========================================================================= #
#  Procedures                                                               #
# ========================================================================= #
def create_connection(db_file: str) -> sqlite3.Connection:
    """ maak connectie met de SQLite databank in db_file
    :param db_file: databankbestand
    :return: Connection object of None
    """

    con = None
    try:
        con = sqlite3.connect(db_file)
    except Error as e:
        logging.error(e)
    return con

def create_tables(con: sqlite3.Connection):
    """ maak de tabellen aan in de SQLite databank
        indien ze nog niet bestaan voor de gegeven connectie con
    :param con: Connection object
    """

    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS audio (
        audio_id                                        INTEGER PRIMARY KEY AUTOINCREMENT,
        audio_bestand                                   TEXT NOT NULL
    );''')

    cur.execute('''CREATE TABLE IF NOT EXISTS input_data (
        input_id                                        INTEGER PRIMARY KEY AUTOINCREMENT,
        datum                                           DATETIME,
        deelnemer                                       TEXT NOT NULL,
        geslacht                                        TEXT,
        leeftijd                                        INTEGER,
        moedertaal                                      TEXT,
        student_zorg                                    BOOLEAN,
        werk_zorg                                       BOOLEAN,
        browser                                         TEXT,
        os                                              TEXT,
        platform                                        TEXT,
        leeftijdsgenoot_opname                          INTEGER,
        oudere_opname                                   INTEGER,
        FOREIGN KEY(leeftijdsgenoot_opname)             REFERENCES audio(audio_id),
        FOREIGN KEY(oudere_opname)                      REFERENCES audio(audio_id)
    );''')

    cur.execute('''CREATE TABLE IF NOT EXISTS teksten (
        tekst_id                                        INTEGER PRIMARY KEY AUTOINCREMENT,
        tekst                                           TEXT,
        methode                                         TEXT,
        audio_id                                        INTEGER NOT NULL,
        FOREIGN KEY(audio_id)                           REFERENCES audio(audio_id)
    );''')

    cur.execute('''CREATE TABLE IF NOT EXISTS praat_resultaten (
        resultaat_id                                    INTEGER PRIMARY KEY AUTOINCREMENT,
        spraaksnelheid                                  REAL,
        geluidsniveau                                   REAL,
        toonhoogte                                      REAL,
        audio_id                                        INTEGER NOT NULL,
        FOREIGN KEY(audio_id)                           REFERENCES audio(audio_id)        
    );''')

    cur.execute('''CREATE TABLE IF NOT EXISTS tekst_resultaten (
        resultaat_id                                    INTEGER PRIMARY KEY AUTOINCREMENT,
        cilt                                            REAL,
        woordlengteratio                                REAL,    
        aantal_collectieve_voornaamwoorden              INTEGER,
        aantal_bevestigende_tussenwerpsels              INTEGER,
        audio_id                                        INTEGER NOT NULL,
        FOREIGN KEY(audio_id)                           REFERENCES audio(audio_id)    
    );''')

def read_input_data_into_db(con: sqlite3.Connection, input_data_file: str):
    """ lees het csv bestand input_data_file in en schrijf de data weg in de databank met connectie con
    :param con: Connection
    :param input_data_file: bestandsnaam als string
    """

    line_count = 0
    with open(input_data_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for rij in csv_reader:
            if line_count > 0:
                cur = con.cursor()

                cur.execute('INSERT INTO audio(audio_bestand) VALUES (:bestand);', { 'bestand': rij[7] })
                #con.commit()
                leeftijdsgenoot_opname = cur.lastrowid

                cur.execute('INSERT INTO audio(audio_bestand) VALUES (:bestand);', { 'bestand': rij[8] })
                #con.commit()
                oudere_opname = cur.lastrowid

                cur.execute('''INSERT INTO input_data(datum,deelnemer,geslacht,leeftijd,moedertaal,student_zorg,werk_zorg,
                    browser,os,platform,leeftijdsgenoot_opname,oudere_opname)
                    VALUES (:datum,:deelnemer,:geslacht,:leeftijd,:moedertaal,:student_zorg,:werk_zorg,
                    :browser,:os,:platform,:leeftijdsgenoot_opname,:oudere_opname);''', {
                        'datum':                    datetime.datetime.strptime(rij[0], '%Y-%m-%dT%H:%M:%S%z'),
                        'deelnemer':                rij[1],
                        'geslacht':                 rij[2],
                        'leeftijd':                 rij[3],
                        'moedertaal':               rij[4],
                        'student_zorg':             ('J' == rij[5]),
                        'werk_zorg':                ('J' == rij[6]),
                        'browser':                  rij[9],
                        'os':                       rij[10],
                        'platform':                 rij[11],
                        'leeftijdsgenoot_opname':   leeftijdsgenoot_opname,
                        'oudere_opname':            oudere_opname
                    })
                con.commit()
            
            line_count += 1
    print('Aantal lijnen ingelezen: ' + str(line_count - 1))

def ophalen_bestandsnamen(con: sqlite3.Connection) -> list:
    bestanden = []

    cur = con.cursor()
    cur.execute('SELECT audio_bestand FROM audio')
    rijen = cur.fetchall()

    for rij in rijen:
        bestanden.append((con, rij[0]))

    return bestanden

# ------------------------------------------------------------------------- #
#  Werkers                                                                  #
# ------------------------------------------------------------------------- #
def doe_analyse_praat(con: sqlite3.Connection, audio_file: str):
    print(audio_file)

def doe_speech_to_text(con: sqlite3.Connection, audio_file: str):
    pass

def doe_analyse_tekst(con: sqlite3.Connection, audio_file: str):
    pass

def export_data_als_csv(con: sqlite3.Connection):
    dir_exists = os.path.exists(output_dir)

    if not dir_exists:
        os.makedirs(dir_exists)

    #with open(output_dir + '/teksten.csv', 'wb') as teksten_file:
    #    writer = csv.writer(teksten_file)
    #    writer.writerow(['tekst_id', 'tekst', 'methode', 'audio_id'])
    #
    #    cur = con.cursor()
    #    cur.execute('select ')

    #    writer.writerows(data)

def do(audio_file):
    audio_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'audio_files', audio_file)

    try:
        con = sqlite3.connect(database)
        cur = con.cursor()

        # speech to text
        cur.execute('SELECT audio_id, transcript_met_dialect_opvangen FROM audio WHERE audio_file = :audio_file', {
            'audio_file': audio_file
        })
        result = cur.fetchone()

        if result:
            audio_id = result[0]
            transcript = result[1]
        else:
            transcript_met_dialect_opvangen = TextBased.transcript(audio_file_path, True)
            transcript_enkel_nl_be = TextBased.transcript(audio_file_path, False)

            cur.execute('''INSERT
                INTO audio  (audio_file, transcript_met_dialect_opvangen, transcript_enkel_nl_be)
                VALUES      (:audio_file, :transcript_met_dialect_opvangen, :transcript_enkel_nl_be)''',
                {
                    'audio_file': audio_file,
                    'transcript_met_dialect_opvangen': transcript_met_dialect_opvangen,
                    'transcript_enkel_nl_be': transcript_enkel_nl_be
                }
            )

            con.commit()
            audio_id = cur.lastrowid

            # algemeen het beste transcript
            transcript = transcript_met_dialect_opvangen

        # langzaam spreken (speech rate) met PRAAT
        spraaksnelheid = PraatBased.spraaksnelheid_in_sylps(audio_file_path)

        # verhoogd stemvolume (voice volume) met PRAAT -> geluidsniveau
        geluidsniveau = PraatBased.geluidsniveau_in_db(audio_file_path)

        # verhoogd stemvolume met machine learning


        # vermindering grammaticale complexiteit met speech to text en formule
        cilt = TextBased.cilt(cur, transcript)
        woordlengte_ratio = TextBased.woordlengte_ratio(transcript)

        # vermindering grammaticale complexiteit met speech to text en machine learning


        # verkleinwoorden met speech to text en tellen


        # verkleinwoorden met speech to text en NLP 


        # collectieve voornaamwoorden met speech to text en tellen
        aantal_collectieve_voornaamwoorden_tellen = TextBased.aantal_collectieve_voornaamwoorden(transcript)

        # collectieve voornaamwoorden met speech to text en machine learning


        # bevestigende tussenwerpsels met speech to text en tellen
        aantal_bevestigende_tussenwerpsels = TextBased.aantal_bevestigende_tussenwerpsels(transcript)

        # verhoogde toonhoogte (pitch) met PRAAT 
        toonhoogte = PraatBased.gemiddelde_toonhoogte_in_hz(audio_file_path)

        # herhalende zinnen met speech to text en terugkijken


        # sentiment analyse met speech to text en NLP

        
        cur.execute('''INSERT
            INTO results (
                audio_id,
                spraaksnelheid,
                geluidsniveau,
                grammaticale_complexiteit_cilt,
                grammaticale_complexiteit_woordlengte_ratio,
                aantal_collectieve_voornaamwoorden_tellen,
                aantal_bevestigende_tussenwerpsels,
                toonhoogte
            )
            VALUES (
                :audio_id,
                :spraaksnelheid,
                :geluidsniveau,
                :grammaticale_complexiteit_cilt,
                :grammaticale_complexiteit_woordlengte_ratio,
                :aantal_collectieve_voornaamwoorden_tellen,
                :aantal_bevestigende_tussenwerpsels,
                :toonhoogte
            )
        ''', {
            'audio_id': audio_id,
            'spraaksnelheid': spraaksnelheid,
            'geluidsniveau': geluidsniveau,
            'grammaticale_complexiteit_cilt': cilt,
            'grammaticale_complexiteit_woordlengte_ratio': woordlengte_ratio,
            'aantal_collectieve_voornaamwoorden_tellen': aantal_collectieve_voornaamwoorden_tellen,
            'aantal_bevestigende_tussenwerpsels': aantal_bevestigende_tussenwerpsels,
            'toonhoogte': toonhoogte
        })
        con.commit()  
        con.close()
    except sqlite3.Error as error:
        logging.exception('Failed to read/write data from/to table')
    finally:
        if (con):
            con.close()

# ========================================================================= #
#  Main program                                                             #
# ========================================================================= #
start_time = time.time()
loggin.info('Start van fase ' + str(fase))

con = create_connection(database)
if con is None:
    raise Exception('Connection is None')
    exit

create_tables(con)

if fase   == 0:
    read_input_data_into_db(con, input_data_file)
elif fase == 4:
    export_data_als_csv(con)
else:
    bestanden = ophalen_bestandsnamen(con)
    pool = ThreadPool(aantal_pools)
    
    if fase   == 1:
        pool.starmap(doe_analyse_praat, bestanden)
    elif fase == 2:
        pool.starmap(doe_speech_to_text, bestanden)
    elif fase == 3:
        pool.starmap(doe_analyse_tekst, bestanden)

    pool.close()
    pool.join()

logging.info('Klaar in ' + str(round(time.time() - start_time, 2)) + 's')