from flask import Flask, render_template, request, redirect, url_for, session, flash
from flaskext.mysql import MySQL
import argon2
import secrets
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import PCMYKColor
from datetime import datetime, timedelta
from abc import ABC

app = Flask(__name__)   

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'crm'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SECRET_KEY'] ="a773df62bbef3b540055f1689cde7d04577da32ed8b7b68df8bd5278b3972a3c"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)


mysql = MySQL()
mysql.init_app(app)


class User(ABC):
    def __init__(self, email, password, siren, company_name, phone, iban, adress, city, postal_code):
        self._siren = siren
        self._company_name = company_name
        self._phone = phone
        self._email = email
        self._password = password
        self._iban = iban
        self._adress = adress
        self._city = city
        self._postal_code = postal_code

class UserLogin():
    def __init__(self, email, password):
        self._email = email
        self._password = password
    
    def try_login(self):
        conn = mysql.connect()
        query = "SELECT email, mot_de_passe, sel FROM utilisateur WHERE email=%(email)s"
        values = {'email': self._email}
        cursor = conn.cursor()
        cursor.execute(query, values)
        user = cursor.fetchone()
        if user:
            if self.check_password(user[2], user[1]):
                query = "SELECT siren, nom, telephone, email, mot_de_passe, iban, adresse, ville, code_postal  FROM utilisateur WHERE email=%(email)s"
                values = {'email': self._email}
                cursor = conn.cursor()
                cursor.execute(query, values)
                user_infos = cursor.fetchone()
                user_infos = UserInformations(*user_infos)
                session['user_is_connected'] = True
                session['user_infos'] = user_infos.to_dict()
                session['last_login'] = datetime.now()
                print('User logged')
        else:
            print("Le compte n'a pas été trouvé")
        conn.close()
    
    def check_password(self, salt, hashed_password):
        if argon2.PasswordHasher().verify(hashed_password, self._password+salt):
            return True
        else:
            return False

class UserRegister(User):
    def __init__(self, email,password, confirm_password, siren, company_name, phone, iban, adress, city, postal_code):
        super().__init__(email, password, siren, company_name, phone, iban, adress, city, postal_code)
        self._confirm_password = confirm_password
        
    def try_register(self):
        if not self.is_email_exist() and not self.is_siren_exist():
            if self.check_password():
                self._password, salt = self.hash_password()
                conn = mysql.connect()
                query = "INSERT INTO utilisateur(siren, nom, telephone, email, mot_de_passe, iban, adresse, ville, code_postal, sel) VALUES (%(siren)s, %(nom)s, %(telephone)s, %(email)s, %(mot_de_passe)s, %(iban)s, %(adresse)s, %(ville)s, %(code_postal)s, %(sel)s);"
                values = {'siren': self._siren, 'nom': self._company_name, 'telephone': self._phone, 'email': self._email, 'mot_de_passe': self._password,
                    'iban': self._iban, 'adresse': self._adress, 'ville': self._city, 'code_postal': self._postal_code, 'sel':salt}
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
                conn.close()
        else:
            flash('Siren ou email deja utilisé', 'info')
                
    def hash_password(self):
        salt = secrets.token_hex(16)
        password = (self._password+salt).encode('utf-8')
        hashed_password = argon2.PasswordHasher().hash(password)
        return (hashed_password, salt)
        
    def check_password(self):
        if self._password == self._confirm_password:
            boolean = True
        else:
            boolean = False
        return boolean
    
    def is_email_exist(self):
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "SELECT email FROM utilisateur WHERE email=%s"
        values = (self._email)
        cursor.execute(query, values)
        email_already_exist = cursor.fetchone()
        conn.close()
        return email_already_exist
    
    def is_siren_exist(self):
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "SELECT siren FROM utilisateur WHERE siren=%s"
        values = (self._siren)
        cursor.execute(query, values)
        siren_already_exist = cursor.fetchone()
        conn.close()
        return siren_already_exist

