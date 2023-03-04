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
                query = "INSERT INTO utilisateur(siren, nom_entreprise, telephone, email, password, iban, adresse, ville, code_postal, sel) VALUES (%(siren)s, %(nom_entreprise)s, %(telephone)s, %(email)s, %(password)s, %(iban)s, %(adresse)s, %(ville)s, %(code_postal)s, %(sel)s);"
                values = {'siren': self.__siren, 'nom_entreprise': self.__company_name, 'telephone': self.__phone, 'email': self.__email, 'password': self.__password,
                    'iban': self.__iban, 'adresse': self.__adress, 'ville': self.__city, 'code_postal': self.__postal_code, 'sel':salt}
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
                conn.close()
                
    def hash_password(self):
        salt = secrets.token_hex(16)
        hashed_password = argon2.PasswordHasher().hash(self.__password.encode() + salt.encode())
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
        
    @property
    def siren(self):
        return self.__siren
    
    @siren.setter
    def siren(self, siren):
        self.__siren = siren
    
    @property
    def company_name(self):
        return self.__company_name
    
    @company_name.setter
    def company_name(self, company_name):
        self.__company_name = company_name
    
    @property
    def phone(self):
        return self.__phone
    
    @phone.setter
    def phone(self, phone):
        self.__phone = phone
    
    @property
    def email(self):
        return self.__email
    
    @email.setter
    def email(self, email):
        self.__email = email
        
    @property
    def password(self):
        return self.__password
    
    @password.setter
    def password(self, password):
        self.__password = password
        
    @property
    def iban(self):
        return self.__iban
    
    @iban.setter
    def iban(self, iban):
        self.__iban = iban
        
    @property
    def adress(self):
        return self.__adress
    
    @adress.setter
    def adress(self, adress):
        self.__adress = adress
        
    @property
    def city(self):
        return self.__city
    
    @city.setter
    def city(self, city):
        self.__city = city
        
    @property
    def postal_code(self):
        return self.__postal_code
    
    @postal_code.setter
    def postal_code(self, postal_code):
        self.__postal_code = postal_code
        

@app.route('/')
def index():
    session['user_is_connected'] = False
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("Select * FROM facture")
    conn.close()
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/register')
def register():
    return render_template('register.html')

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
