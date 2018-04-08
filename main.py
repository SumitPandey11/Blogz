from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '1234567'


class Blog(db.Model) :
    
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(600))
    body = db.Column(db.String(6000))
    

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['GET'])
def index():
    return redirect("/blog")

@app.route('/blog', methods=['GET','POST'])
def blogs():
    
    blogs = Blog.query.all()

   # blogs = [["Blog 1","title 1"], ["Blog 2","title 2"]]
    
    
    return render_template("blog.html", blogs = blogs)


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

        new_blog = Blog(title, body)
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/blog')
    else:
        return render_template("new_post.html")


if __name__ == '__main__':
    app.run()