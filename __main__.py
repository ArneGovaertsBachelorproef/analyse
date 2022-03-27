# ========================================================================= #
#  Imports                                                                  #
# ========================================================================= #
import os
import csv
import time
import boto3
import sqlite3
import logging
import datetime

from dotenv import load_dotenv
from Spraakherkenning import Spraakherkenning, Methode
from TekstGebaseerd import TekstGebaseerd
from PraatGebaseerd import PraatGebaseerd
from botocore.exceptions import ClientError
from multiprocessing.dummy import Pool as ThreadPool
from parselmouth import PraatError

load_dotenv()
logging.basicConfig(level=logging.INFO)

# ========================================================================= #
#  Global variables                                                         #
# ========================================================================= #
db_file        = 'elderspeak_detect.db'
input_bestand   = '_dataverza.csv'
output_dir      = 'output'

aantal_threads    = 3

# ========================================================================= #
#  Procedures                                                               #
# ========================================================================= #
def maak_connectie(db_file: str) -> sqlite3.Connection:
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

def maak_tabellen(con: sqlite3.Connection):
    """ maak de tabellen aan in de SQLite databank
        indien ze nog niet bestaan voor de gegeven connectie con
    :param con: Connection object
    """

    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS audio (
        audio_id                                        INTEGER PRIMARY KEY AUTOINCREMENT,
        audio_bestand                                   TEXT NOT NULL,
        ophalen_ok                                      BOOLEAN DEFAULT 0,
        input_data_ok                                   BOOLEAN DEFAULT 0,
        praat_analyse_ok                                BOOLEAN DEFAULT 0,
        teksten_ok                                      BOOLEAN DEFAULT 0,
        tekst_analyse_ok                                BOOLEAN DEFAULT 0
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
        leeftijdsgenoot_opname                          INTEGER NOT NULL,
        oudere_opname                                   INTEGER NOT NULL,
        FOREIGN KEY(leeftijdsgenoot_opname)             REFERENCES audio(audio_id),
        FOREIGN KEY(oudere_opname)                      REFERENCES audio(audio_id)
    );''')

    cur.execute('''CREATE TABLE IF NOT EXISTS praat_resultaten (
        resultaat_id                                    INTEGER PRIMARY KEY AUTOINCREMENT,
        spraaksnelheid                                  REAL,
        geluidsniveau                                   REAL,
        toonhoogte                                      REAL,
        audio_id                                        INTEGER NOT NULL,
        FOREIGN KEY(audio_id)                           REFERENCES audio(audio_id)        
    );''')

    cur.execute('''CREATE TABLE IF NOT EXISTS teksten (
        tekst_id                                        INTEGER PRIMARY KEY AUTOINCREMENT,
        tekst                                           TEXT,
        methode                                         TEXT,
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
        tekst_id                                        INTEGER NOT NULL,
        FOREIGN KEY(audio_id)                           REFERENCES audio(audio_id),
        FOREIGN KEY(tekst_id)                           REFERENCES audio(tekst_id)   
    );''')

def ophalen_audio_bestanden(con: sqlite3.Connection):
    """ audiobestanden ophalen van Scaleway Object Storage en opslaan in audio_files/
    :param con: Connection
    """

    audio_dir               = 'audio_files/'
    dir_exists              = os.path.exists(audio_dir)

    if not dir_exists:
        os.makedirs(audio_dir)

    cur                     = con.cursor()

    bucket                  = os.environ.get('BUCKET_NAME')
    region_name             = os.environ.get('REGION')
    use_ssl                 = True
    endpoint_url            = os.environ.get('S3_ENDPOINT_URL')
    aws_access_key_id       = os.environ.get('ACCESS_KEY_ID')
    aws_secret_access_key   = os.environ.get('ACCESS_KEY')

    s3 = boto3.resource(
        's3',
        region_name=region_name,
        use_ssl=True,
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    s3_dir = s3.Bucket(bucket)
    for s3_object in s3_dir.objects.all():
        path, filename = os.path.split(s3_object.key)
        s3_dir.download_file(s3_object.key, audio_dir + filename)
    
        cur.execute('UPDATE audio SET ophalen_ok = true WHERE audio_bestand = ?', [filename])
        con.commit()

def lees_input_data(con: sqlite3.Connection, input_bestand: str):
    """ lees het csv bestand input_bestand in en schrijf de data weg in de databank met connectie con
    :param con: Connection
    :param input_bestand: bestandsnaam als string
    """

    line_count = 0
    with open(input_bestand) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        cur = con.cursor()
        for rij in csv_reader:
            if line_count > 0:
                cur.execute('SELECT audio_id, audio_bestand FROM audio WHERE audio_bestand = ?',  [ rij[7] ])
                count = 0
                rijen1 = cur.fetchall()
                for rij1 in rijen1:
                    logging.info('Skip: ' + rij1[1] + ' met id = ' + str(rij1[0]))
                    count += 1
                
                if count == 0:
                    cur.execute('INSERT INTO audio(audio_bestand) VALUES (:bestand);', { 'bestand': rij[7] })
                    leeftijdsgenoot_opname = cur.lastrowid

                    cur.execute('INSERT INTO audio(audio_bestand) VALUES (:bestand);', { 'bestand': rij[8] })
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
                
                    cur.execute('UPDATE audio SET input_data_ok = true WHERE audio_id in (?,?)', [
                        leeftijdsgenoot_opname, oudere_opname
                    ])
                    con.commit()
            
                    line_count += 1
            else:
                line_count += 1
    logging.info('Aantal lijnen ingelezen: ' + str(line_count - 1))

def ophalen_bestandsnamen(con: sqlite3.Connection) -> list:
    """ ophalen van (reeds ingelezen) bestandsnamen uit de databank
    :param con: Connection
    :return list: lijst van bestandsnamen als string
    """

    cur = con.cursor()
    cur.execute('SELECT audio_bestand FROM audio')
    rijen = cur.fetchall()
    bestanden = [rij[0] for rij in rijen]
    return bestanden

def audio_id_op_basis_van_bestand(con: sqlite3.Connection, bestandsnaam: str) -> int:
    """ ophalen audio_id aan de hand vand de bestandsnaam van het audio bestand
    :param con: Connection
    :param bestandsnaam: str
    :return int: audio_id
    """

    cur = con.cursor()
    cur.execute('SELECT audio_id FROM audio WHERE audio_bestand = :bestand', { 'bestand': bestandsnaam })
    rijen = cur.fetchall()

    for rij in rijen:
        return rij[0]
    raise Exception('Bestandsnaam niet gevonden')

def export_data_als_csv(con: sqlite3.Connection):
    dir_exists = os.path.exists(output_dir)

    if not dir_exists:
        os.makedirs(output_dir)

    #with open(output_dir + '/teksten.csv', 'wb') as teksten_file:
    #    writer = csv.writer(teksten_file)
    #    writer.writerow(['tekst_id', 'tekst', 'methode', 'audio_id'])
    #
    #    cur = con.cursor()
    #    cur.execute('select ')

    #    writer.writerows(data)

# ------------------------------------------------------------------------- #
#  Werkers                                                                  #
# ------------------------------------------------------------------------- #
def doe_analyse_praat(audio_file: str):
    """ werkerprocedure voor het analyseren met behulp van PRAAT
    :param audio_file: bestandsnaam als string
    """

    con                         = maak_connectie(db_file)
    audio_id                    = audio_id_op_basis_van_bestand(con, audio_file)
    audio_file_path             = os.path.join(os.path.dirname(os.path.abspath(__file__)),'audio_files', audio_file)
    
    cur.execute('SELECT praat_analyse_ok FROM audio WHERE audio_bestand = ?',  [ audio_file ])
    count = 0
    rijen1 = cur.fetchall()
    for rij1 in rijen1:
        if rij1[0]:
            logging.info('Skip: ' + audio_file + ' met id = ' + str(audio_id))
            count += 1
    if count > 0:
        return

    try:
        praat                       = PraatGebaseerd(audio_file_path)
        geluidsniveau_in_db         = praat.geluidsniveau_in_db()
        spraaksnelheid_in_sylps     = praat.spraaksnelheid_in_sylps()
        gemiddelde_toonhoogte_in_hz = praat.gemiddelde_toonhoogte_in_hz()

        cur = con.cursor()
        cur.execute('''INSERT INTO praat_resultaten(spraaksnelheid,geluidsniveau,toonhoogte,audio_id)
        VALUES (:spraaksnelheid,:geluidsniveau,:toonhoogte,:audio_id);''', {
            'spraaksnelheid':   spraaksnelheid_in_sylps,
            'geluidsniveau':    geluidsniveau_in_db,
            'toonhoogte':       gemiddelde_toonhoogte_in_hz,
            'audio_id':         audio_id
        })
        cur.execute('UPDATE audio SET praat_analyse_ok = true WHERE audio_id = ?', [audio_id])
        con.commit()

        logging.info('Klaar met ' + audio_file)
    except PraatError as e:
        logging.error(str(e))

def doe_speech_to_text(audio_file: str):
    con                         = maak_connectie(db_file)
    audio_id                    = audio_id_op_basis_van_bestand(con, audio_file)

    cur.execute('SELECT teksten_ok FROM audio WHERE audio_bestand = ?',  [ audio_file ])
    count = 0
    rijen1 = cur.fetchall()
    for rij1 in rijen1:
        if rij1[0]:
            logging.info('Skip: ' + audio_file + ' met id = ' + str(audio_id))
            count += 1
    if count > 0:
        return

    audio_file_path             = os.path.join(os.path.dirname(os.path.abspath(__file__)),'audio_files', audio_file)
    spraakherkenning            = Spraakherkenning(audio_file_path)

    try:
        google_enkel_nl_be          = spraakherkenning.tekst(Methode.GOOGLE_ENKEL_NL_BE)
        google_dialect_opvangen     = spraakherkenning.tekst(Methode.GOOGLE_NL_FR)
        vosk                        = spraakherkenning.tekst(Methode.VOSK)

        cur = con.cursor()
        records = [
            (google_enkel_nl_be,        'GOOGLE_ENKEL_NL_BE',   audio_id),
            (google_dialect_opvangen,   'GOOGLE_NL_FR',         audio_id),
            (vosk,                      'VOSK',                 audio_id)
        ]
        cur.executemany('INSERT INTO teksten (tekst,methode,audio_id) VALUES (?,?,?);', records)
        cur.execute('UPDATE audio SET teksten_ok = true WHERE audio_id = ?', [audio_id])
        con.commit()

        logging.info('Klaar met ' + audio_file)
    except google.api_core.exceptions.InvalidArgument as e:
        logging.error(str(e))

def doe_analyse_tekst(audio_file: str):
    pass

# ========================================================================= #
#  Hoofdprogramma                                                           #
# ========================================================================= #
start_time = time.time()

con = maak_connectie(db_file)
if con is None:
    raise Exception('Connection is None')
    exit

# fase 0 = ophalen bestanden en inlezen input data
maak_tabellen(con)
lees_input_data(con, input_bestand)
ophalen_audio_bestanden(con)
bestanden = ophalen_bestandsnamen(con)
logging.info('Klaar met fase 0 na ' + str(round(time.time() - start_time, 2)) + 's')

# fase 1 = analyse met PRAAT
pool = ThreadPool(aantal_threads)
pool.map(doe_analyse_praat, bestanden)
pool.close()
pool.join()
logging.info('Klaar met fase 1 na ' + str(round(time.time() - start_time, 2)) + 's')

# fase 2 = speech to text
pool = ThreadPool(aantal_threads)
pool.map(doe_speech_to_text, bestanden)
pool.close()
pool.join()
logging.info('Klaar met fase 2 na ' + str(round(time.time() - start_time, 2)) + 's')

# fase 3 = analyse tekst
pool = ThreadPool(aantal_threads)
pool.map(doe_analyse_tekst, bestanden)
pool.close()
pool.join()
logging.info('Klaar met fase 3 na ' + str(round(time.time() - start_time, 2)) + 's')

# fase 4 = output data als csv
export_data_als_csv(con)
logging.info('Klaar met fase 4 na ' + str(round(time.time() - start_time, 2)) + 's')
