from flask import render_template, redirect, url_for
from nura.forms import LoginForm
from nura.models import Sysuser

def index():
    return render_template('index.html')


def login():
    form = LoginForm(csrf_enabled=False)
    if form.is_submitted():
        u = Sysuser.query.filter_by(userName=form.username.data).first()
        if u is None:
            print('Invalid User Name')
            return redirect(url_for('login'))
        if u.check_password(form.password.data):
            print('Invalid Password')
            return redirect(url_for('login'))
        msg = "username={}, password={}, remember_me={}".format(
            form.username.data,
            form.password.data,
            form.remember_me.data
        )
        print(msg)
        return redirect(url_for('index'))
    return render_template('login.html', form = form)