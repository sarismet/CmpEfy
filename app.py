from flask import(
    Flask,
    render_template,
    request,
    session,
    g,
    redirect,
    url_for,
    send_from_directory
)
import sys
import re
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="sarismet",
    database="irelia"
)
c = db.cursor()


def get_artist_name():
    artist_name = ""
    if len(session["user"]) == 3:
        artist_name = session["user"][1]+" "+session["user"][2]
    elif len(session["user"]) == 2:
        artist_name = session["user"][1]
    return artist_name


def updating_album():
    albumid = str(session["properties"]["id_of_album"])
    new_genre_of_album = str(session["properties"]["new_genre_of_album"])
    new_title_of_album = str(session["properties"]["new_title_of_album"])
    sql_command = "UPDATE Albums SET genre = %s, title = %s WHERE id = %s "
    c.execute(sql_command, (new_genre_of_album, new_title_of_album, albumid,))
    db.commit()


def updating_song():
    songid = str(session["properties"]["id_of_song"])
    new_title_of_song = str(session["properties"]["new_title_of_song"])
    sql_update_query = """Update Songs set title = %s where id = %s"""
    data = (new_title_of_song, songid)
    c.execute(sql_update_query, data)
    sql_update_main = "UPDATE Main SET title = %s WHERE songid = %s"
    c.execute(sql_update_main, (new_title_of_song, songid,))
    db.commit()


def insert_album(likes=0):

    id = int(session["properties"]["albumid"])
    genre = str(session["properties"]["albumgenre"])
    title = str(session["properties"]["albumtitle"])
    creator = str(session["properties"]["creator"])
    sqlite_insert_with_param = """INSERT INTO Albums (id,genre,title,creator,operation)
                          SELECT * FROM (SELECT %s, %s, %s,%s,%s) AS tmp WHERE NOT EXISTS (SELECT id FROM Albums WHERE id = %s) LIMIT 1;"""
    data_tuple = (id, genre, title, creator, "NULL", id,)
    c.execute(sqlite_insert_with_param, data_tuple)
    db.commit()


def insert_song(mutual, likes=0):

    id = session["properties"]["songid"]
    title = session["properties"]["songtitle"]
    album_id = session["properties"]["which_album"]
    creator = session["properties"]["creator"]
    asistantartist = session["properties"]["asistantartist"] if mutual is True else "no"
    operation = "NULL"
    sqlite_insert_with_param = """INSERT INTO Songs
                          (id,title,albumid,creator,asistantartist,operation)
                          SELECT * FROM (SELECT %s, %s, %s,%s,%s,%s) AS tmp WHERE NOT EXISTS (SELECT id FROM Songs WHERE id = %s) LIMIT 1;"""

    c.execute(sqlite_insert_with_param, (id, title, album_id,
                                         creator, asistantartist, operation, id,))

    db.commit()


def insert_artist(nameandsurname):

    sqlite_insert_with_param = """INSERT INTO Artists(nameandsurname) VALUES (%s);"""
    c.execute(sqlite_insert_with_param, (nameandsurname,))
    sql_start = """INSERT INTO Main (wholiked,title,songid,albumid,creator,asistantartist)
                    VALUES (%s,%s,%s,%s,%s,%s);
                """
    c.execute(sql_start, ("the system", "the system title",
                          0, 0, nameandsurname, "no",))
    db.commit()


def insert_listener(email, username):

    sqlite_insert_with_param = """INSERT INTO Listeners
                          (email, username)
                          VALUES (%s, %s);"""
    c.execute(sqlite_insert_with_param, (email, username,))
    db.commit()


