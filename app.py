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
import sqlite3


DATABASE = "Artist_Listener.db"



def get_db():
    db = sqlite3.connect(DATABASE)
    return db


def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.cursor().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def updating_album():
    albumid=str(session["properties"]["id_of_album"])
    new_genre_of_album=str(session["properties"]["new_genre_of_album"])
    new_title_of_album=str(session["properties"]["new_title_of_album"])


    sql_command="UPDATE Artists SET genre = "+new_genre_of_album+", title "+new_title_of_album+" WHERE id = "+albumid
    db = get_db()
    db.cursor().execute(sql_command)
    db.commit()

def updating_song():
    songid=str(session["properties"]["id_of_song"])
    new_title_of_song=str(session["properties"]["new_title_of_song"])


    sql_update_query = """Update Songs set title = ? where id = ?"""
    data=(new_title_of_song,songid)
    db = get_db()
    db.cursor().execute(sql_update_query,data)
    db.commit()


    

def insert_album(likes=0):

    name = str(session["user"][1])
    surname = str(session["user"][2])
    id = int(session["properties"]["albumid"])
    genre = str(session["properties"]["albumgenre"])
    title = str(session["properties"]["albumtitle"])

    sqlite_insert_with_param = """INSERT INTO Albums
                          (id,genre,title,likes,listsofsongs)
                          VALUES (?,?,?,?,?);"""
    listsofsongs = "songs"+str(id)
    data_tuple = (id, genre, title, likes, listsofsongs)
    db = get_db()
    db.cursor().execute(sqlite_insert_with_param, data_tuple)

    string = "CREATE TABLE IF NOT EXISTS " + \
        listsofsongs+" (idofsong INT NOT NULL);"
    db.cursor().execute(string)

    listsofalbumsofartist = str(name)+str(surname)+"listsofalbums"

    sql_commad = "INSERT INTO "+listsofalbumsofartist + \
        "(idofalbum) VALUES ("+str(id)+");"
    db.cursor().execute(sql_commad)
    db.commit()


def insert_song(likes=0):
    
    id=session["properties"]["songid"]
    album_id=session["properties"]["which_album"]
    title=session["properties"]["songtitle"]

    sqlite_insert_with_param = """INSERT INTO Songs
                          (id,title,likes,albumid)
                          VALUES (?,?,?,?);"""
    songs_table = "songs"+str(album_id)
    sqlite_insert_with_param_2 = "INSERT INTO " + \
        songs_table+"(idofsong) VALUES (?);"
    data_tuple = (id, title, likes,album_id)
    db = get_db()
    db.cursor().execute(sqlite_insert_with_param, data_tuple)
    db.cursor().execute(sqlite_insert_with_param_2, (id))
    db.commit()

def update_song(album_id, id, title, likes=0):
    pass


def insert_artist(name, surname):

    sqlite_insert_with_param = """INSERT INTO Artists
                          (name, surname,listsofalbums)
                          VALUES (?, ?,?);"""
    listsofalbums = str(name)+str(surname)+"listsofalbums"
    data_tuple = (name, surname, listsofalbums)
    db = get_db()
    db.cursor().execute(sqlite_insert_with_param, data_tuple)
    string = "CREATE TABLE IF NOT EXISTS " + \
        listsofalbums+" (idofalbum INT NOT NULL);"
    db.cursor().execute(string)
    db.commit()


def insert_listener(email, username):

    sqlite_insert_with_param = """INSERT INTO Listeners
                          (email, username,listsoflikedsongs)
                          VALUES (?, ?,?);"""
    listsoflikedsongs = str(username)+"likedsongs"
    data_tuple = (email, username, listsoflikedsongs)
    db = get_db()
    db.cursor().execute(sqlite_insert_with_param, data_tuple)
    string = "CREATE TABLE IF NOT EXISTS " + \
        listsoflikedsongs+" (idofsong INT NOT NULL);"
    db.cursor().execute(string)
    db.commit()


