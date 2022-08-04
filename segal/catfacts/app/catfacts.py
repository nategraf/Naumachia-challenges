from flask import Flask, render_template, flash, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from os import path, environ
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
import json
import logging
import random

script_dir = path.dirname(__file__)

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

port                = int(environ.get("CATFACTS_PORT", 443))
app.secret_key      = environ.get("CATFACTS_KEY")
catfact_user        = environ.get("CATFACTS_USER")
catfact_pass        = environ.get("CATFACTS_PASS")
ctf_flag            = environ.get("CTF_FLAG")
cert_path           = environ.get("CERT_PATH", "/etc/ssl/localhost.crt")
key_path            = environ.get("KEY_PATH", "/etc/ssl/localhost.key")

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(process)d] [%(levelname)s] in %(module)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S %z"
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["wsgi"]},
    }
)

class LonelyUser(UserMixin):
    id = catfact_pass

lonely_user = LonelyUser()

class LoginForm(FlaskForm):
    user = StringField('Username', validators=[DataRequired()])
    passwd = PasswordField('Password', validators=[DataRequired()])

@login_manager.user_loader
def load_user(user_id):
    if user_id == lonely_user.get_id():
        return lonely_user
    else:
        return None

class CatFacts:
    def __init__(self, factfile=None, exclfile=None):
        self.facts = []
        self.exclamations = []

        self.load(factfile, exclfile)

    def load(self, factfile, exclfile):
        if factfile:
            with open(factfile) as f:
                self.facts = list(enumerate(json.load(f)))

        if exclfile:
            with open(exclfile) as f:
                self.exclamations = list(json.load(f))

    def random(self):
        num, fact = random.choice(self.facts)
        exclamation = random.choice(self.exclamations)
        return num, fact, exclamation

thefacts = CatFacts()

factfile = path.join(script_dir, 'catfacts.json')
exclfile = path.join(script_dir, 'exclamations.json')
thefacts.load(factfile, exclfile)

@app.route('/login', methods=('POST',))
def login():
    form = LoginForm()
    sucess = False
    if form.validate_on_submit():
        if form.user.data == catfact_user and form.passwd.data == catfact_pass:
            login_user(lonely_user)
            sucess = True
        else:
            flash('Credentials rejected: You are not a true Cat Daddy')
    else:
        flash('Please enter your credentials')

    if sucess:
        return redirect("/#")
    else:
        return redirect("/#login")

@app.route('/logout', methods=('GET',))
@login_required
def logout():
    logout_user()
    return redirect('/#')


@app.route('/')
def hello_world():
    num, fact, exclamation = thefacts.random()
    form = LoginForm()
    return render_template(
            'fact.html',
            fact=fact,
            num=num,
            exclamation=exclamation,
            ctf_flag=ctf_flag,
            login_form=LoginForm()
            )

if __name__ == '__main__':
    # Serve over HTTP to prevent adding another step
    app.run(debug=True, host='0.0.0.0', port=port, ssl_context=(cert_path, key_path))
