import os
import io
import pyphen
import sqlite3
from google.cloud import speech

class TextBased():
    def transcript(audio_file_name) -> str:
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
            alternative_language_codes=['nl-NL', 'fr-BE', 'fr-FR'] # kijken of dit een verbetering is
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
        # met woordlengte_ratio
        return TextBased.woordlengte_ratio(audio_file_name) < 0.05 # aanpassen -> vergelijken tussen leeftijdsgenoten en naar ouderen

    def woordlengte_ratio(audio_file_name) -> float:
        # long word ratio =  the amount of words that contain more than three syllables divided by the total amount of words
        dic = pyphen.Pyphen(lang='nl_NL') # Pyphen kent geen Belgisch Nederlands
        more_than_three_syllables = 0.0

        transcript = TextBased.transcript(audio_file_name).lower().split()

        for word in transcript:
            letterprepen = dic.inserted(word).split('-')
            print(letterprepen)
            if len(letterprepen) > 2:
                more_than_three_syllables += 1

        return more_than_three_syllables / len(transcript)

    def cilt(audio_file_name) -> float: # correct? bruikaar?
        # CILT =  114.49 + 0.28 × freq77 − 12.33 × avgwordlen
        transcript = TextBased.transcript(audio_file_name).lower().split()
        freq77 = 0.0
        avgwordlen = 0.0

        con = sqlite3.connect('elderspeak_detect.db')
        cur = con.cursor()

        for word in transcript:
            avgwordlen += len(word)

            number = cur.execute("SELECT ((SELECT number FROM freq77 where word = :word) * 10000 / count(*)) * 0.0001 FROM freq77;", {
                'word': word
            }).fetchone()[0]

            if number is not None:
                freq77 += number
            else:
                freq77 += 1.0

        avgwordlen /= len(transcript)

        con.close()
        return 114.49 + 0.28 * freq77 - 12.33 * avgwordlen

    def verkleinwoorden(audio_file_name) -> bool:
        # eindigen op -je, -tje, -etje, -pje, -kje, -tsje, -jes, -tjes, -etjes, -pjes, -kjes, -tsjes, -ke of -ken
        # filteren met woordenlijst -> nog op te stellen, zie: https://github.com/OpenTaal/opentaal-wordlist en lijst voornamen en plaatsnamen
        # tellen
        # zie ook vorige BP's
        raise NotImplemented

    def aantal_verkleinwoorden(audio_file_name) -> int:
        transcript = TextBased.transcript(audio_file_name).lower().split()
        count = 0

        con = sqlite3.connect('elderspeak_detect.db')
        cur = con.cursor()

        # for woord in transcript:
        #     if woord[-2:] == 'je' or woord[-3:] == 'jes' or woord[-2:] == 'ke' or woord[-3:] == 'ken':    

        con.close()
        return count

    def collectieve_voornaamwoorden(audio_file_name) -> bool:
        return TextBased.aantal_collectieve_voornaamwoorden(audio_file) > 3 # aanpassen -> kijken of dit echt nuttig is

    def aantal_collectieve_voornaamwoorden(audio_file) -> int:
        text = TextBased.transcript(audio_file_name).lower().split()
        return text.count('we')

    def bevestigende_tussenwerpsels(audio_file_name) -> bool:
        return TextBased.aantal_bevestigende_tussenwerpsels(audio_file_name) > 3 # aanpassen -> vergelijken tussen leeftijdsgenoten en naar ouderen

    def aantal_bevestigende_tussenwerpsels(audio_file_name) -> int:
        text = TextBased.transcript(audio_file_name).lower().split()
        return text.count('hé') + text.count('voilà')

    def herhalende_zinnen(audio_file_name) -> bool:
        # zin per zin verwerken en terugkijken -> zie Standaert
        raise NotImplemented