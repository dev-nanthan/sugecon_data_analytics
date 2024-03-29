from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=False, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Site(db.Model):
    __tablename__ = 'sites'

    site_id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    file_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Site {self.short_name}>"