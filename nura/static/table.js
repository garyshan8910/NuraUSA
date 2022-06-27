function Generator() { };
Generator.prototype.rand = Math.floor(Math.random() * 26) + Date.now();
Generator.prototype.getId = function () {
    return this.rand++;
};
var uid_generator = new Generator()

function table_html(lob, visible = [], hidden = [], extra_col_elems, extra_row_elems) {
    header = header_html(lob[0], visible)
    body = body_html(lob, visible, hidden, extra_col_elems, extra_row_elems)
    html = `<thead>${header}</thead><tbody>${body}</tbody>`
    // console.log(html)
    return html;
}

function header_html(obj, visible = []) {
    if (Object.keys(obj).length == 0) return "";
    result = "<tr><th>#</th>"
    if (visible.length == 0) {
        for (const k in obj) {
            result += `<th>${k}</th>`
        }
    } else {
        for (const i in visible) {
            result += `<th>${visible[i]}</th>`
        }
    }
    result += "</tr>"
    return result
}

function body_html(obj_list, visible = [], hidden = [], extra_col_elems, extra_row_elems) {
    html = ""
    let row_id = 0
    let uid = uid_generator.getId()
    for (let i in obj_list) {
        let obj = obj_list[i]
        let col_len = visible.length
        let row_html = `<tr class="clickable-row"><td>${(parseInt(i) + 1).toString()}</td>`
        if (visible.length == 0 && hidden.length == 0) {
            for (const k in obj) {
                row_html += `<td class="${k}">${render_null(obj[k])}</td>`
            }
        } else {
            for (let i in visible) {
                if (visible[i] == "") row_html += `<td></td>`
                else row_html += `<td class="${visible[i]}">${render_null(obj[visible[i]])}</td>`
            }
            for (let i in hidden) {
                row_html += `<input type="hidden" class="${hidden[i]}" value="${render_null(obj[hidden[i]])}">`
            }
        }
        // 每行按钮等额外组件
        row_html += extra_col_elems
        // 多加一行 accordion 插件
        if (extra_row_elems) { row_html += `<td><button class="accordion-button collapsed" data-bs-toggle="collapse" data-bs-target="#r${uid}_${row_id}"></button></td>` }
        row_html += '</tr>'
        // 多加一行 accordion 插件
        if (extra_row_elems) { row_html += `<tr class="collapse accordion-collapse" id="r${uid}_${row_id}"><td colspan=${col_len + 2}><table class="table table-striped table-sm"></table></td>${extra_row_elems}</tr>` }
        html += row_html
        row_id += 1
    }
    return html
}

function set_clickalbe_row(table_id, can_unselec_row) {
    $(`#${table_id}`).on('click', '.clickable-row', function (event) {
        if (can_unselec_row) {
            if ($(this).hasClass('table-primary')) {
                $(this).removeClass('table-primary')
            }
            else {
                $(this).addClass('table-primary').siblings().removeClass('table-primary');
            }
        } else {
            $(this).addClass('table-primary').siblings().removeClass('table-primary');
        }

    });
}

function render_null(value) {
    return value == null ? "" : value;
}
function paginate(table_id, pager_id, params, total, url, visible, hidden, extra_col_elems, extra_row_elems) {
    table = $(`#${table_id}`)
    pager = $(`#${pager_id}`)
    prePage = pager.find('.pre-page')
    nextPage = pager.find('.next-page')
    totalPage = pager.find('.total-page')
    gotoPage = pager.find('.goto-page')
    pageNum = pager.find('.page-num')
    paramsInput = pager.find('.params')
    pageNum.val("1")
    paramsInput.val(JSON.stringify(params))
    totalItems = pager.find('.total-items')
    totalItems.text(total)

    limit = params['limit']
    total_page = parseInt((total - 1) / limit) + 1
    totalPage.text(total_page)

    if (total_page > 1) {
        pager.show()
    } else {
        pager.hide()
    }

    prePage.unbind()
    prePage.click(function () {
        pager = $(this).closest("nav")
        pageNum = pager.find('.page-num')
        paramsInput = pager.find('.params')
        let curr_page = pageNum.val()
        if (curr_page > 1) {
            curr_page -= 1
        }
        else {
            curr_page = 1
        }
        pageNum.val(curr_page)
        params = JSON.parse(paramsInput.val())
        params["page_num"] = curr_page
        others = {
            "table_id": table_id,
            "pager_id": "",
            "visible_col": visible,
            "hidden_col": hidden,
            "extra_col_elems": extra_col_elems,
            "extra_row_elems": extra_row_elems
        }
        fetch_data(url, params, render_as_table, others)
    })

    nextPage.unbind()
    nextPage.click(function () {
        pager = $(this).closest("nav")
        pageNum = $(this).closest("nav").find('.page-num')
        totalPage = $(this).closest("nav").find('.total-page')
        paramsInput = $(this).closest("nav").find('.params')
        let total_page = parseInt(totalPage.text())
        let curr_page = parseInt(pageNum.val())
        if (curr_page >= total_page) {
            curr_page = total_page
        }
        else {
            curr_page += 1
        }
        pageNum.val(curr_page)
        params = JSON.parse(paramsInput.val())
        console.log('params: ', params)
        params["page_num"] = curr_page
        others = {
            "table_id": table_id,
            "pager_id": "",
            "visible_col": visible,
            "hidden_col": hidden,
            "extra_col_elems": extra_col_elems,
            "extra_row_elems": extra_row_elems
        }
        fetch_data(url, params, render_as_table, others)
    })

    gotoPage.unbind()
    gotoPage.click(function () {
        pager = $(this).closest("nav")
        pageNum = $(this).closest("nav").find('.page-num')
        totalPage = $(this).closest("nav").find('.total-page')
        paramsInput = $(this).closest("nav").find('.params')
        let total_page = parseInt(totalPage.text())
        let curr_page = pageNum.val()
        if (curr_page < 1 || curr_page > total_page) { curr_page = 1 }
        pageNum.val(curr_page)
        params = JSON.parse(paramsInput.val())
        params["page_num"] = curr_page
        others = {
            "table_id": table_id,
            "pager_id": "",
            "visible_col": visible,
            "hidden_col": hidden,
            "extra_col_elems": extra_col_elems,
            "extra_row_elems": extra_row_elems
        }
        fetch_data(url, params, render_as_table, others)
    })
}

