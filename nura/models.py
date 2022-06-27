import hashlib
from nura import db, login_manager
from flask_login import UserMixin

def to_dict(cls, ins):
    '''
    non recursive method to convert an instance for db.model class to dict
    only work for simple model with basic data type for each column
    '''
    ret = {}
    try:
        for c in cls.__table__.columns:
            ret[c.name] = getattr(ins, c.name)

    except:
        print("An exception occurred")
    return ret

class AssistUser(UserMixin, db.Model):
    __tablename__ = 'assist_user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    active = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return 'id = {}, username = {}, password = {}'.format(
            self.id,  self.username, self.password
        )

    def compute_md5_hash(self, password):
        m = hashlib.md5()
        m.update(password.encode('utf-8'))
        return m.hexdigest()

    def set_password(self, password):
        self.password = self.compute_md5_hash(password)

    def check_password(self, password):
        return self.password == self.compute_md5_hash(password)


class Sysuser(UserMixin, db.Model):
    __tablename__ = 'sysuser'

    id = db.Column(db.Integer, primary_key=True)
    activeFlag = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(255))
    firstName = db.Column(db.String(15))
    initials = db.Column(db.String(5))
    lastName = db.Column(db.String(15))
    phone = db.Column(db.String(255))
    userName = db.Column(db.String(100), nullable=False, unique=True)
    userPwd = db.Column(db.String(255), nullable=False)
    customFields = db.Column(db.JSON)
    passwordLastModified = db.Column(db.DateTime)


# 获取用户是否登陆信息
@login_manager.user_loader
def lode_user(id):
    return AssistUser.query.get(int(id))


class Account(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    typeId = db.Column(db.Integer, index=True)


class Accounttype(db.Model):
    __tablename__ = 'accounttype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False, unique=True)


class Asaccount(db.Model):
    __tablename__ = 'asaccount'

    id = db.Column(db.Integer, primary_key=True)
    accountNumber = db.Column(db.String(36))
    accountingHash = db.Column(db.String(30))
    accountingId = db.Column(db.String(36))
    activeFlag = db.Column(db.Integer)
    dateCreated = db.Column(db.DateTime)
    dateLastModified = db.Column(db.DateTime)
    name = db.Column(db.String(155), nullable=False, unique=True)
    typeId = db.Column(db.Integer, index=True)


class Asaccounttype(db.Model):
    __tablename__ = 'asaccounttype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(31), nullable=False, unique=True)


class Calcategory(db.Model):
    __tablename__ = 'calcategory'
    __table_args__ = (
        db.Index('UK1qdinh0w1ixv3bl6fnc36uqsi', 'name', 'parentID'),
    )

    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(32))
    dateCreated = db.Column(db.DateTime)
    dateLastModified = db.Column(db.DateTime)
    lastChangedUserId = db.Column(db.Integer, nullable=False, index=True)
    name = db.Column(db.String(128), index=True)
    parentID = db.Column(db.Integer)
    readOnly = db.Column(db.Integer)


class Carrier(db.Model):
    __tablename__ = 'carrier'

    id = db.Column(db.Integer, primary_key=True)
    activeFlag = db.Column(db.Integer)
    description = db.Column(db.String(256))
    name = db.Column(db.String(60), unique=True)
    readOnly = db.Column(db.Integer)
    scac = db.Column(db.String(4))


class Carrierservice(db.Model):
    __tablename__ = 'carrierservice'
    __table_args__ = (
        db.Index('UKdc1j66ybp3bgqvddhsc9fsdgf', 'code', 'carrierId'),
        db.Index('UKh7ekhrawg2f5g1uuqtb4ctbwq', 'name', 'carrierId')
    )

    id = db.Column(db.Integer, primary_key=True)
    activeFlag = db.Column(db.Integer, nullable=False)
    carrierId = db.Column(db.Integer, nullable=False, index=True)
    code = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    readOnly = db.Column(db.Integer, nullable=False)


