import sqlite3, csv

db_file = 'elderspeak_detect.db'
con = sqlite3.connect(db_file)
cur = con.cursor()

test_data = []

with open('./test.csv', encoding='utf-8') as test_file:
    reader = csv.reader(test_file, delimiter=';')
    for trij in reader:
        cur.execute("select audio_id from teksten where methode = 'GOOGLE_ENKEL_NL_BE' and tekst = ?", [trij[0]])
        sel = cur.fetchone()

        if sel is not None:
            test_data.append([trij[0], int(trij[1]), sel[0]])

print(test_data)

cur.execute('''create table if not exists test_data (
    td_id                   integer primary key autoincrement,
    tekst                   text,
    elderspeak              bool,
    audio_id                integer not null,
    foreign key(audio_id)   references audio(audio_id)
);''')
cur.executemany("insert into test_data (tekst,elderspeak,audio_id) values (?,?,?)", test_data)
con.commit()