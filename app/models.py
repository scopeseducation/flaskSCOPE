from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    scopes_mode = db.Column(db.String(64))
    qr_codes = db.relationship('QR_image', backref='author', lazy='dynamic')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_status(self):
        return self.scopes_mode
        
    def set_status(self, mode):
        self.scopes_mode = mode

class QR_image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qr_code = db.Column(db.String(140))
    image = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        
    def __repr__(self):
        return format(self.image)
