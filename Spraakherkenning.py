import io, sys, json, sqlite3, subprocess

from enum import Enum
from pathlib import Path
from google.cloud import speech
from vosk import Model, KaldiRecognizer, SetLogLevel

class Methode(Enum):
    """ enum voor methodes die aanvaard worden door de klasse Spraakherkenning
    """
    GOOGLE_ENKEL_NL_BE  = 0
    GOOGLE_NL_FR        = 1
    VOSK_SMALL          = 2
    VOSK_BIG            = 3

class Spraakherkenning:
    """ klasse die alle methodes omvat voor spraakherkenning

    methodes:
        * tekst() -> str
    
    constructor:
        :param audio_file_path: bestandsnaam als string
    """
    def __init__(self, audio_file_path: str):
        """ constructor
        :param audio_file_path: bestandsnaam als string
        """
        oud_pad     = Path(audio_file_path)
        nieuw_pad   = oud_pad.with_suffix('.wav')
        process = subprocess.Popen(['ffmpeg', '-y', '-v', 'info', '-i', str(oud_pad.absolute()), str(nieuw_pad.absolute())], stdout=subprocess.PIPE)
        
        self.__audio_file_path    = str(nieuw_pad.absolute())
    
    def tekst(self, methode: Methode) -> str:
        """ omzetten van spraak naar tekst met de opgegeven methode
        :param: methode
        :return str: transcriptie
        """
        if methode   == Methode.GOOGLE_ENKEL_NL_BE:
            return self.__google_cloud(False)
        elif methode == Methode.GOOGLE_NL_FR:
            return self.__google_cloud(True)
        elif methode == Methode.VOSK_SMALL:
            return self.__vosk(small=True)
        elif methode == Methode.VOSK_BIG:
            return self.__vosk(small=False)
        else:
            raise NotImplementedError('Methode niet gekend')

    def __google_cloud(self, dialect_opvangen: bool) -> str:
        client = speech.SpeechClient()

        with io.open(self.__audio_file_path, 'rb') as speech_file:
            content = speech_file.read()

        audio = speech.RecognitionAudio(content=content)

        if dialect_opvangen:
            # nl-BE als hoofdtaal, nl-NL, fr-BE en fr-FR om dialect op te vangen
            config = speech.RecognitionConfig(
                language_code='nl-BE',
                alternative_language_codes=['nl-NL', 'fr-BE', 'fr-FR'] # dialect hiermee opgelost?
            )
        else:
            # uitsluitend nl-BE
            config = speech.RecognitionConfig(
                language_code='nl-BE'
            )

        response = client.recognize(config=config, audio=audio)

        transcript = ''
        for result in response.results:
            transcript = transcript + str(result.alternatives[0].transcript)

        return transcript

    def __vosk(self, small=True) -> str:
        # see: https://github.com/alphacep/vosk-api/blob/master/python/example/test_ffmpeg.py

        SetLogLevel(0)

        sample_rate = 16000
        if small:
            model   = Model('vosk-model-small-nl-0.22')
        else:
            model   = Model('vosk-model-nl-spraakherkenning-0.6')
        rec         = KaldiRecognizer(model, sample_rate)

        process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i', self.__audio_file_path, '-ar', str(sample_rate) ,
            '-ac', '1', '-f', 's16le', '-'], stdout=subprocess.PIPE)

        res = []

        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                temp_res = json.loads(rec.Result())
                res.append(temp_res['text'])
        
        temp_res = json.loads(rec.FinalResult())
        res.append(temp_res['text'])

        return ' '.join(res)
