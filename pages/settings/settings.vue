<template>
	<view class="settings-container">
		<scroll-view scroll-y class="scroll-view">
			<!-- 账号管理 -->
			<view class="list-section">
				<text class="list-title">账号管理</text>
				<view class="list-card">
					<view class="list-item" @click="handleAuthAction">
						<text class="item-title">{{ isLoggedIn ? `欢迎，${username}` : '点击登录' }}</text>
						<view class="item-extra">
							<text class="status-text">{{ isLoggedIn ? '退出登录' : '' }}</text>
							<text class="arrow">›</text>
						</view>
					</view>
				</view>
			</view>

			<!-- 通用设置 -->
			<view class="list-section">
				<text class="list-title">通用设置</text>
				<view class="list-card">
					<view class="list-item">
						<text class="item-title">短信读取权限</text>
						<view class="item-extra">
							<text class="status-text" :class="smsStatusClass">{{ smsPermissionStatusText }}</text>
						</view>
					</view>
					<view class="list-item" @click="clearCache">
						<text class="item-title">清理缓存</text>
						<view class="item-extra">
							<text class="right-text">{{ cacheSize }}</text>
						</view>
					</view>
					<view class="list-item" @click="checkUpdate">
						<text class="item-title">检查更新</text>
						<view class="item-extra">
							<text class="arrow">›</text>
						</view>
					</view>
				</view>
			</view>

			<!-- 关于 -->
			<view class="list-section">
				<text class="list-title">关于</text>
				<view class="list-card">
					<view class="list-item" @click="showContentModal('privacy')">
						<text class="item-title">隐私政策</text>
						<view class="item-extra">
							<text class="arrow">›</text>
						</view>
					</view>
					<view class="list-item" @click="showContentModal('terms')">
						<text class="item-title">用户协议</text>
						<view class="item-extra">
							<text class="arrow">›</text>
						</view>
					</view>
					<view class="list-item" @click="showContentModal('about')">
						<text class="item-title">关于我们</text>
						<view class="item-extra">
							<text class="right-text">{{ '版本 ' + appVersion }}</text>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 开发者测试工具 -->
			<view class="list-section">
				<text class="list-title">开发者测试工具</text>
				<view class="list-card">
					<view class="list-item" @click="injectMockAlerts">
						<text class="item-title">注入模拟预警</text>
						<view class="item-extra">
							<text class="arrow">›</text>
						</view>
					</view>
					<view class="list-item" @click="clearAllAlerts">
						<text class="item-title">清除所有预警</text>
						<view class="item-extra">
							<text class="arrow">›</text>
						</view>
					</view>
				</view>
			</view>

		</scroll-view>

		<!-- 内容模态弹窗 -->
		<view class="modal-overlay" v-if="isModalVisible" @click="closeModal">
			<view class="modal-content" @click.stop>
				<view class="modal-header">
					<text class="modal-title">{{ modalTitle }}</text>
					<text class="modal-close" @click="closeModal">✕</text>
				</view>
				<scroll-view scroll-y class="modal-body">
					<text class="modal-text">{{ modalContent }}</text>
				</scroll-view>
			</view>
		</view>

	</view>
</template>