def create_table():
    sql_t1 = """CREATE TABLE IF NOT EXISTS Artists(
        nameandsurname VARCHAR(200) NOT NULL,
        PRIMARY KEY (nameandsurname)
        );"""
    c.execute(sql_t1)

    sql_t2 = """CREATE TABLE IF NOT EXISTS Listeners(
        email VARCHAR(100) NOT NULL,
        username VARCHAR(100) NOT NULL,
        PRIMARY KEY (username));"""
    c.execute(sql_t2)

    sql_t3 = """CREATE TABLE IF NOT EXISTS Albums(
        id INT NOT NULL,
        genre VARCHAR(30) NOT NULL,
        title TEXT NOT NULL,
        creator VARCHAR(200) NOT NULL,
        operation VARCHAR(30),
        PRIMARY KEY (id),
        FOREIGN KEY (creator) REFERENCES Artists(nameandsurname));"""
    c.execute(sql_t3)

    sql_t4 = """CREATE TABLE IF NOT EXISTS Songs(
        id INT NOT NULL,
        title TEXT NOT NULL,
        albumid INT NOT NULL,
        creator VARCHAR(200) NOT NULL,
        asistantartist VARCHAR(200) NOT NULL,
        operation VARCHAR(30),
        CONSTRAINT pkid PRIMARY KEY (id),
        FOREIGN KEY (albumid) REFERENCES Albums(id),
        FOREIGN KEY (creator) REFERENCES Artists(nameandsurname));"""
    c.execute(sql_t4)

    sql_t5 = """CREATE TABLE IF NOT EXISTS Main(
        wholiked VARCHAR(100) NOT NULL,
        title TEXT NOT NULL,
        songid INT NOT NULL,
        albumid INT NOT NULL,
        creator VARCHAR(200) NOT NULL,
        asistantartist VARCHAR(200) NOT NULL);"""
    c.execute(sql_t5)

    stmt = "SHOW TABLES LIKE 'currentListener'"
    c.execute(stmt)
    result = c.fetchone()
    if not result:
        c.execute('''CREATE TABLE currentListener(username VARCHAR(100));''')
        c.execute("INSERT INTO currentListener(username) VALUES('NULL');")

    c.execute(
        '''CREATE TABLE IF NOT EXISTS rank_artists(artistnames VARCHAR(200));''')
    c.execute('''CREATE TABLE IF NOT EXISTS partners(artistnames VARCHAR(200));''')
    db.commit()


app = Flask(__name__)
app.secret_key = "ismetsari"
app.static_folder = 'static'


@app.route('/login', methods=['GET', 'POST'])
def login():
    create_table()
    session.pop("user", None)
    session.pop("ERROR", None)
    session.pop("goal", None)

    if request.method == 'POST':
        if request.form["button"] == "listener":
            email = str(request.form['email_of_listener'])
            username = str(request.form['username_of_listener'])
            query = "SELECT * FROM Listeners where email = %s and username = %s"

            c.execute(query, (email, username))

            row = c.fetchone()

            if row == None:
                insert_listener(
                    request.form['email_of_listener'], request.form['username_of_listener'])

            sql = "UPDATE currentListener SET username = %s "
            c.execute(sql, (username,))
            db.commit()

            session['user'] = ["listener", request.form['email_of_listener'],
                               request.form['username_of_listener']]

            return redirect(url_for('listener'))

        elif request.form["button"] == "artist":
            name = request.form['name_of_artist']
            surname = request.form['surname_of_artist']

            query = "SELECT * FROM Artists where nameandsurname = %s "

            s = str(name)+"_"+str(surname)
            c.execute(query, (s,))

            row = c.fetchone()
            if row == None:
                insert_artist(s)

            session['user'] = ["artist", request.form['name_of_artist'],
                               request.form['surname_of_artist']]
            return redirect(url_for('artist'))
    return render_template('login.html')


