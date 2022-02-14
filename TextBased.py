import speech_recognition as sr
import sqlite3

class TextBased():
    def get_text(audio_file_name) -> str:
        # if in database, return from database
        # else speech to text
        pass

    def vermindering_grammaticale_complexiteit(audio_file_name) -> bool:
        # a.d.h.v. Cito Leesindex Technisch Lezen of Leesindex A
        # CILT = 114.49 + 0.28 × fwr − 12.33 × c/w met fwr = frequent word ratio en c/w = characters per word
        # A = 195 − 2 × w/sen − 66.7 × syl/w met w/sen = words per sentence en syl/w = syllables per word
        # enkel w/sen
        # -> w/sen is vermoedelijk beste maatstaaf, maar vereist 100% correcte speech to text!
        # long word ratio
        print('vermindering_grammaticale_complexiteit')

    def verkleinwoorden(audio_file_name) -> bool:
        # eindigen op -je, -tje, -etje, -pje, -kje, -tsje, -jes, -tjes, -etjes, -pjes, -kjes, -tsjes, -ke of -ken
        # filteren met woordenlijst -> nog op te stellen, zie: https://github.com/OpenTaal/opentaal-wordlist
        # tellen
        # zie ook vorige BP's
        print('verkleinwoorden')

    def collectieve_voornaamwoorden(audio_file_name) -> bool:
        # tellen
        print('collectieve_voornaamwoorden')

    def bevestigende_tussenwerpsels(audio_file_name) -> bool:
        # tellen
        print('bevestigende_tussenwerpsels')

    def herhalende_zinnen(audio_file_name) -> bool:
        # zin per zin verwerken en terugkijken -> zie Standaert
        print('herhalende_zinnen')
