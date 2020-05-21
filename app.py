from flask import(
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    send_from_directory
)
from flask import g
import sqlite3
class Artist:
    def __init__(self,name,surname):
        self.name=name
        self.surname=surname

DATABASE="Artist_Listener.db"
def get_db():
    db=sqlite3.connect(DATABASE)
    return db




def query_db(query, args=(), one=False):
    db=get_db()
    cur = db.cursor().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv




    


def insert_album(id,genre,title,likes):


    sqlite_insert_with_param = """INSERT INTO Albums
                          (id,genre,title,likes,listsofsongs)
                          VALUES (?,?,?,?,?);"""
    listsofsongs=str(id)+"songs"
    data_tuple = (id,genre,title,likes,listsofsongs)
    db=get_db()
    db.cursor().execute(sqlite_insert_with_param, data_tuple)
    string="CREATE TABLE IF NOT EXISTS "+listsofsongs+" (idofalbum INT NOT NULL);"
    db.cursor().execute(string)
    db.commit()


def insert_song(id,title,likes,album_id):
    

    sqlite_insert_with_param = """INSERT INTO Songs
                          (id,title,likes)
                          VALUES (?,?,?);"""

    data_tuple = (id,title,likes)
    db=get_db()
    db.cursor().execute(sqlite_insert_with_param, data_tuple)
    db.commit()

def insert_artist(name,surname):
    

    sqlite_insert_with_param = """INSERT INTO Artists
                          (name, surname,listsofalbums) 
                          VALUES (?, ?,?);"""
    listsofalbums=str(name)+str(surname)+"listsofalbums"
    data_tuple = (name, surname,listsofalbums)
    db=get_db()
    db.cursor().execute(sqlite_insert_with_param, data_tuple)
    string="CREATE TABLE IF NOT EXISTS "+listsofalbums+" (idofalbum INT NOT NULL);"
    db.cursor().execute(string)
    db.commit()


def insert_listener(email,username):
    

    sqlite_insert_with_param = """INSERT INTO Listeners
                          (email, username,listsoflikedsongs) 
                          VALUES (?, ?,?);"""
    listsoflikedsongs=str(username)+"likedsongs"
    data_tuple = (email, username,listsoflikedsongs)
    db=get_db()
    db.cursor().execute(sqlite_insert_with_param, data_tuple)
    string="CREATE TABLE IF NOT EXISTS "+listsoflikedsongs+" (idofsong INT NOT NULL);"
    db.cursor().execute(string)
    db.commit()



def create_table():
    db=get_db()
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
    title VARCHAR(100) NOT NULL, likes INT
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
            user = query_db('select * from Listeners where email = ? and username = ?', [request.form['email_of_listener'], request.form['username_of_listener']], one=True)
            if user is None:
                insert_listener(request.form['email_of_listener'],request.form['username_of_listener'])
            return redirect(url_for('listener')) 
                
        elif request.form["button"]=="artist":
            user = query_db('select * from Artists where name = ? and surname = ?', [request.form['name_of_artist'], request.form['surname_of_artist']], one=True)
            if user is None:
                insert_artist(request.form['name_of_artist'],request.form['surname_of_artist'])
            return redirect(url_for('artist')) 
    return render_template('login.html')


@app.route('/artist',methods=['GET', 'POST'])
def artist():

    if request.method == 'POST':
        if request.form["button"]=="add_a_song":
            return redirect(url_for('add_song')) 
        elif request.form["button"]=="add_an_album":
            return redirect(url_for('add_album')) 

        elif request.form["button"]=="delete_an_album":
            return redirect(url_for('delete_album')) 

        elif request.form["button"]=="update_an_album":
            return redirect(url_for('update_album')) 

        elif request.form["button"]=="delete_a_song":
            return redirect(url_for('delete_song')) 

        elif request.form["button"]=="update_a_song":
            return redirect(url_for('update_song')) 
           
    return render_template('artist.html')

@app.route('/listener',methods=['GET', 'POST'])
def listener():
    if request.method == 'POST':
        if request.form["button"]=="view_all_everything":
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

        
    return render_template('listener.html')






@app.route('/add_song')
def add_song():

    return render_template('add_song.html')    

@app.route('/delete_song')
def delete_song():

    return render_template('delete_song.html')   

@app.route('/update_song')
def update_song():

    return render_template('update_song.html')   

@app.route('/add_album',methods=['GET', 'POST'])
def add_album():

    return render_template('add_album.html') 

@app.route('/delete_album')
def delete_album():

    return render_template('delete_album.html')   

@app.route('/update_album')
def update_album():

    return render_template('update_album.html')   

@app.route('/view_all_everything')
def view_all_everything():

    return render_template('view_all_everything.html')   

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

    

if __name__ == '__main__':
    app.run(port=5000,debug=True)