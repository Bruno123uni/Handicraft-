import os
import random
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session,url_for, send_file
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
from datetime import datetime
from base64 import b64encode
import base64
from io import BytesIO #Converts data from Database into bytes


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")



Session(app)
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///main.db")


@app.route('/')
def index():
  return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
  session.clear()
  if request.method == "POST":
        # Ensure username was submitted
      if not request.form.get("name"):
            return apology("must provide name", 403)

        # Ensure password was submitted
      elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for usernam
      rows = db.execute("SELECT * FROM users WHERE name = :name",name=request.form.get("name"))
      print(len(rows))
      if len(rows) == 0:
        print("00000000")
        role = "Artisan"
        rows = db.execute("SELECT * FROM artisians WHERE name = :name",name=request.form.get("name"))
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid name and/or password", 403)
        session["user_id"] = rows[0]["id"]
      else:
        print('aa')
        rows = db.execute("SELECT * FROM users WHERE name = :name",name=request.form.get("name"))

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
          return apology("invalid name and/or password", 403)
        role = "Customer"
        session["user_id"] = rows[0]["id"]
      session["role"] = role
      return render_template("index.html",role=role,login=login)

  else:
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("name"):
            return apology("must provide name", 403)
        role = request.form.get("Role")
        if role == "Customer":
            rows = db.execute("SELECT name FROM users")
            for row in rows:
                if request.form.get("name") == row["name"]:
                    return apology("This name is already taken", 403)
        if role == "Artisan":
            rows = db.execute("SELECT name FROM artisians")
            for row in rows:
                if request.form.get("name") == row["name"]:
                    return apology("This name is already taken", 403)
        if not request.form.get("Email"):
            return apology("must provide Email", 403)# Ensure inputs was submitted
        if not request.form.get("password"):
            return apology("must provide password", 403)
        if not request.form.get("confirmation"):
            return apology("must provide input", 403)
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("The passwords must match", 403)
        if not request.form.get("State"):
             return apology("must select state", 403)
        name = request.form.get("name")
        Email = request.form.get("Email")
        State = request.form.get("State")
        password = generate_password_hash(request.form.get("password"))
        if role == "Customer":
            db.execute("INSERT INTO users (name, password,Email,State) VALUES (:username, :passw,:e,:s)", username=name, passw=password,e=Email,s=State)
            return redirect("/login")
        else:
            db.execute("INSERT INTO artisians(name,password,Email,State,Storename,Storedes,Img,Type) VALUES(:username, :passw,:e,:s,'','','','')", username=name, passw=password,e=Email,s=State)
            rows = db.execute("SELECT * FROM artisians WHERE name = :name",name=name)
            session["user_id"] = rows[0]["id"]
            session['name'] = name
            return redirect("/regart")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
