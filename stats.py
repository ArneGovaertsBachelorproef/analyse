import sqlite3
import numpy as np

from matplotlib import pyplot as plt
from scipy.stats import ttest_ind

# ophalen uit databank
db_file = 'elderspeak_detect.db'

con = sqlite3.connect(db_file)
cur = con.cursor()

cur.execute('''select r.spraaksnelheid, r.geluidsniveau, r.toonhoogte, instr(a.audio_bestand, 'oudere') as naar_oudere
from praat_resultaten r
join audio a on a.audio_id = r.audio_id;''')
rijen = cur.fetchall()

# inladen
spraaksnelheid_leeftijdsgenoot = []
spraaksnelheid_oudere = []
geluidsniveau_leeftijdsgenoot = []
geluidsniveau_oudere = []
toonhoogte_leeftijdsgenoot = []
toonhoogte_oudere = []

for rij in rijen:
    if rij[3]:
        if rij[0]:
            spraaksnelheid_oudere.append(rij[0])
        if rij[1]:
            geluidsniveau_oudere.append(rij[1])
        if rij[2]:
            toonhoogte_oudere.append(rij[2])
    else:
        if rij[0]:
            spraaksnelheid_leeftijdsgenoot.append(rij[0])
        if rij[1]:
            geluidsniveau_leeftijdsgenoot.append(rij[1])
        if rij[2]:
            toonhoogte_leeftijdsgenoot.append(rij[2])

spraaksnelheid_leeftijdsgenoot = np.array(spraaksnelheid_leeftijdsgenoot)
spraaksnelheid_oudere = np.array(spraaksnelheid_oudere)
geluidsniveau_leeftijdsgenoot = np.array(geluidsniveau_leeftijdsgenoot)
geluidsniveau_oudere = np.array(geluidsniveau_oudere)
toonhoogte_leeftijdsgenoot = np.array(toonhoogte_leeftijdsgenoot)
toonhoogte_oudere = np.array(toonhoogte_oudere)

# verwerken: spraaksnelheid
print('spraaksnelheid_leeftijdsgenoot:')
print(spraaksnelheid_leeftijdsgenoot)
print()
print('Min:\t\t\t\t' + str(np.amin(spraaksnelheid_leeftijdsgenoot)))
print('Max:\t\t\t\t' + str(np.amax(spraaksnelheid_leeftijdsgenoot)))
print('Mean:\t\t\t\t' + str(np.mean(spraaksnelheid_leeftijdsgenoot)))
print('Median:\t\t\t\t' + str(np.median(spraaksnelheid_leeftijdsgenoot)))
print('Standard Deviation:\t' + str(np.median(spraaksnelheid_leeftijdsgenoot)))
print()
print('spraaksnelheid_oudere:')
print(spraaksnelheid_oudere)
print()
print('Min:\t\t\t\t' + str(np.amin(spraaksnelheid_oudere)))
print('Max:\t\t\t\t' + str(np.amax(spraaksnelheid_oudere)))
print('Mean:\t\t\t\t' + str(np.mean(spraaksnelheid_oudere)))
print('Median:\t\t\t\t' + str(np.median(spraaksnelheid_oudere)))
print('Standard Deviation:\t' + str(np.median(spraaksnelheid_oudere)))
print()
print('Diff:\t\t\t\t' + str(np.mean(spraaksnelheid_oudere) - np.mean(spraaksnelheid_leeftijdsgenoot)))

t_test = ttest_ind(spraaksnelheid_leeftijdsgenoot, spraaksnelheid_oudere, equal_var=False, alternative='greater')
print('Welch t-test:')
print('\tt = ' + str(t_test[0]))
print('\tp = ' + str(t_test[1]))
if t_test[1] < 0.05:
    print('\tSIGNIFICANT')
else:
    print('\tNIET SIGNIFICANT')

p1 = plt.plot(range(len(spraaksnelheid_leeftijdsgenoot)), spraaksnelheid_leeftijdsgenoot, 'r-', label='Leeftijdsgenoot')
p2 = plt.plot(range(len(spraaksnelheid_oudere)), spraaksnelheid_oudere, 'b-', label='Oudere')
plt.legend(loc='upper center', numpoints=1, bbox_to_anchor=(0.5, -0.05), ncol=2, fancybox=True, shadow=True)

plt.savefig('spraaksnelheid.png')
plt.close()

print()
print('====================================')
print()

