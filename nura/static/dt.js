function Generator() { };
Generator.prototype.rand = Math.floor(Math.random() * 26) + Date.now();
Generator.prototype.getId = function () {
    return this.rand++;
};
var uid_generator = new Generator()

class TB {
    constructor(settings) {
        this.data = null
        this.total = 0
        this.curr_page = 1
        this.total_page = 0
        this.limit = 10
        this.params = {}
        this.url = ""
        this.id = ""
        this.visible = []
        this.hidden = []
        this.searchable = []
        this.searchable_type = {}
        this.searchable_html = {
            'date': `<input type="date" class="form-control" placeholder="{}" name="{}" aria-label="field">`
        }
        this.custom_searchable_html = {}
        this.extra_col_elems = null
        this.extra_row_elems = null
        this.refresh_when_created = true
        this.has_fixed_html = true
        $.extend(this, settings)
        $.extend(this.searchable_html, this.custom_searchable_html)

        if (this.has_fixed_html) {
            this.setupDom()
            this.renderSearchForm()
            if (this.refresh_when_created) this.refresh()
            this.bindPagerEvent()
            this.bindSearchBarBtnsEvent()
        }
    }
    setupDom() {
        this.table = $(`#${this.id} table`).eq(0)
        this.pager = $(`#${this.id} nav.pager`).eq(0)
        this.prePage = this.pager.find('a.pre-page').eq(0)
        this.nextPage = this.pager.find('a.next-page').eq(0)
        this.totalPage = this.pager.find('span.total-page').eq(0)
        this.gotoPage = this.pager.find('a.goto-page').eq(0)
        this.totalItems = this.pager.find('span.total-items').eq(0)
        this.pageNum = this.pager.find('input.page-num').eq(0)
        this.extra_col_elems_html = this.getExtraColElemsHtml()
        this.searchDiv = $(`#${this.id} div.search`).eq(0)
        this.searchForm = this.searchDiv.find('form').eq(0)
        this.searchBtn = this.searchDiv.find('button.search-btn').eq(0)
        this.resetBtn = this.searchDiv.find('button.reset-btn').eq(0)
    }
    renderSearchForm() {
        if (this.searchable.length > 0) {
            var html = ""
            for (const i in this.searchable) {
                var field = this.searchable[i]
                var fieldType = this.searchable_type[field]
                if (!fieldType) {
                    html +=
                        `<div class="col">
                            <label class="form-label">${field}
                               <input type="text" class="form-control" placeholder="${field}" name="${field}"aria-label="field">
                            </label>
                        </div>`
                }
                else {
                    var fieldTypeHtml = this.searchable_html[fieldType].replaceAll("{}", field)
                    html +=
                        `<div class="col">
                            <label class="form-label">${field}
                                ${fieldTypeHtml}
                            </label>
                        </div>`
                }
            }
            this.searchForm.find('div.row').eq(0).html(html)
            this.searchDiv.show()
        }
        else {
            this.searchDiv.hide()
        }
    }
    updateData(data) {
        /*
        data: {
            data: list of row record,
            total: total number of record in database for this query
            curr_page: current page number for the data
        }
        */
        console.log("updateData", data)
        $.extend(this, data)
        this.total_page = parseInt((this.total - 1) / this.limit) + 1
    }
    refresh() {
        return this.fetchData(this.renderTable)
    }
    fetchData(callback) {
        var params = { "limit": this.limit, "page_num": this.curr_page }
        $.extend(params, this.getSearchParams(), this.params);
        console.log('table fetch, params: ', params)
        return $.getJSON(this.url, params)
            .then($.proxy(this, "updateData"))
            .then($.proxy(this, callback.name))
            .fail(function (jqxhr, textStatus, error) {
                console.log(textStatus)
            })
    }
    renderTable() {
        /*
        input:
        - data: {
            data: list of row record,
            total: total number of record in database for this query
            curr_page: current page number for the data
        }
        */

        // update this variable where receive new data from server
        console.log("render table", new Date($.now()))

        this.clearTable()
        if (this.data && this.data.length > 0) {
            this.table.find("thead").html(this.theadHtml(this.data[0], this.visible))
            this.table.find("tbody").html(this.tbodyHtml(this.data))
        }
        //pager
        if (this.data) {
            this.totalPage.text(this.total_page)
            this.totalItems.text(this.total)
            this.pageNum.val(this.curr_page)
            if (this.total_page > 1) {
                this.pager.show()
            } else {
                this.pager.hide()
            }
        } else {
            this.pager.hide()
        }
    }
    getSearchParams() {
        var params = {}
        this.searchForm.find('input, textarea').each(function () {
            var value = $(this).val().trim()
            if (value && value != "") {
                params[this.name] = value
            }
        })
        console.log("search form params:", params)
        return params
    }
    clearTable() {
        $(`#${this.id} table thead`).html("")
        $(`#${this.id} table tbody`).html("")
        this.pager.hide()
    }
    theadHtml(obj) {
        var visible = this.visible
        if (!obj || Object.keys(obj).length == 0) return "";
        var result = "<tr><th>#</th>"
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
    tbodyHtml(obj_list) {
        var visible = this.visible
        var hidden = this.hidden
        var extra_row_elems = this.extra_row_elems
        var html = ""
        var row_id = 0
        var uid = uid_generator.getId()
        for (const i in obj_list) {
            var obj = obj_list[i]
            var col_len = visible.length
            var row_html = `<tr class="clickable-row"><td>${(parseInt(i) + 1).toString()}</td>`
            if (visible.length == 0 && hidden.length == 0) {
                for (const k in obj) {
                    row_html += `<td class="${k}">${this.renderNull(obj[k])}</td>`
                }
            } else {
                for (const i in visible) {
                    if (visible[i] == "") row_html += `<td></td>`
                    else row_html += `<td class="${visible[i]}">${this.renderNull(obj[visible[i]])}</td>`
                }
                for (const i in hidden) {
                    row_html += `<input type="hidden" class="${hidden[i]}" value="${this.renderNull(obj[hidden[i]])}">`
                }
            }
            // 每行按钮等额外组件
            row_html += this.extra_col_elems_html
            // 多加一行 accordion 插件
            if (extra_row_elems) { row_html += `<td><button class="accordion-button collapsed" data-bs-toggle="collapse" data-bs-target="#r${uid}_${row_id}"></button></td>` }
            row_html += '</tr>'
            // 多加一行 accordion 插件
            if (extra_row_elems) { row_html += `<tr class="collapse accordion-collapse" id="r${uid}_${row_id}"><td colspan=${col_len + 2}><table class="table table-sm"></table></td>${extra_row_elems}</tr>` }
            html += row_html
            row_id += 1
        }
        return html
    }
    renderNull(value) {
        return value == null ? "" : value;
    }
    onPagerChange(action) {
        var currPageNum = parseInt(this.pageNum.val())
        if (action == "Previous") {
            currPageNum -= 1
        }
        else if (action == "Next") {
            currPageNum += 1
        }
        if (currPageNum <= 0) currPageNum = 1
        else if (currPageNum > this.total_page) currPageNum = this.total_page
        if (currPageNum != this.curr_page) {
            this.curr_page = currPageNum
            this.refresh()
        }
    }
    getExtraColElemsHtml() {
        var html = ""
        for (const i in this.extra_col_elems) {
            var elem = this.extra_col_elems[i]
            html += `<td><${elem['tagName']} class="${elem['classname']}">${this.renderNull(elem['text'])}</${elem['tagName']}></td>`
        }
        return html
    }
    bindPagerEvent() {
        var pager_btns = [this.prePage, this.nextPage, this.gotoPage]
        for (var i in pager_btns) {
            var btn = pager_btns[i]
            var action = btn.attr("aria-label")
            btn.click($.proxy(this, 'onPagerChange', action))
        }
    }
    bindSearchBarBtnsEvent() {
        this.searchBtn.click($.proxy(this, 'onSearchBtnClick'))
        this.resetBtn.click($.proxy(this, 'onResetBtnClick'))
    }
    onSearchBtnClick() {
        var params = this.getSearchParams()
        this.curr_page = 1
        this.refresh()
    }
    onResetBtnClick() {
        this.searchForm.find('input,select,textarea').each(function () {
            $(this).val('')
        })
    }
}

class EF {
    constructor(settings) {
        this.id = ""
        this.url_get = ""
        this.url_update = ""
        this.visible = []
        this.visible_col_type = {}
        this.hidden = []
        this.params = {}
        this.data = null
        this.htmlForInput = {
            "date": `<input type="date" class="form-control" id="m_{}" name="{}"/>`
        }
        this.customHtmlForInput = {}
        $.extend(this, settings)
        $.extend(this.htmlForInput, this.customHtmlForInput)
        this.setupDom()
        this.refresh()
    }
    setupDom() {
        this.form = $(`#${this.id} form`).eq(0)
        this.hiddenDiv = $(`#${this.id} div.hidden-field`).eq(0)
    }
    refresh() {
        if (!$.isEmptyObject(this.params)) {
            return this.fetchData(this.renderForm)
        }
    }
    fetchData(callback) {
        return $.getJSON(this.url_get, this.params)
            .done($.proxy(this, callback.name))
            .fail()
    }
    renderForm(data) {
        /*
        input:
        if it is from $.get response
        - data: {
            data: list of rows,
            total: int
            curr_page: int
        }
        if it is from $.post response
        - data: {
            data: object
            message: str
            success: boolean
        }
        */
        console.log("redner", new Date($.now()))

        this.generalizeData(data)
        this.clearForm()
        var form_html = ""
        for (const i in this.visible) {
            var field = this.visible[i]
            var colType = this.visible_col_type[field]
            var formInputHtml = this.getFormInputHtml(field, colType)
            var temp = `<div class="row mb-3">
                <label for="m_${field}" class="col-sm-3 col-form-label">${field}</label>
                <span for="m_${field}" class="col-sm-4 col-form-label">${this.data == null ? "" : (this.data[field] == null ? "" : this.data[field])}</span>
                <div class="col-sm-5 col-form">
                    ${formInputHtml}
                </div>
            </div>`
            form_html += temp
        }
        this.form.html(form_html)
        var hidden_html = ""
        for (const i in this.hidden) {
            var field = this.hidden[i]
            temp = `<input type=hidden class=${field} value="${this.data == null ? "" : (this.data[field] == null ? "" : this.data[field])}/>"`
            hidden_html += temp
        }
        this.hiddenDiv.html(hidden_html)
    }
    getFormInputHtml(field, colType) {
        var html = ""
        if (!colType || !this.htmlForInput[colType]) {
            html = `<input type="text" class="form-control" id="m_${field}" name="${field}"/>`
        } else {
            html = this.htmlForInput[colType].replaceAll("{}", field)
        }
        return html
    }
    generalizeData(data) {
        /*
        process get/post respone
        store the processed object into this.data 
        {
            field: value
            ...
        }
        */
        if (!data || !data.data) { this.data = null }
        else {
            if ($.isPlainObject(data.data)) {
                this.data = data.data
            }
            else if ($.isArray(data.data)) {
                this.data = data.data.length == 0 ? null : data.data[0]
            }
        }
    }
    clearForm() {
        this.form.html("")
        this.hiddenDiv.html("")
    }
    update_data() {
        var params = $.extend({}, this.params)
        this.form.find("input,select,textarea").each(function () {
            var value = $(this).val().trim()
            if (value && value != "") {
                params[this.name] = value
            }
        })
        let that = this
        return $.post(this.url_update, params)
            .done(function (data) {
                that.post_success = data.success
                that.post_message = data.message
                if (data.success) {
                    that.renderForm(data)
                }
            }).fail(function () {
                that.post_success = false
                that.post_message = "network error"
            })
    }
}

class MD {
    constructor(settings) {
        this.id = ""
        this.parent = null
        $.extend(this, settings)
        this.setupDom()
    }
    setupDom() {
        this.modal = $(`#${this.id}`)
        this.saveBtn = $(`#${this.id} button.save-form`).eq(0)
        this.title = $(`#${this.id} div.modal-header h5.modal-title`).eq(0)
        this.message = $(`#${this.id} div.message`).eq(0)
    }
    show() {
        console.log("show", new Date($.now()))
        this.modal.modal('show')
    }
    clearModal() {
        this.title.text("")
        this.message.text("")
    }
    refreshParent() {
        if (this.parent && typeof this.parent.refresh === 'function') this.parent.refresh()
    }
}

class AF {
    constructor(settings) {
        this.id = ""
        this.url = ""
        this.params = {}
        $.extend(this, settings)
        this.setupDom()
    }
    setupDom() {
        this.form = $(`#${this.id} form`).eq(0)
    }
    submitForm() {
        console.log("this.params", this.params)
        var params = $.extend({}, this.params)
        var hasNewValue = false
        this.form.find("input,textarea").each(function () {
            var value = $(this).val().trim()
            if (value && value != "") {
                params[this.name] = value
                hasNewValue = true
            }
        })
        console.log("submitForm", params)
        if (hasNewValue) {
            let that = this
            return $.post(this.url, params)
                .done(function (data) {
                    that.post_success = data.success
                    that.post_message = data.message
                }).fail(function () {
                    that.post_success = false
                    that.post_message = "network error"
                })
        } else {
            return Promise.resolve()
        }
    }
    clearForm() {
        this.form.find('input,textarea').each(function () {
            $(this).val("")
        })
    }
}

class MessageBox {
    constructor(settings) {
        this.id = ""
        $.extend(this, settings)
        this.setupDom()
    }
    setupDom() {
        this.messageDiv = $(`#${this.id} div.message`).eq(0)
        this.alertDiv = $(`#${this.id} div.alert`).eq(0)
    }

