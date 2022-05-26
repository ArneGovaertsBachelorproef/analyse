import sqlite3, csv

db_file = 'elderspeak_detect.db'
con = sqlite3.connect(db_file)
cur = con.cursor()

test_data = []

with open('./luisteren.csv', encoding='utf-8-sig') as test_file:
    reader = csv.reader(test_file, delimiter=';')
    for trij in reader:
        if trij[0] != 'audio_id':
            test_data.append([int(trij[2]), int(trij[0])])

cur.execute('drop table if exists test_data')
cur.execute('''create table test_data (
    td_id                   integer primary key autoincrement,
    elderspeak              bool,
    audio_id                integer not null,
    foreign key(audio_id)   references audio(audio_id)
);''')
cur.executemany("insert into test_data (elderspeak,audio_id) values (?,?)", test_data)
con.commit()