# verwerken: geluidsniveau
print('geluidsniveau_leeftijdsgenoot:')
print(geluidsniveau_leeftijdsgenoot)
print()
print('Min:\t\t\t\t' + str(np.amin(geluidsniveau_leeftijdsgenoot)))
print('Max:\t\t\t\t' + str(np.amax(geluidsniveau_leeftijdsgenoot)))
print('Mean:\t\t\t\t' + str(np.mean(geluidsniveau_leeftijdsgenoot)))
print('Median:\t\t\t\t' + str(np.median(geluidsniveau_leeftijdsgenoot)))
print('Standard Deviation:\t' + str(np.median(geluidsniveau_leeftijdsgenoot)))
print()
print()
print('geluidsniveau_oudere:')
print(geluidsniveau_oudere)
print()
print('Min:\t\t\t\t' + str(np.amin(geluidsniveau_oudere)))
print('Max:\t\t\t\t' + str(np.amax(geluidsniveau_oudere)))
print('Mean:\t\t\t\t' + str(np.mean(geluidsniveau_oudere)))
print('Median:\t\t\t\t' + str(np.median(geluidsniveau_oudere)))
print('Standard Deviation:\t' + str(np.median(geluidsniveau_oudere)))
print()
print('Diff:\t\t\t\t' + str(np.mean(geluidsniveau_oudere) - np.mean(geluidsniveau_leeftijdsgenoot)))

t_test = ttest_ind(geluidsniveau_leeftijdsgenoot, geluidsniveau_oudere, equal_var=False, alternative='less')
print('Welch t-test:')
print('\tt = ' + str(t_test[0]))
print('\tp = ' + str(t_test[1]))
if t_test[1] < 0.05:
    print('\tSIGNIFICANT')
else:
    print('\tNIET SIGNIFICANT')

p1 = plt.plot(range(len(geluidsniveau_leeftijdsgenoot)), geluidsniveau_leeftijdsgenoot, 'r-', label='Leeftijdsgenoot')
p2 = plt.plot(range(len(geluidsniveau_oudere)), geluidsniveau_oudere, 'b-', label='Oudere')
plt.legend(loc='upper center', numpoints=1, bbox_to_anchor=(0.5, -0.05), ncol=2, fancybox=True, shadow=True)

plt.savefig('geluidsniveau.png')
plt.close()

print()
print('====================================')
print()

# verwerken: toonhoogte
print('toonhoogte_leeftijdsgenoot:')
print(toonhoogte_leeftijdsgenoot)
print()
print('Min:\t\t\t\t' + str(np.amin(toonhoogte_leeftijdsgenoot)))
print('Max:\t\t\t\t' + str(np.amax(toonhoogte_leeftijdsgenoot)))
print('Mean:\t\t\t\t' + str(np.mean(toonhoogte_leeftijdsgenoot)))
print('Median:\t\t\t\t' + str(np.median(toonhoogte_leeftijdsgenoot)))
print('Standard Deviation:\t' + str(np.median(toonhoogte_leeftijdsgenoot)))
print()
print()
print('toonhoogte_oudere:')
print(toonhoogte_oudere)
print()
print('Min:\t\t\t\t' + str(np.amin(toonhoogte_oudere)))
print('Max:\t\t\t\t' + str(np.amax(toonhoogte_oudere)))
print('Mean:\t\t\t\t' + str(np.mean(toonhoogte_oudere)))
print('Median:\t\t\t\t' + str(np.median(toonhoogte_oudere)))
print('Standard Deviation:\t' + str(np.median(toonhoogte_oudere)))
print()
print('Diff:\t\t\t\t' + str(np.mean(toonhoogte_oudere) - np.mean(toonhoogte_leeftijdsgenoot)))

t_test = ttest_ind(toonhoogte_leeftijdsgenoot, toonhoogte_oudere, equal_var=False, alternative='less')
print('Welch t-test:')
print('\tt = ' + str(t_test[0]))
print('\tp = ' + str(t_test[1]))
if t_test[1] < 0.05:
    print('\tSIGNIFICANT')
else:
    print('\tNIET SIGNIFICANT')

p1 = plt.plot(range(len(toonhoogte_leeftijdsgenoot)), toonhoogte_leeftijdsgenoot, 'r-', label='Leeftijdsgenoot')
p2 = plt.plot(range(len(toonhoogte_oudere)), toonhoogte_oudere, 'b-', label='Oudere')
plt.legend(loc='upper center', numpoints=1, bbox_to_anchor=(0.5, -0.05), ncol=2, fancybox=True, shadow=True)

plt.savefig('toonhoogte.png')
plt.close()