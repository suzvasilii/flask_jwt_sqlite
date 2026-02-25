import datetime
import os
from dotenv import load_dotenv
from models import  db, User, Post
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

# Загружаем переменные окружения
load_dotenv()
SECRET = os.getenv("JWT")

class Controller:

    # Контроллер обработки регистрации
    def registration(self, email, password, confirm):
        data = {
            'code': 'unknown',
            'token':''
        }
        if email == "" or password == "":
            data['code'] = '0xC0DE0001'
            return data

        if password != confirm:
            data['code'] = '0xC0DE0020'
            return data
        try:
            candidate = User.query.filter_by(email=email).first()
            if candidate:
                data['code'] = '0xC0DE0019'
                return data

            # Перед сохранением пароля в базу данных "солим" его
            password = generate_password_hash(password, salt_length=16)
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()

            # Создаем jwt-токен, который действует 1 час
            token = jwt.encode({'user': email,
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, SECRET)
            data['code'], data['token'] = '0', token
            return data
        except:
            return data

    # Котроллер обработки логина
    def login(self, email, password):
        data = {
            'code': 'unknown',
            'token': ''
        }
        if email == '' or password == '':
            data['code'] = '0xC0DE0001'
            return data
        try:
            candidate = User.query.filter_by(email=email).first()
            if candidate:
                if check_password_hash(candidate.password,password):
                    token = jwt.encode({'user': email,
                                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, SECRET)
                    print('token=', token)
                    data['code'],data['token'] = '0', token
                    return data
                data['code'] = '0xC0DE0022'
                return data
            data['code'] = '0xC0DE0021'
            return data
        except:
            return data

    # Котроллер обработки создания поста
    def create(self, title, text, email):
        if title == "" or text =="":
            return '0xCODE0031'
        try:
            user = User.query.filter_by(email=email).first()
            if user:
                post = Post(title = title, text = text, user_id = user.id)
                db.session.add(post)
                db.session.commit()
                return '0'
        except Exception as e:
            db.session.rollback()
            print(e)
            return 'unknown'

    # Контроллер получения постов зарегистрированного пользователя
    def get_my_posts(self, email):
        try:
            user = User.query.filter_by(email=email).first()
            return {
                'code':'0',
                'posts':user.posts
            }
        except:
            return {
                'code':'unknown'
            }

    # Контроллер получения всех постов
    def get_all_posts(self):
        try:
            posts = Post.query.all()
            print("get_all")
            print(posts)
            return {
                'code' : '0',
                'posts' : posts
            }
        except:
            return {
                'code': 'unknown'
            }

    def del_post(self, post_id):
        try:
            deleting = Post.query.get(post_id)
            if deleting:
                db.session.delete(deleting)
                db.session.commit()
                return '0'
        except Exception as e:
            return 'unknown'

