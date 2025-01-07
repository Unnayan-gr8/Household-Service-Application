from flask_restful import Resource, Api
from flask import request
from backend.models import *
from werkzeug.utils import secure_filename

api = Api()

class ServiceApi(Resource):
    def get(self):
        services = Service.query.all()
        service_json = []
        for s in services:
            service_json.append({'id' : s.id, 'name' : s.name, 'base_price' : s.base_price, 'time_required' : s.time_required, 'description' : s.description, "photo" : s.photo})
        return service_json
    
    def post(self):
        name = request.json.get("name")
        price = request.json.get("base_price")
        time = request.json.get("time_required")
        desc = request.json.get("description")
        file = request.json.get("photo")
        newservice = Service(name = name, base_price = price, description = desc, time_required = time, photo = secure_filename(file))
        db.session.add(newservice)
        db.session.commit()

    def put(self, id):
        s = Service.query.get(id)
        s.name = request.json.get("name")
        s.base_price = request.json.get("base_price")
        s.time_required = request.json.get("time_required")
        s.description = request.json.get("description")
        s.photo = request.json.get("photo")
        db.session.commit()

    def delete(self, id):
        s = Service.query.get(id)
        db.session.delete(s)
        db.session.commit()

api.add_resource(ServiceApi, "/api/get_services", "/api/post_services", "/api/put_services/<id>", "/api/delete_services/<id>")