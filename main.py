from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:pwd@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '1234567'


class Blog(db.Model) :
    
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(600))
    body = db.Column(db.String(6000))
    user_id = db.Column(db.Integer , db.ForeignKey('user.id'))

    def __init__(self, title, body , user):
        self.title = title
        self.body = body
        self.user = user

class User(db.Model) :
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))
    blog = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template("index.html", users = users)

@app.route('/blog', methods=['GET','POST'])
def blogs():
    
    if request.method == 'GET':
        user_id = request.args.get('user')
        if user_id != None:
            blogs = Blog.query.filter_by(user_id = user_id).all()    
            return render_template('singleUser.html', blogs=blogs)

    individual_blog_page = False
    id = request.args.get('id')
    

    if id == None :
        blogs = Blog.query.order_by(Blog.id.desc()).all()



    else:
        blogs = Blog.query.filter_by(id = id).all()
        individual_blog_page = True
        
        
    
    
    return render_template("blog.html", blogs = blogs, individual_blog_page = individual_blog_page)


@app.route('/newpost', methods=['GET','POST'])
def newpost():
    if request.method == 'POST':
        title = request.form['title'].strip() 
        body = request.form['body'].strip() 
        
        error = False
        title_error = ""
        body_error = ""

        if title == "":
            title_error = "Please fill in the title"
            error = True
        if body == "":
            body_error = "Please fill in the body"
            error = True
        if error :
            return render_template("new_post.html", title = title, title_error = title_error, body = body, body_error = body_error)

        
        # Only logged in user submit the new post, so while login the username is already set to the session.
        # get the 'username' from session 
        
        owner = User.query.filter_by(username=session['username']).first()
        
        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/blog?id='+str(new_blog.id))
    else:
        return render_template("new_post.html")

@app.route('/login',methods=['POST','GET'])
def login():

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['user_password'].strip()
        
        error_message = ""
        
        if username != "" and password != "":
            user = User.query.filter_by(username = username).first()
            
            if not user :
                error_message = 'Username does not exist'
                return render_template('login.html',error_message = error_message)

            elif user and user.password == password :
                session['username'] = username
                return redirect('/newpost')
            
            elif user and user.password != password:
                error_message = 'Password is incorrect'
                return render_template('login.html',error_message = error_message)
            
        else:
            error_message = "Username and Password is mandetory, it can't be blank"
            return render_template('login.html',error_message = error_message)
    else :
        return render_template("login.html")


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        
        username = request.form['username'].strip()
        password = request.form['user_password'].strip()
        verify_password = request.form['verify_password'].strip()

        error_message = ""

        if username != "" and password != "" and verify_password != "":
            
            # User enters different strings into the password and verify fields and gets an error message 
            # that the passwords do not match.
            if password != verify_password :
                error_message = "Password do not match"
                return render_template('signup.html',error_message=error_message)
            
            # User enters a password or username less than 3 characters long 
            # and gets either an invalid username or an invalid password message.
            if  len(username) < 3 or len(password) < 3 :
                error_message = "Usename , Password should be at least 3 chatecter long"
                return render_template('signup.html',error_message=error_message)

            user = User.query.filter_by(username=username).first()

            #User enters a username that already exists and gets an error message that username already exists then rediret to signup page
            #Else create user and redirected to the '/newpost' page with their username being stored in a session

            if user and user.username == username:
                error_message = "User already exists"
                return render_template('signup.html',error_message=error_message)
            else:
                user = User(username,password)
                db.session.add(user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
        else:
            #User leaves any of the username, password, or verify fields blank and gets an error message.
            error_message = "Username, password  and verify password is mandetory, it can't be blank"
            return render_template('signup.html',error_message=error_message)


    else:
        return render_template("signup.html")    

@app.route('/logout',methods=['GET'])
def logout():
    del session['username']
    return redirect('/blog')

@app.before_request
def require_login():
    allowed_routes = ['login','signup','blogs','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

if __name__ == '__main__':
    app.run()