    showMessage(message, style) {
        this.alertDiv.attr("class", `alert alert-${style}`)
        this.messageDiv.text(message).css("color", "")
        setTimeout($.proxy(() => {
            this.alertDiv.attr("class", 'alert')
            this.messageDiv.css("color", "#fff")
        }, this), 5000);
        
    }
}

class DetailListModal extends MD {
    constructor(modalSettings, detailTableSettings, addFormSettings) {
        super(modalSettings)
        this.table = new TB(detailTableSettings)
        this.addForm = new AF(addFormSettings)
        this.bindEvent()
    }
    bindEvent() {
        this.saveBtn.click($.proxy(this, 'onSaveClick'))
    }
    onSaveClick() {
        return this.addForm.submitForm()
            .then($.proxy(this, 'update_table_params'))
            .then($.proxy(this, 'refresh'))
            .then($.proxy(this, 'clearAddForm'))
            .then($.proxy(this, 'refreshParent'))
            .then($.proxy(this, 'showMessage'))
    }
    showMessage() {
        this.message.text(this.addForm.post_message)
    }
    update_table_params(data) {
        if (data.success) {
            console.log("update_table_params", data)
            this.table.params['poiteminfoid'] = data.data.poiteminfoid
        }
    }
    refresh() {
        return this.table.refresh()
    }

    clearAddForm() {
        this.addForm.clearForm()
    }
    showDetailFormModal(params, title) {
        /*
        params: object 
        {
            poitemid: int
        }
        */
        $.extend(this.table.params, params)
        $.extend(this.addForm.params, params)
        this.table.curr_page = 1
        this.clearModal()
        this.title.text(title)
        this.table.refresh()
            .then($.proxy(this, 'show'))
    }
}