def create_table():
    db = get_db()
    db.cursor().execute('''
    CREATE TABLE IF NOT EXISTS Artists(name VARCHAR(20) NOT NULL,
    surname VARCHAR(20) NOT NULL,listsofalbums VARCHAR(45) NOT NULL
    );
    ''')
    db.cursor().execute('''
    CREATE TABLE IF NOT EXISTS Listeners(email VARCHAR(100) NOT NULL,
    username VARCHAR(20) NOT NULL,listsoflikedsongs VARCHAR(35) NOT NULL
    );
    ''')

    db.cursor().execute('''
    CREATE TABLE IF NOT EXISTS Albums(id INT NOT NULL,
    genre VARCHAR(20) NOT NULL , title VARCHAR(20) , likes INT , listsofsongs VARCHAR(25)
    );
    ''')

    db.cursor().execute('''
    CREATE TABLE IF NOT EXISTS Songs(id INT NOT NULL,
    title VARCHAR(100) NOT NULL, likes INT, albumid INT NOT NULL
    );
    ''')

    db.commit()


app = Flask(__name__)
app.secret_key = "ismetsari"
app.static_folder = 'static'
create_table()

@app.route('/login', methods=['GET', 'POST'])
def login():
  
    if request.method == 'POST':
        if request.form["button"]=="listener":
            userN = query_db('select * from Listeners where email = ? and username = ?', [request.form['email_of_listener'], request.form['username_of_listener']], one=True)
            if userN is None:
                insert_listener(request.form['email_of_listener'],request.form['username_of_listener'])
            session['user']=["listener",request.form['email_of_listener'],request.form['username_of_listener']]

            return redirect(url_for('listener')) 
                
        elif request.form["button"]=="artist":
            user = query_db('select * from Artists where name = ? and surname = ?', [request.form['name_of_artist'], request.form['surname_of_artist']], one=True)
            if user is None:
                insert_artist(request.form['name_of_artist'],request.form['surname_of_artist'])

            

            session['user']=["artist",request.form['name_of_artist'],request.form['surname_of_artist']]
            return redirect(url_for('artist')) 
    return render_template('login.html')


@app.route('/artist',methods=['GET', 'POST'])
def artist():
    if "user" in session:
        if request.method == 'POST':
            if request.form["button"]=="add_a_song":
                session["goal"]="add_song"
                return redirect(url_for('add_song')) 
            elif request.form["button"]=="add_an_album":

                session["goal"]="add_album"
                

                return redirect(url_for('add_album')) 

            elif request.form["button"]=="delete_an_album":
                return redirect(url_for('delete_album')) 

            elif request.form["button"]=="delete_a_song":
                return redirect(url_for('delete_song')) 


            elif request.form["button"]=="update_an_album":
                session["goal"]="update_album"
                return redirect(url_for('update_album')) 


            elif request.form["button"]=="update_a_song":
                session["goal"]="update_song"
                return redirect(url_for('update_song')) 
            
        return render_template('artist.html')

@app.route('/listener',methods=['GET', 'POST'])
def listener():
    if "user" in session:
        if request.method == 'POST':
            if request.form["button"]=="view_all_everything":
                session["goal"]="view_all_everything"

                return redirect(url_for('view_all_everything')) 

            elif request.form["button"]=="view_all_everything_of_artist":
                return redirect(url_for('view_all_artist')) 

            elif request.form["button"]=="view_others_liked_song":
                return redirect(url_for('view_others_liked_song')) 

            elif request.form["button"]=="view_popular_song_of_an_artist":
                return redirect(url_for('view_popular_song_of_an_artist')) 

            elif request.form["button"]=="rank_artists":
                return redirect(url_for('rank_artists')) 

            elif request.form["button"]=="view_a_song_with_specific_genre":
                return redirect(url_for('view_a_song_with_specific_genre')) 

            elif request.form["button"]=="Search_a_keyword":
                return redirect(url_for('search_a_keyword')) 

            elif request.form["button"]=="view_partners":
                return redirect(url_for('view_partners')) 
            elif request.form["button"]=="like_album_or_song":
                return redirect(url_for('like_album_or_song')) 

            
        return render_template('listener.html')






