from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL
import argon2
import secrets

app = Flask(__name__)   

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'crm'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql = MySQL()
mysql.init_app(app)

app.secret_key ="a773df62bbef3b540055f1689cde7d04577da32ed8b7b68df8bd5278b3972a3c"

class UserLogin():
    def __init__(self, email, password):
        self.__email = email
        self.__password = password
    
    def try_login(self):
        conn = mysql.connect()
        query = "SELECT email, mot_de_passe, sel FROM utilisateur WHERE email=%(email)s"
        values = {'email': self.__email}
        cursor = conn.cursor()
        cursor.execute(query, values)
        user = cursor.fetchone()
        if user:
            if self.check_password(user[2], user[1]):
                query = "SELECT siren, nom_entreprise, telephone, email, mot_de_passe, iban, adresse, ville, code_postal  FROM utilisateur WHERE email=%(email)s"
                values = {'email': self.__email}
                cursor = conn.cursor()
                cursor.execute(query, values)
                user_infos = cursor.fetchone()
                user_infos = UserInformations(*user_infos)
                session['user_is_connected'] = True
                session['user_infos'] = user_infos.to_dict()
                print('User logged')
        else:
            print("Le compte n'a pas été trouvé")
        conn.close()
    
    def check_password(self, salt, hashed_password):
        if argon2.PasswordHasher().verify(hashed_password, self.__password+salt):
            return True
        else:
            return False

class UserRegister():
    def __init__(self, email,password, confirm_password, siren, company_name, phone, iban, adress, city, postal_code):
        self.__siren = siren
        self.__company_name = company_name
        self.__phone = phone
        self.__email = email
        self.__password = password
        self.__confirm_password = confirm_password
        self.__iban = iban
        self.__adress = adress
        self.__city = city
        self.__postal_code = postal_code
        
    def try_register(self):
        if not self.is_email_exist() or not self.is_siren_exist():
            if self.check_password():
                self.__password, salt = self.hash_password()
                print(self.__password)
                print(salt)
                conn = mysql.connect()
                query = "INSERT INTO utilisateur(siren, nom_entreprise, telephone, email, mot_de_passe, iban, adresse, ville, code_postal, sel) VALUES (%(siren)s, %(nom_entreprise)s, %(telephone)s, %(email)s, %(mot_de_passe)s, %(iban)s, %(adresse)s, %(ville)s, %(code_postal)s, %(sel)s);"
                values = {'siren': self.__siren, 'nom_entreprise': self.__company_name, 'telephone': self.__phone, 'email': self.__email, 'mot_de_passe': self.__password,
                    'iban': self.__iban, 'adresse': self.__adress, 'ville': self.__city, 'code_postal': self.__postal_code, 'sel':salt}
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
                conn.close()
                
    def hash_password(self):
        salt = secrets.token_hex(16)
        password = (self.__password+salt).encode('utf-8')
        hashed_password = argon2.PasswordHasher().hash(password)
        return (hashed_password, salt)
        
    def check_password(self):
        if self.__password == self.__confirm_password:
            boolean = True
        else:
            boolean = False
        return boolean
    
    def is_email_exist(self):
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "SELECT email FROM utilisateur WHERE email=%s"
        values = (self.__email)
        cursor.execute(query, values)
        email_already_exist = cursor.fetchone()
        conn.close()
        return email_already_exist
    
    def is_siren_exist(self):
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "SELECT siren FROM utilisateur WHERE siren=%s"
        values = (self.__siren)
        cursor.execute(query, values)
        siren_already_exist = cursor.fetchone()
        conn.close()
        return siren_already_exist

class UserInformations():
    def __init__(self, siren, company_name, phone, email, password, iban, adress, city, postal_code):
        self.__siren = siren
        self.__company_name = company_name
        self.__phone = phone
        self.__email = email
        self.__password = password
        self.__iban = iban
        self.__adress = adress
        self.__city = city
        self.__postal_code = postal_code
        
    def to_dict(self):
        return {
            "siren": self.__siren,
            "company_name": self.__company_name,
            "phone": self.__phone,
            "email": self.__email,
            "password": self.__password,
            "iban": self.__iban,
            "adress": self.__adress,
            "city": self.__city,
            "postal_code": self.__postal_code
        }
        
class CompanyInformations():
    def __init__(self, company_name, description, url, siret):
        self.__company_name = company_name
        self.__description = description
        self.__url = url
        self.__siret = siret
    
    def to_dict(self):
        return {
            "company_name": self.__company_name,
            "description": self.__description,
            "url": self.__url,
            "siret": self.__siret
        }
        
        
@app.route('/')
def index():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("Select * FROM facture")
    conn.close()
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/add_new_company', methods=['POST', 'GET'])
def add_new_company():
    if request.method == "POST":
        request_to_dict = {
            "siret": request.form.get('siret'),
            "name": request.form.get('name'),
            "description": request.form.get('description'),
            "adress": request.form.get('adress'),
            "city": request.form.get('city'),
            "postal_code": request.form.get('postal_code'),
            "url": request.form.get('url'),
            "user_siren": session['user_infos']['siren']
        }
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "INSERT INTO entreprise(siret, nom, description, adresse, ville, code_postal, url, utilisateur_siren) VALUES (%(siret)s, %(name)s, %(description)s, %(adress)s, %(city)s, %(postal_code)s, %(url)s, %(user_siren)s)"
        values = (request_to_dict)
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    return render_template('add_new_company.html')
        

@app.route('/list_company')
def list_company():
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "SELECT nom, description, url, siret FROM entreprise WHERE utilisateur_siren=%s"
    values = (session['user_infos']['siren'])
    cursor.execute(query, values)
    list_company = cursor.fetchall()
    list_company_dict =[]
    for company_tuple in list_company:
        company = CompanyInformations(*company_tuple).to_dict()
        list_company_dict.append(company)
    conn.close()
    return render_template('list_company.html', list_company=list_company_dict)

@app.route('/company/<int:numero>')
def company(numero):
    return f"Vous avez choisi le siren {numero}"

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/disconnect')
def disconnect():
    if session['user_is_connected']:
        session.pop('user_is_connected')
        session.clear()
    return redirect(url_for('index'))
    

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/traitement_register', methods=["POST", "GET"])
def traitement_register():
    if request.method == "POST":
        user_form = request.form.to_dict()
        user = UserRegister(**user_form)
        user.try_register()
    return redirect(url_for('index'))
    
@app.route('/traitement_login', methods=["POST", "GET"])
def traitement_login():
    if request.method == "POST":
        user_form = request.form.to_dict()
        user = UserLogin(**user_form)
        user.try_login()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