class UserInformations(User):
    def __init__(self, siren, company_name, phone, email, password, iban, adress, city, postal_code):
        super().__init__(email, password, siren, company_name, phone, iban, adress, city, postal_code)

    def to_dict(self):
        return {
            "siren": self._siren,
            "company_name": self._company_name,
            "phone": self._phone,
            "email": self._email,
            "password": self._password,
            "iban": self._iban,
            "adress": self._adress,
            "city": self._city,
            "postal_code": self._postal_code
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
        
class ContactInformations():
    def __init__(self, name, last_name, post, id):
        self.__name = name
        self.__last_name = last_name
        self.__post = post
        self.__id = id
    
    def to_dict(self):
        return {
            "name": self.__name,
            "last_name": self.__last_name,
            "post": self.__post,
            "id": self.__id,
        }
        
class NewInvoice():
    def __init__(self, invoice_infos):
        self.__contact_name = invoice_infos[0]
        self.__company_name = invoice_infos[1]
        self.__company_adress = invoice_infos[2]
        self.__company_city = invoice_infos[3]
        self.__company_postal_code = invoice_infos[4]
        self.__user_name = invoice_infos[5]
        self.__user_adress = invoice_infos[6]
        self.__user_postal_code = invoice_infos[7]
        self.__user_city = invoice_infos[8]
        self.__user_siren = invoice_infos[9]
        self.__user_phone = invoice_infos[10]
        self.__user_email = invoice_infos[11]
        self.__user_iban = invoice_infos[12]

    def to_dict(self):
        return {
            "contact_name": self.__contact_name,
            "company_name": self.__company_name,
            "company_adress": self.__company_adress,
            "company_city": self.__company_city,
            "company_postal_code": self.__company_postal_code,
            "user_name": self.__user_name,
            "user_adress": self.__user_adress,
            "user_postal_code": self.__user_postal_code,
            "user_city": self.__user_city,
            "user_siren": self.__user_siren,
            "user_phone": self.__user_phone,
            "user_email": self.__user_email,
            "user_iban": self.__user_iban,
        }
    
    def make_invoice(self, invoice_infos, contact_id):
        num_facture = uuid.uuid4()
        self.__draw_invoice(num_facture, invoice_infos)
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "INSERT INTO facture(num_facture, chemin, utilisateur_siren, contact_id) VALUES(%(num_facture)s, %(chemin)s, %(utilisateur_siren)s, %(contact_id)s)"
        invoce_dict = {
            'num_facture': num_facture,
            'utilisateur_siren': self.__user_siren,
            'contact_id': contact_id,
            'chemin': f"invoices/facture_{num_facture}.pdf",
        }
        cursor.execute(query, invoce_dict)
        conn.commit()
        conn.close()
        
    def __draw_invoice(self, num_facture, invoice_infos):
        pdf_file = canvas.Canvas(f"invoices/facture_{num_facture}.pdf", pagesize=letter)
        
        # Titres de la facture
        pdf_file.setFont("Helvetica-Bold", 20)
        pdf_file.drawString(10,765, "{}".format(invoice_infos['user_name']))
        pdf_file.drawString(380, 680, "FACTURE")
        pdf_file.drawString(380, 570, "{}".format(invoice_infos['company_name']))
        
        # Informations sur l'utilisateur qui créer la facture
        pdf_file.setFont("Helvetica", 12)
        pdf_file.drawString(10, 745, "{}".format(invoice_infos['user_adress']))
        pdf_file.drawString(10, 730, "{} {}".format(invoice_infos['user_postal_code'], invoice_infos['user_city']))
        pdf_file.drawString(10, 660, "N° de SIREN {}".format(invoice_infos['user_siren']))
        pdf_file.drawString(45, 630, "{}".format(invoice_infos['user_phone']))
        pdf_file.drawString(55, 610, "{}".format(invoice_infos['user_email']))
        pdf_file.drawString(50, 590, "{}".format(invoice_infos['user_iban']))
        
        # Pour mettre en gras les infos
        pdf_file.setFont("Helvetica-Bold", 12)
        pdf_file.drawString(10, 630, "Tel. :")
        pdf_file.drawString(10, 610, "Email :")
        pdf_file.drawString(10, 590, "IBAN :")
        
        # Informations sur le prospect
        pdf_file.setFont("Helvetica", 12)
        pdf_file.drawString(380, 550, "{}".format(invoice_infos['contact_name']))
        pdf_file.drawString(380, 535, "{}".format(invoice_infos['company_adress']))
        pdf_file.drawString(380, 520, "{} {}".format(invoice_infos['company_postal_code'], invoice_infos['company_city']))
        
        # Partie pour faire le numéro et date de facture
        pdf_file.setFont("Helvetica-Bold", 12)
        gray = PCMYKColor(0, 0, 0, 10, alpha=100)
        pdf_file.setFillColor(gray)
        pdf_file.rect(0, 540, 300, 20, fill=1, stroke=0)
        pdf_file.setFillColorRGB(0,0,0)
        pdf_file.drawString(10, 545, "Facture")
        pdf_file.drawString(180, 545, "Date")
        pdf_file.setFont("Helvetica", 8)
        pdf_file.drawString(10, 530, "{}".format(num_facture))
        pdf_file.drawString(180, 530, "{}".format(datetime.now().date()))
        
        
        pdf_file.save()


@app.before_request
def check_user_logged_in():
    '''
    utilisateur non connecté, rediriger vers la page de connexion
    '''
    if not session.get('user_infos') and request.endpoint not in ['login', 'register', 'index', 'page_not_found', 'traitement_login', 'traitement_register']:
        return redirect(url_for('login'))
    
@app.route('/')
def index():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("Select * FROM facture")
    conn.close()
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    '''
    Gère la page 404
    '''
    return render_template('404.html'), 404

@app.route('/parameters')
def parameters():
    '''
    Permet de changer les informations sur un compte utilisateur
    '''
    pass
    #TODO -> a mon avis il faut changer un petit peu les classes, on peut
    #faire une classe mere et UserInformations, UserRegister et UserParameters va en hériter

@app.route('/add_new_company', methods=['POST', 'GET'])
def add_new_company():
    '''
    Ajoute une nouvelle entreprise à un utilisateur
    '''
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
        query = "INSERT INTO entreprise(siret, nom, description, adresse, ville, code_postal, url, utilisateur_siren) " \
            " VALUES (%(siret)s, %(name)s, %(description)s, %(adress)s, %(city)s, %(postal_code)s, %(url)s, %(user_siren)s)"
        values = (request_to_dict)
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    return render_template('add_new_company.html')
        

@app.route('/list_company')
def list_company():
    '''
    Liste de toutes les entreprises qu'a un utilisateur
    '''
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

@app.route('/company/<int:number>')
def company(number):
    '''
    Affiche tous les contacts d'une entreprise en particulier
    '''
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "SELECT siret FROM entreprise WHERE utilisateur_siren=%s and siret=%s"
    values = (session['user_infos']['siren'], number)
    cursor.execute(query, values)
    is_correct_user = cursor.fetchone()
    if is_correct_user:
        cursor = conn.cursor()
        query = "SELECT nom, prenom, poste, id FROM contact WHERE entreprise_siret=%s and entreprise_utilisateur_siren=%s"
        values = (number, session['user_infos']['siren'])
        cursor.execute(query, values)
        list_contact = cursor.fetchall()
        list_contact_dict = []
        for contact_tuple in list_contact:
            contact = ContactInformations(*contact_tuple).to_dict()
            list_contact_dict.append(contact)
    else:
        return redirect(url_for('index'))
    conn.close()
    return render_template('company.html', contacts=list_contact, siret=number)

@app.route('/add_new_contact/<int:number>', methods=['POST', 'GET'])
def add_new_contact(number):
    '''
    Permet d'ajouter un nouveau contact à une entreprise spécifique
    '''
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "SELECT id, nom FROM statut"
    cursor.execute(query)
    status = cursor.fetchall()
    if request.method == "POST":
        request_to_dict = {
            "name": request.form.get('name'),
            "last_name": request.form.get('last_name'),
            "email": request.form.get('email'),
            "phone": request.form.get('phone'),
            "statut_id": request.form.get('statut_id'),
            "post": request.form.get('post'),
            "company_siret": number,
            "user_siren": session['user_infos']['siren'],
        }
        cursor = conn.cursor()
        query = "INSERT INTO contact(nom, prenom, email, telephone, entreprise_siret, entreprise_utilisateur_siren, statut_id, poste) " \
            "VALUES (%(last_name)s, %(name)s, %(email)s, %(phone)s, %(company_siret)s, %(user_siren)s, %(statut_id)s, %(post)s)"
        values = (request_to_dict)
        cursor.execute(query, values)
        conn.commit()
    conn.close()
    return render_template('add_new_contact.html', status=status, number=number)

@app.route('/generate_invoice', methods=['POST', 'GET'])
def generate_invoice():
    '''
    Permet de générer la facture au format PDF
    '''
    if request.method == "POST":
        post_dict = {
            "contact_id": request.form['contact_id'],
        }
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "SELECT contact.nom, entreprise.nom, entreprise.adresse, entreprise.ville, entreprise.code_postal, utilisateur.nom, " \
                "utilisateur.adresse, utilisateur.code_postal, utilisateur.ville, utilisateur.siren, utilisateur.telephone, utilisateur.email, utilisateur.iban FROM contact " \
                "INNER JOIN entreprise ON contact.entreprise_siret = entreprise.siret AND contact.entreprise_utilisateur_siren = entreprise.utilisateur_siren " \
                "INNER JOIN utilisateur ON entreprise.utilisateur_siren = utilisateur.siren " \
                "WHERE contact.id=%(contact_id)s"
        cursor.execute(query, post_dict)
        invoice_infos = cursor.fetchone()
        invoice = NewInvoice(invoice_infos)
        invoice_infos = invoice.to_dict()
        invoice.make_invoice(invoice_infos, post_dict['contact_id'])
        conn.close()
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))
    