@app.route('/add_song',methods=['GET', 'POST'])
def add_song():

    if "add_song" == session["goal"]:
        if request.method == 'POST':
            session["properties"]={"songid":request.form['ID_of_song'],"songtitle":request.form['title_of_song'],"which_album":request.form['which_album']}
            
            insert_song()

            return redirect(url_for('artist')) 
    
    
    return render_template('add_song.html')    
@app.route('/add_album',methods=['GET', 'POST'])
def add_album():

    if "add_album" == session["goal"]:
        if request.method == 'POST':

            session["properties"]={"albumid":request.form['id_of_album'],"albumgenre":request.form['genre_of_album'],"albumtitle":request.form['title_of_album']}
            
            insert_album()

            return redirect(url_for('artist')) 

        return render_template('add_album.html') 

@app.route('/delete_song')
def delete_song():

    return render_template('delete_song.html')   





@app.route('/delete_album')
def delete_album():

    return render_template('delete_album.html')   

@app.route('/update_album',methods=['GET', 'POST'])
def update_album():

    if "update_album" == session["goal"]:
        if request.method == 'POST':

            session["properties"]={"albumid":request.form['id_of_album'],"new_genre_of_album":request.form['new_genre_of_album'],"new_title_of_album":request.form['new_title_of_album']}
            
            updating_album()

            return redirect(url_for('artist')) 

        return render_template('update_album.html')   

@app.route('/update_song',methods=['GET', 'POST'])
def update_song():

    if "update_song" == session["goal"]:
        if request.method == 'POST':

            session["properties"]={"id_of_song":request.form['id_of_song'],"new_title_of_song":request.form['new_title_of_song']}
            
            updating_song()

            return redirect(url_for('artist')) 

        return render_template('update_song.html')   






@app.route('/view_all_everything')
def view_all_everything():
    if "view_all_everything" == session["goal"]:
        db=get_db()
        
        rows=db.cursor().execute("select * from Songs").fetchall()
        print('This is row output in Songs', rows,file=sys.stdout)
        my_song_array=[]
        
        for row in rows:

            my_song_array.append(row[1])
            
            print('This is row output in songs', row,file=sys.stdout)

        rows=db.cursor().execute("select * from Albums").fetchall()
        my_album_dict=[]
        for row in rows:
            my_album_dict.append({"genre":row[1],"title":row[2]})
            print('This is row output in Albums', row,file=sys.stdout)

        rows=db.cursor().execute("select * from Artists").fetchall()
        my_artist_array=[]
        for row in rows:
            my_artist_array.append(row[1])
            print('This is row output in Artists', row,file=sys.stdout)

    return render_template('view_all_everything.html',my_song_li=my_song_array,my_album_di=my_album_dict,my_artist_li=my_artist_array)   

@app.route('/view_all_artist')
def view_all_artist():

    return render_template('view_all_artist.html')  

@app.route('/view_others_liked_song')
def view_others_liked_song():

    return render_template('view_others_liked_songs.html')  

@app.route('/view_popular_song_of_an_artist')
def view_popular_song_of_an_artist():

    return render_template('view_all_popular_artist.html')  


@app.route('/view_a_song_with_specific_genre')
def view_a_song_with_specific_genre():

    return render_template('view_a_song_with_specific_genre.html')  


@app.route('/search_a_keyword')
def search_a_keyword():

    return render_template('search_a_keyword.html')  

    
@app.route('/like_album_or_song')
def like_album_or_song():

    return render_template('like_album_or_song.html')  


if __name__ == '__main__':
    app.run(port=5000,debug=True)