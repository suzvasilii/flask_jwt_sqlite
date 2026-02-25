from flask import redirect, url_for
import operator as op
import os
import jwt
from dotenv import load_dotenv
import functools

# Загружаем переменные окружения
load_dotenv()
SECRET = os.getenv("JWT")

# Фильтрация всех постов
def filter_posts(author, title, posts):
    filtered = [post for post in posts if (op.contains(post.title, title) and op.contains(post.user.email, author))]
    return filtered

# Фильтрация постов текущего пользователя
def filter_my_posts(title, posts):
    filtered = [post for post in posts if op.contains(post.title, title)]
    return filtered

# Декоратор для роутов, где нужна JWT-авторизация
def token_required(context): # Внешний декоратор должен принимать контекст
    def intern_decorator(func):
        @functools.wraps(func) # Передаем функцию во внтруненний декоратор
        def wrapper(*args, **kwargs):
            token = context.token # Получаем токен из контекста
            if token is None:
                return redirect(url_for('index'))
            try:
                jwt.decode(token, SECRET, algorithms="HS256") # Пробуем распознать токен
                return func(*args, **kwargs)
            except Exception as e: # Если токен невалидный
                return "<h1> При проверке подлинности произошла ошибка, выполните вход в систему заново </h1>"
        # Внутреннему декоратору даем __name__ декорируемой функции, чтобы можно было применить к нескольким функциям
        wrapper.__name__ = func.__name__
        return wrapper # Возвращаем обертку декорируемой функции
    return intern_decorator # Возвращаем внутренний декоратор

# Установка контекста текущей сессии пользвоателя
def set_context(context, email=None, is_authorized=False, data=None, redirect_for='index'):
    context.email = email
    context.is_authorized = is_authorized
    context.token = data['token'] if data is not None else None
    return redirect(redirect_for)
