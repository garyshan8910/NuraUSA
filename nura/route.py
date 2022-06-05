from flask import jsonify, render_template, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from nura.forms import LoginForm, RegisterForm, SoForm
from nura.models import AssistUser, NuraSoitemPoitemMap, So, Po
from nura import db
from nura.query import query_result_all, query_result_by_page
from nura.sopomapSQL import *
from datetime import datetime

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


@login_required
def so():
    return render_template('so.html')


@login_required
def so_items():
    return render_template('soitems.html')


def get_tables_by_page(sql):
    page_num = request.args.get('page_num', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    total, curr_page, rows = query_result_by_page(sql, limit, page_num)
    return jsonify(data=rows, total=total, curr_page=curr_page)

def get_tables_all(sql):
    rows = query_result_all(sql)
    return jsonify(data=rows)

@login_required
def get_po_items():
    partId = request.args.get('partId', 0, type=int)
    sql = sql_po_items(partId)
    return get_tables_by_page(sql)


@login_required
def get_inventory():
    partId = request.args.get('partId', 0, type=int)
    sql = sql_inventory(partId)
    return get_tables_by_page(sql)


@login_required
def get_so_items():
    sql = sql_so_items()
    return get_tables_by_page(sql)


@login_required
def create_soitem_poitem_map_record():
    '''
    if so_item_id + po_item_id
    '''
    so_item_id = request.form.get('so_item_id', 0, type=int)
    po_item_id = request.form.get('po_item_id', None, type=int)
    allocate_type_id = request.form.get('allocate_type_id', 0, type=int)
    qty = request.form.get('qty', 0, type=float)
    obj = NuraSoitemPoitemMap(soitemid=so_item_id, poitemid=po_item_id,
                              qty=qty, userid=current_user.get_id(), allocateTypeId=allocate_type_id)
    db.session.add(obj)
    db.session.commit()
    return jsonify(success=True)


@login_required
def get_soitem_poitem_map():
    so_id = request.args.get('so_id', 0, type=int)
    allocate_type_id = request.args.get('allocate_type_id', 0, type=int)
    sql = sql_soitem_poitem_map(so_id, allocate_type_id)
    return get_tables_by_page(sql)


@login_required
def get_so():
    sql = sql_so()
    return get_tables_by_page(sql)

@login_required
def get_soitem_map():
    so_itemid = request.args.get('so_itemid', 0, type=int)
    sql = sql_soitem_map(so_itemid)
    return get_tables_all(sql)
