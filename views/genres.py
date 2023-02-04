from flask_restx import Resource, Namespace
from flask import request
from models import Genre, GenreSchema
from setup_db import db

from views.auth import auth_required, auth_admin

genre_ns = Namespace('genres')


"""представление для реализации методов CRUD для модели жанры"""
@genre_ns.route('/')
class GenresView(Resource):
    @auth_required
    def get(self):
        rs = db.session.query(Genre).all()
        res = GenreSchema(many=True).dump(rs)
        return res, 200

    @auth_admin
    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)

        db.session.add(new_genre)
        db.session.commit()
        return "", 201, {"location": f"/movies/{new_genre.id}"}


@genre_ns.route('/<int:gid>')
class GenreView(Resource):
    @auth_required
    def get(self, gid):
        r = db.session.query(Genre).get(gid)
        sm_d = GenreSchema().dump(r)
        return sm_d, 200

    @auth_admin
    def put(self, gid):
        genre = db.session.query(Genre).get(gid)
        req_json = request.json
        genre.name = req_json.get("name")

        db.session.add(genre)
        db.session.commit()
        return "", 204

    @auth_admin
    def delete(self, gid):
        genre = db.session.query(Genre).get(gid)
        db.session.add(genre)
        db.session.commit()
        return "", 204
