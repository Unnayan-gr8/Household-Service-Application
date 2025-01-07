from flask import Flask, make_response, jsonify, render_template, request, redirect, flash, session
from .models import *
from flask import current_app as app
from sqlalchemy import and_
from datetime import datetime
from werkzeug.utils import secure_filename
import os 
import urllib.request

UPLOAD_FOLDER = './Service Professional Resume'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER1'] = './static'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'html', 'jpg', 'jpeg', 'png', 'ppt', 'pptx'])


ALLOWED_EXTENSIONS1 = set(['jpeg', 'jpg', 'png', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file1(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS1

@app.route('/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_id = request.form.get("email_id")
        password = request.form.get("password")
        existing_user = db.session.query(Users_info).filter(and_(Users_info.email_id == email_id, Users_info.password == password)).first()
        if existing_user:
            if existing_user.roles == 0:
                return redirect('/home')
            elif existing_user.roles == 1:
                user = Customers.query.filter_by(email_id=email_id).first()
                return redirect(f'/userhome/{user.id}')
            elif existing_user.roles == 2:
                prof = Service_professionals.query.filter_by(email_id=email_id).first()
                if(prof.status != "Rejected"):
                    return redirect(f'/profhome/{prof.id}')
                else:
                    return render_template("login.html", message = "Rejected User !!!!!")
            else:
                return render_template("login.html", message = "Incorrect Password")
        else:
            return render_template("login.html", message = "No User Found")
    return render_template("login.html")

@app.route('/home')
def home():
    services = Service.query.all()
    professionals = Service_professionals.query.filter_by(status='pending').all()
    requests = Service_request.query.all()
    return render_template("adminhome.html", services = services, professionals = professionals, requests = requests)

@app.route('/search', methods=['GET', 'POST'])
def search():
    # Initial request to get all closed service requests
    requests = Service_request.query.filter_by(service_status='closed').all()

    if request.method == "POST":
        st = request.form.get("servicetype")  # Search type (service_request, customer, etc.)
        query = request.form.get("search")  # Search query (e.g., service name, customer pincode)

        # Search logic based on selected service type
        if st == "service_request":
            # Searching Service Request by service_status
            sq = Service_request.query.filter(Service_request.service_status.like(f"%{query}%")).all()
            return render_template("adminsearch.html", requests=sq, st="SR")

        elif st == "customer":
            # Searching Customers by pincode
            sq = Customers.query.filter(Customers.pincode.like(f"%{query}%")).all()
            return render_template("adminsearch.html", requests=sq, st="C")

        elif st == "professional":
            # Searching Service Professionals by service_type
            sq = Service_professionals.query.all()
            nsq = []
            for s in sq:
                if s.service and query in s.service.name:
                    nsq.append(s)
            return render_template("adminsearch.html", requests=nsq, st="SP")

        elif st == "service":
            # Searching Services by name
            sq = Service.query.filter(Service.name.like(f"%{query}%")).all()
            return render_template("adminsearch.html", requests=sq, st="S")

    # Default return with all closed service requests
    return render_template("adminsearch.html", requests=requests, st="SR")

@app.route('/create', methods = ['GET', 'POST'])
def create():
    if request.method == "POST":
        email_id = request.form.get("emailid")
        password = request.form.get("password")
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        address = request.form.get("address")
        pin = request.form.get("pin")
        contactno = request.form.get("contactno")
        newuser = Users_info(email_id = email_id, password = password, roles = 1)
        try:
            db.session.add(newuser)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return render_template("login.html", message = "Resgistration Unsuccessful, Use Different Email ID !!! Try Again")
        newcustomers = Customers(email_id = newuser.email_id, first_name = fname, last_name = lname, address = address, pincode = pin, contact_number = contactno)
        try:
            db.session.add(newcustomers)
            db.session.commit()
            return render_template("login.html", message = "Registration Successful, New User Created")
        except Exception as e:
            db.session.rollback()
            return render_template("login.html", message = "Resgistration Unsuccessful, Use Different User ID Try Again")
    return render_template("customer_signup.html")

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == "POST":
        email_id = request.form.get("emailid")
        password = request.form.get("password")
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        date = datetime.now()
        description = request.form.get("description")
        service_type = request.form.get("servicetype")
        experience = request.form.get("experience")
        file = request.files.get("myfile")
        address  = request.form.get("address")
        pin = request.form.get("pin")
        contactno = request.form.get("contactno")
        newuser = Users_info(email_id = email_id, password = password, roles = 2)
        try:
            db.session.add(newuser)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return render_template("login.html", message = "Service Professional Resgistration Unsuccessful, Use Different Email ID !!! Try Again")
        if file and allowed_file(file.filename):
            newcustomers = Service_professionals(email_id = newuser.email_id, first_name = fname, last_name = lname, date_created = date, description = description, service_type = service_type, experience = experience, address = address, pincode = pin, contact_number = contactno, status = "pending", rating = 0, documentname = secure_filename(file.filename))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
            try:
                db.session.add(newcustomers)
                db.session.commit()
                return render_template("login.html", message = "Service Professional Resgistration Successful, New professional Created")
            except Exception as e:
                db.session.rollback()
                print(f"Error: {e}")
                return render_template("login.html", message = "Resgistration Unsuccessful, Use Different User ID Try Again")
        else:
            return render_template("login.html", message = "Resgistration Unsuccessful, Invalid extension")    
    services = db.session.query(Service).all()
    return render_template("serviceprofessionalsignup.html", services = services)

@app.route('/service/<int:id>')
def service_details(id):
    service = Service.query.get(id)
    return render_template("service_id.html", service = service)

@app.route('/professional/<int:id>')
def professional_details(id):
    professional = Service_professionals.query.get(id)
    return render_template("professional_id.html", professional = professional)

@app.route('/service/update/<int:id>', methods = ['GET', 'POST'])
def update(id):
    service = Service.query.get(id)
    if request.method == "POST":
        price = request.form.get("price")
        time = request.form.get("time")
        desc = request.form.get("desc")
        service.base_price = price
        service.time_required= time
        service.description = desc
        db.session.commit()
        return redirect('/home')
    return render_template("editservice.html", service = service)

@app.route('/service/delete/<int:id>')
def delete(id):
    service = Service.query.get(id)
    db.session.delete(service)
    db.session.commit()
    return redirect('/home')

@app.route('/new', methods = ['GET', 'POST'])
def new():
    if request.method == "POST":
        name = request.form.get("name")
        desc = request.form.get("description")
        price = request.form.get("price")
        time = request.form.get("time")
        file = request.files.get("myfile")
        print(file)
        if file and allowed_file1(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER1'], secure_filename(file.filename)))
            newservice = Service(name = name, base_price = price, description = desc, time_required = time, photo = secure_filename(file.filename))
            db.session.add(newservice)
            db.session.commit()
            return redirect('/home')
        return redirect('/home')
    return render_template("newservice.html")

@app.route('/professional/approve/<int:id>')
def approve(id):
    prof = Service_professionals.query.get(id)
    prof.status = "Approved"
    db.session.commit()
    return redirect('/home')

@app.route('/professional/reject/<int:id>')
def reject(id):
    prof = Service_professionals.query.get(id)
    prof.status = "Rejected"
    db.session.commit()
    return redirect('/home')

@app.route('/professional/delete/<int:id>')
def deleteprof(id):
    prof = Service_professionals.query.get(id)
    email_id = prof.email_id
    user = Users_info.query.filter_by(email_id = email_id).first()
    db.session.delete(prof)
    db.session.delete(user)
    db.session.commit()
    return redirect('/home')

@app.route('/view')
def viewallprof():
    prof = Service_professionals.query.all()
    return render_template("viewallprof.html", prof = prof)

@app.route('/admin_chart')
def admin_chart():
    rating = Service_request.query.all() 
    good = 0
    bad = 0
    for r in rating:
        if r.rating:
            if "good" in r.remark or "best" in r.remark or "Top-notch" in r.remark or "high-quality" in r.remark:
                good += 1
            else:
                bad += 1
    service_requests_pending = len(Service_request.query.filter_by(service_status='requested').all())
    approved_requests_pending = len(Service_request.query.filter_by(service_status='accepted').all())
    closed_requests_pending = len(Service_request.query.filter_by(service_status='closed').all())
    print(service_requests_pending,approved_requests_pending,closed_requests_pending)
    return render_template("admin_chart.html", good = good , bad = bad, service_request = (service_requests_pending), accepted_request = (approved_requests_pending), closed_request = (closed_requests_pending))

@app.route('/profhome/<int:id>')
def profhome(id):
    prof = Service_professionals.query.filter_by(id=id).first()
    prof_service = Service.query.filter_by(name = prof.service_type).first()
    services = Service_request.query.filter(Service_request.service_status == 'requested', Service_request.service_id == prof_service.id).all()
    closed_services = Service_request.query.filter(Service_request.professional_id == id,Service_request.service_status == 'closed').all()
    return render_template("professionalhome.html", services = services, closed_services = closed_services, prof = prof)

@app.route('/profsearch/<int:id>', methods = ["GET", "POST"])
def profsearch(id):
    prof = Service_professionals.query.get(id)
    service_id = Service.query.filter_by(name = prof.service_type).first()
    if request.method == "POST":
        st = request.form.get("servicetype")
        query = request.form.get("search")
        if st == "date":
            sq = Service_request.query.filter_by(service_id = service_id.id).all()
            nsq = []
            for s in sq:
                day = str(s.date_of_request.year) + "-" + str(s.date_of_request.month) + "-" + str(s.date_of_request.day) 
                if query in day:
                    nsq.append(s)
            return render_template("professional_search.html", prof = prof, requests = nsq, st = "C") 
        elif st == "location":
            sq = Service_request.query.filter_by(service_id = service_id.id).all()
            nsq = []
            for s in sq:
                if query in s.customers.address:
                    nsq.append(s)
            return render_template("professional_search.html", prof = prof, requests = nsq, st = "C") 
        elif st == "name":
            sq = Service_request.query.filter_by(service_id = service_id.id).all()
            nsq = []
            for s in sq:
                name = s.customers.first_name + " " + s.customers.last_name
                if query in name:
                    nsq.append(s)
            return render_template("professional_search.html", prof = prof, requests = nsq, st = "C")
        elif st == "pincode":
            sq = Service_request.query.filter_by(service_id = service_id.id).all()
            nsq = []
            for s in sq:
                if int(query) == s.customers.pincode:
                    nsq.append(s)
            return render_template("professional_search.html", prof = prof, requests = nsq, st = "C")
    service_id = Service.query.filter_by(name = prof.service_type).first()
    requests = Service_request.query.filter_by(service_id=service_id.id).all()
    return render_template("professional_search.html", prof = prof, requests = requests, st = "SR")

@app.route('/profile/<int:id>', methods = ['GET', 'POST'])
def profile(id):
    prof = Service_professionals.query.get(id)
    if request.method == "POST":
        prof.first_name = request.form.get("fname")
        prof.last_name = request.form.get("lname")
        prof.description = request.form.get("description")
        prof.experience = request.form.get("experience")
        prof.address  = request.form.get("address")
        prof.pincode = request.form.get("pin")
        prof.contact_number = request.form.get("contactno")
        db.session.commit()
        return redirect(f'/profhome/{prof.id}')
    return render_template("profile.html", prof = prof)

@app.route('/accept/<int:id1>/<int:id2>')
def acc(id1, id2):
    prof = Service_professionals.query.get(id1)
    service_request = Service_request.query.get(id2)
    service_request.professional_id = id1
    service_request.service_status = "accepted"
    db.session.commit()
    return redirect(f'/profhome/{prof.id}')

@app.route('/rejected/<int:id1>/<int:id2>')
def rej(id1, id2):
    prof = Service_professionals.query.get(id1)
    service_request = Service_request.query.get(id2)
    service_request.professional_id = id1
    service_request.service_status = "rejected"
    db.session.commit()
    return redirect(f'/profhome/{prof.id}')

@app.route('/professional_chart/<int:id>')
def prof_chart(id):
    prof = prof = Service_professionals.query.get(id)
    rating = Service_request.query.filter_by(professional_id=id).all() 
    good = 0
    bad = 0
    for r in rating:
        if r.rating:
            if "good" in r.remark or "best" in r.remark or "Top-notch" in r.remark or "high-quality" in r.remark:
                good += 1
            else:
                bad += 1
    accepted_requests = len(Service_request.query.filter_by(service_status='accepted', professional_id=id).all())
    closed_requests = len(Service_request.query.filter_by(service_status='closed', professional_id=id).all())
    rejected_requests = len(Service_request.query.filter_by(service_status='rejected', professional_id=id).all())
    return render_template("professional_chart.html", prof = prof, good = good , bad = bad, accept = accepted_requests, closed = closed_requests, reject = rejected_requests)

@app.route('/userhome/<int:id>')
def userhome(id):
    user = Customers.query.get(id)
    services = Service.query.distinct(Service.name).all()
    rs = Service_request.query.filter(Service_request.customer_id == user.id).all()
    return render_template("user_home.html", user = user, services = services, requested_services = rs)

@app.route('/user_profile/<int:id>', methods = ['GET', 'POST'])
def user_profile(id):
    user = Customers.query.get(id)
    if request.method == "POST":
        user.first_name = request.form.get("fname")
        user.last_name = request.form.get("lname")
        user.description = request.form.get("description")
        user.experience = request.form.get("experience")
        user.address  = request.form.get("address")
        user.pincode = request.form.get("pin")
        user.contact_number = request.form.get("contactno")
        db.session.commit()
        return redirect(f'/userhome/{user.id}')
    return render_template("user_profile.html", user = user)

@app.route('/service_request/<int:id1>/<int:id2>')
def sr(id1, id2):
    user = Customers.query.get(id1)
    s = Service.query.get(id2)
    services = Service.query.filter(Service.name == s.name).all()
    rs = Service_request.query.filter(Service_request.customer_id == user.id).all()
    return render_template("service_request.html", user = user, services = services, requested_services = rs, service = s)

@app.route('/book/<int:id1>/<int:id2>')
def book(id1, id2):
    time = datetime.now()
    new_service = Service_request(service_id = id2, customer_id = id1, date_of_request = time, service_status = "requested")
    db.session.add(new_service)
    db.session.commit()
    return redirect(f'/userhome/{id1}')

@app.route('/closeit/<int:id1>/<int:id2>', methods = ['GET', 'POST'])
def closeit(id1, id2):
    user = Customers.query.get(id1)
    service_request = Service_request.query.get(id2)
    if request.method == "POST":
        time = datetime.now()
        service_request.rating = request.form.get("rating")
        prof_id = service_request.professional_id
        prof = Service_professionals.query.get(prof_id)
        if prof.rating:
            prof.rating += Service_request.rating
            prof.rating /= 2
        else:
            prof.rating = Service_request.rating
        service_request.remark = request.form.get("remark")
        service_request.date_of_completion = time
        service_request.service_status = "closed"
        db.session.commit()
        return redirect(f'/userhome/{id1}')
    return render_template("service_remark.html", user = user, service_request = service_request)

@app.route('/user_search/<int:id>', methods = ["GET", "POST"])
def usersearch(id):
    user = Customers.query.get(id)
    if request.method == "POST":
        st = request.form.get("servicetype")
        query = request.form.get("search")
        if st == "name":
            sq = Service.query.all()
            nsq = []
            for s in sq:
                if query in s.name:
                    nsq.append(s)
            return render_template("user_search.html", user = user, requests = nsq) 
        elif st == "location":
            sp = Service_professionals.query.order_by(Service_professionals.rating.desc()).all()
            nsq = []
            for s in sp:
                if query in s.address:
                    s1 = Service.query.filter(Service.name == s.service_type).all()
                    nsq.append(s1)
            return render_template("user_search.html", user = user, requests = nsq[0]) 
        elif st == "time":
            sq = Service.query.all()
            nsq = []
            for s in sq:
                if int(query) == s.time_required :
                    nsq.append(s)
            return render_template("user_search.html", user = user, requests = nsq)
        elif st == "pincode":
            sp = Service_professionals.query.order_by(Service_professionals.rating.desc()).all()
            nsq = []
            for s in sp:
                if int(query) == s.pincode:
                    s1 = Service.query.filter(Service.name == s.service_type).all()
                    nsq.append(s1)
            return render_template("user_search.html", user = user, requests = nsq[0])
    requests = Service.query.all()
    return render_template("user_search.html", user = user, requests = requests)

@app.route('/user_chart/<int:id>')
def user_chart(id):
    user = Customers.query.get(id)
    
    if not user:
        return "User not found", 404
    
    # Count the number of requests for each status
    accepted_requests = Service_request.query.filter_by(service_status='accepted', customer_id=id).count()
    closed_requests = Service_request.query.filter_by(service_status='closed', customer_id=id).count()
    requested_requests = Service_request.query.filter_by(service_status='requested', customer_id=id).count()

    return render_template("user_chart.html", user=user, accept=accepted_requests, closed=closed_requests, request=requested_requests)

@app.route('/del_cus/<int:id>')
def del_cus(id):
    cus = Customers.query.get(id)
    us_in = Users_info.query.filter(Users_info.email_id == cus.email_id).first()
    db.session.delete(cus)
    db.session.delete(us_in)
    db.session.commit()
    requests = Service_request.query.filter_by(service_status='closed').all()
    return render_template("adminsearch.html", requests=requests, st="SR")

@app.route('/del_sp/<int:id>')
def del_sp(id):
    cus = Service_professionals.query.get(id)
    us_in = Users_info.query.filter(Users_info.email_id == cus.email_id).first()
    db.session.delete(cus)
    db.session.delete(us_in)
    db.session.commit()
    requests = Service_request.query.filter_by(service_status='closed').all()
    return render_template("adminsearch.html", requests=requests, st="SR")