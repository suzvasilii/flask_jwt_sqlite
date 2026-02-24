from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
import jwt
from controller import Controller
from errors import ErrorHandler
from context import Context
from utils import filter_posts, filter_my_posts
from models import db

load_dotenv()
SECRET = os.getenv("JWT")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdb.db'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_timeout' : 30,
    'pool_pre_ping' : True,
    'pool_size' : 10,
    'connect_args': {'timeout': 15}
}
app.config['secret_key'] = SECRET
handler = ErrorHandler(app)
controller = Controller()
context = Context()

@app.before_request
def clear():
    print(request.cookies)

@app.context_processor
def inject_globals():
    return dict(
        context=context
    )

def token_required(func):
    def decorator(*args, **kwargs):
        token = context.token
        if token is None:
            return "<h1>Необходимо авторизоваться</h1>"
        try:
            jwt.decode(token, app.config['secret_key'], algorithms="HS256")
            return func(*args, **kwargs)
        except Exception as e:
            return "<h1> При проверке подлинности произошла ошибка, выполните вход в систему заново </h1>"
    decorator.__name__ = func.__name__
    return decorator

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        data = controller.login(email,password)
        if data['code'] == '0':
            return set_context(email=email, is_authorized=True, data=data)
        return handler.throw_error(data['code'])
    return render_template('login.html')

@app.route("/reg", methods=['POST','GET'])
def reg():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm']
        data = controller.registration(email, password, confirm_password)
        if data['code'] == '0':
            return set_context(email=email, is_authorized=True, data=data)
        return handler.throw_error(data['code'])
    return render_template('reg.html')

@app.route("/logout")
def logout():
    return set_context()

@app.route("/create", methods=['POST', 'GET'], endpoint='create')
@token_required
def create():
    if request.method == 'POST':
        title, text = request.form['title'], request.form['text']
        code= controller.create(title, text, context.email)
        return redirect("/myposts") if code == '0' else handler.throw_error(code)
    return render_template('create.html')

@app.route("/myposts", methods=['POST', 'GET'])
@token_required
def myposts():
    if request.method == 'POST':
        title = request.form['title']
        filtered = filter_my_posts(title, context.posts)
        return render_template('posts.html', posts=filtered, my=True)
    data = controller.get_my_posts(context.email)
    if data['code'] == '0':
        context.posts = data['posts']
        return render_template('posts.html', posts=data['posts'], my=True)
    return handler.throw_error(data['code'])

@app.route("/allposts", methods=['POST', 'GET'])
@token_required
def allposts():
    if request.method == 'POST':
        author, title = request.form['author'], request.form['title']
        filtered_posts = filter_posts(author, title, context.posts)
        return render_template('posts.html', posts=filtered_posts, my=False)
    data = controller.get_all_posts()
    if data['code'] == '0':
        context.posts = data['posts']
        return render_template('posts.html', posts=data['posts'], my=False)
    return handler.throw_error(data['code'])

def set_context(email=None, is_authorized=False, data=None, redirect_for='index'):
    context.email = email
    context.is_authorized = is_authorized
    context.token = data['token'] if data is not None else None
    return redirect(redirect_for)

if __name__ == "__main__":
    try:
        db.init_app(app)
        with app.app_context():
            db.create_all()
        app.run(debug=True)
    except Exception as e:
        print("При запуске приложения произошла ошибка\n", e)
