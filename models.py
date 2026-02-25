from flask_sqlalchemy import SQLAlchemy
import datetime
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email =db.Column(db.String(300), nullable=False)
    password =db.Column(db.String(300), nullable=False)
    posts = db.relationship('Post', back_populates='user') # Делаем обратную связь с таблицей постов

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='posts') # Делаем обратную связь с таблицей пользователей
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())