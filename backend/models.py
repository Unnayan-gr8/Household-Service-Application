from flask_sqlalchemy import SQLAlchemy

#------------------------------------DATABASE MANAGEMENT---------------------------------------------------------------------
db = SQLAlchemy()

class Users_info(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    email_id = db.Column(db.String(), unique = True, nullable = False)
    password = db.Column(db.String(), nullable = False)
    roles = db.Column(db.Integer, nullable = False)
    customers = db.relationship("Customers", cascade = "all,delete", backref = "users_info", lazy = True)
    professionals = db.relationship("Service_professionals", cascade = "all,delete", backref = "users_info", lazy = True)

class Customers(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    email_id = db.Column(db.String(), db.ForeignKey('users_info.email_id'), nullable = False)
    first_name = db.Column(db.String(), nullable = False)
    last_name = db.Column(db.String(), nullable = False)
    address = db.Column(db.String(), nullable = False)
    pincode = db.Column(db.Integer, nullable = False)
    contact_number = db.Column(db.Integer, nullable = False)
    service_request = db.relationship("Service_request", cascade = "all,delete", backref = "customers", lazy = True)

class Service_professionals(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    email_id = db.Column(db.String(), db.ForeignKey('users_info.email_id'), nullable = False)
    first_name = db.Column(db.String(), nullable = False)
    last_name = db.Column(db.String(), nullable = False)
    date_created = db.Column(db.DateTime(), nullable = False)
    description = db.Column(db.String(), nullable = True)
    service_type = db.Column(db.Integer, db.ForeignKey('service.id'), nullable = True)
    experience = db.Column(db.Integer, nullable = True)
    address = db.Column(db.String(), nullable = False)
    pincode = db.Column(db.Integer, nullable = False)
    contact_number = db.Column(db.Integer, nullable = False)
    status = db.Column(db.String(), nullable = False)
    rating = db.Column(db.Integer)
    documentname = db.Column(db.String(255), nullable=False)
    service_request = db.relationship("Service_request", cascade = "all,delete", backref = "service_professionals", lazy = True)

    
class Service(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    name = db.Column(db.String(), nullable = False)
    base_price = db.Column(db.Integer, nullable = False)
    time_required = db.Column(db.Integer, nullable = False)
    description = db.Column(db.String(), unique = True, nullable = False)
    photo = db.Column(db.String(255), nullable=False)
    professionals = db.relationship("Service_professionals", cascade = "all,delete", backref = "service", lazy = True)
    requests = db.relationship("Service_request", cascade = "all,delete", backref = "service", lazy = True)

class Service_request(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professionals.id'))
    date_of_request = db.Column(db.DateTime(), nullable = False)
    date_of_completion = db.Column(db.DateTime(), nullable = True)
    service_status = db.Column(db.String(), nullable = False)
    rating = db.Column(db.String())
    remark = db.Column(db.String())