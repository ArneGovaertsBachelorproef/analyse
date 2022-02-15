import os
import io
import sqlite3
from google.cloud import speech

class TextBased():
    def get_text(audio_file_name) -> str:
        con = sqlite3.connect('elderspeak_detect.db')
        cur = con.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS speech_to_text (
            audio_file_name TEXT NOT NULL PRIMARY KEY,
            transcript      TEXT NOT NULL
        );''')

        res = cur.execute("SELECT transcript FROM speech_to_text WHERE audio_file_name = :audio_file_name;", {
            'audio_file_name': audio_file_name
        }).fetchone()
        if res is not None:
            # reeds in database
            return res[0]
        
        # speech to text met Google Cloud
        audio_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'audio_files' , audio_file_name)
        
        client = speech.SpeechClient()

        with io.open(audio_file, 'rb') as speech_file:
            content = speech_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            language_code='nl-BE',
            alternative_language_codes=['nl-NL', 'fr-BE', 'fr-FR']
        )

        response = client.recognize(config=config, audio=audio)

        transcript = ''
        for result in response.results:
            transcript = transcript + str(result.alternatives[0].transcript)

        # save in database
        cur.execute("INSERT INTO speech_to_text (audio_file_name, transcript) VALUES (:audio_file_name, :transcript);", {
            'audio_file_name': audio_file_name,
            'transcript': transcript
        })

        con.commit()  
        con.close()

        return transcript

    def vermindering_grammaticale_complexiteit(audio_file_name) -> bool:
        # a.d.h.v. Cito Leesindex Technisch Lezen of Leesindex A
        # CILT = 114.49 + 0.28 × fwr − 12.33 × c/w met fwr = frequent word ratio en c/w = characters per word
        # A = 195 − 2 × w/sen − 66.7 × syl/w met w/sen = words per sentence en syl/w = syllables per word
        # enkel w/sen
        # -> w/sen is vermoedelijk beste maatstaaf, maar vereist 100% correcte speech to text!
        # long word ratio
        raise NotImplemented

    def verkleinwoorden(audio_file_name) -> bool:
        # eindigen op -je, -tje, -etje, -pje, -kje, -tsje, -jes, -tjes, -etjes, -pjes, -kjes, -tsjes, -ke of -ken
        # filteren met woordenlijst -> nog op te stellen, zie: https://github.com/OpenTaal/opentaal-wordlist
        # tellen
        # zie ook vorige BP's
        raise NotImplemented

    def collectieve_voornaamwoorden(audio_file_name) -> bool:
        # tellen
        raise NotImplemented

    def bevestigende_tussenwerpsels(audio_file_name) -> bool:
        # tellen
        raise NotImplemented

    def herhalende_zinnen(audio_file_name) -> bool:
        # zin per zin verwerken en terugkijken -> zie Standaert
        raise NotImplemented