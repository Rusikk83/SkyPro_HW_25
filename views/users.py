from flask import request
from flask_restx import Resource, Namespace

from models import User, UserSchema
from setup_db import db

from views.auth import auth_required, auth_admin

user_ns = Namespace('users')

"""представление для реализации методов CRUD для модели пользователь"""
@user_ns.route('/')
class UsersView(Resource):
    def post(self):
        req_json = request.json
        new_user = User(**req_json)
        new_user.password = new_user.get_hash()

        db.session.add(new_user)
        db.session.commit()
        return "", 201, {"location": f"/users/{new_user.id}"}


@user_ns.route('/<int:uid>')
class UserView(Resource):
    @auth_admin
    def get(self, uid):
        u = db.session.query(User).get(uid)
        sm_d = UserSchema().dump(u)
        return sm_d, 200

    # @auth_admin
    def put(self, uid):
        user = db.session.query(User).get(uid)
        req_json = request.json
        user.username = req_json.get("username")
        user.password = req_json.get("password")
        user.role = req_json.get("role")

        user.password = user.get_hash()

        db.session.add(user)
        db.session.commit()
        return "", 201

    # @auth_admin
    def delete(self, uid):
        user = db.session.query(User).get(uid)

        db.session.delete(user)
        db.session.commit()
        return "", 204