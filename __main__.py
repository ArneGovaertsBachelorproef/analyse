# see: https://chriskiehl.com/article/parallelism-in-one-line

import os
import sqlite3
import logging

from multiprocessing.dummy import Pool as ThreadPool
from TextBased import TextBased
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

database = 'elderspeak_detect.db'

def do(audio_file):
    try:
        con = sqlite3.connect(database)
        cur = con.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS audio (
            audio_id                                    INTEGER PRIMARY KEY AUTOINCREMENT,
            audio_file                                  TEXT NOT NULL,
            transcript_met_dialect_opvangen             TEXT,
            transcript_enkel_nl_be                      TEXT
        );''')

        cur.execute('''CREATE TABLE IF NOT EXISTS results (
            result_id                                   INTEGER PRIMARY KEY AUTOINCREMENT,
            audio_id                                    INTEGER NOT NULL,

            grammaticale_complexiteit_cilt              REAL,
            grammaticale_complexiteit_woordlengte_ratio REAL,

            aantal_collectieve_voornaamwoorden          INTEGER,

            aantal_bevestigende_tussenwerpsels          INTEGER,

            FOREIGN KEY(audio_id) REFERENCES audio(audio_id)
        );''')

        # speech to text
        cur.execute('SELECT audio_id, transcript_met_dialect_opvangen FROM audio WHERE audio_file = :audio_file', {
            'audio_file': audio_file
        })
        result = cur.fetchone()

        if result:
            audio_id = result[0]
            transcript = result[1]
        else:
            audio_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'audio_files', audio_file)

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

        # langzaam spreken met PRAAT


        # verhoogd stemvolume met PRAAT


        # verhoogd stemvolume met machine learning


        # vermindering grammaticale complexiteit met speech to text en formule
        cilt = TextBased.cilt(cur, transcript)
        woordlengte_ratio = TextBased.woordlengte_ratio(transcript)

        # vermindering grammaticale complexiteit met speech to text en machine learning


        # verkleinwoorden met speech to text en tellen


        # collectieve voornaamwoorden met speech to text en tellen
        aantal_collectieve_voornaamwoorden = TextBased.aantal_collectieve_voornaamwoorden(transcript)

        # collectieve voornaamwoorden met speech to text en machine learning


        # bevestigende tussenwerpsels met speech to text en tellen
        aantal_bevestigende_tussenwerpsels = TextBased.aantal_bevestigende_tussenwerpsels(transcript)

        # verhoogde toonhoogte met PRAAT 


        # herhalende zinnen met speech to text en terugkijken


        con.commit()  
        con.close()
    except sqlite3.Error as error:
        logging.error('Failed to read/write data from/to table' + error)
    finally:
        if (con):
            con.close()

files = [file for file in os.listdir('audio_files')]     
count_files = len(files)

pool = ThreadPool()
pool.map(do, files)
pool.close()
pool.join()

logging.info('Aantal bestanden\t:  %s', count_files)

try:
    con = sqlite3.connect(database)
    cur = con.cursor()
    
    cur.execute('select count(audio_id) from results')
    count_table_records = cur.fetchone()[0]

    logging.info('Aantal verwerkt\t\t:  %s', count_table_records)

    con.close()
except sqlite3.Error as error:
    logging.error('Failed to read data from table %s', error)
finally:
    if (con):
        con.close()