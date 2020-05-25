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
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="sarismet",
    database="mydb"
)
c = db.cursor()


def updating_album():
    albumid = str(session["properties"]["id_of_album"])
    new_genre_of_album = str(session["properties"]["new_genre_of_album"])
    new_title_of_album = str(session["properties"]["new_title_of_album"])

    sql_command = "UPDATE Artists SET genre = "+new_genre_of_album + \
        ", title "+new_title_of_album+" WHERE id = "+albumid

    c.execute(sql_command)
    db.commit()


def updating_song():
    songid = str(session["properties"]["id_of_song"])
    new_title_of_song = str(session["properties"]["new_title_of_song"])

    sql_update_query = """Update Songs set title = %s where id = %s"""
    data = (new_title_of_song, songid)

    c.execute(sql_update_query, data)
    db.commit()


def insert_album(likes=0):

    name = str(session["user"][1])
    surname = str(session["user"][2])
    id = int(session["properties"]["albumid"])
    genre = str(session["properties"]["albumgenre"])
    title = str(session["properties"]["albumtitle"])
    creator = str(session["properties"]["creator"])
    sqlite_insert_with_param = """INSERT INTO Albums
                          (id,genre,title,likes,listsofsongs,creator)
                          VALUES (%s,%s,%s,%s,%s,%s);"""
    listsofsongs = "songs"+str(id)
    data_tuple = (id, genre, title, likes, listsofsongs, creator)

    c.execute(sqlite_insert_with_param, data_tuple)

    string = "CREATE TABLE IF NOT EXISTS " + \
        listsofsongs+" (idofsong INT NOT NULL);"
    c.execute(string)

    listsofalbumsofartist = str(name)+str(surname)+"listsofalbums"

    sql_commad = "INSERT INTO "+listsofalbumsofartist + \
        "(idofalbum) VALUES ("+str(id)+");"
    c.execute(sql_commad)
    db.commit()


def insert_song(mutual, likes=0):

    id = session["properties"]["songid"]
    album_id = session["properties"]["which_album"]
    title = session["properties"]["songtitle"]
    creator = session["properties"]["creator"]
    asistant_artist = "no"
    if mutual is True:
        asistant_artist = session["properties"]["asistant_artist"]

    sqlite_insert_with_param = """INSERT INTO Songs
                          (id,title,likes,albumid,creator,asistant_artist)
                          VALUES (%s,%s,%s,%s,%s,%s);"""
    songs_table = "songs"+str(album_id)
    sqlite_insert_with_param_2 = "INSERT INTO {} (idofsong) VALUES ({});".format(
        songs_table, id)
    data_tuple = (id, title, likes, album_id, creator, asistant_artist)

    c.execute(sqlite_insert_with_param, data_tuple)
    c.execute(sqlite_insert_with_param_2)
    if asistant_artist != "no":
        coworker_table = creator+"coworkers"
        sql_command = "INSERT INTO {} (name) VALUES ('{}')".format(
            coworker_table, asistant_artist)
        c.execute(sql_command)
    db.commit()


def insert_artist(name, surname, likes=0):

    sqlite_insert_with_param = """INSERT INTO Artists
                          (name_surname,listsofalbums,likes,coworker)
                          VALUES (%s, %s,%s,%s);"""
    listsofalbums = str(name)+str(surname)+"listsofalbums"
    name_surname = str(name)+"_"+str(surname)
    coworker = name_surname+"coworkers"
    data_tuple = (name_surname, listsofalbums, likes, coworker)

    c.execute(sqlite_insert_with_param, data_tuple)
    string = "CREATE TABLE IF NOT EXISTS " + \
        listsofalbums+" (idofalbum INT NOT NULL);"
    c.execute(string)

    string2 = "CREATE TABLE IF NOT EXISTS " + \
        coworker+" (name TEXT NOT NULL);"
    c.execute(string2)
    db.commit()


def insert_listener(email, username):

    sqlite_insert_with_param = """INSERT INTO Listeners
                          (email, username,listsoflikedsongs)
                          VALUES (%s, %s,%s);"""
    listsoflikedsongs = str(username)+"likedsongs"
    data_tuple = (email, username, listsoflikedsongs)

    c.execute(sqlite_insert_with_param, data_tuple)
    string = "CREATE TABLE IF NOT EXISTS " + \
        listsoflikedsongs+" (idofsong INT NOT NULL);"
    c.execute(string)
    db.commit()