class Currency(db.Model):
    __tablename__ = 'currency'

    id = db.Column(db.Integer, primary_key=True)
    activeFlag = db.Column(db.Integer)
    code = db.Column(db.String(3))
    dateCreated = db.Column(db.DateTime)
    dateLastModified = db.Column(db.DateTime)
    excludeFromUpdate = db.Column(db.Integer)
    homeCurrency = db.Column(db.Integer)
    lastChangedUserId = db.Column(db.Integer, nullable=False, index=True)
    name = db.Column(db.String(255), unique=True)
    rate = db.Column(db.Float(asdecimal=True))
    symbol = db.Column(db.Integer)


class Customer(db.Model):
    __tablename__ = 'customer'
    __table_args__ = (
        db.Index('UKce8f1dpemolf390y20ijetd7k', 'name', 'parentId'),
    )

    id = db.Column(db.Integer, primary_key=True)
    accountId = db.Column(db.Integer, nullable=False, index=True)
    accountingHash = db.Column(db.String(30))
    accountingId = db.Column(db.String(36))
    activeFlag = db.Column(db.Integer, nullable=False)
    carrierServiceId = db.Column(db.Integer, index=True)
    creditLimit = db.Column(db.Numeric(28, 9))
    currencyId = db.Column(db.Integer, index=True)
    currencyRate = db.Column(db.Numeric(28, 9))
    dateCreated = db.Column(db.DateTime)
    dateLastModified = db.Column(db.DateTime)
    defaultCarrierId = db.Column(db.Integer, index=True)
    defaultPaymentTermsId = db.Column(db.Integer, nullable=False, index=True)
    defaultPriorityId = db.Column(db.Integer, index=True)
    defaultSalesmanId = db.Column(db.Integer)
    defaultShipTermsId = db.Column(db.Integer, nullable=False, index=True)
    jobDepth = db.Column(db.Integer)
    lastChangedUser = db.Column(db.String(100))
    name = db.Column(db.String(41), nullable=False, index=True)
    note = db.Column(db.String(256))
    number = db.Column(db.String(30), nullable=False, unique=True)
    parentId = db.Column(db.Integer, index=True)
    qbClassId = db.Column(db.Integer, index=True)
    statusId = db.Column(db.Integer, nullable=False, index=True)
    sysUserId = db.Column(db.Integer)
    taxExempt = db.Column(db.Integer, nullable=False)
    taxExemptNumber = db.Column(db.String(30))
    taxRateId = db.Column(db.Integer, index=True)
    toBeEmailed = db.Column(db.Integer, nullable=False)
    toBePrinted = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(256))
    issuableStatusId = db.Column(db.Integer, index=True)
    customFields = db.Column(db.JSON)


class Customerstatu(db.Model):
    __tablename__ = 'customerstatus'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False, unique=True)


class Fobpoint(db.Model):
    __tablename__ = 'fobpoint'

    id = db.Column(db.Integer, primary_key=True)
    activeFlag = db.Column(db.Integer)
    name = db.Column(db.String(15), nullable=False, unique=True)


class Issuablestatu(db.Model):
    __tablename__ = 'issuablestatus'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True)


class Locationgroup(db.Model):
    __tablename__ = 'locationgroup'

    id = db.Column(db.Integer, primary_key=True)
    activeFlag = db.Column(db.Integer, nullable=False)
    dateLastModified = db.Column(db.DateTime)
    name = db.Column(db.String(30), nullable=False, unique=True)
    qbClassId = db.Column(db.Integer, index=True)


class Ordertype(db.Model):
    __tablename__ = 'ordertype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False, unique=True)


class Paymentterm(db.Model):
    __tablename__ = 'paymentterms'

    id = db.Column(db.Integer, primary_key=True)
    accountingHash = db.Column(db.String(30))
    accountingId = db.Column(db.String(36))
    activeFlag = db.Column(db.Integer, nullable=False)
    dateCreated = db.Column(db.DateTime)
    dateLastModified = db.Column(db.DateTime)
    defaultTerm = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Float(asdecimal=True))
    discountDays = db.Column(db.Integer)
    name = db.Column(db.String(31), nullable=False, unique=True)
    netDays = db.Column(db.Integer)
    nextMonth = db.Column(db.Integer)
    readOnly = db.Column(db.Integer, nullable=False)
    typeId = db.Column(db.Integer, nullable=False, index=True)


class Paymenttermstype(db.Model):
    __tablename__ = 'paymenttermstype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)


