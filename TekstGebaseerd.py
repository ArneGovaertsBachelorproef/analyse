import os
import io
import pyphen
import sqlite3



class TekstGebaseerd:
    

    def woordlengte_ratio(transcript) -> float:
        # long word ratio =  the amount of words that contain more than three syllables divided by the total amount of words
        dic = pyphen.Pyphen(lang='nl_NL') # Pyphen kent geen Belgisch Nederlands
        drie_of_meer_lettergrepen = 0.0

        woorden = transcript.lower().split()

        for woord in woorden:
            letterprepen = dic.inserted(woord).split('-')
            if len(letterprepen) > 2:
                drie_of_meer_lettergrepen += 1

        return drie_of_meer_lettergrepen / len(woorden)

    def cilt(cursor, transcript) -> float:
        # zie ook: https://www.nemokennislink.nl/publicaties/leesniveau-zegt-niets-over-leesplezier/
        # CILT =  114.49 + 0.28 × freq77 − 12.33 × avgwordlen
        transcript = transcript.lower()
        transcript_list = transcript.split()
        freq77 = 0.0
        avgwordlen = 0.0

        for word in transcript_list:
            avgwordlen += len(word)

            number = cursor.execute("SELECT ((SELECT number FROM freq77 where word = :word) * 10000 / count(*)) * 0.0001 FROM freq77;", {
                'word': word
            }).fetchone()[0]

            if number is not None:
                freq77 += 1

        freq77 /= len(transcript_list)
        avgwordlen /= len(transcript.replace(" ", ""))

        return 114.49 + 0.28 * freq77 - 12.33 * avgwordlen

    def aantal_verkleinwoorden(cur, transcript) -> int:
        # eindigen op -je, -tje, -etje, -pje, -kje, -tsje, -jes, -tjes, -etjes, -pjes, -kjes, -tsjes, -ke of -ken
        # filteren met woordenlijst -> nog op te stellen, zie: https://github.com/OpenTaal/opentaal-wordlist en lijst voornamen en plaatsnamen
        # tellen
        transcript = transcript.lower().split()
        count = 0

        for woord in transcript:
            if woord[-2:] == 'je' or woord[-3:] == 'jes' or woord[-2:] == 'ke' or woord[-3:] == 'ken':
                if not_in_basiswoordenlijst:
                    count += 1

        return count

    def aantal_collectieve_voornaamwoorden(transcript) -> int:
        transcript = transcript.lower().split()
        return transcript.count('we') + transcript.count('ons')

    def aantal_bevestigende_tussenwerpsels(transcript) -> int:
        transcript = transcript.lower().split()
        return transcript.count('hé') + transcript.count('voilà')