from flask import Flask, render_template, request, redirect, url_for
from flask_jwt_extended import JWTManager, jwt_required, get_jwt
from flask import make_response
from controller import Controller
from errors import ErrorHandler
from context import Context
from model import db
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdb.db'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_timeout' : 30,
    'pool_pre_ping' : True,
    'pool_size' : 10,
    'connect_args': {'timeout': 15}
}
app.config['JWT_SECRET_KEY'] = 'Y~O~2KH}'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
jwt = JWTManager(app)
handler = ErrorHandler(app)
controller = Controller()
context = Context()

@jwt.unauthorized_loader
def unauthorized_loader(error):
    return "<h1>Зарегистрируйтесь или войдите</h1>"

@jwt.invalid_token_loader
def invalid_token_loader(error):
    return "<h1>Получен неверный токен</h1>"

@jwt.expired_token_loader
def expired_token_loader(jwt_header, jwt_payload):
    return "<h1>Зайдите в систему заново или зарегистрируйтесь</h1>"
@app.route("/")
@app.route("/index")
def index():
    print(context.get_is_authorized())
    return render_template('index.html', context = context)

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

@app.route("/create", methods=['POST', 'GET'])
@jwt_required()
def create():
    if request.method == 'POST':
        title, text = request.form['title'], request.form['text']
        code= controller.create(title, text, context.get_name())
        return redirect("/myposts") if code == '0' else handler.throw_error(code)
    return render_template('create.html')
@app.route("/myposts")
@jwt_required()
def myposts():
    data = controller.get_my_posts(context.get_name())
    if data['code'] == '0':
        return render_template('posts.html', posts=data['posts'])
    return handler.throw_error(data['code'])

@app.route("/allposts")
@jwt_required()
def allposts():
    print("get_all")
    data = controller.get_all_posts()
    if data['code'] == '0':
        return render_template('posts.html', posts=data['posts'])
    return handler.throw_error(data['code'])

def set_context(email=None, is_authorized=False, data=None, redirect_for='index'):
    context.set_name(email)
    context.set_is_authorized(is_authorized)
    response = make_response(redirect(url_for(redirect_for)))
    token = data['token'] if data is not None else ''
    response.set_cookie('access_token',token, httponly=True)
    return response

if __name__ == "__main__":
    try:
        db.init_app(app)
        with app.app_context():
            db.create_all()
        app.run()
    except Exception as e:
        print("При запуске приложения произошла ошибка\n", e)
