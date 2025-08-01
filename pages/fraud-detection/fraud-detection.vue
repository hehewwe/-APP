<template>
	<view class="fraud-detection-container">
		<view class="header">
			<view class="back-button" @click="goBack">
				<text class="icon">←</text>
			</view>
			<view class="title">智能检测</view>
			<view class="subtitle">AI智能分析，识别诈骗风险</view>
		</view>
		
		<view class="content">
			<view class="input-section">
				<view class="input-label">请输入需要分析的内容：</view>
				<textarea class="input-area" v-model="textToAnalyze" placeholder="在此输入可疑短信内容..." />
				<view class="char-count">{{textToAnalyze.length}}/500字</view>
			</view>
			
			<view class="button-section">
				<button class="analyze-button" @click="analyzeText" :disabled="!textToAnalyze.trim()">
					<text class="button-icon">🔍</text>
					<text>开始分析</text>
				</button>
			</view>
			
			<view class="result-section" v-if="hasResult">
				<view class="result-header">
					<text class="result-title">分析结果</text>
					<!-- 根据后端返回的“诈骗类别”动态显示标签 -->
					<text :class="['result-tag', resultClass]">{{result.诈骗类别}}</text>
				</view>
				
				<view class="result-content">
					<!-- 新增：显示分析编号 -->
					<view class="result-item">
						<text class="item-label">分析编号：</text>
						<text class="item-value">{{result.编号}}</text>
					</view>
					<!-- 修改：只显示一个核心的诈骗类别 -->
					<view class="result-item">
						<text class="item-label">信息类别：</text>
						<text :class="['item-value', resultClass]">{{result.诈骗类别}}</text>
					</view>
					<!-- 修改：显示诈骗信息详情 -->
					<view class="result-item analysis-detail">
						<text class="item-label">分析详情：</text>
						<text class="item-value detail-text">{{result.诈骗信息}}</text>
					</view>
				</view>
				
				<!-- 诈骗信息举报引导 -->
				<view class="report-guide" v-if="resultClass === 'high-risk'">
					<view class="report-info">
						<text class="report-icon">🚨</text>
						<view class="report-text">
							<text class="report-title">发现诈骗信息？</text>
							<text class="report-desc">快速举报，帮助更多人避免受骗</text>
						</view>
					</view>
					<button class="report-button" @click="goToReport">立即举报</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import config from '@/utils/config.js';

	export default {
		data() {
			return {
				textToAnalyze: '',
				hasResult: false,
				// 更新 result 对象结构以匹配新API的返回
				result: {
					"编号": "",
					"诈骗类别": "",
					"诈骗信息": ""
				}
			}
		},
		onShow() {
			// 每次进入页面时都检查登录状态
			this.checkLoginStatus();
		},
		onLoad(options) {
			// 如果有传递文本参数，则自动填充到输入框
			if (options.text) {
				this.textToAnalyze = decodeURIComponent(options.text);
				// 如果有文本，自动开始分析
				if (this.textToAnalyze.trim()) {
					this.analyzeText();
				}
			}
		},
		computed: {
			// 这个计算属性可以简化或移除，但为了兼容性和样式我们暂时保留
			// 它会根据诈骗类别是否为“正常信息”来决定样式
			resultClass() {
				if (this.result.诈骗类别 && this.result.诈骗类别 !== '正常信息') {
					return 'high-risk'; // 所有非正常信息都标记为高风险样式
				} else {
					return 'safe'; // 正常信息使用安全样式
				}
			}
		},
		methods: {
			checkLoginStatus() {
				uni.request({
					url: `${config.BASE_URL}/session`,
					success: (res) => {
						if (res.statusCode !== 200 || !res.data.username) {
							// 如果未登录，则提示并跳转到登录页
							uni.showToast({
								title: '请先登录',
								icon: 'none',
								duration: 1500
							});
							setTimeout(() => {
								uni.navigateTo({
									url: '/pages/settings/login'
								});
							}, 1500);
						}
					},
					fail: () => {
						// 网络失败也视为未登录，跳转到登录页
						uni.showToast({
							title: '请先登录',
							icon: 'none',
							duration: 1500
						});
						setTimeout(() => {
							uni.navigateTo({
								url: '/pages/settings/login'
							});
						}, 1500);
					}
				});
			},
			goBack() {
				uni.navigateBack();
			},
			analyzeText() {
				if (!this.textToAnalyze.trim()) {
					uni.showToast({
						title: '请输入要分析的文本',
						icon: 'none'
					});
					return;
				}
				
				uni.showLoading({
					title: '正在分析中...'
				});
				
				// 使用 uni.request 调用后端 API
				uni.request({
					url: `${config.BASE_URL}/analyze_text`,
					method: 'POST',
					data: {
						"短信文本": this.textToAnalyze
					},
					success: (res) => {
						if (res.statusCode === 200) {
							console.log('从服务器收到的分析结果:', res.data);
							this.result = res.data;
							this.hasResult = true;
						} else {
							// 处理非200的成功请求，例如400, 500等
							uni.showToast({
								title: `分析失败: ${res.data.msg || '未知错误'}`,
								icon: 'none'
							});
						}
					},
					fail: (err) => {
						// 处理网络层面的失败
						console.error('API请求失败:', err);
						uni.showToast({
							title: '分析服务连接失败',
							icon: 'error'
						});
					},
					complete: () => {
						// 无论成功或失败，最后都隐藏加载提示
						uni.hideLoading();
					}
				});
			},
			
			goToReport() {
				// 创建分类映射表
				const categoryMapping = {
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
				};
				
				// 获取对应的分类代码
				const typeCode = categoryMapping[this.result.诈骗类别] || 'a';
				
				// 构建跳转URL，传递检测结果
				const params = {
					type: typeCode,
					content: encodeURIComponent(this.textToAnalyze.trim()),
					source: '智能检测系统'
				};
				
				const queryString = Object.keys(params).map(key => `${key}=${params[key]}`).join('&');
				
				uni.navigateTo({
					url: `/pages/safety-center/report-page?${queryString}`
				});
			}
		}
	}
