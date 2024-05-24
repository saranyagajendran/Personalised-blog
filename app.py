from flask import Flask, render_template, request,session,flash
from flask_pymongo import PyMongo,MongoClient
import os
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key="Meghana123"
app.config["MONGO_URI"] = "mongodb://localhost:27017/sample"
mongo =PyMongo(app)
from dotenv import load_dotenv


def config():
    load_dotenv()


app.config["MONGO_URI"] = os.getenv('mongo_url')
client=MongoClient(os.getenv('mongo_url'))
db=client['Blog']

@app.route('/',methods=["GET","POST"])
def home():
    
   if request.method=='POST':
        existing_user = db.user.find_one({'name': request.form['name']})
        if existing_user is None:
            name=request.form['name']
            phone_no=request.form['phone']
            email=request.form['email']
            hash_pass = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
            query={'name':name}
            doc ={'$set':{'email':email,'name':name,"phone_no":phone_no,"password":hash_pass}}
            db.user.update_one(query,doc,upsert=True)
            # mongo.db.user.insert_one({"name":name,"phone_no":phone_no,"email":email,"password":hash_pass})
            return render_template('home.html')
        else:
            return 'User already exists!'
   else:
            return render_template('home.html')

@app.route('/register')
def register():
   
    return render_template('register.html')

@app.route('/login')
def login():
        return render_template('login.html')
        

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if request.method=="POST":
        user = db.user
        login_email = user.find_one({'email' : request.form['email']})
        
        # email = user.find_one({'name' : name})
        # session["email"]=email['email']
        # session['email']=login_email
        # print(login_email)
        if login_email:
            if check_password_hash(login_email['password'], request.form['password']):
                session['email']=request.form['email']
                name=login_email['name']
                session["uname"]=name
                return render_template('dashboard.html',name=name)
            else:
                return "Invalid username/password combination"
        else:
            return 'Username not found.Please Register'
    else:
        if "uname"in session:
            name=session["uname"]
            return render_template("dashboard.html", name= name) 


   


@app.route('/launch',methods=['GET','POST'])
def launchblog():
    if request.method=='POST':
        name=session["uname"]
        email=session["email"]
        title = request.form.get('title')
        content = request.form.get('content')
        data = {'label': title, 'content': content}
        query={'email':email}
        doc ={'$push':{'blog':data}}
        db.user.update_one(query,doc,upsert=True)
    return render_template('dashboard.html',name=name)


@app.route('/about',methods=['GET','POST'])
def about():
    return render_template('about.html')

@app.route('/blog',methods=['GET','POST'])
def blog():
    return render_template('blog.html')

@app.route('/viewblog',methods=['GET','POST'])
def viewblog():
    user=db.user.find_one({'email':session["email"]})
    result = db.user.find_one({'email':session["email"], 'blog': {'$exists': True}})
    if result:
        blog=user['blog']
        return render_template('viewblog.html',blogs=blog)
    else:
        flash("No blogs yet")
        return render_template("dashboard.html",name=session['uname'])

if __name__ == '__main__':
    app.run(debug=True) 