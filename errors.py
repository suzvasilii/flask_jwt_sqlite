from flask import Flask, render_template, redirect, url_for, request

class ErrorHandler:
    def __init__(self, app):
        self.app = app
        @self.app.route('/error')
        def error():
            code = request.args.get('code')
            message = request.args.get('message')
            return render_template('error.html',code=code,message=message)

    def throw_error(self, code='0xC0DEUNKNWN'):
        errors_codes = {
            '0xC0DEUNKNWN': "Unknown error",
            '0xCODE0REG': "Неудачная попытка регистрации",
            '0xC0DE0019': "Пользователь с таким email уже зарегистрирован",
            '0xC0DE0001': "Не указан email или пароль",
            '0xC0DE0020': "Введенные вами пароли не совпадают",
            '0xC0DE0021': "Email не найден",
            '0xC0DE0022': "Неверный пароль"
        }
        message = errors_codes.get(code, "Unknown error")
        return redirect(url_for('error', code=code, message=message))