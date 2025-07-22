from flask import Flask,request,jsonify,session
import os
import requests
from flask_cors import CORS

app = Flask(__name__)#创建Flask应用程序实例
app.secret_key = os.urandom(24)#使用session前必须设置一个密钥 更安全的随机密钥
CORS(app, supports_credentials=True)  # 支持跨域



# 临时存储用户数据（实际项目替换）
temp_users = {
    "13800138000": {"password": "123456"}
}

@app.route("/test/my/first",methods=["POST"])
def first_post():
    try:
        #检查登录状态
        if 'username' not in session:
            return jsonify(msg="请先登录",code=401),401
        my_json = request.get_json()
        print("收到请求数据：",my_json)
        get_number = my_json.get("案件编号")
        get_text = my_json.get("案情描述")
        get_classify = my_json.get("案件类别")
        if not all([get_number,get_text,get_classify]):
            return jsonify(msg="缺少参数",code=400),400

        #构造模型输入
        model_input = {"text":get_text,"case_id":get_number}
        #调用模型
        try:
            response = requests.post(json=model_input,timeout=5)
            response.raise_for_status()
            model_result = response.json()
        except Exception as e:
            print("模型服务异常：", e)
            return jsonify(msg="模型服务异常", code=503), 503

        return jsonify(
            code=200,
            msg="处理成功",
            data={
                "案件编号":get_number,
                "案情描述":get_text,
                "案件类别":get_classify,
                "处理状态":"已接收",
                "模型分析结果":{
            "是否诈骗":model_result["is_fraud"],
            "诈骗类型":model_result["fraud_type"]
                }
            }
        )
        # return "good"
    except Exception as e:
        print("处理出错",e)
        return jsonify(msg="出错了哦，请查看是否正确访问",code=500),500

#设置登录、检查登录状态和退出登录的三个接口
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
        user = temp_users.get(username)
        if user and user["password"] == password:
            # 如果验证通过，保存登录状态在session中
            session["username"] = username
            return jsonify(
                code=200,
                msg="登录成功",
                data={
                    "username": username
                }
            )
        else:
            return jsonify(msg="账号或密码错误", code=401), 401
    except Exception as e:
        print("登录出错:", e)
        return jsonify(msg="登录失败", code=500), 500

#检查登录状态
@app.route("/session",methods=["GET"])
def check_session():
    username = session.get("username")
    if username is not None:
        #中间可以加操作逻辑、数据库什么的
        return jsonify(username=username)
    else:
        return jsonify(msg="出错了，没登录",code=401),401

#退出登录
@app.route("/try/logout",methods=["GET"])
def logout():
    session.clear()
    return jsonify(msg="成功退出登录!",code=200),200

# 为App端诈骗信息识别功能提供一个需要登录的接口
@app.route("/analyze_text", methods=["POST"])
def analyze_text_for_app():
    try:
        # 增加登录验证
        if 'username' not in session:
            return jsonify(msg="请先登录后再使用本功能", code=401), 401

        my_json = request.get_json()
        get_text = my_json.get("text")
        if not get_text:
            return jsonify(msg="缺少text参数", code=400), 400

        # 构造一个临时的案件编号，改为随机6位数字
        import random
        case_id = str(random.randint(100000, 999999))
        
        # --- 升级版AI分析逻辑（直接在此实现） ---
        
        # 定义诈骗类别及其关键词
        fraud_categories = {
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
            "网络婚恋、交友类（非虚假网络投资理财类）": ["网恋", "交友", "杀猪盘", "感情投资"],
            "网黑案件": ["网黑", "曝光你", "黑料"]
        }

        is_fraud = False
        fraud_type = "正常信息" # 默认为正常信息

        # 遍历所有类别进行匹配
        for category, keywords in fraud_categories.items():
            for keyword in keywords:
                if keyword in get_text:
                    is_fraud = True
                    fraud_type = category
                    break # 找到一个匹配就跳出内层循环
            if is_fraud:
                break # 找到一个匹配就跳出外层循环

        # --- 格式化返回结果 ---
        if is_fraud:
            analysis_detail = f"经分析，该信息高度疑似'{fraud_type}'类型诈骗，请务必警惕，切勿转账或透露个人信息。"
        else:
            analysis_detail = "经分析，未发现明显的诈骗特征，但仍需保持警惕。"

        # 返回符合新需求的JSON格式
        return jsonify({
            "编号": case_id,
            "诈骗类别": fraud_type,
            "诈骗信息": analysis_detail
        })

    except Exception as e:
        print("处理/analyze_text时出错", e)
        return jsonify(msg="服务器内部错误", code=500), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)#启动Flask开发服务器,任何人都可以访问