def create_table():
    c.execute('''
    CREATE TABLE IF NOT EXISTS Artists(name_surname TEXT NOT NULL,listsofalbums VARCHAR(45) NOT NULL,
    likes INT NOT NULL,coworker TEXT NOT NULL
    );
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS Listeners(email TEXT NOT NULL,
    username TEXT NOT NULL,listsoflikedsongs TEXT NOT NULL
    );
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS Albums(id INT NOT NULL,
    genre TEXT NOT NULL , title TEXT , likes INT , listsofsongs TEXT, creator TEXT NOT NULL
    );
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS Songs(id INT NOT NULL,
    title TEXT NOT NULL, likes INT, albumid INT NOT NULL,creator TEXT NOT NULL,asistant_artist TEXT NOT NULL
    );
    ''')

    db.commit()


app = Flask(__name__)
app.secret_key = "ismetsari"
app.static_folder = 'static'


@app.route('/login', methods=['GET', 'POST'])
def login():
    create_table()

    if request.method == 'POST':
        if request.form["button"] == "listener":
            email = str(request.form['email_of_listener'])
            username = str(request.form['username_of_listener'])
            query = "SELECT * FROM Listeners where email = '{}' and username = '{}' ".format(
                email, username)

            c.execute(query)

            row = c.fetchone()

            print("ROW BURDA ", file=sys.stdout)

            if row == None:
                insert_listener(
                    request.form['email_of_listener'], request.form['username_of_listener'])

            session['user'] = ["listener", request.form['email_of_listener'],
                               request.form['username_of_listener']]

            return redirect(url_for('listener'))

        elif request.form["button"] == "artist":
            name_surname = str(
                request.form['name_of_artist'])+"_"+str(request.form['surname_of_artist'])
            query = "SELECT * FROM Artists where name_surname = %s "

            c.execute(query, (name_surname,))

            row = c.fetchone()
            print("ROW BURDA ", row, file=sys.stdout)
            if row == None:
                insert_artist(
                    request.form['name_of_artist'], request.form['surname_of_artist'])

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
                return redirect(url_for('delete_album'))

            elif request.form["button"] == "delete_a_song":
                return redirect(url_for('delete_song'))

            elif request.form["button"] == "update_an_album":
                session["goal"] = "update_album"
                return redirect(url_for('update_album'))

            elif request.form["button"] == "update_a_song":
                session["goal"] = "update_song"
                return redirect(url_for('update_song'))

        return render_template('artist.html', Artist_name=name)


@app.route('/listener', methods=['GET', 'POST'])
def listener():
    if "user" in session:
        if request.method == 'POST':
            if request.form["button"] == "view_all_everything":
                session["goal"] = "view_all_everything"

                return redirect(url_for('view_all_everything'))

            elif request.form["button"] == "view_all_everything_of_artist":
                session["goal"] = "view_all_artist"
                return redirect(url_for('view_all_artist'))

            elif request.form["button"] == "view_others_liked_song":
                return redirect(url_for('view_others_liked_song'))

            elif request.form["button"] == "view_popular_song_of_an_artist":
                return redirect(url_for('view_popular_song_of_an_artist'))

            elif request.form["button"] == "rank_artists":
                return redirect(url_for('rank_artists'))

            elif request.form["button"] == "view_a_song_with_specific_genre":
                session["goal"] = "view_a_song_with_specific_genre"
                return redirect(url_for('view_a_song_with_specific_genre'))

            elif request.form["button"] == "Search_a_keyword":
                return redirect(url_for('search_a_keyword'))

            elif request.form["button"] == "view_partners":
                session["goal"] = "view_partners"
                return redirect(url_for('view_partners'))

            elif request.form["button"] == "like_album_or_song":
                session["goal"] = "like_album_or_song"

                return redirect(url_for('like_album_or_song'))

        return render_template('listener.html')


