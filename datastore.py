from flask_sqlalchemy import SQLAlchemy
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Mask(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    filename = db.Column(db.String(50),nullable = False)
    mask_filename = db.Column(db.String(50),nullable = False)
    mask_values = db.Column(db.String(30), nullable = False)
    created = db.Column(db.String(20), nullable = False)