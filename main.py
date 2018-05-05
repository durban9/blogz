from flask import Flask, redirect, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config ['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(700))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)        
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref = 'owner')
    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['blog', 'index', 'signup', 'login']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/blog', methods = ['GET'])
def blog():
    user_id = request.args.get('user_id')
    blog_id = request.args.get('blog_id')
    
        
    if user_id:
        blog_entries = Blog.query.filter_by(owner_id=user_id).all()

        print()
        print(blog_entries)
        print()
        return render_template('user_entries.html', blogs=blog_entries)

    if blog_id:
        blog_entry = Blog.query.filter_by(id = blog_id).first()       
        print()
        print(blog_entry)
        print()
        return render_template('single_entry.html', blog = blog_entry)

    blogs = Blog.query.all()
    return render_template('blogs.html', title="Blogz", blogs=blogs)
    

@app.route('/newpost', methods = ['POST', 'GET'])
def add_new_post():
   
    if request.method == 'POST':
        error_message = ''
        title = request.form['title']
        body = request.form['blog']
        user_id = session['username']
         
        if title == '' or body == '':
            
            error_message = "Neither text field may be left blank. Please enter a title for your blog."
            return render_template('newpost.html', title= "Blogs", error_message=error_message)
        
        elif body == '':
            
            error_message = "Body of Blog may not be left blank. Please enter a statement for the body of your blog."        
        
        else: 
            
            blog_title = request.form['title']
            blog = request.form['blog']
            owner_id = User.query.filter_by(username=user_id).first()
            blog_and_title = Blog(blog_title, blog, owner_id)
            db.session.add(blog_and_title)
            db.session.commit()
            return redirect('/')
    return render_template('newpost.html', title="Blogs")


@app.route('/login', methods =['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        correct_username = User.query.filter_by(username=username).first()
        correct_password = User.query.filter_by(password = password).first()
        error_message = ''
        if not correct_username: 
            error_message = 'Please loging using a registered username or click the "Create Account" link to create an account.'
            return render_template('/login.html', error_message = error_message)

        if not correct_password:
            error_message = 'Please login using a registered password.'
            return render_template('/login.html', error_message = error_message)  
         
        
        else:
            if correct_username and correct_password:
                session['username']=username
                
                return redirect('/newpost')
    return render_template ('login.html')


@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verification = request.form['verification']
        error_message = ''

        if username == '':
            error_message = 'Username field cannot be left blank. Please enter a valid username.'
            return render_template('signup.html', error_message = error_message)
        if password == '':
            error_message = 'Password field cannot be left blank. Please enter a valid password.'
            return render_template('signup.html', error_message = error_message)
        if verification == '':
            error_message = 'Verification field cannot be left blank. Please enter a proper verification.'
            return render_template('signup.html', error_message = error_message)
        if len(password) < 3:
            error_message = 'Please enter a password that is greater than three characters long.'
            password = ''
            return render_template('signup.html', error_message = error_message)

        if len(username) < 3:
            error_message = 'Please enter a username that is greater than three characters long.'
            username = ''
            return render_template('signup.html', error_message = error_message)
        if verification != password:
            error_message = "Your password verification entry and password do not match. Please re-enter your password and verification."
            password = ''
            verification = ''    
            return render_template('signup.html', error_message = error_message)
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
            return redirect('/newpost')
    return render_template('signup.html')            

        
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')



        

if __name__ == '__main__':
  app.run()