@app.route('/add_comment', methods=['POST'])
def add_comment():
    '''
    Permet d'ajouter un commentaire sur un contact
    '''
    #TODO -> au final il faut rajouter l'utilisateur ID et changer l'UI
    #a clarifier avec erwann
    if request.form.get('comment'):
        request_dict = {
            'contact_id': request.form.get('contact_id'),
            'description': request.form.get('comment'),
            'author': session['user_infos']['nom']
        }
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "INSERT INTO commentaire(description, contact_id) VALUES (%(description)s, %(contact_id)s)"
        cursor.execute(query, request_dict)
        conn.commit()
        return redirect(url_for('index'))
    else:
        return render_template('add_new_comment.html', contact_id=request.form.get('contact_id'))
    
@app.route('/list_comment', methods=['POST'])
def list_comment():
    '''
    Permet de voir la liste des commentaires sur un contact
    '''
    request_dict = {
        'contact_id': request.form.get('contact_id')
    }
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "SELECT description FROM commentaire WHERE contact_id=%(contact_id)s"
    values = (request_dict)
    cursor.execute(query, values)
    comments = cursor.fetchall()
    conn.close()
    return render_template('list_comment.html', contact_id=request_dict['contact_id'], comments = comments)

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
    '''
    Page de traitement pour créer un nouvel utilisateur
    '''
    if request.method == "POST":
        user_form = request.form.to_dict()
        user = UserRegister(**user_form)
        user.try_register()
    return redirect(url_for('index'))
    
@app.route('/traitement_login', methods=["POST", "GET"])
def traitement_login():
    '''
    Page de traitement pour se connecter
    '''
    if request.method == "POST":
        user_form = request.form.to_dict()
        user = UserLogin(**user_form)
        user.try_login()
    return redirect(url_for('index'))

@app.route('/easter_egg')
def easter_egg():
    '''
    Ester egg
    '''
    return redirect('https://www.youtube.com/watch?v=sZkpGKWCr94')

if __name__ == '__main__':
    app.run(debug=True)