@app.route('/add_song', methods=['GET', 'POST'])
def add_song():

    if "add_song" == session["goal"]:
        if request.method == 'POST':
            mutual = False
            if request.form["button"] == "add_individual_song":
                creator = session['user'][1]+session['user'][2]
                session["properties"] = {"songid": request.form['ID_of_song'], "songtitle": request.form['title_of_song'],
                                         "which_album": request.form['which_album'], "creator": creator}

            elif request.form["button"] == "add_common_song":
                mutual = True
                creator = session['user'][1]+session['user'][2]
                session["properties"] = {"songid": request.form['ID_of_song'], "songtitle": request.form['title_of_song'],
                                         "which_album": request.form['which_album'],
                                         "asistant_artist": request.form['name_of_assistant'], "creator": creator}

            insert_song(mutual)

            return redirect(url_for('artist'))

    return render_template('add_song.html')


@app.route('/add_album', methods=['GET', 'POST'])
def add_album():

    if "add_album" == session["goal"]:
        if request.method == 'POST':
            creator = session['user'][1]+session['user'][2]
            session["properties"] = {"albumid": request.form['id_of_album'], "albumgenre": request.form['genre_of_album'],
                                     "albumtitle": request.form['title_of_album'], "creator": creator}

            insert_album()

            return redirect(url_for('artist'))

        return render_template('add_album.html')


@app.route('/delete_song')
def delete_song():

    return render_template('delete_song.html')


@app.route('/delete_album')
def delete_album():

    return render_template('delete_album.html')


@app.route('/update_album', methods=['GET', 'POST'])
def update_album():

    if "update_album" == session["goal"]:
        if request.method == 'POST':

            session["properties"] = {"albumid": request.form['id_of_album'], "new_genre_of_album":
                                     request.form['new_genre_of_album'], "new_title_of_album": request.form['new_title_of_album']}

            updating_album()

            return redirect(url_for('artist'))

        return render_template('update_album.html')


@app.route('/update_song', methods=['GET', 'POST'])
def update_song():

    if "update_song" == session["goal"]:
        if request.method == 'POST':

            session["properties"] = {"id_of_song": request.form['id_of_song'],
                                     "new_title_of_song": request.form['new_title_of_song']}

            updating_song()

            return redirect(url_for('artist'))

        return render_template('update_song.html')


@app.route('/view_all_everything')
def view_all_everything():
    if "view_all_everything" == session["goal"]:

        c.execute("select * from Songs")
        rows = c.fetchall()
        print('This is row output in Songs', rows, file=sys.stdout)
        my_song_array = []

        for row in rows:

            my_song_array.append(row[1])

            print('This is row output in songs', row, file=sys.stdout)

        c.execute("select * from Albums")
        rows = c.fetchall()
        my_album_dict = []
        for row in rows:
            my_album_dict.append({"genre": row[1], "title": row[2]})
            print('This is row output in Albums', row, file=sys.stdout)

        c.execute("select * from Artists")
        rows = c.fetchall()
        my_artist_array = []
        for row in rows:

            x = row.split("_")

            name = x[0]+" "+x[1]
            my_artist_array.append(name)
            print('This is row output in Artists', row, file=sys.stdout)

    return render_template('view_all_everything.html', my_song_li=my_song_array, my_album_di=my_album_dict, my_artist_li=my_artist_array)


@app.route('/view_all_artist', methods=['GET', 'POST'])
def view_all_artist():
    if "view_all_artist" == session["goal"]:
        if request.method == 'POST':

            name = request.form['name']
            surname = request.form['surname']

            sql_cmd = "select listsofalbums from Artists where name = '%s' and surname = '%s' "
            data = (name, surname)
            albumplace = c.execute(sql_cmd, data).fetchall()

            print("albumplace is", albumplace, file=sys.stdout)

            take_all_albumsid = "select * from "+albumplace[0][0]

            albumsids = c.execute(take_all_albumsid).fetchall()

            print("albumsids is", albumsids, file=sys.stdout)

            array_of_albums = []
            for row in albumsids:
                print("row is", row[0], file=sys.stdout)
                st = "select * from Albums where id = "+str(row[0])

                albumproperty = c.execute(st).fetchall()

                array_of_albums.append(
                    {"genre": albumproperty[0][1], "title": albumproperty[0][2]})

                songplace = str(albumproperty[0][4])

                stx = "select idofsong from "+songplace

                songids = c.execute(stx).fetchall()
                print("songids is", songids, file=sys.stdout)
                songstitles = []
                for i in songids:
                    print("i is", i, file=sys.stdout)
                    sql_cmd = "select title from Songs where id = "+str(i[0])

                    songstitle = c.execute(sql_cmd).fetchall()
                    songstitles.append(songstitle[0][0])

            return render_template('view_all_artist.html', songslist=songstitles, albums=array_of_albums)

    return render_template('view_all_artist.html')


