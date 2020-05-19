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
                insert_artist(request.form['email_of_listener'],request.form['username_of_listener'])
                return redirect(url_for('first')) 
    return render_template('login.html')


@app.route('/listener')
def listener():
    return render_template('listener.html')


@app.route('/first')
def first():

    return render_template('first.html')
if __name__ == '__main__':
    app.run(port=5000,debug=True)