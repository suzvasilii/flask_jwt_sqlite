from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email =db.Column(db.String(300), nullable=False)
    password =db.Column(db.String(300), nullable=False)