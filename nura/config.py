

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1:3306/nura_usa'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'Admin'
