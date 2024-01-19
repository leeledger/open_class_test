from flask import Flask, render_template, request,jsonify,redirect,url_for,session,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import logging
import os
import shutil
from flask_login import LoginManager,UserMixin, login_user, logout_user, login_required, current_user
import platform


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@192.168.0.225:3306/open_class'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = '12345'
app.config['UPLOAD_FOLDER'] = 'photos'  # Flask 서버의 photos 폴더

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    # GET 요청인 경우 (로그인 페이지에 처음 접근한 경우)
    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Enable SQL query logging 
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
if __name__ == '__main__':
    app.run('0.0.0.0', port=5050)

