import hashlib

from flask import request
from flask_restx import Resource, Namespace, abort
import jwt
import calendar
import datetime
from config import Config

from models import User
from setup_db import db

auth_ns = Namespace('auth')


def auth_required(func):
    """Декоратор проверки авторизации пользователя"""

    def wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers:  # проверем наличие заголовка с данными авторизации
            abort(401)

        data = request.headers['Authorization']  # получаем значение заголовка авторизации
        token = data.split("Bearer ")[-1]  # выделяем сам токен из строки авторизации
        try:
            jwt.decode(token, Config.SECRET_HERE, algorithms=['HS256'])  # декодируем токен авторизации
        except Exception:  # если токен не валиден, возвращаем ответ 401
            abort(401)

        return func(*args, **kwargs)  # если исключение не вызвалось, выполняем декорируемую функцию

    return wrapper


def auth_admin(func):
    """Декоратор проверки авторизации и прав пользователя"""

    def wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers:  # проверем наличие заголовка с данными авторизации
            abort(401)

        data = request.headers['Authorization']  # получаем значение заголовка авторизации
        token = data.split("Bearer ")[-1]  # выделяем сам токен из строки авторизации
        role = None  # инициируем переменную значения роли пользователя

        try:
            user = jwt.decode(token, Config.SECRET_HERE, algorithms=['HS256'])  # декодируем токен авторизации
            role = user.get("role")  # получаем значение роли из токена
        except Exception:
            abort(401)

        if role != 'admin':  # проверяем, что роль admin
            abort(403)

        return func(*args, **kwargs)  # если все условия выполнены выполняется декорируемая функция

    return wrapper


def generate_tokens(username, password, is_refresh=False):
    """
    генерирует токен для пользователя по паролю или refresh-токену.
    в токен записывается имя пользователя и роль
    """
    user = db.session.query(User).filter(User.username == username)[0]  # получаем пользователя по имени из БД
    if user is None:
        raise abort(404)

    if not is_refresh:  # если по паролю, а не по рефреш-токену
        if hashlib.md5(password.encode('utf-8')).hexdigest() != user.password:  # проверяем пароль сравнением хешей
            raise abort(400)

    data = {
        "username": user.username,
        "role": user.role,
    }

    # формируем токены с заданными параметрами срока действия
    min30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    data['exp'] = calendar.timegm(min30.timetuple())
    access_token = jwt.encode(data, Config.SECRET_HERE, algorithm='HS256')

    days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
    data['exp'] = calendar.timegm(days130.timetuple())
    refresh_token = jwt.encode(data, Config.SECRET_HERE, algorithm='HS256')

    return {  # возвращаем токен лоступа и рефреш-токен
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def approve_refresh_token(refresh_token):
    """предоставление новых токенов по рефреш-токену"""
    try:
        data = jwt.decode(jwt=refresh_token, key=Config.SECRET_HERE,
                          algorithms=['HS256'])  # декодирование рефреш-токена

        username = data.get("username")  # получение имени пользователя из токена
        return generate_tokens(username, None, is_refresh=True)  # получение новой пары токенов

    except Exception:  # если то рефреш-токен не валиден вызываем исключение
        raise abort(400)


"""представление для получения токенов авторизации"""
@auth_ns.route('/')
class AuthView(Resource):
    """получение токенов авторизации по логину и паролю"""
    def post(self):
        data = request.json
        # получение имени пользователя и пароля из запроса
        username = data.get("username", None)
        password = data.get("password", None)

        if None in [username, password]:
            return "", 400

        tokens = generate_tokens(username, password)  # получение токеноа по логину и паролю
        return tokens, 201

    def put(self):
        """обновление токенов авторизации по рефреш-токену"""
        data = request.json
        # получение рефреш-токена из запроса
        token = data.get("refresh_token")

        tokens = approve_refresh_token(token)  #получение токенов по рефреш-токену

        return tokens, 201
