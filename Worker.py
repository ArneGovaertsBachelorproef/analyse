from TextBased import TextBased
from PraatBased import PraatBased

class Worker():
    def do(task_array):
       print({
            'langzaam_spreken': PraatBased.langzaam_spreken,
            'verhoogd_stemvolume': PraatBased.verhoogd_stemvolume,
            #'verhoogd_stemvolume': MachineLearningBased.verhoogd_stemvolume,
            'vermindering_grammaticale_complexiteit': TextBased.vermindering_grammaticale_complexiteit,
            #'vermindering_grammaticale_complexiteit': MachineLearningBased.vermindering_grammaticale_complexiteit,
            'verkleinwoorden': TextBased.verkleinwoorden,
            'collectieve_voornaamwoorden': TextBased.collectieve_voornaamwoorden,
            'bevestigende_tussenwerpsels': TextBased.bevestigende_tussenwerpsels,
            'verhoging_toonhoogte': PraatBased.verhoogde_toonhoogte,
            'herhalende_zinnen': TextBased.herhalende_zinnen
       }[task_array[1]](task_array[0]))