@app.route('/artist', methods=['GET', 'POST'])
def artist():
    if "user" in session:
        name = session["user"][1]+" "+session["user"][2]
        if request.method == 'POST':
            if request.form["button"] == "add_a_song":
                session["goal"] = "add_song"
                return redirect(url_for('add_song'))
            elif request.form["button"] == "add_an_album":

                session["goal"] = "add_album"

                return redirect(url_for('add_album'))

            elif request.form["button"] == "delete_an_album":
                session["goal"] = "delete_album"
                return redirect(url_for('delete_album'))

            elif request.form["button"] == "delete_a_song":
                session["goal"] = "delete_song"
                return redirect(url_for('delete_song'))

            elif request.form["button"] == "update_an_album":
                session["goal"] = "update_album"
                return redirect(url_for('update_album'))

            elif request.form["button"] == "update_a_song":
                session["goal"] = "update_song"
                return redirect(url_for('update_song'))

            elif request.form["a"] == "home":
                return redirect(url_for('login'))

        return render_template('artist.html', Artist_name=name)


@app.route('/listener', methods=['GET', 'POST'])
def listener():
    if "user" in session:
        listener_username = session["user"][2]
        if request.method == 'POST':
            if request.form["button"] == "view_all_everything":
                session["goal"] = "view_all_everything"

                return redirect(url_for('view_all_everything'))

            elif request.form["button"] == "view_all_everything_of_artist":
                session["goal"] = "view_all_artist"
                return redirect(url_for('view_all_artist'))

            elif request.form["button"] == "view_others_liked_song":
                session["goal"] = "view_others_liked_song"
                return redirect(url_for('view_others_liked_song'))

            elif request.form["button"] == "view_popular_song_of_an_artist":
                session["goal"] = "view_popular_song_of_an_artist"
                return redirect(url_for('view_popular_song_of_an_artist'))

            elif request.form["button"] == "rank_artists":
                session["goal"] = "rank_artists"
                return redirect(url_for('rank_artists'))

            elif request.form["button"] == "view_a_song_with_specific_genre":
                session["goal"] = "view_a_song_with_specific_genre"
                return redirect(url_for('view_a_song_with_specific_genre'))

            elif request.form["button"] == "Search_a_keyword":
                session["goal"] = "search_a_keyword"
                return redirect(url_for('search_a_keyword'))

            elif request.form["button"] == "view_partners":
                session["goal"] = "view_partners"
                return redirect(url_for('view_partners'))

            elif request.form["button"] == "like_album_or_song":
                session["goal"] = "like_album_or_song"

                return redirect(url_for('like_album_or_song'))

            elif request.form["button"] == "view_all_songs_of_an_album":
                session["goal"] = "view_all_songs_of_an_album"

                return redirect(url_for('view_all_songs_of_an_album'))
        return render_template('listener.html', Listener=listener_username)


@app.route('/add_song', methods=['GET', 'POST'])
def add_song():
    artist_name = get_artist_name()

    if request.method == 'POST':
        mutual = False
        if request.form["button"] == "add_individual_song":
            creator = re.sub(" ", "_", artist_name)

            session["properties"] = {"songid": request.form['ID_of_song'], "songtitle": request.form['title_of_song'],
                                     "which_album": request.form['which_album'], "creator": creator}

        elif request.form["button"] == "add_common_song":
            mutual = True
            creator = re.sub(" ", "_", artist_name)

            asistans = re.sub(", ", ",", str(
                request.form['name_of_assistant']))
            asistans = re.sub(" ", "_", asistans)

            check = asistans.split(",")
            for ch in check:

                stmt = "SELECT nameandsurname FROM Artists WHERE nameandsurname LIKE %s"
                c.execute(stmt, (ch,))
                result = c.fetchone()
                if not result:
                    insert_artist(ch)

            session["properties"] = {"songid": request.form['ID_of_song'], "songtitle": request.form['title_of_song'],
                                     "which_album": request.form['which_album'],
                                     "asistantartist": asistans, "creator": creator}

        insert_song(mutual)

        return redirect(url_for('artist'))

    return render_template('add_song.html', Artist=artist_name)


