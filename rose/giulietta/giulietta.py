from flask import Flask, render_template, flash, redirect, request, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired
from os import path, environ, urandom
import random
import json

script_dir = path.dirname(__file__)

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

HTTP_PORT       = int(environ.get("HTTP_PORT", 80))
ADMIN_USER      = environ.get("ADMIN_USER", "admin")
app.secret_key  = environ.get("FLASK_KEY", None) or urandom(32)
ADMIN_PASS      = environ["ADMIN_PASS"]
CTF_FLAG        = environ["CTF_FLAG"]

class RoseUser(UserMixin):
    users = {}

    def __init__(self, username, name, password, admin=False):
        self.id = username
        self.name = name
        self.password = password
        self.admin = admin

    @classmethod
    def login(cls, username, password):
        user = cls.users.get(username, None)
        
        if user and user.password == password:
            return user
        else:
            return None

    @classmethod
    def create(cls, *args, **kwargs):
       user = cls(*args, **kwargs) 
       cls.users[user.id] = user
       return user

RoseUser.create("luca", "Luca", "aerosmith1")
RoseUser.create("myrka", "Myrka", "yuiop")
RoseUser.create("moroder", "Giorgio", "mazda626")
RoseUser.create(ADMIN_USER, "Guilietta", ADMIN_PASS, True)

class RoseProduct:
    def __init__(self, name, descriptor, price, img):
        self.name = name
        self.descriptor = descriptor
        self.price = price
        self.img = img

roses = [
    RoseProduct("Ingrid Bergman", "Rosso tradizional", 1.39, "static/img/ingrid_bergman.jpg"),
    RoseProduct("Liquirizia bianca", "Latte bianco", 1.89, "static/img/liquiriza_bianca.jpg"),
    RoseProduct("Bassa marea", "Viola profondo", 1.69, "static/img/bassa_marea.jpg"),
    RoseProduct("Nuova Zelanda", "Rosa inebriante", 1.59, "static/img/bassa_marea.jpg"),
    RoseProduct("Graham Thomas", "Giallo pallido", 1.29, "static/img/graham_thomas.jpg")
]

class LoginForm(FlaskForm):
    class Meta:
        csrf = False

    user = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

@login_manager.user_loader
def load_user(user_id):
    return RoseUser.users.get(user_id, None)

@app.route('/esci', methods=['GET'])
@login_required
def esci():
    logout_user()
    return redirect('#')

@app.route('/home', methods=['GET'])
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/informazioni', methods=['GET'])
def informazioni():
    return render_template('informazioni.html')

@app.route('/negozio', methods=['GET'])
def negozio():
    return render_template('negozio.html', roses=roses)

@app.route('/accedi', methods=['GET', 'POST'])
def accedi():
    if request.method == 'POST':
        form = LoginForm()
        sucess = False
        if form.validate_on_submit():
            user = RoseUser.login(form.user.data, form.password.data)
            if user:
                login_user(user)
                sucess = True
            else:
                flash('Informazioni account non valido')
        else:
            flash('Si prega di inserire username e password')

        if sucess:
            return redirect('home')
        else:
            return redirect('accedi')
    else:
        return render_template('accedi.html', login_form=LoginForm())

@app.route('/amministratore', methods=['GET'])
def amministratore():
    if current_user.is_authenticated and current_user.admin:
        return render_template('amministratore.html', ctf_flag=CTF_FLAG)
    else:
        abort(404)

if __name__ == '__main__':
    # Serve over HTTP to prevent adding another step
    app.run(debug=True, host='0.0.0.0', port=HTTP_PORT)