@app.route('/view_a_song_with_specific_genre', methods=['GET', 'POST'])
def view_a_song_with_specific_genre():
    if "view_a_song_with_specific_genre" == session["goal"]:
        if request.method == 'POST':

            the_type = request.form["genre_of_song"]

            sql_cmd = "select listsofsongs from Albums WHERE genre = '"+the_type+"'"

            specificsongs = c.execute(sql_cmd).fetchall()
            print("specificsongs is", specificsongs, file=sys.stdout)

            stx = "select idofsong from "+specificsongs[0][0]

            songids = c.execute(stx).fetchall()
            print("songids is", songids, file=sys.stdout)
            songstitles = []
            for i in songids:
                print("i is", i, file=sys.stdout)
                sql_cmd = "select title from Songs where id = "+str(i[0])

                songstitle = c.execute(sql_cmd).fetchall()
                songstitles.append(songstitle[0][0])

            return render_template('view_a_song_with_specific_genre.html', songs=songstitles)

    return render_template('view_a_song_with_specific_genre.html')


@app.route('/view_others_liked_song')
def view_others_liked_song():

    return render_template('view_others_liked_songs.html')


@app.route('/view_popular_song_of_an_artist')
def view_popular_song_of_an_artist():

    return render_template('view_all_popular_artist.html')


@app.route('/search_a_keyword')
def search_a_keyword():

    return render_template('search_a_keyword.html')


@app.route('/like_album_or_song', methods=['GET', 'POST'])
def like_album_or_song():
    if request.method == 'POST':
        if request.form["button"] == "song":
            username = session["user"][2]
            songid = request.form["songid"]
            sql_command = "UPDATE Songs SET likes = likes+1 WHERE id = {}".format(
                songid)

            c.execute(sql_command)
            db.commit()

            sql_cmd = "select * from Songs WHERE id = {}".format(songid)

            specificsongs = c.execute(sql_cmd).fetchall()

            adbumid = specificsongs[0][3]
            creator = specificsongs[0][4]

            sql_command = "UPDATE Albums SET likes = likes+1 WHERE id = {}".format(
                adbumid)
            c.execute(sql_command)

            sql_cmd = "select listsoflikedsongs from Listeners WHERE username = '{}'".format(
                username)
            listsoflikedsongs = c.execute(sql_cmd).fetchall()[0][0]

            sql_command = "INSERT INTO {} (idofsong) VALUES ({})".format(
                listsoflikedsongs, songid)
            c.execute(sql_command)
            db.commit()
            sql_command = "UPDATE Artists SET likes = likes+1 WHERE name_surname = '{}'".format(
                creator)
            c.execute(sql_command)
            db.commit()
        elif request.form["button"] == "album":
            albumid = request.form["albumid"]
            table_liked_songs = str(session["user"][2])+"likedsongs"

            f=open("file.txt","r")
            sql_trigger=""
            lines=f.read()
            

            c.execute(lines)

            query = "UPDATE Albums set likes = (likes + (select count(*) from Songs where albumid = {})); ".format(
                albumid)
            #c.execute(query)
            db.commit()

    return render_template('like_album_or_song.html')


@app.route('/view_partners', methods=['GET', 'POST'])
def view_partners():
    if request.method == 'POST':
        if request.form["button"] == "search":
            name = request.form["name_of_artist"]
            surname = request.form["surname_of_artist"]

            coworker_table_name = name+surname+"coworkers"

            sql_cmd = "SELECT name From "+coworker_table_name

            c.execute(sql_cmd)

            rows = c.fetchall()
            name_of_partners = []
            for row in rows:
                name_of_partners.append(row[0])

            return render_template('view_partners.html', partners=name_of_partners)

    return render_template('view_partners.html')


if __name__ == '__main__':
    app.run(port=5000, debug=True)