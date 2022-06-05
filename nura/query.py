from nura import db


def add_limit_to_sql(sql, limit=100, offset=0):
    '''
    sql: select * from table
    ret: select * from table limit {offset}, {limit}
    '''
    sql = sql.lower()
    if ";" in sql:
        sql = sql.strip().replace(";", "")
    limit_index = sql.rfind('limit')
    if limit_index != -1:
        sql = sql[:limit_index]
    return f'{sql} limit {offset}, {limit}'


def get_count_sql(sql):
    if ";" in sql:
        sql = sql.strip().replace(";", "")
    limit_index = sql.rfind('limit')
    if limit_index != -1:
        sql = sql[:limit_index]
    return f'select count(1) as count from ({sql}) as t'


def get_offset(page_num, limit):
    return (page_num - 1) * limit if page_num > 0 else 0


def query_result(sql, limit, offset):
    '''
    ret: 
     - int: total pages
     - int: current page
     - list: rows  
    '''
    # print("offset:", offset)
    # print("limit:", limit)
    count_sql = get_count_sql(sql)
    sql = add_limit_to_sql(sql, limit, offset)
    total = db.engine.execute(count_sql).scalar()
    # print("total:", total)
    result = db.engine.execute(sql).fetchall()
    rows = [dict(row) for row in result]
    # print("rows:", rows)
    curr_page = offset // limit + 1 if offset < total and total > 0 else 0
    return total, curr_page, rows


def query_result_by_page(sql, limit, page_num):
    '''
    ret: 
     - int: total pages
     - int: current page
     - list: rows  
    '''
    offset = get_offset(page_num, limit)
    return query_result(sql, limit, offset)


def query_result_all(sql):
    '''
    ret:
    - list: rows
    '''
    result = db.engine.execute(sql).fetchall()
    rows = [dict(row) for row in result]
    return rows
