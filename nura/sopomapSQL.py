from nura import db


def get_and_where_clause(hash_map):
    result = []
    for k in hash_map:
        if hash_map[k]:
            result.append(f'and {hash_map[k]}')
    return "\n".join(result)


def get_data_types(model):
    '''return dictionary with column name as key and data type as value'''
    d = {}
    for c in model.__table__.columns:
        c_type = str(c.type)
        if '(' in str(c.type):
            c_type = c_type[:c_type.index('(')]
        d[str(c.name)] = c_type
    return d


def sql_inventory(partId):
    return f'''
    SELECT
        PART.ID AS PARTID,
        PART.NUM AS PART,
        PART.DESCRIPTION,
        UOM.CODE AS UOMCODE,
        (SELECT NAME FROM COMPANY WHERE ID = 1) AS COMPANY,
        COALESCE(INVENTORYTOTALS.TOTALONHAND,0) AS qtyOnHand,
        COALESCE(INVENTORYTOTALS.TOTALNOTAVAILABLE,0) AS UNAVAILABLE,
        COALESCE(INVENTORYTOTALS.TOTALDROPSHIP,0) AS DROPSHIP,
        COALESCE(COMMITTED.TOTAL,0) AS QTYCOMMITTED,
        COALESCE(INVENTORYTOTALS.TOTALALLOCATED,0) AS qtyAllocated,
        COALESCE(INVENTORYTOTALS.TOTALONORDER,0) AS qtyOnOrder,
        COALESCE(INVENTORYTOTALS.totalNotAvailabletopick,0) totalNotAvailabletopick,
        COALESCE(inventorytotals.totalonhand + inventorytotals.totalonorder - inventorytotals.totalallocated ,0) AS extra,
        COALESCE(partcost.avgcost, COALESCE(part.stdcost, 0)) AS AVGCOST,
        DATE(EXPINFO.EXP)  EXP
    FROM
        part
        LEFT JOIN uom ON part.uomid = uom.id
        LEFT JOIN (
            SELECT
                partId,
                SUM(qtyOnHand) AS totalOnHand,
                SUM(qtyNotAvailable) AS totalNotAvailable,
                SUM(qtyNotAvailabletopick) AS totalNotAvailabletopick,
                SUM(qtyDropship) AS totalDropship,
                SUM(qtyAllocated) AS totalAllocated,
                SUM(qtyOnOrder) AS totalOnOrder
            FROM
                qtyInventoryTotals
            WHERE locationGroupId IN (1,2,3,5,6,7,11,12,13)
            GROUP BY partId
        ) AS inventoryTotals ON inventoryTotals.partId = part.id
        LEFT JOIN (
            SELECT
                partId,
                SUM(qty) AS total
            FROM
                qtyCommitted
            WHERE locationGroupId IN (1,2,3,5,6,7,11,12,13)
            GROUP BY partId
        ) AS committed ON committed.partId = part.id
        LEFT JOIN partcost ON (part.id = partcost.partid)
        LEFT JOIN (
            select tag.`partId` as TAGPARTID,  min(info) EXP from tag
            left join trackingdate on trackingdate.`tagId` = tag.id
            group by tag.`partId`
        ) as EXPINFO on EXPINFO.TAGPARTID = PART.id
    WHERE
        part.id = {partId}
        AND part.id != 0
        AND part.typeid = 10
        AND part.activeflag = 1
    ORDER BY part.num
    '''


def sql_po_items(partId):
    return f'''select poitem.id poitemid, po.num poNum, poitem.description, ROUND(qtyToFulfill,2) qtyToFulfill, ROUND(qtyFulfilled,2) qtyFulfilled, postatus.name status from po
    left join poitem on poitem.poid = po.id
    left join postatus on postatus.id = po.statusId
    where poitem.partId = {partId}
    order by po.id desc, poitem.id'''


def sql_so_items(so=1):
    return f'''select soitem.id soitemid, so.num soNum, part.num partNum, ROUND(qtyOrdered,2) qtyOrdered, part.id partId, part.description, product.num productnum, map_records.mapcnt from so
    join soitem on soitem.soid = so.id
    left join product on soitem.productId = product.id
    left join part on part.id = product.partId
    left join (
    select soitemid, count(1) mapcnt from nura_soitem_poitem_map
    group by soitemid
    ) as map_records on map_records.soitemid = soitem.id
    where 1=1
    order by so.id desc, soitem.id
    '''


