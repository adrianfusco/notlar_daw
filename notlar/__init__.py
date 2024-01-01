
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from flask_babel import Babel
from dotenv import load_dotenv
import resend
import sys
from itsdangerous import URLSafeTimedSerializer

load_dotenv()

app = Flask(
    __name__,
    template_folder= os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
    static_folder= os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
)

app.config['BABEL_DEFAULT_LOCALE'] = 'es'
app.config['LANGUAGES'] = [
    'en',
    'es',
    'gl',
]

babel = Babel(app)

def check_env_variable(env_name):
    value = os.getenv(env_name)
    if not value:
        print(f"Error: {env_name} environment variable is missing.")
        sys.exit(1)
    return value

postgres_user = check_env_variable('POSTGRES_USER')
postgres_password = check_env_variable('POSTGRES_PASSWORD')
postgres_host = check_env_variable('POSTGRES_HOST')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:5432/notlar'



db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = '/'
login_manager.init_app(app)

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'img', 'users')

if not os.access(UPLOAD_FOLDER, os.W_OK):
    print("Upload folder does not have write permissions!")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

resend.api_key = check_env_variable('RESEND_API_KEY')

if not resend.api_key:
    print("Error: RESEND_API_KEY environment variable is missing.")
    sys.exit(1)

flask_secret_key = check_env_variable('FLASK_SECRET_KEY')

app.config['SECRET_KEY'] = flask_secret_key

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

flask_server_name = check_env_variable('SERVER_NAME')

app.config['SERVER_NAME'] = flask_server_name

from notlar import routes, models, auth
