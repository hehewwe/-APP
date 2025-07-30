from flask import Flask,request,jsonify,session
import os
import requests
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy import inspect, func, text
from datetime import datetime, time

app = Flask(__name__)#创建Flask应用程序实例
app.secret_key = os.urandom(24)#使用session前必须设置一个密钥 更安全的随机密钥
CORS(app, supports_credentials=True)  # 支持跨域

#数据库配置（连接池）
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+pymysql://root:123456@localhost:3306/data?charset=utf8mb4'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,        # 连接池大小
    'max_overflow': 20,     # 溢出时最多再新建几个
    'pool_pre_ping': True   # 每次取出连接前先检测可用性
}
db = SQLAlchemy(app)

#映射已存在的user表
class User(db.Model):
    __tablename__ = 'user'
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role     = db.Column(db.String(10), nullable=False, default='user') # 'user' or 'admin'
#短信记录表
class SmsRecord(db.Model):
    __tablename__ = 'sms_record'
    id         = db.Column(db.BigInteger, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    case_no    = db.Column(db.String(6), unique=True, nullable=False)
    sms_text   = db.Column(db.Text, nullable=False)
    is_fraud   = db.Column(db.Boolean, nullable=False)
    fraud_type = db.Column(db.String(64))
    detail     = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

#编号发号器表
class CaseSerial(db.Model):
    __tablename__ = 'case_serial'
    category = db.Column(db.String(1), primary_key=True)  # 类别标识
    next_val = db.Column(db.Integer, nullable=False, default=1)  # 当前编号
    max_val = db.Column(db.Integer, nullable=False, default=99999)  # 最大值
def gen_case_no(category: str) -> str:
    """线程/进程安全的编号发号器，根据类别生成编号"""
    with db.session.begin_nested():
        row = db.session.execute(
            db.text("SELECT next_val FROM case_serial WHERE category = :category FOR UPDATE"),
            {"category": category}
        ).fetchone()
        if row is None:
            # 如果类别不存在，则初始化该类别
            db.session.execute(
                db.text("INSERT INTO case_serial (category, next_val, max_val) VALUES (:category, 1, 99999)"),
                {"category": category}
            )
            return f"{category}00001"
        next_val = row[0]
        if next_val > 99999:
            raise RuntimeError(f"类别 {category} 的编号已耗尽")
        db.session.execute(
            db.text("UPDATE case_serial SET next_val = next_val + 1 WHERE category = :category"),
            {"category": category}
        )
    return f"{category}{next_val:05d}"  # 格式化为类别字母+五位数字

#假设模型服务地址（后期替换为真实地址）
MODEL_URL = os.getenv("MODEL_URL", "http://model-service:8000/predict")

# 临时存储用户数据（实际项目替换）
temp_users = {
    "13800138000": {"password": "123456"}
}

#假设模型判断输出（关键词规则）
#定义诈骗类别及其关键词
FRAUD_CATEGORIES = {
    "刷单返利类": ["刷单", "返利", "点赞", "做任务"],
    "虚假网络投资理财类": ["投资", "理财", "导师", "内部消息", "高回报", "稳赚"],
    "冒充电商物流客服类": ["客服", "退款", "快递", "包裹丢失", "订单异常", "赔付"],
    "贷款、代办信用卡类": ["贷款", "额度", "信用卡", "黑户", "秒批", "无抵押"],
    "网络游戏产品虚假交易类": ["游戏币", "装备", "账号交易", "代练", "低价点券"],
    "虚假购物、服务类": ["免费领取", "中奖", "海外代购", "清仓"],
    "冒充公检法及政府机关类": ["公安", "法院", "检察院", "通缉", "配合调查", "逮捕令"],
    "虚假征信类": ["征信", "信用污点", "消除记录", "影响信用"],
    "冒充领导、熟人类": ["领导", "老板", "方便转账吗", "我是你领导", "有急事"],
    "冒充军警购物类诈骗": ["军需", "部队采购", "军官", "后勤"],
    "网络婚恋、交友类": ["网恋", "交友", "杀猪盘", "感情投资"],
    "网黑案件": ["网黑", "曝光你", "黑料"]
}
# 为每个类别分配一个字母标识
CATEGORY_CODE = {
    "刷单返利类": "a",
    "虚假网络投资理财类": "b",
    "冒充电商物流客服类": "c",
    "贷款、代办信用卡类": "d",
    "网络游戏产品虚假交易类": "e",
    "虚假购物、服务类": "f",
    "冒充公检法及政府机关类": "g",
    "虚假征信类": "h",
    "冒充领导、熟人类": "i",
    "冒充军警购物类诈骗": "j",
    "网络婚恋、交友类": "k",
    "网黑案件": "l"
}
def mock_model(text: str):
    is_fraud = False
    fraud_type = "正常信息"
    for category, keywords in FRAUD_CATEGORIES.items():
        if any(k in text for k in keywords):
            is_fraud = True
            fraud_type = category
            break
    detail = (
        f"经分析，该信息疑似“{fraud_type}”类型诈骗，请务必警惕，切勿转账或透露个人信息。"
        if is_fraud
        else "经分析，未发现明显诈骗特征，但仍需保持警惕。"
    )
    return {"is_fraud": is_fraud, "fraud_type": fraud_type, "analysis_detail": detail}

@app.route("/analyze_text",methods=["POST"])
def analyze_text():
    try:
        #检查登录状态
        if 'username' not in session:
            return jsonify(msg="请先登录",code=401),401
        data = request.get_json()
        get_text = data.get("短信文本")
        if not get_text:
        #if not all([get_number,get_text,get_classify]):
            return jsonify(msg="缺少参数",code=400),400

        #调用模型
        try:
            #构造模型输入
            model_input = {"text": get_text}
            response = requests.post(MODEL_URL,json=model_input,timeout=5)
            response.raise_for_status()
            model_result = response.json()
        except Exception as e:
            print("模型服务异常，使用假设规则测试：", e)
            model_result = mock_model(get_text)
            #print("模型服务异常：", e)
            #return jsonify(msg="模型服务异常", code=503), 503

        #解析模型返回
        is_fraud = model_result.get("is_fraud", False)
        fraud_type = model_result.get("fraud_type", "")
        analysis_detail = model_result.get("analysis_detail", "")

        #生成编号
        category_code = CATEGORY_CODE.get(fraud_type, "z")  # 默认为未知类别
        case_id = gen_case_no(category_code)

        # 保存到数据库
        user = User.query.filter_by(username=session["username"]).first()
        if user:
            record = SmsRecord(
                user_id=user.id,#用户
                case_no=case_id,#案件编号
                sms_text=get_text,#短信文本
                is_fraud=is_fraud,#模型分析得到的是否为诈骗结果
                fraud_type=fraud_type,#诈骗类型
                detail=analysis_detail#详细信息
            )
            db.session.add(record)
            db.session.commit()

        return jsonify({
            "编号":case_id,
            "诈骗类别":fraud_type,
            "诈骗信息":analysis_detail
        }),200
        # return "good"
    except Exception as e:
        print("处理出错",e)
        return jsonify(msg="出错了哦，请查看是否正确访问",code=500),500

#设置注册、登录、检查登录状态和退出登录的三个接口
#注册接口
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        # 非空校验
        if not all([username, password]):
            return jsonify(msg="账号和密码不能为空", code=400), 400
        # 先查重
        if User.query.filter_by(username=username).first():
            return jsonify(msg="该账号已存在", code=400), 400
        # 写入数据库
        db.session.add(User(username=username, password=password))
        db.session.commit()
        return jsonify(msg="注册成功", code=200), 200
    except Exception as e:
        db.session.rollback()
        print("注册异常:", e)
        return jsonify(msg="注册失败", code=500), 500

#登录 账号(手机号)username 密码password
@app.route("/try/login",methods=["POST"])
def login():
    try:
        get_data = request.get_json()
    #前端JSON:{"username":"13800138000","password":"123456"}
        username = get_data.get("username")
        password = get_data.get("password")
        if not all([username, password]):
            return jsonify(msg="账号和密码不能为空", code=400), 400
        # 查库
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return jsonify(msg="账号或密码输入错误", code=401), 401
        #登录成功，写session
        if user and user.password == password:
            # 如果验证通过，保存登录状态在session中
            session["username"] = username
            session["role"] = user.role # Store role in session
            return jsonify(
                code=200,
                msg="登录成功",
                data={
                    "username": username,
                    "role": user.role # Also return role on login
                }
            )
    except Exception as e:
        print("登录出错:", e)
        return jsonify(msg="登录失败", code=500), 500

#检查登录状态
@app.route("/session",methods=["GET"])
def check_session():
    username = session.get("username")
    role = session.get("role")
    if username is not None:
        #中间可以加操作逻辑、数据库什么的
        return jsonify(username=username, role=role)
    else:
        return jsonify(msg="出错了，没登录",code=401),401

#退出登录
@app.route("/try/logout",methods=["GET"])
def logout():
    session.clear()
    return jsonify(msg="成功退出登录!",code=200),200
# -------------------------------------------------
# ------------------- ADMIN API -------------------
# 权限装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            return jsonify(msg="无权访问，需要管理员权限", code=403), 403
        return f(*args, **kwargs)
    return decorated_function

# 获取所有允许操作的表模型
def get_allowed_models():
    return {
        'user': User,
        'sms_record': SmsRecord,
        'case_serial': CaseSerial
    }

# 通用查询接口
@app.route("/admin/data/<table_name>", methods=["GET"])
@admin_required
def get_table_data(table_name):
    models = get_allowed_models()
    if table_name not in models:
        return jsonify(msg="无效的表名", code=404), 404
    
    Model = models[table_name]
    
    # 修正：只有在表包含 id 字段时才按id排序
    if hasattr(Model, 'id'):
        # 修改为按ID升序
        items = Model.query.order_by(Model.id.asc()).all()
    else:
        # 对于没有id字段的表（如 case_serial），不进行特定排序
        items = Model.query.all()
    
    # 将ORM对象列表转换为字典列表以便JSON序列化
    def to_dict(obj):
        # created_at 需要特殊处理，因为它可能是 datetime 对象
        return {c.name: str(getattr(obj, c.name)) for c in obj.__table__.columns}

    results = [to_dict(item) for item in items]
    return jsonify(data=results, code=200), 200

# 通用删除接口
@app.route("/admin/data/<table_name>/<int:item_id>", methods=["DELETE"])
@admin_required
def delete_table_item(table_name, item_id):
    models = get_allowed_models()
    if table_name not in models:
        return jsonify(msg="无效的表名", code=404), 404
        
    Model = models[table_name]
    
    # 查找要删除的主项目
    item_to_delete = Model.query.get(item_id)
    
    if not item_to_delete:
        return jsonify(msg="指定的项目不存在", code=404), 404
        
    try:
        # 特殊处理：如果删除的是用户，先删除其所有关联的短信记录
        if table_name == 'user':
            SmsRecord.query.filter_by(user_id=item_id).delete()
            
        # 现在可以安全地删除主项目了
        db.session.delete(item_to_delete)
        db.session.commit()
        return jsonify(msg=f"成功删除 {table_name} 表中 id={item_id} 的项目及其关联数据", code=200), 200
    except Exception as e:
        db.session.rollback()
        print(f"删除失败: {e}")
        return jsonify(msg="删除失败，请查看服务器日志", code=500), 500

# 增强版记录查询接口
@app.route("/admin/sms_records", methods=["GET"])
@admin_required
def get_sms_records():
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        fraud_type = request.args.get('fraud_type', None, type=str)
        is_fraud = request.args.get('is_fraud', None, type=str)
        search_keyword = request.args.get('search_keyword', None, type=str)

        # 基础查询，并关联 user 表
        query = db.session.query(SmsRecord, User.username).join(User, SmsRecord.user_id == User.id)

        # 应用筛选条件
        if fraud_type:
            query = query.filter(SmsRecord.fraud_type == fraud_type)
        if is_fraud is not None:
            query = query.filter(SmsRecord.is_fraud == (is_fraud.lower() == 'true'))
        if search_keyword:
            query = query.filter(
                (SmsRecord.sms_text.ilike(f"%{search_keyword}%")) |
                (User.username.ilike(f"%{search_keyword}%"))
            )

        # 分页 (修改为按ID升序)
        pagination = query.order_by(SmsRecord.id.asc()).paginate(page=page, per_page=per_page, error_out=False)
        records = pagination.items
        
        results = []
        for record, username in records:
            item = {c.name: str(getattr(record, c.name)) for c in record.__table__.columns}
            item['username'] = username
            results.append(item)

        return jsonify({
            'data': results,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        }), 200

    except Exception as e:
        print(f"查询记录失败: {e}")
        return jsonify(msg="服务器查询出错", code=500), 500

# 新增：统计接口
@app.route("/admin/stats", methods=["GET"])
@admin_required
def get_stats():
    try:
        today_start = datetime.combine(datetime.today(), time.min)
        
        # 1. 今日新增记录
        today_new_records = db.session.query(func.count(SmsRecord.id)).filter(SmsRecord.created_at >= today_start).scalar()
        
        # 2. 诈骗记录总数
        total_fraud_records = db.session.query(func.count(SmsRecord.id)).filter(SmsRecord.is_fraud == True).scalar()
        
        # 3. 占比最高的类型
        top_fraud_type_query = db.session.query(
                SmsRecord.fraud_type, 
                func.count(SmsRecord.id).label('count')
            ).filter(SmsRecord.is_fraud == True)\
            .group_by(SmsRecord.fraud_type)\
            .order_by(text('count DESC'))\
            .first()

        top_fraud_type_info = {
            "type": top_fraud_type_query[0] if top_fraud_type_query else "无",
            "percentage": round((top_fraud_type_query[1] / total_fraud_records) * 100, 2) if top_fraud_type_query and total_fraud_records > 0 else 0
        }

        return jsonify({
            "today_new_records": today_new_records,
            "total_fraud_records": total_fraud_records,
            "top_fraud_type": top_fraud_type_info
        }), 200

    except Exception as e:
        print(f"获取统计数据失败: {e}")
        return jsonify(msg="服务器统计出错", code=500), 500

# 新增：一键重置接口
@app.route("/admin/reset_data", methods=["POST"])
@admin_required
def reset_data():
    try:
        # 使用事务确保操作的原子性
        with db.session.begin():
            # 1. 清空 sms_record 表
            db.session.execute(text("DELETE FROM sms_record"))
            # 2. 重置 case_serial 表的计数器
            db.session.execute(text("UPDATE case_serial SET next_val = 1"))
        
        # 如果上面的操作没有抛出异常，事务会自动提交
        return jsonify(msg="所有记录已清空，案件编号已重置", code=200), 200

    except Exception as e:
        # 如果发生任何错误，事务会自动回滚
        db.session.rollback()
        print(f"重置数据失败: {e}")
        return jsonify(msg="重置数据失败，请查看服务器日志", code=500), 500

# 新增：重置单个分类计数器的接口
@app.route("/admin/reset_category/<string:category_pk>", methods=["POST"])
@admin_required
def reset_category_counter(category_pk):
    try:
        item_to_update = CaseSerial.query.filter_by(category=category_pk).first()
        if not item_to_update:
            return jsonify(msg="指定的类别不存在", code=404), 404
        
        item_to_update.next_val = 1
        db.session.commit()
        return jsonify(msg=f"类别 '{category_pk}' 的计数器已成功归1", code=200), 200

    except Exception as e:
        db.session.rollback()
        print(f"重置分类计数器失败: {e}")
        return jsonify(msg="重置分类计数器失败，请查看服务器日志", code=500), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)#启动Flask开发服务器,任何人都可以访问
