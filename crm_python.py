from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL

app = Flask(__name__)   

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'crm'
app.config['MYSQL_DATABASE_HOST'] = 'localhost:3307'

mysql = MySQL()
mysql.init_app(app)

app.secret_key ="a773df62bbef3b540055f1689cde7d04577da32ed8b7b68df8bd5278b3972a3c"

@app.route('/')
def index():
    session['user_is_connected'] = False
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO CRM VALUES ('test')")
    conn.close()
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/traitement_register', methods=["POST", "GET"])
def traitement_register():
    if request.method == "POST":
        donnees = request.form
        donnees
        return render_template('register.html')
    else:
        return redirect(url_for('index'))
    
@app.route('/traitement_login', methods=["POST", "GET"])
def traitement_login():
    if request.method == "POST":
        donnees = request.form
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
