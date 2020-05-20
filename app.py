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




    


def insert_artist(name,surname):


    sqlite_insert_with_param = """INSERT INTO Artists
                          (name, surname) 
                          VALUES (?, ?);"""

    data_tuple = (name, surname)
    db=get_db()
    db.cursor().execute(sqlite_insert_with_param, data_tuple)
    db.commit()

def insert_listener(email,username):
    

    sqlite_insert_with_param = """INSERT INTO Artists
                          (email, username) 
                          VALUES (?, ?);"""

    data_tuple = (email, username)
    db=get_db()
    db.cursor().execute(sqlite_insert_with_param, data_tuple)
    db.commit()



def create_table():
    db=get_db()
    db.cursor().execute('''
    CREATE TABLE IF NOT EXISTS Artists(name VARCHAR(20) NOT NULL,
    surname VARCHAR(20) NOT NULL
    );
    ''')
    db.cursor().execute('''
    CREATE TABLE IF NOT EXISTS Listeners(email VARCHAR(100) NOT NULL,
    username VARCHAR(20) NOT NULL
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
                insert_artist(request.form['email_of_listener'],request.form['username_of_listener'])
            return redirect(url_for('listener')) 
                
        elif request.form["button"]=="artist":
            user = query_db('select * from Artists where name = ? and surname = ?', [request.form['name_of_artist'], request.form['surname_of_artist']], one=True)
            if user is None:
                insert_artist(request.form['name_of_artist'],request.form['surname_of_artist'])
            return redirect(url_for('artist')) 
    return render_template('login.html')


@app.route('/listener',methods=['GET', 'POST'])
def listener():
    return render_template('listener.html')


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

@app.route('/add_song')
def add_song():

    return render_template('add_song.html')    

@app.route('/delete_song')
def delete_song():

    return render_template('delete_song.html')   

@app.route('/update_song')
def update_song():

    return render_template('update_song.html')   

@app.route('/add_album')
def add_album():

    return render_template('add_album.html') 

@app.route('/delete_album')
def delete_album():

    return render_template('delete_album.html')   

@app.route('/update_album')
def update_album():

    return render_template('update_album.html')   


if __name__ == '__main__':
    app.run(port=5000,debug=True)