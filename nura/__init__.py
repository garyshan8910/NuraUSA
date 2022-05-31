from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from nura.config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'

from nura.route import get_po_items, get_so_items, index, login, logout, register, so_po_mapping, po_details, so_details, test

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    app.add_url_rule('/index', 'index', index)
    app.add_url_rule('/', 'index', index)
    app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'logout', logout)
    app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
    app.add_url_rule('/so_po_mapping', 'so_po_mapping', so_po_mapping, methods=['GET', 'POST'])
    app.add_url_rule('/po_details', 'po_details', po_details, methods=['GET', 'POST'])
    app.add_url_rule('/so_details', 'so_details', so_details, methods=['GET', 'POST'])
    app.add_url_rule('/test', 'test', test, methods=['GET', 'POST'])
    app.add_url_rule('/get_po_items', 'get_po_items', get_po_items, methods=['GET', 'POST'])
    app.add_url_rule('/get_so_items', 'get_so_items', get_so_items, methods=['GET', 'POST'])
    return app