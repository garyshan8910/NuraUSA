from nura import db

class Sysuser(db.Model):
    __tablename__ = 'sysuser'

    id = db.Column(db.Integer, primary_key=True)
    activeFlag = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(255))
    firstName = db.Column(db.String(15))
    initials = db.Column(db.String(5))
    lastName = db.Column(db.String(15))
    phone = db.Column(db.String(255))
    userName = db.Column(db.String(100), nullable=False, unique=True)
    userPwd = db.Column(db.String(255), nullable=False)
    customFields = db.Column(db.JSON)
    passwordLastModified = db.Column(db.DateTime)