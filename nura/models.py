import hashlib
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

    def __repr__(self):
        return 'id = {}, name = {} {}, userName = {}, userPwdHash = {}'.format(
            self.id, self.firstName, self.lastName, self.userName, self.userPwd
        )

    def compute_md5_hash(self, password):
        m = hashlib.md5()
        m.update(password.encode('utf-8'))
        return m.hexdigest()
    
    def set_password(self, password):
        self.userPwd = self.compute_md5_hash(password)

    def check_password(self, password):
        return self.userPwd == self.compute_md5_hash(password)