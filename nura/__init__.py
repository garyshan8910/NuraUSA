from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask.json import JSONEncoder
from datetime import date
from nura.config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'

from nura.route import add_poiteminfo_detail, create_soitem_poitem_map_record, get_inventory, get_po_items, get_po_item_info_details, get_poitem_info, get_so, get_so_items, get_soitem_map, get_soitem_poitem_map, index, login, logout, po_items, register, so, po_item_info, so_items, so_po_mapping, po_details, so_details, update_poitem_info

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.strftime('%m/%d/%Y')
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

def create_app():
    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder
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
    app.add_url_rule('/so', 'so', so, methods=['GET'])
    app.add_url_rule('/so_items', 'so_items', so_items, methods=['GET'])
    app.add_url_rule('/po_details', 'po_details', po_details, methods=['GET', 'POST'])
    app.add_url_rule('/so_details', 'so_details', so_details, methods=['GET', 'POST'])
    app.add_url_rule('/po_items', 'po_items', po_items, methods=['GET'])
    app.add_url_rule('/get_po_items', 'get_po_items', get_po_items, methods=['GET', 'POST'])
    app.add_url_rule('/get_so_items', 'get_so_items', get_so_items, methods=['GET', 'POST'])
    app.add_url_rule('/get_inventory', 'get_inventory', get_inventory, methods=['GET', 'POST'])
    app.add_url_rule('/create_soitem_poitem_map_record', 'create_soitem_poitem_map_record', create_soitem_poitem_map_record, methods=['POST'])
    app.add_url_rule('/get_so', 'get_so', get_so, methods=['GET'])
    app.add_url_rule('/get_soitem_poitem_map', 'get_soitem_poitem_map', get_soitem_poitem_map, methods=['GET'])
    app.add_url_rule('/get_soitem_map', 'get_soitem_map', get_soitem_map, methods=['GET'])
    app.add_url_rule('/get_poitem_info', 'get_poitem_info', get_poitem_info, methods=['GET'])
    app.add_url_rule('/update_poitem_info', 'update_poitem_info', update_poitem_info, methods=['POST'])
    app.add_url_rule('/get_po_item_info_details', 'get_po_item_info_details', get_po_item_info_details, methods=['GET'])
    app.add_url_rule('/add_poiteminfo_detail', 'add_poiteminfo_detail', add_poiteminfo_detail, methods=['POST'])
    app.add_url_rule('/po_item_info', 'po_item_info', po_item_info, methods=['GET'])
    
    return app