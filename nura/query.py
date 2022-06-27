import copy

from inflect import CONSONANTS
from nura import db
from nura.sopomapSQL import sql_soitem_map


def add_limit_to_sql(sql_stmt, limit=100, offset=0):
    '''
    input:
    - sql_stmt: str or sqlalchemy.sql.elements.TextClause (e.g. db.text(""))

    ret:
    - sqlalchemy.sql.elements.TextClause (e.g. db.text(""))
    e.g: input sql: select * from table
         ret sql: select * from table limit {offset}, {limit}
    '''
    r_sql_stmt = db.text("")
    sql = ""
    if type(sql_stmt) == str:
        sql = sql_stmt
    elif type(sql_stmt) == type(db.text("")):
        sql = sql_stmt.text
        r_sql_stmt = copy.deepcopy(sql_stmt)
    else:
        raise Exception("sql_stmt type error")

    sql = sql.lower()
    if ";" in sql:
        sql = sql.strip().replace(";", "")
    limit_index = sql.rfind('limit')
    if limit_index != -1:
        sql = sql[:limit_index]
    r_sql_stmt.text = f'{sql} limit {offset}, {limit}'
    return r_sql_stmt


def get_count_sql(sql_stmt):
    '''
    input:
    - sql_stmt: str or sqlalchemy.sql.elements.TextClause (e.g. db.text(""))

    ret:
    - sqlalchemy.sql.elements.TextClause (e.g. db.text(""))

    '''
    r_sql_stmt = db.text("")
    sql = ""
    if type(sql_stmt) == str:
        sql = sql_stmt
    elif type(sql_stmt) == type(db.text("")):
        sql = sql_stmt.text
        r_sql_stmt = copy.deepcopy(sql_stmt)
    else:
        raise Exception("sql_stmt type error")

    if ";" in sql:
        sql = sql.strip().replace(";", "")
    limit_index = sql.rfind('limit')
    if limit_index != -1:
        sql = sql[:limit_index]
    sql = f'select count(1) as count from ({sql}) as t'
    r_sql_stmt.text = sql
    return r_sql_stmt


def get_offset(page_num, limit):
    return (page_num - 1) * limit if page_num > 0 else 0


def query_result(sql, limit, offset, params):
    '''
    input:
    - sql: str or sqlalchemy.sql.elements.TextClause (e.g. db.text(""))
    - limit: int
    - offset: int

    ret: 
     - int: total pages
     - int: current page
     - list: rows  
    '''
    # print("offset:", offset)
    # print("limit:", limit)
    count_sql_stmt = get_count_sql(sql)
    # print("count_sql_stmt", count_sql_stmt.text)
    sql_limit_stmt = add_limit_to_sql(sql, limit, offset)
    # print("sql_limit_stmt", sql_limit_stmt.text)
    total = db.engine.execute(count_sql_stmt, **params).scalar()
    # print("total:", total)
    result = db.engine.execute(sql_limit_stmt, **params).fetchall()
    rows = [dict(row) for row in result]
    # print("rows:", rows)
    curr_page = offset // limit + 1 if offset < total and total > 0 else 0
    return total, curr_page, rows


def query_result_by_page(sql, limit, page_num, params):
    '''
    input:
    - sql: str or sqlalchemy.sql.elements.TextClause (e.g. db.text(""))
    - limit: int
    - page_num: int

    ret: 
     - int: total pages
     - int: current page
     - list: rows  
    '''
    offset = get_offset(page_num, limit)
    return query_result(sql, limit, offset, params)


def query_result_all(sql):
    '''
    ret:
    - list: rows
    '''
    result = db.engine.execute(sql).fetchall()
    rows = [dict(row) for row in result]
    return rows


class SQL_STMT:
    def __init__(self,
                 base_sql,
                 order_by,
                 request_args,
                 clause_dict,
                 limit,
                 page_num,
                 wildcard_search_fields,
                 required_args):
        self.base_sql = base_sql.lower()
        self.order_by = order_by
        self.request_args = request_args
        self.clause_dict = clause_dict
        self.limit = limit
        self.page_num = page_num
        self.total = 0
        self.wildcard_search_fields = wildcard_search_fields
        self.required_args = required_args

        self.offset = 0
        self.get_offset()
        self.clauses = []
        self.get_clauses()
        self.value_dict = {}
        self.get_value_dict()
        self.clauses_str = ""
        self.get_sql_and_clauses_str()
        self.get_total()

    def get_clauses(self):
        for key in self.request_args.keys():
            clause = self.clause_dict.get(key, "")
            if clause:
                self.clauses.append(clause.format(key))

    def get_value_dict(self):
        for key, value in self.request_args.items():
            if key in self.clause_dict:
                v = value if key not in self.wildcard_search_fields else f'%{value}%'
                self.value_dict[key] = v

    def get_sql_and_clauses_str(self):
        self.clauses_str = '\n'.join([f"and {c}" for c in self.clauses])

    def get_sql_count_str(self):
        return f'select count(1) as count from ({self.base_sql} where 1=1 {self.clauses_str}) as t'

    def get_sql_limit_str(self):
        return f'''{self.base_sql} 
        where 1=1 
        {self.clauses_str} 
        {self.order_by}
        limit {self.offset}, {self.limit}'''

    def get_sql_all_str(self):
        return f'''{self.base_sql} 
        where 1=1 
        {self.clauses_str} 
        {self.order_by}'''

    def get_sql_limit_stmt(self):
        return db.text(self.get_sql_limit_str()).params(**self.value_dict)

    def get_sql_count_stmt(self):
        return db.text(self.get_sql_count_str()).params(**self.value_dict)

    def get_sql_all_stmt(self):
        return db.text(self.get_sql_all_str()).params(**self.value_dict)

    def get_offset(self):
        self.offset = (self.page_num - 1) * \
            self.limit if self.page_num > 0 else 0

    def get_total(self):
        with db.engine.connect() as conn:
            self.total = conn.execute(self.get_sql_count_stmt()).scalar()

    def missed_required_args(self):
        for key in self.required_args:
            if key not in self.request_args or not self.request_args[key]:
                return True
        return False

    def query_by_page(self):
        if self.missed_required_args():
            print("missed_required_args")
            return 0, 0, []
        with db.engine.connect() as conn:
            # print(self.get_sql_limit_stmt().__dict__)
            result = conn.execute(self.get_sql_limit_stmt()).fetchall()
            rows = [dict(row) for row in result]
            # print(self.total)
            curr_page = self.offset // self.limit + \
                1 if self.offset < self.total and self.total > 0 else 0
            return self.total, curr_page, rows

    def query_all(self):
        if self.missed_required_args():
            print("missed_required_args")
            return 0, 0, []
        with db.engine.connect() as conn:
            result = conn.execute(self.get_sql_all_stmt()).fetchall()
            rows = [dict(row) for row in result]
            return self.total, 1, rows
