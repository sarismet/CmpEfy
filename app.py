from flask import(
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for
)


app = Flask(__name__)
app.secret_key = "ismetsari"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        return redirect(url_for('profile'))
    elif request.method == 'artist':

        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/profile')
def profile():

    return render_template('profile.html')