def sql_soitem_poitem_map(soid, allocateTypeId):
    return f'''select nura_soitem_poitem_map.id as mapid, soitemid, poitemid, soitem.productNum, part.num partnum, ROUND(qty,2) qty, allocateTypeId, userid, assist_user.username, po.num as ponum, poitem.description poitemdes, so.id soid
    from so
    join soitem on so.id = soitem.soid
    left join nura_soitem_poitem_map on soitem.id = nura_soitem_poitem_map.soitemid
    join product on product.id = soitem.productid
    join part on part.id = product.partid
    left join assist_user on nura_soitem_poitem_map.userid = assist_user.id
    left join poitem on poitem.id = nura_soitem_poitem_map.poitemid
    left join po on po.id = poitem.poid
    where so.id = {soid} and allocateTypeId = {allocateTypeId}
    order by so.id desc, nura_soitem_poitem_map.soitemid, nura_soitem_poitem_map.allocateTypeId, nura_soitem_poitem_map.created desc'''


def sql_so():
    return f'''select so.id soid, so.num sonum, customerContact, dateCreated, salesman, totalPrice from so
    where id in (
    select so.id from nura_soitem_poitem_map
    join soitem on nura_soitem_poitem_map.soitemid = soitem.id
    join so on so.id = soitem.soid
    )
    order by id desc'''


def sql_soitem_map(soitemid):
    return f'''select coalesce(po.num, 'inventory') ponum,   Round(nura_soitem_poitem_map.qty,2) qty , assist_user.id userid, assist_user.username, nura_soitem_poitem_map.created, allocateTypeId from soitem
    join nura_soitem_poitem_map on nura_soitem_poitem_map.soitemid = soitem.id
    join assist_user on  assist_user.id = nura_soitem_poitem_map.userid
    left join poitem on poitem.id = nura_soitem_poitem_map.poitemid
    left join po on po.id = poitem.poid
    where soitem.id = {soitemid}
    order by allocateTypeId, created '''


def sql_poitem_so_due_date(poitemid):
    return f'''SELECT nura_soitem_poitem_map.*, STR_TO_DATE(JSON_EXTRACT(so.customFields, '$."4".value'),'"%Y-%m-%d %H:%i:%s') due_date, so.* from nura_soitem_poitem_map
    join poitem on nura_soitem_poitem_map.poitemid = poitem.id
    join soitem on soitem.id = nura_soitem_poitem_map.soitemid
    join so on so.id = soitem.soid
    where poitem.id ={poitemid}'''


def sql_poitem_info_details(hash_map):
    where_clause = get_and_where_clause(hash_map)
    return f'''SELECT nura_po_item_info_detail.id, poiteminfoid, userid, username, content, nura_po_item_info_detail.created FROM nura_po_item_info_detail
    left join assist_user on assist_user.id = userid
    where 1=1
    {where_clause}
    order by nura_po_item_info_detail.id desc
    '''


poiteminfo_base_sql = '''SELECT poitem.id _poitemid, po.num ponum, poitem.description, part.num partnum, poitem.vendorPartNum, Round(poitem.qtyToFulfill,2) qtyToFulfill, nura_po_item_info.* FROM poitem
    join po on po.id = poitem.poId
    left join part on part.id = poitem.partid
    left join nura_po_item_info on nura_po_item_info.poitemid = poitem.id'''
poiteminfo_order_by = 'order by po.id desc, poitem.id'
poiteminfo_clause_dict = {
    "id": "nura_po_item_info.id = :{}",
    "_poitemid": "poitem.id = :{}",
    "poitemid": "poitem.id = :{}",
    "ponum": "po.num = :{}",
    "vendorpartnum": "poitem.vendorPartNum = :{}",
    "description": 'poitem.description like :{}',
    "etd_start": "nura_po_item_info.etd >= :{}",
    "etd_end": "nura_po_item_info.etd <= :{}",
    "eta_start": "nura_po_item_info.eta >= :{}",
    "eta_end": "nura_po_item_info.eta <= :{}",
}
poiteminfo_wildcard_fields = set(["description"])
poiteminfo_required_args = set()


poiteminfo_detail_base_sql = '''SELECT nura_po_item_info_detail.id, poiteminfoid, userid, username, content, nura_po_item_info_detail.created FROM nura_po_item_info_detail
    left join assist_user on assist_user.id = userid'''
poiteminfo_detail_order_by = '''order by nura_po_item_info_detail.id desc'''
poiteminfo_detail_clause_dict = {
    "poiteminfoid": "nura_po_item_info_detail.poiteminfoid = :{}"
}
poiteminfo_detail_wildcard_fields = set()
poiteminfo_detail_required_args = set()