@app.route("/regart", methods=["GET", "POST"])
def regart():
    name = session["name"]
    if request.method == "GET":
        return render_template("regart.html")
    else:
        if not request.form.get("Storename"):
            return apology("must provide storename", 403)
        if not request.form.get("Description"):
            return apology("must provide description", 403)
        if not request.form.get("Type"):
            return apology("must provide type of handicraft", 403)
        Store = request.form.get("Storename")
        Type = request.form.get("Type")
        Des = request.form.get("Description")
        file = request.form.get("Img")
        add = request.form.get("Address")
        ph = request.form.get("Ph")
        rows = db.execute("SELECT * FROM artisians WHERE name = :name",name=name)
        session["user_id"] = rows[0]["id"]
        db.execute("UPDATE artisians SET Storename =:Store WHERE id = :iod",Store=Store, iod=session["user_id"])
        db.execute("UPDATE artisians SET Storedes = :Des WHERE id = :iod",Des=Des, iod=session["user_id"])
        db.execute("UPDATE artisians SET Img = :Storeimg WHERE id = :iod",Storeimg=file, iod=session["user_id"])
        db.execute("UPDATE artisians SET Type = :Type WHERE id =:iod",Type=Type, iod=session["user_id"])
        db.execute("UPDATE artisians SET PhoneNo = :Type WHERE id =:iod",Type=ph, iod=session["user_id"])
        db.execute("UPDATE artisians SET Address = :Type WHERE id =:iod",Type=add, iod=session["user_id"])
        Img1 = request.form.get("Upload1")
        price1 = request.form.get("Priceofproduct1")
        name1 = request.form.get('NameofProduct1')
        Img2 = request.form.get("Upload2")
        price2 = request.form.get("Priceofproduct2")
        name2= request.form.get('NameofProduct2')
        Img3 = request.form.get("Upload3")
        price3 = request.form.get("Priceofproduct3")
        name3= request.form.get('NameofProduct3')
        Img4 = request.form.get("Upload4")
        price4 = request.form.get("Priceofproduct4")
        name4= request.form.get('NameofProduct4')
        Img5 = request.form.get("Upload5")
        price5 = request.form.get("Priceofproduct5")
        name5= request.form.get('NameofProduct5')
        db.execute("INSERT INTO products(Image,Name,Price,Id) VALUES(:i,:n,:p,:aid)", i=Img1,n=name1,p=price1,aid=session["user_id"])
        db.execute("INSERT INTO products(Image,Name,Price,Id) VALUES(:i,:n,:p,:aid)", i=Img2,n=name2,p=price2,aid=session["user_id"])
        db.execute("INSERT INTO products(Image,Name,Price,Id) VALUES(:i,:n,:p,:aid)", i=Img3,n=name3,p=price3,aid=session["user_id"])
        db.execute("INSERT INTO products(Image,Name,Price,Id) VALUES(:i,:n,:p,:aid)", i=Img4,n=name4,p=price4,aid=session["user_id"])
        db.execute("INSERT INTO products(Image,Name,Price,Id) VALUES(:i,:n,:p,:aid)", i=Img5,n=name5,p=price5,aid=session["user_id"])
        return redirect("/login")

@app.route("/Stories", methods=["GET"])
def stories():
    if request.method == "GET":
        return render_template("stories.html")
@app.route("/search",methods=["GET","POST"])
def search():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM artisians")
        return render_template("Artisanssearch.html",rows=rows)
    else:
        rows = db.execute("SELECT * FROM artisians")
        if request.form.get("Type of Handicraft") and not request.form.get("State"):
            Type=request.form.get("Type of Handicraft")
            rows = db.execute("SELECT * FROM artisians WHERE Type=:t",t=Type)
        if request.form.get("State") and not request.form.get("Type of Handicraft"):
            State=request.form.get("State")
            rows = db.execute("SELECT * FROM artisians WHERE State=:s",s=State)
        if request.form.get("State") and  request.form.get("Type of Handicraft"):
            State=request.form.get("State")
            Type=request.form.get("Type of Handicraft")
            rows = db.execute("SELECT * FROM artisians WHERE State=:s AND Type=:t",s=State,t=Type)
        return render_template("Artisanssearch.html",rows=rows)
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
@app.route("/eprofile",methods=["GET","POST"])
def eprofile():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM artisians WHERE id = :i",i = session["user_id"])
        return render_template("editprofie.html",rows=rows)
@app.route("/profile",methods=["POST"])
def profile():
    session['a'] = request.form.get("store")
    print(request.form.get("store"))
    return redirect("/r")
@app.route("/r",methods=["GET","POST"])
def r():
    a = session['a']
    if request.method == "GET":
        rows = db.execute("SELECT * FROM artisians WHERE Storename = :i",i = a)
        aid = rows[0]["id"]
        Name = rows[0]["Storename"]
        Img = rows[0]["Img"]
        Add = rows[0]["Address"]
        p = rows[0]["PhoneNo"]
        e= rows[0]["Email"]
        print(aid)
        rows1 = db.execute("SELECT * FROM products WHERE id = :a",a = aid)
        return render_template("er.html",n=Name,I=Img,a=Add,p=p,rows1=rows1,e=e)