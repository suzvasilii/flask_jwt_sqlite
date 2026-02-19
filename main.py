from flask import Flask, render_template, request, redirect
from controller import Controller
from model import db
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdb.db'
controller = Controller(app)
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
        return controller.login(email,password)
    return render_template('login.html')

@app.route("/reg", methods=['POST','GET'])
def reg():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm']
        return controller.registration(email, password, confirm_password)
    else:
        return render_template('reg.html')


if __name__ == "__main__":
    try:
        db.init_app(app)
        with app.app_context():
            db.create_all()
        app.run(debug=True)
    except:
        print("При запуске приложения произошла ошибка")
