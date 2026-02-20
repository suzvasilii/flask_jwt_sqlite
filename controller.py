from model import  db, User
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
class Controller:

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
            password = generate_password_hash(password, salt_length=16)
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()
            access_token = create_access_token(identity=email)
            data['code'], data['token'] = '0', access_token
            return data
        except:
            return data

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
                    access_token = create_access_token(identity=email)
                    data['code'],data['token'] = '0', access_token
                    return data
                data['code'] = '0xC0DE0021'
                return data
        except:
            return data