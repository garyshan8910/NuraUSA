from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

from nura.route import index, login

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URL'] = 'mysql+pymysql://root:123456@127.0.0.1:3306/nura_usa'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'Admin'
    db.init_app(app)
    migrate.init_app(app, db)
    app.add_url_rule('/index', 'index', index)
    app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
    return app