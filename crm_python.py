from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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
