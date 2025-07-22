/**
 * @name advanced-risk-analyzer.js
 * @description 高级风险分析引擎（接口 & 模拟实现）
 * 职责：接收短信，进行深度分析，并返回详细的风险报告。
 * 这是为您的团队预留的接口。
 */

import alertManager from './alert-manager.js'; // 引入预警管理器

// 模拟的关键词和风险类型映射
const MOCK_RISK_PATTERNS = {
	'高风险': ['银行', '账户', '冻结', '验证', '转账', '黑名单', 'www.bank-risk.com'],
	'中风险': ['中奖', '澳门', '赌场', '投注', '包裹', '地址不详', 't.cn/'],
	'低风险': ['优惠', '红包', '折扣', '特价', '活动', '退订']
};

const MOCK_RISK_TYPES = {
	'高风险': ['金融诈骗', '身份冒充'],
	'中风险': ['钓鱼链接', '博彩广告'],
	'低风险': ['营销推广']
};

/**
 * 【接口】分析短信的风险
 * @param {Array<Object>} messages - 需要分析的短信对象数组
 * @param {string} messages[].id - 短信的唯一ID
 * @param {string} messages[].sender - 发件人
 * @param {string} messages[].body - 短信内容
 * @param {number} messages[].date - 短信的Unix时间戳
 * @returns {Promise<Array<Object>>} 一个Promise，解析后返回风险结果数组
 */
async function analyze(messages) {
	// 1. 模拟网络请求延迟
	console.log('[高级分析引擎] 接收到分析任务:', messages);
	await new Promise(resolve => setTimeout(resolve, 1500)); // 模拟1.5秒的分析耗时

	const results = messages.map(sms => {
		// 1.5. 新增：白名单检查
		if (alertManager.isSenderInSafelist(sms.sender)) {
			console.log(`[高级分析引擎] 发件人 ${sms.sender} 在白名单中，跳过分析。`);
			return null;
		}

		const lowerBody = sms.body.toLowerCase();
		let riskLevel = null;

		// 2. 模拟分析逻辑：根据关键词匹配风险
		if (MOCK_RISK_PATTERNS['高风险'].some(p => lowerBody.includes(p))) {
			riskLevel = 'high';
		} else if (MOCK_RISK_PATTERNS['中风险'].some(p => lowerBody.includes(p))) {
			riskLevel = 'medium';
		} else if (MOCK_RISK_PATTERNS['低风险'].some(p => lowerBody.includes(p))) {
			riskLevel = 'low';
		}

		// 3. 如果识别出风险，构建返回结果
		if (riskLevel) {
			const riskType = MOCK_RISK_TYPES[riskLevel === 'high' ? '高风险' : riskLevel === 'medium' ? '中风险' : '低风险'][0] || '未知类型';
			
			// 合并原短信信息和分析结果
			return {
				...sms, // 包含 id, sender, body, date
				riskLevel: riskLevel,
				riskType: riskType,
				suggestion: `[模拟建议] 此消息被判定为${riskType}，请谨慎处理。`
			};
		}

		return null; // 如果没有风险，返回null
	}).filter(Boolean); // 过滤掉没有风险的结果 (null)

	console.log('[高级分析引擎] 分析完成，返回结果:', results);
	return results;
}


export default {
	analyze
}; 