<script>
	import config from '@/utils/config.js';
	import smsClassifier from '@/utils/sms-classifier.js';
	import advancedAnalyzer from '@/utils/advanced-risk-analyzer.js';
	import alertManager from '@/utils/alert-manager.js';

	const SMS_PERMISSION = 'android.permission.READ_SMS';

	export default {
		data() {
			return {
				smsPermissionStatus: 'checking', // checking, granted, denied
				appVersion: '1.0.0',
				isModalVisible: false,
				modalTitle: '',
				modalContent: '',
				isLoggedIn: false, // 登录状态
				username: '', // 用户名
			};
		},
		computed: {
			smsPermissionStatusText() {
				const statusMap = {
					checking: '检查中...',
					granted: '已授予',
					denied: '未授予'
				};
				return statusMap[this.smsPermissionStatus] || '未知';
			},
			smsStatusClass() {
				return {
					'status-granted': this.smsPermissionStatus === 'granted',
					'status-denied': this.smsPermissionStatus === 'denied'
				};
			}
		},
		onShow() {
			// #ifdef APP-PLUS
			this.checkSmsPermission();
			// #endif
			// 页面显示时检查登录状态
			this.checkLoginStatus();
		},
		onLoad() {
			// 监听登录状态变化
			uni.$on('user-log-changed', this.checkLoginStatus);
		},
		onUnload() {
			// 移除监听
			uni.$off('user-log-changed', this.checkLoginStatus);
		},
		methods: {
			checkSmsPermission() {
				// #ifdef APP-PLUS
				this.smsPermissionStatus = 'checking';
				console.log('[settings.vue] 通过尝试读取短信来验证权限...');
				try {
					const Uri = plus.android.importClass("android.net.Uri");
					const main = plus.android.runtimeMainActivity();
					const contentResolver = main.getContentResolver();
					const SMS_INBOX = Uri.parse("content://sms/");
					const projection = ["_id"]; // 只查询id列即可，目的只是为了测试是否能查询成功
			
					const cursor = plus.android.invoke(contentResolver, 'query', SMS_INBOX, projection, null, null, "date desc LIMIT 1");
			
					if (cursor) {
						// 只要能成功执行查询并获得cursor对象（即使是空的），就代表有权限
						plus.android.invoke(cursor, 'close');
						console.log('[settings.vue] 成功执行查询，权限已授予。');
						this.smsPermissionStatus = 'granted';
					} else {
						// 查询返回null，这不代表权限问题，但为了UI一致性，也认为是有权限的，因为没有抛出错误
						console.log('[settings.vue] 查询返回null，但未抛出异常，假定权限已授予。');
						this.smsPermissionStatus = 'granted';
					}
				} catch (e) {
					// 如果在查询过程中抛出任何异常，基本可以断定是权限问题
					console.error('[settings.vue] 尝试读取短信时发生错误，判定权限未授予。', JSON.stringify(e));
					this.smsPermissionStatus = 'denied';
				}
				// #endif
			},
			async injectMockAlerts() {
				uni.showLoading({
					title: '正在生成模拟数据...'
				});

				// 1. 定义10条更真实的模拟原始短信
				const mockRawSms = [{
					sender: '1069****4321',
					body: '【XX打车】您的周末出行券已到账，点击 http://promo.xx-taxi.com/c/123 领取，回T退订。'
				}, {
					sender: '95533',
					body: '【建设银行】您尾号8888的储蓄卡收入人民币2,500.00元，活期余额10000.00元。'
				}, {
					sender: '10086',
					body: '尊敬的客户，您的本月套餐已使用8.5GB，剩余1.5GB。超出后将按标准资费收取。'
				}, {
					sender: '快递员小张',
					body: '您的快递到了，放您家门口了，记得取一下。'
				}, {
					sender: '物业管理处',
					body: '温馨提示：本周六下午小区将进行电路检修，预计停电2小时，请提前做好准备。'
				}, {
					sender: '1069****9988',
					body: '【XX钱包】安全提醒：您正在申请尾号XX99的消费贷，金额50000元，验证码198432，切勿泄露。非本人操作请忽略。'
				}, {
					sender: '+852 **** 3456',
					body: '恭喜您！您的手机号已被香港“六合彩”中心抽中为幸运二等奖，获得奖金188万元及苹果手机一部，请速速访问 www.6h-vip.com 登记领取。'
				}, {
					sender: '法务部',
					body: '【XX仲裁委】通知：您涉及的一起网络借贷纠纷案已立案，如未在24小时内处理，将冻结您名下所有资产。详情请咨询 t.cn/AbcDefG'
				}, {
					sender: '1065****1111',
					body: '【XX航空】紧急通知：您预订的CA1234航班因机械故障已取消。我们为您办理了退票并给予300元补偿金，请点击 www.ca-refund-fly.com 办理。'
				}, {
					sender: '95588',
					body: '【工商银行】紧急通知：您的电子密码器即将于次日失效，请立即登录我行手机网站 wap.icbc-global-vip.com 进行安全更新，以免影响正常使用。'
				}].map((sms, index) => ({
					...sms,
					id: `mock_${Date.now()}_${index}`,
					date: Date.now() - 1000 * 60 * (index + 1) * 5, // 时间戳错开
					type: 1
				}));

				// 2. 模拟接收短信：更新全局短信列表
				const storedSms = uni.getStorageSync('monitoredSmsList') || [];
				const updatedSmsList = [...mockRawSms, ...storedSms];
				if (updatedSmsList.length > 200) { // 保持列表长度
					updatedSmsList.splice(200);
				}
				uni.setStorageSync('monitoredSmsList', updatedSmsList);
				uni.$emit('monitored-sms-updated'); // 通知“短信分析”页面更新
				console.log(`[设置页] 注入了${mockRawSms.length}条新短信到全局列表。`);


				// 3. 初步筛选出可疑短信
				const suspiciousSms = mockRawSms.filter(sms => {
					const category = smsClassifier.classify(sms);
					// 将“其他”类和包含可疑链接的“推广”类视为需要高级分析
					return category === '其他' || (category === '推广' && (sms.body.includes('t.cn') || sms.body.includes('.com')));
				});
				console.log(`[设置页] 初级引擎筛选出${suspiciousSms.length}条可疑短信。`);


				// 4. 交给高级引擎进行分析
				try {
					const riskAlerts = await advancedAnalyzer.analyze(suspiciousSms);
					console.log(`[设置页] 高级引擎分析完成，生成${riskAlerts.length}条风险预警。`);

					if (riskAlerts && riskAlerts.length > 0) {
						// 5. 存储最终的风险预警
						alertManager.storeRiskAlerts(riskAlerts);
						uni.hideLoading();
						uni.showToast({
							title: `成功注入${riskAlerts.length}条风险预警！`,
							icon: 'success'
						});
					} else {
						uni.hideLoading();
						uni.showToast({
							title: '未检测到新风险',
							icon: 'none'
						});
					}
				} catch (error) {
					uni.hideLoading();
					console.error('[设置页] 高级分析失败:', error);
					uni.showToast({
						title: '分析引擎出错',
						icon: 'error'
					});
				}
			},
			clearAllAlerts() {
				uni.showModal({
					title: '确认',
					content: '确定要清除所有风险预警数据吗？',
					success: (res) => {
						if (res.confirm) {
							alertManager.clearAllRiskAlerts();
							uni.showToast({ title: '预警已全部清除', icon: 'none' });
						}
					}
				});
			},
			clearCache() {
				uni.navigateTo({
					url: '/pages/settings/cleaning-cache'
				});
			},
			checkUpdate() {
				uni.showToast({ title: '已是最新版本', icon: 'none' });
			},
			formatContent(text, lineLength = 21) {
				// 辅助函数：将文本按指定长度换行
				const cleanText = text.replace(/\\n/g, ''); // 移除已有的换行符
				let result = '';
				for (let i = 0; i < cleanText.length; i += lineLength) {
					result += cleanText.substring(i, i + lineLength);
					if (i + lineLength < cleanText.length) {
						result += '\n';
					}
				}
				return result;
			},
			showContentModal(type) {
				if (type === 'privacy') {
					this.modalTitle = '隐私政策';
					const rawContent = `欢迎使用我们的应用！我们非常重视您的隐私。本政策将说明我们如何收集、使用、存储和保护您的个人信息。我们仅在必要时，为实现产品功能，才会收集您的信息，例如，我们需要读取您的短信列表以进行安全分析。所有分析均在您的设备本地完成，您的任何短信内容都不会被上传到我们的服务器。我们承诺会采取严格的安全措施保护您的数据安全。`;
					this.modalContent = this.formatContent(rawContent);
				} else if (type === 'terms') {
					this.modalTitle = '用户协议';
					const rawContent = `感谢您使用本应用。使用本产品即表示您同意本协议。您同意授予应用读取您的短信内容的权限，以便进行安全分析和风险预警。您理解并同意，所有分析处理均在您的设备上本地进行，我们不会存储或上传您的个人短信。本服务旨在帮助您识别潜在的诈骗、钓鱼等风险短信，但分析结果仅供参考，我们不对此承担任何法律责任。请勿将本应用用于任何非法目的。`;
					this.modalContent = this.formatContent(rawContent);
				} else if (type === 'about') {
					this.modalTitle = '关于我们';
					const rawContent = `我们是一款专注于保护用户免受短信诈骗威胁的安全应用。我们的核心技术能够在您的设备上，离线分析收到的短信，及时发现钓鱼链接、恶意软件、诈骗话术等风险，并向您发出预警。我们的使命是为您提供一个纯净、安全的数字通信环境。感谢您的信任和支持!                \n当前版本: ${this.appVersion}`;
					this.modalContent = this.formatContent(rawContent);
				}
				this.isModalVisible = true;
			},
			closeModal() {
				this.isModalVisible = false;
			},
			checkLoginStatus() {
				uni.request({
					url: `${config.BASE_URL}/session`,
					success: (res) => {
						if (res.statusCode === 200 && res.data.username) {
							this.isLoggedIn = true;
							this.username = res.data.username;
						} else {
							this.isLoggedIn = false;
							this.username = '';
						}
					},
					fail: () => {
						this.isLoggedIn = false;
						this.username = '';
					}
				});
			},
			handleAuthAction() {
				if (this.isLoggedIn) {
					// 如果已登录，则执行退出操作
					uni.showModal({
						title: '提示',
						content: '确定要退出登录吗？',
						success: (res) => {
							if (res.confirm) {
								this.logout();
							}
						}
					});
				} else {
					// 如果未登录，则跳转到登录页面
					uni.navigateTo({
						url: '/pages/settings/login'
					});
				}
			},
			logout() {
				uni.request({
					url: `${config.BASE_URL}/try/logout`,
					success: (res) => {
						uni.showToast({
							title: '已退出登录',
							icon: 'success'
						});
						this.isLoggedIn = false;
						this.username = '';
						uni.$emit('user-log-changed');
					}
				});
			}
		}
	}
