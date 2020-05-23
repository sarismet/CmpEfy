"""import sqlite3

DATABASE = "artist_listener.db"



db = sqlite3.connect(DATABASE)



db.cursor().execute('''CREATE TABLE IF NOT EXISTS artists(name TEXT NOT NULL,surname TEXT NOT NULL,listsofalbums TEXT NOT NULL)''')


db.cursor().execute('''INSERT INTO artists VALUES("İSMET", 'Alex', "8")''')
db.commit()


db.cursor().execute("SELECT name FROM artists")

print(db.cursor().fetchall())"""


import sqlite3

conn = sqlite3.connect('mysqlite.db')
c = conn.cursor()

#create table
c.execute('''CREATE TABLE IF NOT EXISTS artists(name TEXT NOT NULL,surname TEXT NOT NULL,listsofalbums TEXT NOT NULL)''')

c.execute('''INSERT INTO artists VALUES("İSMET", 'Alex', "8")''')

conn.commit()

c.execute("SELECT name FROM artists")
print(c.fetchall())