@app.route('/add_album', methods=['GET', 'POST'])
def add_album():
    artist_name = get_artist_name()
    if request.method == 'POST':
        creator = re.sub(" ", "_", artist_name)
        session["properties"] = {"albumid": request.form['id_of_album'], "albumgenre": request.form['genre_of_album'],
                                 "albumtitle": request.form['title_of_album'], "creator": creator}
        insert_album()
        return redirect(url_for('artist'))
    return render_template('add_album.html', Artist=artist_name)


@app.route('/update_album', methods=['GET', 'POST'])
def update_album():
    artist_name = get_artist_name()

    if request.method == 'POST':
        albumid = request.form['id_of_album']
        sql = "SELECT creator From Albums WHERE id = %s"
        c.execute(sql, (albumid,))
        row = c.fetchall()
        creator = row[0][0]
        if creator == re.sub(" ", "_", artist_name):

            session["properties"] = {"id_of_album": request.form['id_of_album'], "new_genre_of_album":
                                     request.form['new_genre_of_album'], "new_title_of_album": request.form['new_title_of_album']}

            updating_album()

            return redirect(url_for('artist'))
        else:
            session["ERROR"] = "You are not allowed to update this album"
            return redirect(url_for('error'))

    return render_template('update_album.html', Artist=artist_name)


@app.route('/update_song', methods=['GET', 'POST'])
def update_song():
    artist_name = get_artist_name()
    if "update_song" == session["goal"]:
        if request.method == 'POST':
            songid = request.form['id_of_song']
            sql = "SELECT creator From Songs WHERE id = %s"
            c.execute(sql, (songid,))
            row = c.fetchall()
            creator = row[0][0]
            if creator == re.sub(" ", "_", artist_name):
                session["properties"] = {"id_of_song": songid,
                                         "new_title_of_song": request.form['new_title_of_song']}
                updating_song()
                return redirect(url_for('artist'))
            else:
                session["ERROR"] = "You are not allowed to update this song"
                return redirect(url_for('error'))
        return render_template('update_song.html', Artist=artist_name)


@app.route('/view_all_everything')
def view_all_everything():

    c.execute("select title from Songs")
    rows = c.fetchall()
    db.commit()
    my_song_array = []
    for row in rows:
        my_song_array.append(row[0])

    c.execute("select genre,title from Albums")
    rows = c.fetchall()
    db.commit()
    my_album_dict = []
    for row in rows:
        my_album_dict.append({"genre": row[0], "title": row[1]})

    c.execute("select nameandsurname from Artists")
    rows = c.fetchall()
    db.commit()
    my_artist_array = []
    for row in rows:
        name = re.sub("_", " ", row[0])
        my_artist_array.append(name)

    return render_template('view_all_everything.html', my_song_li=my_song_array, my_album_di=my_album_dict, my_artist_li=my_artist_array)


@app.route('/view_all_artist', methods=['GET', 'POST'])
def view_all_artist():

    if request.method == 'POST':

        name = request.form['name']
        surname = request.form['surname']
        artist_name = name+"_"+surname
        sql_cmd = "select title from Albums where creator = %s"
        c.execute(sql_cmd, (artist_name,))
        rows = c.fetchall()
        db.commit()

        array_of_albums = []
        for row in rows:
            array_of_albums.append(row[0])
        keyword = "%"+artist_name+"%"
        sql_cmd = "select title from Songs where creator = %s or asistantartist LIKE %s "
        c.execute(sql_cmd, (artist_name, keyword,))
        rows = c.fetchall()
        db.commit()

        array_of_songs = []
        for row in rows:
            array_of_songs.append(row[0])

        return render_template('view_all_artist.html', songslist=array_of_songs, albums=array_of_albums)

    return render_template('view_all_artist.html')


