from flask import render_template, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from nura.forms import LoginForm
from nura.models import Sysuser

# 这里加装饰器，就会要求用户要登陆才能访问这个页面
@login_required
def index():
    posts = [
        {
            'author': {'username': 'root'},
            'body': "hi I'm root!"
        },
        {
            'author': {'username': 'test'},
            'body': "hi I'm test!"
        },
        {
            'author': {'username': 'test1'},
            'body': "hi I'm test1!"            
        }      
    ]
    return render_template('index.html', posts=posts)


def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(csrf_enabled=False)
    if form.is_submitted():
        u = Sysuser.query.filter_by(userName=form.username.data).first()
        if u is None:
            print('Invalid User Name')
            return redirect(url_for('login'))
        if u.check_password(form.password.data) == False:
            print('Invalid Password')
            return redirect(url_for('login'))
        msg = "username={}, password={}, remember_me={}".format(
            form.username.data,
            form.password.data,
            form.remember_me.data
        )
        print(msg)
        login_user(u, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))
    return render_template('login.html', form = form)

def logout():
    logout_user()
    return redirect(url_for('login'))