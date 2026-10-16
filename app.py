from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from num2words import num2words
import os
import qrcode  
import io
import base64
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "padmanayaka_secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///padmanayaka_pro.db"
db = SQLAlchemy(app)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="PADMANAYAKA FARMER PRODUCER COMPANY LTD")
    address = db.Column(
        db.String(250), default="Main Road Gokunda Tq. Kinwat Dist. Nanded 431804"
    )
    gstin = db.Column(db.String(20), default="27AANCP3874B1Z8")
    mobile = db.Column(db.String(15), default="9422170515")
    bank_name = db.Column(db.String(100), default="Maharashtra Gramin Bank")
    acc_no = db.Column(db.String(30), default="80079048616")
    ifsc = db.Column(db.String(20), default="MAHG0004154")


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.Integer, unique=True)
    date = db.Column(db.String(20))
    due_date = db.Column(db.String(20))  
    bill_to = db.Column(db.Text)
    ship_to = db.Column(db.Text)

    buyer_gstin = db.Column(db.String(100))
    transporter_id_name = db.Column(db.String(100), default="SELF")
    trans_doc_no = db.Column(db.String(100))
    transport_mode = db.Column(db.String(100), default="Road")
    vehicle_no = db.Column(db.String(100))
    transport_from = db.Column(db.String(100), default="Nanded")
    cewb_no = db.Column(db.String(100), default="-")
    multi_veh_info = db.Column(db.String(50), default="-")
    portal_no = db.Column(db.String(100), default="1")
    approx_distance = db.Column(db.String(100), default="0 km")

    total_taxable = db.Column(db.Float)
    total_tax = db.Column(db.Float)
    grand_total = db.Column(db.Float)
    items = db.relationship(
        "InvoiceItem", backref="invoice", cascade="all, delete-orphan"
    )