</script>

<style>
	.fraud-detection-container {
		padding: 0;
		background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
		min-height: 100vh;
		display: flex;
		flex-direction: column;
        padding-top: 75rpx;
        padding-bottom: 100rpx;        
	}
	
	.header {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 30rpx;
		background: rgba(255, 255, 255, 0.95);
		border-bottom: 1rpx solid #eee;
		position: relative;
		backdrop-filter: blur(10rpx);
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
	}
	
	.back-button {
		position: absolute;
		left: 30rpx;
		width: 60rpx;
		height: 60rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.icon {
		font-size: 40rpx;
		font-weight: bold;
	}
	
	.title {
		text-align: center;
		font-size: 36rpx;
		font-weight: bold;
		color: #2c3e50;
		margin-bottom: 8rpx;
		text-shadow: 0 2rpx 4rpx rgba(44, 62, 80, 0.1);
	}
	
	.subtitle {
		font-size: 24rpx;
		color: #7f8c8d;
		text-align: center;
	}
	
	.content {
		flex: 1;
		padding: 30rpx;
	}
	
	.input-section {
		background: white;
		border-radius: 20rpx;
		padding: 30rpx;
		margin-bottom: 30rpx;
		box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.1);
	}
	
	.input-label {
		font-size: 28rpx;
		font-weight: bold;
		color: #2c3e50;
		margin-bottom: 15rpx;
	}
	
	.input-area {
		width: 100%;
		height: 300rpx;
		padding: 20rpx;
		font-size: 26rpx;
		border: 2rpx solid #e9ecef;
		border-radius: 12rpx;
		background: #f8f9fa;
		box-sizing: border-box;
		line-height: 1.5;
		transition: border-color 0.3s;
	}
	
	.input-area:focus {
		border-color: #3498db;
		background: #fff;
	}
	
	.char-count {
		text-align: right;
		font-size: 22rpx;
		color: #6c757d;
		margin-top: 10rpx;
	}
	
	.button-section {
		margin-bottom: 30rpx;
	}
	
	.analyze-button {
		width: 100%;
		height: 88rpx;
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #3498db, #2980b9);
		color: #fff;
		font-size: 32rpx;
		font-weight: bold;
		border-radius: 44rpx;
		border: none;
		margin: 0 auto;
		box-shadow: 0 4rpx 12rpx rgba(52, 152, 219, 0.3);
		transition: all 0.3s;
	}
	
	.analyze-button[disabled] {
		background: #bdc3c7;
		color: #7f8c8d;
		box-shadow: none;
	}
	
	.analyze-button::after {
		border: none;
	}
	
	.button-icon {
		font-size: 32rpx;
		margin-right: 8rpx;
	}
	
	.result-section {
		background: white;
		border-radius: 20rpx;
		padding: 30rpx;
		box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.1);
		animation: slideInUp 0.3s ease-out;
	}
	
	@keyframes slideInUp {
		from {
			opacity: 0;
			transform: translateY(30rpx);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
	
	.result-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 30rpx;
		padding-bottom: 20rpx;
		border-bottom: 1rpx solid #eee;
	}
	
	.result-title {
		font-size: 32rpx;
		font-weight: bold;
	}
	
	.result-tag {
		padding: 8rpx 20rpx;
		border-radius: 30rpx;
		font-size: 26rpx;
		color: #fff;
	}
	
	.high-risk {
		background-color: #F44336;
	}
	
	.medium-risk {
		background-color: #FF9800;
	}
	
	.low-risk {
		background-color: #2196F3;
	}
	
	.safe {
		background-color: #4CAF50;
	}
	
	.result-content {
		padding: 10rpx 0;
	}
	
	.result-item {
		margin-bottom: 30rpx;
		display: flex;
		align-items: flex-start;
	}
	
	.item-label {
		font-size: 28rpx;
		color: #666;
		width: 180rpx;
		flex-shrink: 0;
	}
	
	.item-value {
		font-size: 28rpx;
		color: #171616;
		font-weight: bold;
		flex: 1;
	}
	
	.analysis-detail {
		flex-direction: column;
	}
	
	.analysis-detail .item-label {
		margin-bottom: 10rpx;
	}
	
	.detail-text {
		font-weight: normal;
		line-height: 1.6;
		background: #f8f9fa;
		padding: 20rpx;
		border-radius: 12rpx;
		font-size: 26rpx;
		border-left: 4rpx solid #3498db;
	}
	
	/* 举报引导样式 */
	.report-guide {
		margin-top: 30rpx;
		padding: 25rpx;
		background: linear-gradient(135deg, #e74c3c, #c0392b);
		border-radius: 16rpx;
		display: flex;
		align-items: center;
		justify-content: space-between;
		box-shadow: 0 6rpx 16rpx rgba(231, 76, 60, 0.3);
		animation: pulse 2s infinite;
	}
	
	@keyframes pulse {
		0%, 100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.02);
		}
	}
	
	.report-info {
		display: flex;
		align-items: center;
		flex: 1;
	}
	
	.report-icon {
		font-size: 48rpx;
		margin-right: 20rpx;
	}
	
	.report-text {
		display: flex;
		flex-direction: column;
	}
	
	.report-title {
		font-size: 28rpx;
		font-weight: bold;
		color: #ffffff;
		margin-bottom: 5rpx;
	}
	
	.report-desc {
		font-size: 24rpx;
		color: #ffe6e6;
	}
	
	.report-button {
		padding: 12rpx 24rpx;
		background: white;
		color: #e74c3c;
		font-size: 24rpx;
		font-weight: bold;
		border-radius: 20rpx;
		border: 2rpx solid rgba(255, 255, 255, 0.3);
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.15);
		min-width: 120rpx;
		transition: all 0.3s;
	}
	
	.report-button:active {
		transform: scale(0.95);
	}
	
	.report-button::after {
		border: none;
	}
</style> 