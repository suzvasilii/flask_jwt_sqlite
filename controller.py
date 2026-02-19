from flask import Flask, render_template, redirect, url_for, request
from errors import ErrorHandler
from model import  db, User

class Controller:
    def __init__(self,app):
        self.handler = ErrorHandler(app)

    def registration(self, email, password, confirm):
        if email == "" or password == "":
            return self.handler.throw_error('0xC0DE0001')
        if password != confirm:
            return self.handler.throw_error('0xC0DE0020')
        try:
            candidate = User.query.filter_by(email=email).first()
            if candidate:
                return self.handler.throw_error('0xC0DE0019')
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        except:
            return self.handler.throw_error()

    def login(self, email, password):
        if email == '' or password == '':
            return self.handler.throw_error('0xC0DE0001')
        try:
            candidate = User.query.filter_by(email=email).first()
            if candidate:
                if candidate.password == password:
                    return redirect('/')
                return self.handler.throw_error('0xC0DE0022')
            return self.handler.throw_error('0xC0DE0021')
        except:
            return self.handler.throw_error()