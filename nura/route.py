from email import message
from sre_constants import SUCCESS
from flask import jsonify, render_template, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from inflect import CONSONANTS
from sqlalchemy import true
from nura.forms import LoginForm, RegisterForm, SoForm
from nura.models import AssistUser, NuraPoItemInfo, NuraPoItemInfoDetail, NuraSoitemPoitemMap, NuraSoitemPoitemMapCategory, NuraSoitemPoitemMapDetail, NuraSoitemPoitemMapStatu, So, Po, to_dict
from nura import db
from nura.query import SQL_STMT, query_result_all, query_result_by_page
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
def so():
    return render_template('so.html')


@login_required
def so_items():
    return render_template('soitems.html')


@login_required
def po_items():
    return render_template('poitems.html')


@login_required
def po_item_info():
    return render_template('poiteminfo.html')


@login_required
def soitem_poitem_map_info():
    return render_template('soitem_poitem_map_info.html')


def get_tables_by_page(sql, params={}):
    page_num = request.args.get('page_num', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    total, curr_page, rows = query_result_by_page(sql, limit, page_num, params)
    return jsonify(data=rows, total=total, curr_page=curr_page)


def get_tables_all(sql):
    rows = query_result_all(sql)
    return jsonify(data=rows)


@login_required
def get_po_items():
    sql_stmt_obj = SQL_STMT(poitem_base_sql,
                            poitem_order_by,
                            request.args,
                            poitem_clause_dict,
                            request.args.get("limit", 10, type=int),
                            request.args.get("page_num", 1, type=int),
                            poitem_wildcard_fields,
                            poitem_required_args)
    total, curr_page, rows = sql_stmt_obj.query_by_page()
    return jsonify(data=rows, total=total, curr_page=curr_page)


@login_required
def get_inventory():
    sql_stmt_obj = SQL_STMT(inventory_base_sql,
                            inventory_order_by,
                            request.args,
                            inventory_clause_dict,
                            request.args.get("limit", 10, type=int),
                            request.args.get("page_num", 1, type=int),
                            inventory_wildcard_fields,
                            inventory_required_args)
    total, curr_page, rows = sql_stmt_obj.query_by_page()
    return jsonify(data=rows, total=total, curr_page=curr_page)


@login_required
def get_so_items():
    sql_stmt_obj = SQL_STMT(soitem_base_sql,
                            soitem_order_by,
                            request.args,
                            soitem_clause_dict,
                            request.args.get("limit", 10, type=int),
                            request.args.get("page_num", 1, type=int),
                            soitem_wildcard_fields,
                            soitem_required_args)
    total, curr_page, rows = sql_stmt_obj.query_by_page()
    return jsonify(data=rows, total=total, curr_page=curr_page)


@login_required
def create_soitem_poitem_map_record():
    '''
    if so_item_id + po_item_id
    '''
    so_item_id = request.form.get('so_item_id', 0, type=int)
    po_item_id = request.form.get('po_item_id', None, type=int)
    allocate_type_id = request.form.get('allocate_type_id', 0, type=int)
    qty = request.form.get('qty', 0, type=float)
    obj = NuraSoitemPoitemMap(soitemid=so_item_id,
                              poitemid=po_item_id,
                              qty=qty,
                              userid=current_user.get_id(),
                              allocateTypeId=allocate_type_id)
    db.session.add(obj)
    db.session.commit()
    return jsonify(data=to_dict(NuraSoitemPoitemMap, obj), success=True, message="create mapping success")


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
    sql_stmt_obj = SQL_STMT(soitemmap_base_sql,
                            soitemmap_order_by,
                            request.args,
                            soitemmap_clause_dict,
                            request.args.get("limit", 10, type=int),
                            request.args.get("page_num", 1, type=int),
                            soitemmap_wildcard_fields,
                            soitemmap_required_args)
    total, curr_page, rows = sql_stmt_obj.query_all()
    return jsonify(data=rows, total=total, curr_page=curr_page)


@login_required
def get_poitem_info():
    sql_stmt_obj = SQL_STMT(poiteminfo_base_sql,
                            poiteminfo_order_by,
                            request.args,
                            poiteminfo_clause_dict,
                            request.args.get("limit", 10, type=int),
                            request.args.get("page_num", 1, type=int),
                            poiteminfo_wildcard_fields,
                            poiteminfo_required_args)
    total, curr_page, rows = sql_stmt_obj.query_by_page()
    return jsonify(data=rows, total=total, curr_page=curr_page)


@login_required
def update_poitem_info():
    print(request.form)
    obj = NuraPoItemInfo(**request.form)
    if not obj.id and NuraPoItemInfo.query.filter(
            NuraPoItemInfo.poitemid == obj.poitemid).first() == None:
        obj.id = None
        db.session.add(obj)
    else:
        the_obj = NuraPoItemInfo.query.filter(
            NuraPoItemInfo.poitemid == obj.poitemid).first()
        if the_obj:
            for c in NuraPoItemInfo.__table__.columns:
                if getattr(obj, c.name):
                    setattr(the_obj, c.name, getattr(obj, c.name))
        obj = the_obj
    db.session.commit()
    return jsonify(data=to_dict(NuraPoItemInfo, obj), success=True, message="success")


@login_required
def get_po_item_info_details():
    sql_stmt_obj = SQL_STMT(poiteminfo_detail_base_sql,
                            poiteminfo_detail_order_by,
                            request.args,
                            poiteminfo_detail_clause_dict,
                            request.args.get("limit", 10, type=int),
                            request.args.get("page_num", 1, type=int),
                            poiteminfo_detail_wildcard_fields,
                            poiteminfo_detail_required_args)
    total, curr_page, rows = sql_stmt_obj.query_by_page()
    return jsonify(data=rows, total=total, curr_page=curr_page)


@login_required
def add_poiteminfo_detail():
    request_form = dict(request.form)
    print(request_form)
    request_form["userid"] = current_user.get_id()
    poitemid = request_form.pop("poitemid")
    poiteminfoid = request_form["poiteminfoid"]
    print(request_form)
    if not poiteminfoid or not db.session.query(NuraPoItemInfo.query.filter(NuraPoItemInfo.id == poiteminfoid).exists()).scalar():
        if not db.session.query(NuraPoItemInfo.query.filter(NuraPoItemInfo.poitemid == poitemid).exists()).scalar():
            poiteminfo_obj = NuraPoItemInfo(**{"poitemid": poitemid})
            db.session.add(poiteminfo_obj)
            # 获取插入poiteminfo_obj后的ID
            db.session.flush()
            request_form["poiteminfoid"] = poiteminfo_obj.id
        else:
            poiteminfo_obj = NuraPoItemInfo.query.filter(NuraPoItemInfo.poitemid == poitemid).first()
            request_form["poiteminfoid"] = poiteminfo_obj.id
    obj = NuraPoItemInfoDetail(**request_form)
    db.session.add(obj)
    db.session.commit()
    return jsonify(data=to_dict(NuraPoItemInfoDetail, obj), success=True, message="success")


@login_required
def get_soitem_poitem_map_info():
    sql_stmt_obj = SQL_STMT(soitem_poitem_map_base_sql,
                            soitem_poitem_map_order_by,
                            request.args,
                            soitem_poitem_map_clause_dict,
                            request.args.get("limit", 10, type=int),
                            request.args.get("page_num", 1, type=int),
                            soitem_poitem_map_wildcard_fields,
                            soitem_poitem_map_required_args)
    total, curr_page, rows = sql_stmt_obj.query_by_page()
    return jsonify(data=rows, total=total, curr_page=curr_page)


@login_required
def get_soitem_poitem_map_details():
    sql_stmt_obj = SQL_STMT(soitem_poitem_map_detail_base_sql,
                            soitem_poitem_map_detail_order_by,
                            request.args,
                            soitem_poitem_map_detail_clause_dict,
                            request.args.get("limit", 10, type=int),
                            request.args.get("page_num", 1, type=int),
                            soitem_poitem_map_detail_wildcard_fields,
                            soitem_poitem_map_detail_required_args)
    # print(sql_stmt_obj.__dict__)
    total, curr_page, rows = sql_stmt_obj.query_by_page()
    return jsonify(data=rows, total=total, curr_page=curr_page)


@login_required
def add_soitem_poitem_map_detail():
    request_form = dict(request.form)
    print(request_form)
    request_form["userid"] = current_user.get_id()
    mapid = request_form["mapid"]
    print(request_form)
    if not mapid or not db.session.query(NuraSoitemPoitemMap.query.filter(NuraSoitemPoitemMap.id == mapid).exists()).scalar():
        return jsonify(data={}, success=False, message="mapid is not provided")
    obj = NuraSoitemPoitemMapDetail(**request_form)
    db.session.add(obj)
    db.session.commit()
    return jsonify(data=to_dict(NuraSoitemPoitemMapDetail, obj), success=True, message="success")


@login_required
def update_soitem_poitem_map():
    print(request.form)
    obj = NuraSoitemPoitemMap(**request.form)
    if not obj.id or NuraSoitemPoitemMap.query.filter(NuraSoitemPoitemMap.id == obj.id).first() == None:
        return jsonify(data={}, success=False, message=f"map entry id is not found in DB, id={obj.id}")
    else:
        the_obj = NuraSoitemPoitemMap.query.filter(
            NuraSoitemPoitemMap.id == obj.id).first()
        if the_obj:
            for c in NuraSoitemPoitemMap.__table__.columns:
                if getattr(obj, c.name):
                    setattr(the_obj, c.name, getattr(obj, c.name))
        obj = the_obj
        db.session.commit()
        sql_stmt_obj = SQL_STMT(soitem_poitem_map_base_sql,
                                soitem_poitem_map_order_by,
                                {'id': obj.id},
                                soitem_poitem_map_clause_dict,
                                1,
                                1,
                                soitem_poitem_map_wildcard_fields,
                                soitem_poitem_map_required_args)
        total, curr_page, rows = sql_stmt_obj.query_by_page()
        return jsonify(data=rows, success=True, message="success")


@login_required
def get_soitem_poitem_map_category():
    objs = NuraSoitemPoitemMapCategory.query.order_by(
        NuraSoitemPoitemMapCategory.id).all()
    return jsonify(data=[to_dict(NuraSoitemPoitemMapCategory, obj) for obj in objs], success=True, message="success")


@login_required
def get_soitem_poitem_map_status():
    objs = NuraSoitemPoitemMapStatu.query.order_by(
        NuraSoitemPoitemMapStatu.id).all()
    return jsonify(data=[to_dict(NuraSoitemPoitemMapStatu, obj) for obj in objs], success=True, message="success")
