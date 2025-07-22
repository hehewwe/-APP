/**
 * @name sms-classifier.js
 * @description 本地短信快速分类器。
 * 职责：快速将短信分为几个基本类别，不进行深度的风险分析。
 */

// 关键词库
const KEYWORDS = {
	VERIFICATION: ['验证码', 'verification code', 'código de verificación', 'mã xác minh', 'kode verifikasi', 'pin', '动态密码', '校验码', 'dynamic code'],
	PROMOTION_HIGH_PRIORITY: ['退订', '回t退订', '回t'],
	OPERATORS: ['10086', '10010', '10000'],
	BANK_KEYWORDS: ['银行', 'bank', '信用卡', '储蓄卡', '贷款', 'loan'],
	PROMOTION_GENERAL: ['优惠', '红包', '折扣', '特价', '活动', 'http', 'www.', '.com', '.cn', '点击', '登录', '领取']
};

/**
 * 对单条短信进行分类
 * @param {object} sms - 短信对象
 * @param {string} sms.sender - 发件人
 * @param {string} sms.body - 短信内容
 * @returns {string} 分类结果: '验证码', '通知', '推广', '可疑'
 */
function classify(sms) {
	// 防御式编程：确保 body 和 sender 即使为 null 或 undefined 也不会导致崩溃
	const lowerBody = (sms.body || '').toLowerCase();
	const lowerSender = (sms.sender || '').toLowerCase(); // 修复：使用 .sender 而不是 .address

	// 1. 最高优先级：识别验证码
	for (const keyword of KEYWORDS.VERIFICATION) {
		if (lowerBody.includes(keyword)) {
			return '验证码';
		}
	}

	// 2. 识别运营商和银行通知
	if (KEYWORDS.OPERATORS.some(op => lowerSender.startsWith(op)) || KEYWORDS.BANK_KEYWORDS.some(kw => lowerBody.includes(kw) || sms.body.includes(kw))) {
		// 检查是否包含推广退订信息，如果是，则归为推广
		if (KEYWORDS.PROMOTION_HIGH_PRIORITY.some(kw => lowerBody.includes(kw))) {
			return '推广';
	}
		return '通知';
	}
	
	// 3. 识别106开头的服务号
	if (lowerSender.startsWith('106')) {
		// 进一步判断内容
		if (KEYWORDS.PROMOTION_HIGH_PRIORITY.some(kw => lowerBody.includes(kw))) {
			return '推广';
		}
		// 如果包含大量推广性关键词，也认为是推广
		if (KEYWORDS.PROMOTION_GENERAL.some(kw => lowerBody.includes(kw))) {
			return '推广';
		}
		// 否则认为是普通通知
		return '通知';
	}

	// 4. 默认分类
	// 如果包含推广关键词，归为推广
	if (KEYWORDS.PROMOTION_GENERAL.some(kw => lowerBody.includes(kw))) {
		return '推广';
	}

	// 5. 其他所有情况，暂时归为其他
	return '其他';
}

export default {
	classify
}; 