soitem_base_sql = '''select soitem.id soitemid, so.num soNum, part.num partNum, ROUND(qtyOrdered,2) qtyOrdered, part.id partId, part.description, product.num productnum, map_records.mapqty from so
    join soitem on soitem.soid = so.id
    left join product on soitem.productId = product.id
    left join part on part.id = product.partId
    left join (
    select soitemid, ROUND(sum(qty), 2) mapqty from nura_soitem_poitem_map
    group by soitemid
    ) as map_records on map_records.soitemid = soitem.id
    '''
soitem_order_by = '''order by so.id desc, soitem.id'''
soitem_clause_dict = {
    "partnum": "part.num = :{}",
    "sonum": " so.num = :{}",
    "description": 'part.description like :{}',
    "RAW_mapqty": "map_records.mapqty :{}",

}
soitem_wildcard_fields = set(["description"])
soitem_required_args = set()

inventory_base_sql = '''SELECT
        PART.ID AS PARTID,
        PART.NUM AS PART,
        PART.DESCRIPTION,
        UOM.CODE AS UOMCODE,
        (SELECT NAME FROM COMPANY WHERE ID = 1) AS COMPANY,
        COALESCE(INVENTORYTOTALS.TOTALONHAND,0) AS qtyOnHand,
        COALESCE(INVENTORYTOTALS.TOTALNOTAVAILABLE,0) AS UNAVAILABLE,
        COALESCE(INVENTORYTOTALS.TOTALDROPSHIP,0) AS DROPSHIP,
        COALESCE(COMMITTED.TOTAL,0) AS QTYCOMMITTED,
        COALESCE(INVENTORYTOTALS.TOTALALLOCATED,0) AS qtyAllocated,
        COALESCE(INVENTORYTOTALS.TOTALONORDER,0) AS qtyOnOrder,
        COALESCE(INVENTORYTOTALS.totalNotAvailabletopick,0) totalNotAvailabletopick,
        COALESCE(inventorytotals.totalonhand + inventorytotals.totalonorder - inventorytotals.totalallocated ,0) AS extra,
        COALESCE(partcost.avgcost, COALESCE(part.stdcost, 0)) AS AVGCOST,
        DATE(EXPINFO.EXP)  EXP
    FROM
        part
        LEFT JOIN uom ON part.uomid = uom.id
        LEFT JOIN (
            SELECT
                partId,
                SUM(qtyOnHand) AS totalOnHand,
                SUM(qtyNotAvailable) AS totalNotAvailable,
                SUM(qtyNotAvailabletopick) AS totalNotAvailabletopick,
                SUM(qtyDropship) AS totalDropship,
                SUM(qtyAllocated) AS totalAllocated,
                SUM(qtyOnOrder) AS totalOnOrder
            FROM
                qtyInventoryTotals
            WHERE locationGroupId IN (1,2,3,5,6,7,11,12,13)
            GROUP BY partId
        ) AS inventoryTotals ON inventoryTotals.partId = part.id
        LEFT JOIN (
            SELECT
                partId,
                SUM(qty) AS total
            FROM
                qtyCommitted
            WHERE locationGroupId IN (1,2,3,5,6,7,11,12,13)
            GROUP BY partId
        ) AS committed ON committed.partId = part.id
        LEFT JOIN partcost ON (part.id = partcost.partid)
        LEFT JOIN (
            select tag.`partId` as TAGPARTID,  min(info) EXP from tag
            left join trackingdate on trackingdate.`tagId` = tag.id
            group by tag.`partId`
        ) as EXPINFO on EXPINFO.TAGPARTID = PART.id'''
inventory_order_by = '''ORDER BY part.num'''
inventory_clause_dict = {
    "partId": '''part.id = :{} 
                 AND part.id != 0
                 AND part.typeid = 10
                 AND part.activeflag = 1'''}
inventory_wildcard_fields = set()
inventory_required_args = set(["partId"])

poitem_base_sql = '''select poitem.id poitemid, po.num poNum, poitem.description, ROUND(qtyToFulfill,2) qtyToFulfill, ROUND(qtyFulfilled,2) qtyFulfilled, postatus.name status, coalesce(round(mapsum.mapqty,2), 0) mapqty from po
left join poitem on poitem.poid = po.id
left join postatus on postatus.id = po.statusId
left join (
select poitemid, sum(qty) mapqty from nura_soitem_poitem_map where poitemid is not null group by poitemid 
) mapsum on mapsum.poitemid = poitem.id'''
poitem_order_by = '''order by po.id desc, poitem.id'''
poitem_clause_dict = {
    "partId": "poitem.partId = :{}",
    "status_in": "postatus.name in :{}"
}
poitem_wildcard_fields = set()
poitem_required_args = set(["partId"])