@app.route('/view_all_songs_of_an_album', methods=['GET', 'POST'])
def view_all_songs_of_an_album():

    if request.method == 'POST':

        albumid = request.form['albumid']

        sql_cmd = "select title from Songs where albumid = %s "
        c.execute(sql_cmd, (albumid,))
        rows = c.fetchall()
        db.commit()

        array_of_songs = []
        for row in rows:
            array_of_songs.append(row[0])

        return render_template('view_all_song_album.html', songslist=array_of_songs)

    return render_template('view_all_song_album.html')


@app.route('/view_a_song_with_specific_genre', methods=['GET', 'POST'])
def view_a_song_with_specific_genre():

    if request.method == 'POST':

        the_genre = request.form["genre_of_song"]
        sql_cmd = "select title from Songs WHERE albumid IN (SELECT id FROM Albums WHERE genre = %s)"

        c.execute(sql_cmd, (the_genre,))
        rows = c.fetchall()
        db.commit()

        array_of_songs = []
        for row in rows:
            array_of_songs.append(row[0])

        return render_template('view_a_song_with_specific_genre.html', songs=array_of_songs)

    return render_template('view_a_song_with_specific_genre.html')


@app.route('/view_others_liked_song', methods=['GET', 'POST'])
def view_others_liked_song():

    if request.method == 'POST':
        if request.form["button"] == "compare":
            my_username = session["user"][2]
            username_of_other = request.form["username_of_other"]

            sql_other = "SELECT title FROM Main WHERE wholiked = %s"
            c.execute(sql_other, (username_of_other,))
            rows = c.fetchall()
            db.commit()
            others_liked_song = []
            for row in rows:
                others_liked_song.append(row[0])

            sql_my = "SELECT title FROM Main WHERE wholiked = %s"
            c.execute(sql_my, (my_username,))
            rows = c.fetchall()
            db.commit()
            my_liked_song = []
            for row in rows:
                my_liked_song.append(row[0])

            return render_template('view_others_liked_songs.html', yourlists=my_liked_song, otherslists=others_liked_song)

    return render_template('view_others_liked_songs.html')


@app.route('/view_popular_song_of_an_artist', methods=['GET', 'POST'])
def view_popular_song_of_an_artist():

    if request.method == 'POST':
        if request.form["button"] == "search":

            name_surname = request.form["name_of_artist"] + \
                "_"+request.form["surname_of_artist"]
            keyword = "%"+name_surname+"%"
            sql_cmd = "SELECT title,count(title) FROM Main WHERE (creator = %s or asistantartist LIKE %s) and wholiked <> 'the system' GROUP BY title ORDER BY count(*) DESC LIMIT 3;"
            c.execute(sql_cmd, (name_surname, keyword,))
            rows = c.fetchall()
            print("rows is : ", rows, file=sys.stdout)
            db.commit()
            popular_songs = []
            for row in rows:
                popular_songs.append(row[0])

            return render_template('view_all_popular_artist.html', songs=popular_songs)

    return render_template('view_all_popular_artist.html')


@app.route('/search_a_keyword', methods=['GET', 'POST'])
def search_a_keyword():

    if request.method == 'POST':
        if request.form["button"] == "search":
            keyword = "%"+request.form["keyword"]+"%"
            sql_cmd = "SELECT title FROM Songs WHERE title LIKE %s"
            c.execute(sql_cmd, (keyword,))
            rows = c.fetchall()
            db.commit()

            array_of_songs = []
            for row in rows:
                array_of_songs.append(row[0])

            return render_template('search_a_keyword.html', songs=array_of_songs)
    return render_template('search_a_keyword.html')


@app.route('/like_album_or_song', methods=['GET', 'POST'])
def like_album_or_song():

    if request.method == 'POST':
        if request.form["button"] == "song":
            username = session["user"][2]
            songid = request.form["songid"]

            sql_update = "UPDATE Songs SET operation='like song' WHERE id = %s"
            c.execute(sql_update, (songid,))
            db.commit()

        elif request.form["button"] == "album":

            username = session["user"][2]
            albumid = request.form["albumid"]

            sql_update = "UPDATE Songs SET operation='like album' WHERE albumid = %s"
            c.execute(sql_update, (albumid,))
            db.commit()

    return render_template('like_album_or_song.html')