class Po(db.Model):
    __tablename__ = 'po'

    id = db.Column(db.Integer, primary_key=True)
    buyer = db.Column(db.String(100))
    buyerId = db.Column(db.Integer, nullable=False, index=True)
    carrierId = db.Column(db.Integer, nullable=False, index=True)
    carrierServiceId = db.Column(db.Integer, index=True)
    currencyId = db.Column(db.Integer, index=True)
    currencyRate = db.Column(db.Float(asdecimal=True))
    customerSO = db.Column(db.String(25))
    dateCompleted = db.Column(db.DateTime)
    dateConfirmed = db.Column(db.DateTime)
    dateCreated = db.Column(db.DateTime)
    dateFirstShip = db.Column(db.DateTime)
    dateIssued = db.Column(db.DateTime)
    dateLastModified = db.Column(db.DateTime)
    dateRevision = db.Column(db.DateTime)
    deliverTo = db.Column(db.String(30))
    email = db.Column(db.String(256))
    fobPointId = db.Column(db.Integer, nullable=False, index=True)
    locationGroupId = db.Column(db.Integer, nullable=False, index=True)
    note = db.Column(db.String)
    num = db.Column(db.String(25), nullable=False, unique=True)
    paymentTermsId = db.Column(db.Integer, nullable=False, index=True)
    phone = db.Column(db.String(256))
    qbClassId = db.Column(db.Integer, index=True)
    remitAddress = db.Column(db.String(90))
    remitCity = db.Column(db.String(30))
    remitCountryId = db.Column(db.Integer)
    remitStateId = db.Column(db.Integer)
    remitToName = db.Column(db.String(60))
    remitZip = db.Column(db.String(10))
    revisionNum = db.Column(db.Integer)
    shipTermsId = db.Column(db.Integer, nullable=False, index=True)
    shipToAddress = db.Column(db.String(90))
    shipToCity = db.Column(db.String(30))
    shipToCountryId = db.Column(db.Integer)
    shipToName = db.Column(db.String(60))
    shipToStateId = db.Column(db.Integer)
    shipToZip = db.Column(db.String(10))
    statusId = db.Column(db.Integer, nullable=False, index=True)
    taxRateId = db.Column(db.Integer, index=True)
    taxRateName = db.Column(db.String(31))
    totalIncludesTax = db.Column(db.Integer, nullable=False)
    totalTax = db.Column(db.Numeric(28, 9))
    typeId = db.Column(db.Integer, nullable=False, index=True)
    url = db.Column(db.String(256))
    username = db.Column(db.String(100))
    vendorContact = db.Column(db.String(30))
    vendorId = db.Column(db.Integer, nullable=False, index=True)
    vendorSO = db.Column(db.String(25))
    customFields = db.Column(db.JSON)
    issuedByUserId = db.Column(db.Integer, index=True)


class Postatu(db.Model):
    __tablename__ = 'postatus'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)


class Potype(db.Model):
    __tablename__ = 'potype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)


class Priority(db.Model):
    __tablename__ = 'priority'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)


class Qbclas(db.Model):
    __tablename__ = 'qbclass'
    __table_args__ = (
        db.Index('UKpewxai5b5r7949a2jybe14jy3', 'name', 'parentId'),
    )

    id = db.Column(db.Integer, primary_key=True)
    accountingHash = db.Column(db.String(30))
    accountingId = db.Column(db.String(36))
    activeFlag = db.Column(db.Integer, nullable=False)
    dateCreated = db.Column(db.DateTime)
    dateLastModified = db.Column(db.DateTime)
    name = db.Column(db.String(31), nullable=False, index=True)
    parentId = db.Column(db.Integer, nullable=False, index=True)


class Shipterm(db.Model):
    __tablename__ = 'shipterms'

    id = db.Column(db.Integer, primary_key=True)
    activeFlag = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(30), nullable=False, unique=True)
    readOnly = db.Column(db.Integer, nullable=False)


