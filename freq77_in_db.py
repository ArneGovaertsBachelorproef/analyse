import sqlite3

con = sqlite3.connect('elderspeak_detect.db')
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS freq77 (
    number  INTEGER PRIMARY KEY AUTOINCREMENT,
    word    TEXT NOT NULL
);""")

with open('freq77.txt') as freq77_file:
    while True:
        line = freq77_file.readline()
        if not line:
            break
        line = str(line.lstrip().rstrip())
        if line != '' and line[0] != '#':
            print(line)
            cur.execute("INSERT INTO freq77 (word) VALUES (:word)", {
                'word': line
            })

con.commit()
con.close()