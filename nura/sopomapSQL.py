def sql_inventory(partId):
    return f'''
    SELECT
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
    return f'''select po.num poNum, poitem.description, ROUND(qtyToFulfill,2) qtyToFulfill, ROUND(qtyFulfilled,2) qtyFulfilled, postatus.name status from po
    left join poitem on poitem.poid = po.id
    left join postatus on postatus.id = po.statusId 
    where poitem.partId = {partId}
    order by po.datecreated desc;'''


def sql_so_items(so=1):
    return f'''select soitem.id soitemid, so.num soNum, part.num partNum, ROUND(qtyOrdered,2) qtyOrdered, part.id partId from so
    left join soitem on soitem.soid = so.id
    left join product on soitem.productId = product.id
    left join part on part.id = product.partId
    where 1=1
    order by so.dateCreated desc
    limit 10'''
