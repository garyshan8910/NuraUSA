from operator import inv
from tokenize import String
from flask import jsonify, render_template, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from nura.forms import LoginForm, RegisterForm, SoForm
from nura.models import AssistUser, So, Po
from nura import db
from nura.sopomapSQL import *

# 这里加装饰器，就会要求用户要登陆才能访问这个页面


@login_required
def index():
    return render_template('index.html')


def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(csrf_enabled=False)
    if form.is_submitted():
        u = AssistUser.query.filter_by(username=form.username.data).first()
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
    return render_template('login.html', form=form)


def logout():
    logout_user()
    return redirect(url_for('login'))


def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = AssistUser(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.active = 1
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Registration', form=form)


@login_required
def so_po_mapping():
    # header = ['soNum', 'partNum', 'qtyOrdered', 'partId']
    # result = db.engine.execute(sql_so())
    # print(result.fetchall())
    return render_template('sopomapping.html')


@login_required
def so_details():
    so_form = SoForm(request.form)
    if request.method == "POST":
        so_form.validate_on_submit()
        # print(so_form.__dict__)
        # print(request.method)
        so_details = So.query.filter(So.num.contains(so_form.num.data)).all()
    else:
        so_details = So.query.all()
    return render_template('sodetails.html', so_details=so_details, so_form=so_form)


@ login_required
def po_details():
    po_details = Po.query
    return render_template('podetails.html', po_details=po_details)


@login_required
def test():
    return render_template('dynamic_table.html')


def columnFilter(sql_rows, columns):
    '''
    sql_rows = db.engine.execute(sql).fetchall()
    columns = ["",]
    '''
    column_set = set(columns)
    ret = []
    for row in sql_rows:
        obj = dict(row)
        tmp_obj = dict()
        for k in obj:
            if k in column_set:
                tmp_obj[k] = obj[k]
        ret.append(tmp_obj)
    return ret


@login_required
def get_po_items():
    partId = request.args.get('partId', 0, type=int)
    inventory = db.engine.execute(sql_inventory(partId)).fetchall()
    inventory = columnFilter(
        inventory, ["qtyOnHand", "qtyAllocated", "qtyOnOrder", "extra"])
    poItems = db.engine.execute(sql_po_items(partId)).fetchall()
    poItems = [dict(row) for row in poItems]
    return jsonify(poItems=poItems, inventory=inventory)


@login_required
def get_so_items():
    soItems = db.engine.execute(sql_so_items()).fetchall()
    soItems = [dict(row) for row in soItems]
    return jsonify(soItems=soItems)


@login_required
def create_soitem_poitem_map_record(so_item_id, po_item_id, allocate_type, allocate_num):
    pass