soitemmap_base_sql = '''select coalesce(po.num, 'inventory') ponum,   Round(nura_soitem_poitem_map.qty,2) qty , assist_user.id userid, assist_user.username, nura_soitem_poitem_map.created, allocateTypeId from soitem
    join nura_soitem_poitem_map on nura_soitem_poitem_map.soitemid = soitem.id
    join assist_user on  assist_user.id = nura_soitem_poitem_map.userid
    left join poitem on poitem.id = nura_soitem_poitem_map.poitemid
    left join po on po.id = poitem.poid'''
soitemmap_order_by = '''order by allocateTypeId, created'''
soitemmap_clause_dict = {"so_itemid": "soitem.id = :{}"}
soitemmap_wildcard_fields = set()
soitemmap_required_args = set(["so_itemid"])

soitem_poitem_map_base_sql = '''
    select 
    so.salesman, 
    so.num as sonum,
    so.customerPO as customerPO,
    so.dateCreated as soCreated,
    po.num as ponum, 
    soitem.description,
    soitem.productNum,
    nura_soitem_poitem_map.id as mapid, 
    nura_soitem_poitem_map.soitemid,
    nura_soitem_poitem_map.poitemid,
    nura_soitem_poitem_map.whs,
    nura_soitem_poitem_map.shipDate, 
    nura_soitem_poitem_map.shipForEom, 
    nura_soitem_poitem_map.nuraLot,
    nura_soitem_poitem_map.mfgBatchLot,
    nura_soitem_poitem_map.qcReleased,
    nura_soitem_poitem_map.creditReleased,
    nura_soitem_poitem_map.needToChangeLabel,
    nura_soitem_poitem_map.allocateTypeId,
    nura_soitem_poitem_map.created as mapCreated,
    nura_soitem_poitem_map.userid,
    Round(nura_soitem_poitem_map.qty,2) as qty,
    nura_soitem_poitem_map_status.name as status,
    nura_soitem_poitem_map.statusId as statusId,
    nura_soitem_poitem_map_category.name as category,
    nura_soitem_poitem_map.categoryId as categoryId,
    nura_po_item_info.id as poiteminfoid,
    assist_user.username
    from nura_soitem_poitem_map
    left join soitem on soitem.id = nura_soitem_poitem_map.soitemid
    left join poitem on poitem.id = nura_soitem_poitem_map.poitemid
    left join so on so.id = soitem.soid
    left join po on po.id = poitem.poid
    left join assist_user on assist_user.id = nura_soitem_poitem_map.userid
    left join nura_soitem_poitem_map_status on nura_soitem_poitem_map_status.id = nura_soitem_poitem_map.statusId
    left join nura_soitem_poitem_map_category on nura_soitem_poitem_map_category.id = nura_soitem_poitem_map.categoryId
    left join nura_po_item_info on nura_po_item_info.poitemid = nura_soitem_poitem_map.poitemid
'''
soitem_poitem_map_order_by = '''order by so.id desc, soitem.id '''
soitem_poitem_map_clause_dict = {
    "sonum": "so.num = :{}",
    "ponum": "po.num = :{}",
    "description": "soitem.description like :{}",
    "productnum": "soitem.productNum like :{}",
    "salesman": "so.salesman like :{}",
    "customerpo": "so.customerPO like :{}", 
    "id": "nura_soitem_poitem_map.id = :{}",
    "statusId": "nura_soitem_poitem_map.statusId = :{}",
    "categoryId": "nura_soitem_poitem_map.categoryId = :{}",
}
soitem_poitem_map_wildcard_fields = set(["description","productnum","salesman","customerpo"])
soitem_poitem_map_required_args = set([])

soitem_poitem_map_detail_base_sql = '''SELECT nura_soitem_poitem_map_detail.id as mapid, userid, username, content, nura_soitem_poitem_map_detail.created FROM nura_soitem_poitem_map_detail
    left join assist_user on assist_user.id = userid'''
soitem_poitem_map_detail_order_by = '''order by nura_soitem_poitem_map_detail.id desc'''
soitem_poitem_map_detail_clause_dict = {
    "mapid": "nura_soitem_poitem_map_detail.mapid = :{}"
}
soitem_poitem_map_detail_wildcard_fields = set()
soitem_poitem_map_detail_required_args = set()
