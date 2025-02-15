from flask import Flask
from flask_restful import Api, Resource, marshal_with, reqparse, fields
from werkzeug.exceptions import HTTPException
from werkzeug.sansio.response import Response
from datetime import datetime
from passlib.hash import sha256_crypt
from backend.api_models import *
from backend.models import db

app = Flask(__name__)

def setup_app():
    
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///householddb.sqlite3"
    db.init_app(app)
    api.init_app(app)
    app.app_context().push()
    app.debug = True
    print("App Started ............")

setup_app()

#--------------------------------------Routes---------------------------------------------------------------------------------
from backend.routes import *


# from flask import Flask
# from flask_restful import Api, Resource, marshal_with, reqparse, fields
# from werkzeug.exceptions import HTTPException
# from werkzeug.sansio.response import Response
# from datetime import datetime
# from passlib.hash import sha256_crypt
# from datetime import datetime
# from backend.api_models import *

# from backend.models import db

# app = None

# def setup_app():
#     app = Flask(__name__)
#     app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///householddb.sqlite3"
#     db.init_app(app)
#     api.init_app(app)
#     app.app_context().push()
#     app.debug = True
#     print("App Started ............")

# setup_app()

# #--------------------------------------Routes---------------------------------------------------------------------------------
# from backend.routes import *
