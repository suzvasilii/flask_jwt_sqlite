from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
from controller import Controller
from errors import ErrorHandler
from context import Context
from utils import filter_posts, filter_my_posts, token_required, set_context
from models import db

# Загружаем переменные окружения
load_dotenv()
SECRET = os.getenv("JWT")

# Конфигурируем приложение
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdb.db' # Подключаем базу данных sqlite
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size' : 10, # Максимальное количество соединений
    'connect_args': {'timeout': 15} # Тайм-аут соединения
}
app.config['secret_key'] = SECRET # Секретный ключ для JWT
handler = ErrorHandler(app) # Подключаем написанный самостоятельно обработчик ошибок
controller = Controller() # Подключаем написанный самостоятельно контроллер для работы с базой данных
context = Context() # Подключаем написанный самостоятельно контекст текущей сессии

# Делаем контекст глобальным во всем приложении
@app.context_processor
def inject_globals():
    return dict(
        context=context
    )

# Роут главной страницы
@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

# Роут страницы о сайте
@app.route("/about")
def about():
    return render_template('about.html')

# Роут страницы логина
@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST': # Если был отправлен POST-запрос с этой страницы
        email = request.form['email']
        password = request.form['password']
        data = controller.login(email,password) # Передаем данные из формы в запросе в контроллер
        if data['code'] == '0': # Если вернулся код успеха, то меняем контекст на авторизованного пользователя
            return set_context(context,email=email, is_authorized=True, data=data)
        return handler.throw_error(data['code']) # Если вернулся другой код (код ошибки), то возвращаем страницу с ошибкой
    return render_template('login.html') # Если мы просто зашли по этому роуту, то рендерим страницу

# Роут страницы регистрации
@app.route("/reg", methods=['POST','GET'])
def reg():
    if request.method == 'POST': # Если был отправлен POST-запрос с этой страницы
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm']
        data = controller.registration(email, password, confirm_password) # Передаем данные из формы в запросе в контроллер
        if data['code'] == '0': # Если вернулся код успеха, то меняем контекст на авторизованного пользователя
            return set_context(context, email=email, is_authorized=True, data=data)
        return handler.throw_error(data['code']) # Если вернулся другой код (код ошибки), то возвращаем страницу с ошибкой
    return render_template('reg.html') # Если мы просто зашли по этому роуту, то рендерим страницу

# Роут выхода из системы
@app.route("/logout")
def logout():
    return set_context(context)

# Роут создания поста
@app.route("/create", methods=['POST', 'GET'], endpoint='create')
@token_required(context) # Для доступа к этому ресурсу нужна jwt-авторизация
def create():
    if request.method == 'POST': # Если с этой страницы был отправлен POST-запрос
        title, text = request.form['title'], request.form['text'] # Получаем данные из формы
        code= controller.create(title, text, context.email) # Передаем данные из формы в контроллер
        # Если вернулся код успеха 0, то редиректим на страницу моих постов иначе на страницу с ошибкой
        return redirect("/myposts") if code == '0' else handler.throw_error(code)
    return render_template('create.html')

# Роут для доступа к постам авторизованного в данный момент пользователя
@app.route("/myposts", methods=['POST', 'GET'])
@token_required(context) # Для доступа к этому ресурсу нужна jwt-авторизация
def myposts():
    if request.method == 'POST': # Если с этой страницы был отправлен POST-запрос на фильтр постов
        title = request.form['title'] # получаем данные из формы
        filtered = filter_my_posts(title, context.posts) # Фильтруем посты
        return render_template('posts.html', posts=filtered, my=True) # Рендерим страницу с отфильтррованными постами
    data = controller.get_my_posts(context.email) # Если просто зашли по роуту делаем запрос в БД через контроллер
    if data['code'] == '0': # Если вернулся код успеха, то рендерим страницу с постами текущего пользователя
        context.posts = data['posts']
        return render_template('posts.html', posts=data['posts'], my=True)
    return handler.throw_error(data['code']) # Если вернулся код ошибки, рендерим страницу с ошибкой

# Роут удаления поста
@app.route("/delete/<id>")
@token_required(context)
def delete(id):
    code = controller.del_post(id) # Получаем код из контроллера
    if code == '0': # В случая успеха редиректим на страницу моих постов
        return redirect(url_for("myposts"))
    return handler.throw_error(code) # В ином случае редиректим на страницу с кодом ошибки

# Роут всех постов
@app.route("/allposts", methods=['POST', 'GET'])
@token_required(context) # Для доступа к этому ресурсу нужна jwt-авторизация
def allposts():
    if request.method == 'POST': # Если с этой страницы был отправлен POST-запрос на фильтр постов
        author, title = request.form['author'], request.form['title']
        filtered_posts = filter_posts(author, title, context.posts) # Фильтруем посты
        return render_template('posts.html', posts=filtered_posts, my=False) # Рендерим страницу с отфильтррованными постами
    data = controller.get_all_posts() # Если просто зашли по роуту делаем запрос в БД через контроллер
    if data['code'] == '0': # Если вернулся код успеха, то рендерим страницу с постами текущего пользователя
        context.posts = data['posts']
        return render_template('posts.html', posts=data['posts'], my=False)
    return handler.throw_error(data['code']) # Если вернулся код ошибки, рендерим страницу с ошибкой

# Точка входа
if __name__ == "__main__":
    try:
        # Инициализируем базу данных и стартуем наше приложение
        db.init_app(app)
        with app.app_context():
            db.create_all()
        app.run(debug=True)
    except Exception as e:
        print("При запуске приложения произошла ошибка\n", e)
