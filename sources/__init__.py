from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = b'*\x94?F\xb0\xf2\xcb$\x8fh\x7fh\xd9\x02\xcd^\xf7\xba\xc2\x9a\xed\xc2\x83x'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIl_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'cmiolimpiadas@gmail.com'
    app.config['MAIL_PASSWORD'] = 'quienhizolasilla'

    db.init_app(app)

    from .views import views
    from .auth import auth
    from .functions import functions
    from .social import social

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(functions, url_prefix="/functions")
    app.register_blueprint(social, url_prefix="/social")

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('sources/' + DB_NAME):
        db.create_all(app=app)
        print('DATABASE CREATED!')
