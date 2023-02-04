from flask_restx import Resource, Namespace
from flask import request

from models import Director, DirectorSchema
from setup_db import db

from views.auth import auth_required, auth_admin

director_ns = Namespace('directors')


"""представление для реализации методов CRUD для модели режиссер"""
@director_ns.route('/')
class DirectorsView(Resource):
    @auth_required
    def get(self):
        rs = db.session.query(Director).all()
        res = DirectorSchema(many=True).dump(rs)
        return res, 200

    @auth_admin
    def post(self):
        req_json = request.json
        new_director = Director(**req_json)

        db.session.add(new_director)
        db.session.commit()
        return "", 201, {"location": f"/movies/{new_director.id}"}




@director_ns.route('/<int:rid>')
class DirectorView(Resource):
    @auth_required
    def get(self, rid):
        r = db.session.query(Director).get(rid)
        sm_d = DirectorSchema().dump(r)
        return sm_d, 200

    @auth_admin
    def put(self, rid):
        director = db.session.query(Director).get(rid)
        req_json = request.json
        director.name = req_json.get("name")

        db.session.add(director)
        db.session.commit()
        return "", 204
    @auth_admin
    def delete(self, rid):
        director = db.session.query(Director).get(rid)
        db.session.add(director)
        db.session.commit()
        return "", 204