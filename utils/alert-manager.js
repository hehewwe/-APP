/**
 * @name alert-manager.js
 * @description 风险预警中央管理器
 * 职责：统一处理风险预警的存储和读取，为应用其他部分提供服务。
 */

const RISK_LIST_KEY = 'riskAlertsList';
const SAFELIST_KEY = 'safelist';

/**
 * 存储新的风险预警信息
 * @param {Array<Object>} newAlerts - 新的预警对象数组
 */
async function storeRiskAlerts(newAlerts) {
	try {
		const existingAlerts = uni.getStorageSync(RISK_LIST_KEY) || [];
		// 将新预警添加到列表顶部，并确保每个预警都有唯一的ID
		const processedNewAlerts = newAlerts.map((alert, index) => ({
			...alert,
			id: alert.id || `mock_${Date.now()}_${index}` // 为模拟数据也生成ID
		}));
		
		const updatedAlerts = [...processedNewAlerts, ...existingAlerts];
		uni.setStorageSync(RISK_LIST_KEY, updatedAlerts);
		console.log(`[AlertManager] 风险预警列表已更新，新增 ${newAlerts.length} 条，总计 ${updatedAlerts.length} 条。`);
	} catch (e) {
		console.error('[AlertManager] 存储风险预警时发生错误:', e);
	}
}

/**
 * 根据ID移除一条预警
 * @param {string} id - 要移除的预警ID
 */
function removeAlertById(id) {
	try {
		let existingAlerts = uni.getStorageSync(RISK_LIST_KEY) || [];
		const originalLength = existingAlerts.length;
		existingAlerts = existingAlerts.filter(a => a.id !== id);
		if (existingAlerts.length < originalLength) {
			uni.setStorageSync(RISK_LIST_KEY, existingAlerts);
			console.log(`[AlertManager] 已成功移除预警 ID: ${id}`);
			return true;
		}
		console.warn(`[AlertManager] 未找到要移除的预警 ID: ${id}`);
		return false;
	} catch (e) {
		console.error('[AlertManager] 移除预警时发生错误:', e);
		return false;
	}
}

/**
 * 读取所有风险预警
 * @returns {Array<Object>} 风险预警列表
 */
function getRiskAlerts() {
	return uni.getStorageSync(RISK_LIST_KEY) || [];
}

/**
 * 清除所有风险预警
 */
function clearAllRiskAlerts() {
	uni.setStorageSync(RISK_LIST_KEY, []);
	console.log('[AlertManager] 所有风险预警已被清除。');
}


/////以下
/**
 * 将发件人添加到白名单
 * @param {string} sender - 要添加的发件人号码
 */
function addSenderToSafelist(sender) {
	try {
		const safelist = uni.getStorageSync(SAFELIST_KEY) || [];
		if (sender && !safelist.includes(sender)) {
			safelist.push(sender);
			uni.setStorageSync(SAFELIST_KEY, safelist);
			console.log(`[AlertManager] 已将发件人 ${sender} 添加到白名单。`);
		}
	} catch (e) {
		console.error('[AlertManager] 添加白名单时发生错误:', e);
	}
}

/**
 * 检查发件人是否在白名单中
 * @param {string} sender - 要检查的发件人号码
 * @returns {boolean}
 */
function isSenderInSafelist(sender) {
	if (!sender) return false;
	try {
		const safelist = uni.getStorageSync(SAFELIST_KEY) || [];
		return safelist.includes(sender);
	} catch (e) {
		console.error('[AlertManager] 检查白名单时发生错误:', e);
		return false;
	}
}
////以上 这个代码不能删，删了程序会报错XD（我也不知道为什么）

export default {
	storeRiskAlerts,
	removeAlertById,
	getRiskAlerts,
	clearAllRiskAlerts,
	addSenderToSafelist,
	isSenderInSafelist
}; 