class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoice.id"))
    name = db.Column(db.String(100))
    hsn = db.Column(db.String(20))
    weight = db.Column(db.String(20))
    qty = db.Column(db.Float)
    rate = db.Column(db.Float)
    amount = db.Column(db.Float)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Party(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gstin = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        hashed_pw = generate_password_hash("admin123", method="pbkdf2:sha256")
        admin_user = User(username="admin", password=hashed_pw)
        db.session.add(admin_user)
        db.session.commit()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user and check_password_hash(user.password, request.form.get("password")):
            login_user(user)
            return redirect(url_for("index"))
        flash("Invalid Username or Password", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old_pw = request.form.get("old_password")
        new_pw = request.form.get("new_password")

        if check_password_hash(current_user.password, old_pw):
            current_user.password = generate_password_hash(
                new_pw, method="pbkdf2:sha256"
            )
            db.session.commit()
            flash("Password changed successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash("Old password is incorrect", "danger")
    return render_template("change_password.html")



with app.app_context():
    db.create_all()
    if not Company.query.first():
        db.session.add(Company())
        db.session.commit()


def format_amount_to_words(amount):
    from num2words import num2words

    
    amount = round(float(amount), 2)

    rupees = int(amount)
    paise = int(round((amount - rupees) * 100))

 
    rupees_str = (
        num2words(rupees, lang="en_IN").replace(",", "").replace("-", " ").title()
    )

    if paise > 0:
        paise_str = (
            num2words(paise, lang="en_IN").replace(",", "").replace("-", " ").title()
        )
        return f"{rupees_str} Rupees and {paise_str} Paise Only"
    else:
        return f"{rupees_str} Rupees Only"



@app.route("/index")
def index():
    stats = {
        "total_bills": Invoice.query.count(),
        "recent": Invoice.query.order_by(Invoice.invoice_no.desc()).limit(3).all(),
    }
    return render_template("index.html", stats=stats)


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
  
        last_inv = Invoice.query.order_by(Invoice.invoice_no.desc()).first()
        new_no = (last_inv.invoice_no + 1) if last_inv else 61

        qtys = request.form.getlist("qty[]")
        rates = request.form.getlist("rate[]")
        taxable = sum(float(q) * float(r) for q, r in zip(qtys, rates) if q and r)

        inv = Invoice(
            invoice_no=new_no,
            date=request.form["date"],
            bill_to=request.form["bill_to"],
            ship_to=request.form["ship_to"],
            total_taxable=taxable,
            total_tax=taxable * 0.05,
            grand_total=taxable * 1.05,
        )

        names, hsns, weights = request.form.getlist('item_name[]'),request.form.getlist('hsn[]'),request.form.getlist('weight[]')
        for i in range(len(names)):
            if names[i]:
                print("QTY",repr(qtys[i]))
                item = InvoiceItem(
                    name=names[i],
                    hsn=hsns[i],
                    weight=weights[i],
                    qty=float(qtys[i]),
                    rate=float(rates[i]),
                    amount=float(qtys[i]) * float(rates[i])
                )
                inv.items.append(item)

        approx_dist = request.form.get("approx_distance")


        if approx_dist and "km" not in approx_dist.lower():
            approx_dist = f"{approx_dist}km"

        inv.approx_distance = approx_dist
        inv.buyer_gstin = request.form.get("buyer_gstin")
        inv.trans_doc_no = request.form.get("trans_doc_no")
        inv.vehicle_no = request.form.get("vehicle_no")
        inv.transporter_id_name = request.form.get("transporter_id_name")
        db.session.add(inv)
        db.session.commit()
        return redirect(url_for("view_invoice", inv_id=inv.id))

    parties = Party.query.order_by(Party.name).all()
    last_inv = Invoice.query.order_by(Invoice.invoice_no.desc()).first()
    next_no = (last_inv.invoice_no + 1) if last_inv else 61
    return render_template(
        "create.html",
        next_no=next_no,
        today=datetime.now().strftime("%Y-%m-%d"),
        parties=parties,
    )


@app.route("/add-party", methods=["POST"])
@login_required
def add_party():
    name = request.form.get("name")
    address = request.form.get("address")
    gstin = request.form.get("gstin")

    if Party.query.filter_by(name=name).first():
        return {"success": False, "message": "Party already exists"}, 400

    new_party = Party(name=name, address=address, gstin=gstin)
    db.session.add(new_party)
    db.session.commit()

    return {
        "success": True,
        "id": new_party.id,
        "name": new_party.name,
        "address": f"{new_party.name}\n{new_party.address}\nGSTIN: {new_party.gstin}",
    }


@app.route("/company", methods=["GET", "POST"])
def company_details():
 
    comp = Company.query.first()

    if request.method == "POST":
        if not comp:
            comp = Company()

     
        comp.name = request.form.get("name")
        comp.address = request.form.get("address")
        comp.gstin = request.form.get("gstin")


        comp.mobile = request.form.get("mobile")
        comp.bank_name = request.form.get("bank_name")
        comp.acc_no = request.form.get("acc_no")
        comp.ifsc = request.form.get("ifsc")

        db.session.add(comp)
        db.session.commit()
        return redirect(url_for("index"))  
    return render_template("company.html", comp=comp)


@app.route("/edit/<int:inv_id>", methods=["GET", "POST"])
def edit(inv_id):
    inv = Invoice.query.get_or_404(inv_id)
    if request.method == "POST":
       
        inv.date = request.form["date"]
        inv.due_date = request.form.get("due_date")
        inv.bill_to = request.form["bill_to"]
        inv.ship_to = request.form["ship_to"]
        InvoiceItem.query.filter_by(invoice_id=inv.id).delete()

        qtys = request.form.getlist("qty[]")
        rates = request.form.getlist("rate[]")
        
        qtys = request.form.getlist("qty[]")
        rates = request.form.getlist("rate[]")

        print("QTYS:", repr(qtys))
        print("RATES:", repr(rates))

        taxable = sum(float(q) * float(r) for q, r in zip(qtys, rates) if q and r)
        

        inv.total_taxable, inv.total_tax, inv.grand_total = (
            taxable,
            taxable * 0.05,
            taxable * 1.05,
        )

        names, hsns, weights = (
            request.form.getlist("item_name[]"),
            request.form.getlist("hsn[]"),
        )
        request.form.getlist("weight[]")
        for i in range(len(names)):
            if names[i]:
                item = InvoiceItem(
                    name=names[i],
                    hsn=hsns[i],
                    weight=weights[i],
                    qty=float(qtys[i]),
                    rate=float(rates[i]),
                    amount=float(qtys[i]) * float(rates[i]),
                )
                inv.items.append(item)
        db.session.commit()
        return redirect(url_for("view_invoice", inv_id=inv.id))
    return render_template(
        "create.html", inv=inv, next_no=inv.invoice_no, today=inv.date
    )


@app.route("/invoice/<int:inv_id>")
def view_invoice(inv_id):
    inv = Invoice.query.get_or_404(inv_id)
    comp = Company.query.first()

    words_formatted = format_amount_to_words(inv.grand_total)

    return render_template("invoice.html", inv=inv, comp=comp, words=words_formatted)


@app.route("/history")
@login_required
def history():
    bills = Invoice.query.order_by(Invoice.invoice_no.desc()).all()
    return render_template("history.html", bills=bills)


@app.route("/eway-bill/<int:inv_id>")
def eway_bill(inv_id):
    inv = Invoice.query.get_or_404(inv_id)
    comp = Company.query.first()
  
    now = datetime.now()
    generated_at = now.strftime("%d/%m/%Y %I:%M %p")

   
    valid_upto = (now + timedelta(days=2)).strftime("%d/%m/%Y")
    eway_no = f"2621 {4510 + inv.id} {3237 + inv.id}"

    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(f"EWBill:{eway_no}|GSTIN:{comp.gstin}|Amt:{inv.grand_total}")
    qr.make(fit=True)


    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf)
    qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template('eway_bill.html',
                       inv=inv,
                       comp=comp,
                       generated_at=generated_at,
                       valid_upto=valid_upto,
                       eway_no=f"2621 4510 {3237 + inv.id}",
                       qr_code=qr_base64) 


if __name__ == '__main__':
    app.run(debug=True)