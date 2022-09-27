from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://todoappadmin:password123@localhost/todo"
# use `heroku config --app <appname>` to get postgres url for heroku 
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://gkbtrwkruhxyod:4ff4bc30450ce96e838024b7f446d610ca28b365ffce90ba7c6acb6811153629@ec2-54-91-223-99.compute-1.amazonaws.com:5432/dfvtngfjg4e13r"
app.config['SECRET_KEY'] = 'shhhhhhhhhhh'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Mapping User Class Object to User Table(Relation)
class User(db.Model):
	uid = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), unique=True, nullable=False)
	password = db.Column(db.String(24), nullable=False)

	tasks = db.relationship('ToDo', backref='user')

	def __init__(self, username, password):
		self.username = username
		self.password = password

class ToDo(db.Model):
	tid = db.Column(db.Integer, primary_key=True)
	task_title = db.Column(db.String(100))
	task_desc = db.Column(db.String(240))
	user_id = db.Column(db.Integer, db.ForeignKey('user.uid'))

	def __init__(self, task_title, task_desc, user_id ):
		self.task_title = task_title
		self.task_desc = task_desc
		self.user_id = user_id

	def __repr__(self) -> str:
		return f"{self.tid} - {self.task_title}"

@app.route('/')
def website():
	return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register( ):
	if request.method=='POST':
		username = request.form['username']
		password = request.form['password']
		cpassword = request.form['confirmpassword']
		checkusername = User.query.filter_by(username=username).first()
		checkusernameflag = True
		checkpasswordflag = True
		if(checkusername is not None): #username already present
			checkusernameflag = False
			flash("username already present!")
		if(password != cpassword):
			checkpasswordflag = False
			flash("passwords did not match!")
		if(checkusernameflag and checkpasswordflag):
			user = User(username=username, password=password)
			db.session.add(user)
			db.session.commit()
			session["name"] = request.form["username"]
			return redirect(url_for("tasks"))	
	return render_template('register.html')
	

@app.route('/login',methods=['GET', 'POST'])
def login():
	if request.method=='POST':
		uname = request.form["username"]
		passw = request.form["password"]
		login = User.query.filter_by(username=uname, password=passw).first()
		if login is not None:
			print(login)
			print('login successful')
			session["name"] = uname  # uname= request.form["username"] same as request.form.get("username")
			return redirect(url_for("tasks"))
		else:
			flash("incorrect username or password!")	
	return render_template('login.html')

@app.route('/tasks',methods=['GET','POST'])
def tasks():
	uname = session.get("name")
	print(uname)
	if not uname:
		return redirect(url_for("login"))
	if request.method=='POST':
		title = request.form['title']
		desc = request.form['desc']
		print(uname)
		user = db.session.query(User).filter(User.username==uname).first()
		todo = ToDo(task_title=title, task_desc=desc, user_id=user.uid)
		db.session.add(todo)
		db.session.commit()
	current_user = db.session.query(User).filter(User.username==uname).first()
	allTodo = db.session.query(ToDo).filter(ToDo.user_id==current_user.uid).all() 
	#print(allTodo)
	return render_template('tasks.html', allTodo=allTodo)	#passing variables from python to jinja template variable

	if request.method=='GET':
		current_user = db.session.query(User).filter(User.username==uname).first()
		allTodo = db.session.query(ToDo).filter(ToDo.user_id==current_user.uid).all()
		#print(allTodo)
		return render_template("tasks.html", allTodo=allTodo) #allTodo is the variable for jinja

@app.route("/update/<int:tid>", methods=['GET','POST'])
def update(tid):
	if request.method == 'POST':
		new_title =request.form['title']
		new_desc = request.form['desc']
		oldtodo = ToDo.query.filter_by(tid=tid).first() #Select Old Task by its id
		oldtodo.task_title = new_title #Replace Old Task title by new title
		oldtodo.task_desc = new_desc
		db.session.add(oldtodo)
		db.session.commit()
		return redirect(url_for("tasks"))

	#for GET request, show older task title and description
	oldtodo = ToDo.query.filter_by(tid=tid).first()
	return render_template('update.html', todo=oldtodo) #todo is the variable for jinja

@app.route('/delete/<int:tid>')
def delete(tid):
	todo = ToDo.query.filter_by(tid=tid).first()
	db.session.delete(todo)
	db.session.commit()
	return redirect(url_for("tasks"))

@app.route("/logout")
def logout():
	session["name"] = None #remove data of current user from session(cookies)
	session.clear()
	return redirect("/")

if __name__ == "__main__":
	app.run(debug=True, port=8000)