</script>

<style scoped>
	.settings-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background-color: #f2f2f7;
	}

	.scroll-view {
		flex: 1;
		box-sizing: border-box;
	}

	.list-section {
		margin-top: 20rpx;
	}

	.list-title {
		display: block;
		margin: 0 30rpx 10rpx;
		font-size: 28rpx;
		color: #666;
		padding-left: 10rpx;
	}

	.list-card {
		background-color: #fff;
		border-radius: 12rpx;
		margin: 0 20rpx;
		overflow: hidden;
	}

	.list-item {
		display: flex;
		align-items: center;
		padding: 28rpx 30rpx;
		position: relative;
		transition: background-color 0.2s;
	}

	.list-item:active {
		background-color: #f7f7f7;
	}

	.list-item:not(:last-child)::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 30rpx;
		right: 0;
		height: 1px;
		background-color: #e5e5e5;
		transform: scaleY(0.5);
	}

	.permission-display {
		justify-content: space-between;
	}

	.item-title {
		font-size: 32rpx;
		color: #333;
	}

	.item-extra {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		flex-grow: 1;
	}

	.right-text {
		font-size: 30rpx;
		color: #888;
		margin-left: auto;
	}

	.arrow {
		font-size: 36rpx;
		color: #ccc;
		margin-left: 10rpx;
	}

	.status-text {
		font-size: 30rpx;
	}

	.status-granted {
		color: #28a745;
		/* Green */
	}

	.status-denied {
		color: #dc3545;
		/* Red */
	}
	
	.permission-button {
		margin-left: 20rpx;
		background-color: #007aff;
		color: white;
		border: none;
		border-radius: 30rpx;
		font-size: 24rpx;
		padding: 8rpx 20rpx;
		line-height: 1.2;
		height: auto;
	}
	
	.permission-button:active {
		background-color: #0056b3;
	}

/* 模态弹窗样式 */
.modal-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-color: rgba(0, 0, 0, 0.6);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
	animation: fade-in 0.3s ease;
}

.modal-content {
	width: 85%;
	max-width: 400px;
	height: 60%;
	background-color: #fff;
	border-radius: 16rpx;
	display: flex;
	flex-direction: column;
	overflow: hidden;
	animation: slide-up 0.3s ease;
}

.modal-header {
	padding: 24rpx 30rpx;
	border-bottom: 1rpx solid #e5e5e5;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.modal-title {
	font-size: 34rpx;
	font-weight: bold;
	color: #333;
}

.modal-close {
	font-size: 40rpx;
	color: #999;
	font-weight: lighter;
}

.modal-body {
	flex: 1;
	padding: 30rpx;
	line-height: 1.6;
}

.modal-text {
	font-size: 28rpx;
	color: #555;
	white-space: pre-wrap; /* 保持文本换行 */
}

@keyframes fade-in {
	from { opacity: 0; }
	to { opacity: 1; }
}

@keyframes slide-up {
	from { transform: translateY(50px); }
	to { transform: translateY(0); }
}
</style> 