@app.route('/delete_song', methods=['GET', 'POST'])
def delete_song():
    name = session["user"][1]
    surname = session["user"][2]
    artist_name = name+" "+surname
    if request.method == 'POST':
        if request.form["button"] == "delete_song":

            songid = request.form["id_of_song"]

            sql = "SELECT creator From Songs WHERE id = %s"
            c.execute(sql, (songid,))
            row = c.fetchall()
            creator = row[0][0]
            if creator == name+"_"+surname:

                sql_update = "UPDATE Songs SET operation = 'delete song' WHERE id = %s"
                c.execute(sql_update, (songid,))

                sql_detete = "DELETE FROM Songs Where id = %s"
                c.execute(sql_detete, (songid,))
                db.commit()

            else:
                session["ERROR"] = "You are not allowed to delete this song"
                return redirect(url_for('error'))
    return render_template('delete_song.html', Artist=artist_name)


@app.route('/delete_album', methods=['GET', 'POST'])
def delete_album():
    artist_name = session["user"][1]+" "+session["user"][2]
    if request.method == 'POST':
        if request.form["button"] == "delete_album":
            albumid = request.form["id_of_album"]

            sql_cmd = "SELECT creator FROM Albums WHERE id = %s"
            c.execute(sql_cmd, (albumid,))
            row = c.fetchall()
            creator = row[0][0]

            name_surname = session["user"][1]+"_"+session["user"][2]

            if name_surname == str(creator):

                sql_update = "UPDATE Albums SET operation = 'delete album' WHERE id = %s"
                c.execute(sql_update, (albumid,))

                sql_delete = "DELETE FROM Albums WHERE id = %s"
                c.execute(sql_delete, (albumid,))
                db.commit()

            else:
                session["ERROR"] = "You are not allowed to delete this album."
                return redirect(url_for('error'))

    return render_template('delete_album.html', Artist=artist_name)


@app.route('/view_partners', methods=['GET', 'POST'])
def view_partners():
    if request.method == 'POST':

        name = request.form["name_of_artist"]
        surname = request.form["surname_of_artist"]
        name_of_partners = []

        c.callproc('curdemo', [name, surname, ])
        print("Printing stored_results details",
              c.stored_results(), file=sys.stdout)
        for result in c.stored_results():
            rows = result.fetchall()
            for row in rows:
                name = re.sub("_", " ", row[0])
                name_of_partners.append(name)

        c.execute("DELETE FROM partners;")
        db.commit()
        return render_template('view_partners.html', partners=name_of_partners)

    return render_template('view_partners.html')


@app.route('/rank_artists', methods=['GET', 'POST'])
def rank_artists():

    sql_cmd2 = """select asistantartist from Main where asistantartist <> 'no';"""
    c.execute(sql_cmd2)

    rows = c.fetchall()

    for row in rows:
        thename = row[0]
        c.callproc("Splitforrank", [thename, ])

    sql_cmd = """insert into rank_artists select creator from Main;"""
    c.execute(sql_cmd)
    db.commit()

    sql_main = "SELECT artistnames,count(artistnames) FROM rank_artists GROUP BY artistnames ORDER BY count(*) DESC;"
    c.execute(sql_main)
    rank_array = []
    rows = c.fetchall()
    db.commit()
    for row in rows:
        name = re.sub("_", " ", row[0])
        rank_array.append(name)
    c.execute("delete from rank_artists;")
    db.commit()
    return render_template('rank_artist.html', artists=rank_array)


@app.route('/error', methods=['GET', 'POST'])
def error():

    message = session["ERROR"]
    if request.method == 'POST':
        session.pop("ERROR", "None")
        return redirect(url_for('login'))

    return render_template('error.html', masage=message)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