function query_pager_check(obj) {
    if (!('page_num' in obj) || obj['page_num'] < 1) {
        obj['page_num'] = 1
    }
    if (!('limit' in obj) || obj['limit'] <= 0) {
        obj['limit'] = 10
    }
}

function accordion_button_click(url, so_itemid, callback, others) {
    params = { "so_itemid": so_itemid }
    fetch_data(url, params, callback, others)
}

function render_accordion_row(data, url, params, others) {
    row_id = others["row_id"]
    visible = others["visible"]
    extra = others["extra"]
    // console.log(others)
    // console.log(data)
    extra_row = ""
    if (data.data.length > 0) {
        extra_row = get_summary_qty_tr(data.data, visible)
    }
    $(`#${row_id}`).find("table").html(body_html(data.data, visible, [], "", "") + extra_row)
}

function get_summary_qty_tr(rows, visible) {
    total = 0
    for (let i in rows) {
        total += parseFloat(rows[i]["qty"])
    }
    row_html = `<tr><td></td>`
    for (let i in visible) {
        if (visible[i] == "qty") row_html += `<td class="total"}">${total.toFixed(2)}</td>`
        else row_html += `<td></td>`
    }
    row_html += `</tr>`
    return row_html
}

function fetch_data(url, params, callback, others) {
    query_pager_check(params)
    // console.log("params:",params)
    $.getJSON(url, params, function (data) {
        callback(data, url, params, others)
    })
}

function render_as_table(data, url, params, others) {
    table_id = others["table_id"]
    pager_id = others["pager_id"]
    visible_col = others["visible_col"]
    hidden_col = others["hidden_col"]
    extra_col_elems = others["extra_col_elems"]
    extra_row_elems = others["extra_row_elems"]
    query_pager_check(params)

    if ($(`#${table_id}`).length > 0) {
        clear_table(table_id)
    }
    if (data.total > 0 && $(`#${table_id}`).length > 0) {
        $(`#${table_id}`).html(table_html(data.data, visible_col, hidden_col, extra_col_elems, extra_row_elems))
    }
    if (pager_id != "" && $(`#${pager_id}`).length > 0) {
        paginate(table_id, pager_id, params, data.total, url, visible_col, hidden_col, extra_col_elems, extra_row_elems)
    }
}

function clear_table(table_id) {
    $(`#${table_id} thead`).html("")
    $(`#${table_id} tbody`).html("")
}

function alert_show_then_clear(message, style) {
    $(`#${allocate_alert_id}`).attr("class", `alert alert-${style}`)
    $(`#${allocate_alert_message_id}`).text(message).css("color", "")
    setTimeout(function () {
        $(`#${allocate_alert_id}`).attr("class", `alert`)
        $(`#${allocate_alert_message_id}`).css("color", "#fff")
    }, 5000);
}

const data_type_map = {
    "INTEGER": "number",
    "VARCHAR": "text",
    "DATETIME": "date",
    "BOOLEAN": "text",
}

const cols = {
    "id": "INTEGER",
    "poitemid": "INTEGER",
    "transport": "VARCHAR",
    "priceBeforeNeg": "DECIMAL",
    "priceAfterNeg": "DECIMAL",
    "etd": "DATETIME",
    "eta": "DATETIME",
    "coaReq": "VARCHAR",
    "coaCheck": "VARCHAR",
    "labelCheck": "VARCHAR",
    "shippingDoc": "VARCHAR",
    "arrivalNotice": "VARCHAR",
    "Customer": "VARCHAR",
    "mfgBatch": "VARCHAR",
    "nuraBatch": "VARCHAR",
    "shipperQualified": "VARCHAR",
    "qualificationNote": "VARCHAR",
    "qcRelease": "VARCHAR",
    "needNuraCoa": "VARCHAR",
    "mfg": "VARCHAR",
    "lotNuraCoa": "BOOLEAN"
}