from flask import Flask
from flask_restx import Api

from config import Config
from models import User
from setup_db import db
from views.directors import director_ns
from views.genres import genre_ns
from views.movies import movie_ns
from views.users import user_ns
from views.auth import  auth_ns


def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_extensions(app)
    return app


def create_data(app, db):
    """Использется для первоначального создания пользователей в БД"""
    with app.app_context():
        db.create_all()

        u1 = User(username="vasya", password="my_little_pony", role="user")
        u1.password = u1.get_hash()
        u2 = User(username="oleg", password="qwerty", role="user")
        u2.password = u2.get_hash()
        u3 = User(username="oleg_2", password="P@ssw0rd", role="admin")
        u3.password = u3.get_hash()

        with db.session.begin():
            db.session.add_all([u1, u2, u3])


def register_extensions(app):
    db.init_app(app)
    api = Api(app)

    # подключаем неймспейсы
    api.add_namespace(director_ns)
    api.add_namespace(genre_ns)
    api.add_namespace(movie_ns)
    api.add_namespace(user_ns)
    api.add_namespace((auth_ns))

   # create_data(app, db)


app = create_app(Config())
app.debug = True

if __name__ == '__main__':
    app.run(host="localhost", port=10001, debug=True)
