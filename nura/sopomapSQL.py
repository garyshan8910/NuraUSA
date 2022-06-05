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