class So(db.Model):
    __tablename__ = 'so'

    id = db.Column(db.Integer, primary_key=True)
    billToAddress = db.Column(db.String(90))
    billToCity = db.Column(db.String(30))
    billToCountryId = db.Column(db.Integer)
    billToName = db.Column(db.String(60))
    billToStateId = db.Column(db.Integer)
    billToZip = db.Column(db.String(10))
    calCategoryId = db.Column(db.Integer, index=True)
    carrierId = db.Column(db.Integer, nullable=False, index=True)
    carrierServiceId = db.Column(db.Integer, index=True)
    cost = db.Column(db.Numeric(28, 9))
    createdByUserId = db.Column(db.Integer, index=True)
    currencyId = db.Column(db.Integer, index=True)
    currencyRate = db.Column(db.Float(asdecimal=True))
    customerContact = db.Column(db.String(30))
    customerId = db.Column(db.Integer, nullable=False, index=True)
    customerPO = db.Column(db.String(25))
    dateCalStart = db.Column(db.DateTime)
    dateCalEnd = db.Column(db.DateTime)
    dateCompleted = db.Column(db.DateTime)
    dateCreated = db.Column(db.DateTime)
    dateExpired = db.Column(db.DateTime)
    dateFirstShip = db.Column(db.DateTime)
    dateIssued = db.Column(db.DateTime)
    dateLastModified = db.Column(db.DateTime)
    dateRevision = db.Column(db.DateTime)
    email = db.Column(db.String(256))
    estimatedTax = db.Column(db.Numeric(28, 9))
    fobPointId = db.Column(db.Integer, nullable=False, index=True)
    locationGroupId = db.Column(db.Integer, nullable=False, index=True)
    mcTotalTax = db.Column(db.Numeric(28, 9))
    note = db.Column(db.String)
    num = db.Column(db.String(25), nullable=False, unique=True)
    paymentTermsId = db.Column(db.Integer, nullable=False, index=True)
    phone = db.Column(db.String(256))
    priorityId = db.Column(db.Integer, nullable=False, index=True)
    qbClassId = db.Column(db.Integer, index=True)
    registerId = db.Column(db.Integer)
    shipToResidential = db.Column(db.Integer, nullable=False)
    revisionNum = db.Column(db.Integer)
    salesman = db.Column(db.String(100))
    salesmanId = db.Column(db.Integer, nullable=False, index=True)
    salesmanInitials = db.Column(db.String(5))
    shipTermsId = db.Column(db.Integer, index=True)
    shipToAddress = db.Column(db.String(90))
    shipToCity = db.Column(db.String(30))
    shipToCountryId = db.Column(db.Integer)
    shipToName = db.Column(db.String(60))
    shipToStateId = db.Column(db.Integer)
    shipToZip = db.Column(db.String(10))
    statusId = db.Column(db.Integer, nullable=False, index=True)
    taxRate = db.Column(db.Float(asdecimal=True))
    taxRateId = db.Column(db.Integer, index=True)
    taxRateName = db.Column(db.String(31))
    toBeEmailed = db.Column(db.Integer, nullable=False)
    toBePrinted = db.Column(db.Integer, nullable=False)
    totalIncludesTax = db.Column(db.Integer, nullable=False)
    totalTax = db.Column(db.Numeric(28, 9))
    subTotal = db.Column(db.Numeric(28, 9), nullable=False,
                         server_default=db.FetchedValue())
    totalPrice = db.Column(db.Numeric(28, 9), nullable=False,
                           server_default=db.FetchedValue())
    typeId = db.Column(db.Integer, nullable=False, index=True)
    url = db.Column(db.String(256))
    username = db.Column(db.String(100))
    vendorPO = db.Column(db.String(25))
    customFields = db.Column(db.JSON)


class Sostatu(db.Model):
    __tablename__ = 'sostatus'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False, unique=True)


class Sotype(db.Model):
    __tablename__ = 'sotype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)


class Taxrate(db.Model):
    __tablename__ = 'taxrate'

    id = db.Column(db.Integer, primary_key=True)
    accountingHash = db.Column(db.String(30))
    accountingId = db.Column(db.String(36))
    activeFlag = db.Column(db.Integer, nullable=False)
    code = db.Column(db.String(5))
    dateCreated = db.Column(db.DateTime)
    dateLastModified = db.Column(db.DateTime)
    defaultFlag = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(256))
    name = db.Column(db.String(31), nullable=False, unique=True)
    orderTypeId = db.Column(db.Integer, index=True)
    rate = db.Column(db.Float(asdecimal=True))
    taxAccountId = db.Column(db.Integer, index=True)
    typeCode = db.Column(db.String(25))
    typeId = db.Column(db.Integer, nullable=False, index=True)
    unitCost = db.Column(db.Numeric(28, 9))
    vendorId = db.Column(db.Integer, index=True)


