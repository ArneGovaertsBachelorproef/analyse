# see: https://chriskiehl.com/article/parallelism-in-one-line

from multiprocessing.dummy import Pool as ThreadPool
from Worker import Worker
from TextBased import TextBased
from dotenv import load_dotenv

load_dotenv()

audio_file_name = 'oudere.flac'
TextBased.transcript(audio_file_name)
print(TextBased.woordlengte_ratio(audio_file_name))

# tasks = [
#     [audio_file_name, 'langzaam_spreken'],
#     [audio_file_name, 'verhoogd_stemvolume'],
#     [audio_file_name, 'vermindering_grammaticale_complexiteit'],
#     [audio_file_name, 'verkleinwoorden'],
#     [audio_file_name, 'collectieve_voornaamwoorden'],
#     [audio_file_name, 'bevestigende_tussenwerpsels'],
#     [audio_file_name, 'verhoging_toonhoogte'],
#     [audio_file_name, 'herhalende_zinnen']
# ]
 
# pool = ThreadPool()
# results = pool.map(Worker.do, tasks)
# pool.close()
# pool.join()