class Taxratetype(db.Model):
    __tablename__ = 'taxratetype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)


class Vendor(db.Model):
    __tablename__ = 'vendor'

    id = db.Column(db.Integer, primary_key=True)
    accountId = db.Column(db.Integer, nullable=False, index=True)
    accountNum = db.Column(db.String(30), index=True)
    accountingHash = db.Column(db.String(30))
    accountingId = db.Column(db.String(36))
    activeFlag = db.Column(db.Integer, nullable=False)
    creditLimit = db.Column(db.Numeric(28, 9))
    currencyId = db.Column(db.Integer, index=True)
    currencyRate = db.Column(db.Float(asdecimal=True))
    dateEntered = db.Column(db.DateTime)
    dateLastModified = db.Column(db.DateTime)
    defaultCarrierId = db.Column(db.Integer, nullable=False, index=True)
    defaultCarrierServiceId = db.Column(db.Integer, index=True)
    defaultPaymentTermsId = db.Column(db.Integer, nullable=False, index=True)
    defaultShipTermsId = db.Column(db.Integer, nullable=False, index=True)
    lastChangedUser = db.Column(db.String(100))
    leadTime = db.Column(db.Integer)
    minOrderAmount = db.Column(db.Numeric(28, 9))
    name = db.Column(db.String(41), nullable=False, unique=True)
    note = db.Column(db.String(256))
    statusId = db.Column(db.Integer, nullable=False, index=True)
    sysUserId = db.Column(db.Integer)
    taxRateId = db.Column(db.Integer, index=True)
    url = db.Column(db.String(256))
    customFields = db.Column(db.JSON)


class Vendorstatu(db.Model):
    __tablename__ = 'vendorstatus'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False, unique=True)


class NuraSoitemPoitemMap(db.Model):
    __tablename__ = 'nura_soitem_poitem_map'
    __table_args__ = (
        db.Index('index', 'soitemid', 'poitemid', 'allocateTypeId'),
    )

    id = db.Column(db.Integer, primary_key=True)
    soitemid = db.Column(db.Integer, nullable=False)
    poitemid = db.Column(db.Integer)
    created = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))
    qty = db.Column(db.DECIMAL(28, 9), nullable=False)
    userid = db.Column(db.Integer, nullable=False)
    allocateTypeId = db.Column(db.Integer, nullable=False)


class NuraPoItemInfo(db.Model):
    __tablename__ = 'nura_po_item_info'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    poitemid = db.Column(db.Integer, nullable=False, index=True)
    transport = db.Column(db.VARCHAR(45))
    priceBeforeNeg = db.Column(db.DECIMAL(28, 4))
    priceAfterNeg = db.Column(db.DECIMAL(28, 0))
    etd = db.Column(db.DateTime)
    eta = db.Column(db.DateTime)
    coaReq = db.Column(db.VARCHAR(45))
    coaCheck = db.Column(db.VARCHAR(45))
    labelCheck = db.Column(db.VARCHAR(45))
    shippingDoc = db.Column(db.VARCHAR(45))
    arrivalNotice = db.Column(db.VARCHAR(45))
    Customer = db.Column(db.VARCHAR(45))
    mfgBatch = db.Column(db.VARCHAR(45))
    nuraBatch = db.Column(db.VARCHAR(45))
    shipperQualified = db.Column(db.VARCHAR(45))
    qualificationNote = db.Column(db.VARCHAR(45))
    qcRelease = db.Column(db.VARCHAR(45))
    needNuraCoa = db.Column(db.VARCHAR(45))
    mfg = db.Column(db.VARCHAR(45))
    lotNuraCoa = db.Column(db.VARCHAR(45))

class NuraPoItemInfoDetail(db.Model):
    __tablename__ = 'nura_po_item_info_detail'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    poiteminfoid = db.Column(db.Integer, nullable=False)
    userid = db.Column(db.Integer, nullable=False)
    content = db.Column(db.VARCHAR(256), nullable=False)
    created = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))