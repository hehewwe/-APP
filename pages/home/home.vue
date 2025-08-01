<template>
	<view class="home-container">
		<!-- 顶部状态卡片 -->
		<view class="status-card" :class="{ 'danger': !isSafe }">
			<view class="status-header">
				<view class="status-title">实时守护已开启</view>
			</view>
			<view class="last-scan-time">
				<text>服务状态: 持续监控中...</text>
			</view>
			<view class="status-indicator">
				<text class="status-text">{{ isSafe ? '安全' : '不安全' }}</text>
			</view>
			<view class="scan-summary">
				<text>当前监控最新 200 条短信</text>
			</view>
		</view>

		<!-- 风险统计卡片 -->
		<view class="stats-card">
			<view class="stats-title">风险统计</view>
			<view class="stats-content">
				<!-- 使用Canvas原生绘图实现环形图表 -->
				<view class="chart-container">
					<canvas canvas-id="riskChart" id="riskChart" class="risk-chart-canvas"></canvas>
					<view class="chart-center-text">
						<text class="chart-total">{{ riskStats.high + riskStats.medium + riskStats.low + riskStats.safe }}</text>
						<text class="chart-label">总计</text>
					</view>
				</view>
				<view class="stats-legend">
					<view class="legend-item high-risk">
						<text class="legend-dot"></text>
						<text>高风险: {{ riskStats.high }}条</text>
					</view>
					<view class="legend-item medium-risk">
						<text class="legend-dot"></text>
						<text>中风险: {{ riskStats.medium }}条</text>
					</view>
					<view class="legend-item low-risk">
						<text class="legend-dot"></text>
						<text>低风险: {{ riskStats.low }}条</text>
					</view>
					<view class="legend-item safe">
						<text class="legend-dot"></text>
						<text>安全: {{ riskStats.safe }}条</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 诈骗信息智能识别 -->
		<view class="fraud-detection-section">
			<view class="section-title">诈骗信息智能识别</view>
			<view class="detection-input-area">
				<input class="detection-input" type="text" placeholder="输入可疑短信内容..." v-model="suspiciousText" />
				<!-- 将 button 改为 view 以增加点击事件的兼容性 -->
				<view class="detection-button" @click="analyzeText">
					<text class="button-icon">🔍</text>
					<text>立即分析</text>
				</view>
			</view>
		</view>

		<!-- 最近预警 -->
		<view class="alerts-section">
			<view class="alerts-title">最近预警</view>
			<view class="alert-list">
				<view v-if="recentAlerts.length === 0" class="empty-alerts">
					<text>太好了！暂无风险预警</text>
				</view>
				<view v-for="(alert, index) in recentAlerts" :key="alert.id" class="alert-item" @click="viewAlertDetail(alert)">
					<view class="alert-header">
						<text :class="['alert-tag', getRiskLevelTagClass(alert.riskLevel)]">{{ getRiskLevelText(alert.riskLevel) }}</text>
						<text class="alert-sender">{{ alert.sender }}</text>
						<text class="alert-time">{{ formatAlertTime(alert.date) }}</text>
					</view>
					<view class="alert-content">{{ alert.body }}</view>
				</view>
			</view>
			<view v-if="recentAlerts.length > 0" class="view-all-alerts">
				<text @click="viewAllAlerts">查看全部预警 ›</text>
			</view>
		</view>

	</view>
</template>

<script>
	import alertManager from '@/utils/alert-manager.js';
	
	export default {
		data() {
			return {
				// 初始化风险统计数据
				riskStats: {
					high: 0,
					medium: 0,
					low: 0,
					safe: 0
				},
				isSafe: true, // 用于控制UI状态
				intervalId: null, // 用于存储定时器ID
				// 图表颜色配置
				chartColors: {
					high: "#F44336",
					medium: "#FF9800",
					low: "#2196F3",
					safe: "#4CAF50"
				},
				recentAlerts: [], // 新增：用于存储最近预警数据
				suspiciousText: '' // 新增：用于存储待分析的文本
			}
		},
		onShow() {
			const updateDataAndStatus = () => {
				// 直接从原始数据源（风险预警列表和监控短信列表）计算统计信息
				const riskAlerts = uni.getStorageSync('riskAlertsList') || [];
				// App.vue中存了被监控的短信列表
				const monitoredSms = uni.getStorageSync('monitoredSmsList') || [];
				const totalMonitoredCount = monitoredSms.length;

				// 分别计算高、中、低风险的数量
				const highRiskCount = riskAlerts.filter(a => a.riskLevel === 'high').length;
				const mediumRiskCount = riskAlerts.filter(a => a.riskLevel === 'medium').length;
				const lowRiskCount = riskAlerts.filter(a => a.riskLevel === 'low').length;

				// 安全短信数量 = 总数 - 风险总数
				const totalRiskCount = highRiskCount + mediumRiskCount + lowRiskCount;
				const safeCount = Math.max(0, totalMonitoredCount - totalRiskCount);

				// 更新本地的riskStats对象以驱动UI
				this.riskStats = {
					high: highRiskCount,
					medium: mediumRiskCount,
					low: lowRiskCount,
					safe: safeCount,
				};

				// 更新图表数据已被移除

				// 根据最新数据更新UI状态
				this.updateStatus();
				
				// 绘制环形图表
				this.$nextTick(() => {
					this.drawRiskChart();
				});

				// 获取最近预警数据
				this.updateRecentAlerts(riskAlerts);
			};
			
			updateDataAndStatus(); // 页面显示时立即执行一次，以获取当前状态
			
			// 启动定时器，轮询获取最新数据，实现"实时"效果
			this.intervalId = setInterval(updateDataAndStatus, 3000); // 每 3 秒检查一次缓存
		},
		onLoad() {
			// 监听风险预警删除事件，更新预警列表
			uni.$on('risk-alert-deleted', this.updateRecentAlerts);
		},
		onHide() {
			// 页面隐藏时清除定时器，避免后台运行消耗资源
			if (this.intervalId) {
				clearInterval(this.intervalId);
				this.intervalId = null;
			}
		},
		onUnload() {
			// 页面卸载时同样清除定时器
			if (this.intervalId) {
				clearInterval(this.intervalId);
				this.intervalId = null;
			}
			// 取消监听
			uni.$off('risk-alert-deleted', this.updateRecentAlerts);
		},
		methods: {
			// 绘制环形图表
			drawRiskChart() {
				const ctx = uni.createCanvasContext('riskChart', this);
				const canvasWidth = 90; // 180rpx = 90px
				const canvasHeight = 90;
				const centerX = canvasWidth / 2;
				const centerY = canvasHeight / 2;
				const radius = Math.min(centerX, centerY) - 5;
				const innerRadius = radius * 0.7; // 内圆半径，控制环形宽度
				
				// 计算总数
				const total = this.riskStats.high + this.riskStats.medium + this.riskStats.low + this.riskStats.safe;
				if (total <= 0) {
					// 如果没有数据，绘制一个灰色的完整圆环
					ctx.beginPath();
					ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
					ctx.arc(centerX, centerY, innerRadius, 0, 2 * Math.PI, true);
					ctx.setFillStyle('#e0e0e0');
					ctx.fill();
					ctx.draw();
					return;
				}
				
				// 准备数据
				const data = [
					{ value: this.riskStats.high, color: this.chartColors.high },
					{ value: this.riskStats.medium, color: this.chartColors.medium },
					{ value: this.riskStats.low, color: this.chartColors.low },
					{ value: this.riskStats.safe, color: this.chartColors.safe }
				].filter(item => item.value > 0); // 只处理有数据的部分
				
				// 绘制环形图
				let startAngle = -0.5 * Math.PI; // 从12点钟方向开始
				
				data.forEach(item => {
					const portion = item.value / total;
					const endAngle = startAngle + portion * 2 * Math.PI;
					
					ctx.beginPath();
					ctx.arc(centerX, centerY, radius, startAngle, endAngle);
					ctx.arc(centerX, centerY, innerRadius, endAngle, startAngle, true);
					ctx.closePath();
					ctx.setFillStyle(item.color);
					ctx.fill();
					
					startAngle = endAngle;
				});
				
				ctx.draw();
			},
			
			// 根据风险数据更新isSafe状态
			updateStatus() {
				const hasRisk = this.riskStats.high > 0 || this.riskStats.medium > 0;
				this.isSafe = !hasRisk;
			},
			viewSmsAnalysis() {
				uni.switchTab({
					url: '/pages/analysis/analysis'
				});
			},
			viewRiskAlerts() {
				uni.switchTab({
					url: '/pages/alerts/alerts'
				});
			},
			// 格式化预警时间
			formatAlertTime(timestamp) {
				if (!timestamp) return '';
				const date = new Date(timestamp);
				const now = new Date();
				const diffMinutes = Math.floor((now - date) / (1000 * 60));

				if (diffMinutes < 60) {
					return `${diffMinutes}分钟前`;
				} else if (diffMinutes < 24 * 60) {
					return `${Math.floor(diffMinutes / 60)}小时前`;
				} else {
					const month = date.getMonth() + 1;
					const day = date.getDate();
					const hours = date.getHours().toString().padStart(2, '0');
					const minutes = date.getMinutes().toString().padStart(2, '0');
					return `${month}/${day} ${hours}:${minutes}`;
				}
			},
			// 新增：获取风险等级标签类名
			getRiskLevelTagClass(level) {
				switch (level) {
					case 'high':
						return 'high-risk-tag';
					case 'medium':
						return 'medium-risk-tag';
					case 'low':
						return 'low-risk-tag';
					case 'safe':
						return 'safe-tag';
					default:
						return '';
				}
			},
			// 新增：获取风险等级文本
			getRiskLevelText(level) {
				switch (level) {
					case 'high':
						return '高风险';
					case 'medium':
						return '中风险';
					case 'low':
						return '低风险';
					case 'safe':
						return '安全';
					default:
						return level;
				}
			},
			// 新增：跳转到预警详情页面
			viewAlertDetail(alert) {
				uni.navigateTo({
					url: `/pages/alert-detail/alert-detail?alert=${encodeURIComponent(JSON.stringify(alert))}`
				});
			},
			// 新增：跳转到全部预警页面
			viewAllAlerts() {
				uni.switchTab({
					url: '/pages/alerts/alerts'
				});
			},
			// 更新最近预警列表
			updateRecentAlerts(alerts) {
				const riskAlerts = alerts || alertManager.getRiskAlerts();
				this.recentAlerts = riskAlerts.slice(-5).map(alert => ({
					id: alert.id,
					sender: alert.sender,
					body: alert.body,
					riskLevel: alert.riskLevel,
					date: alert.date
				}));
			},
			// 新增：诈骗信息智能识别方法
			analyzeText() {
				if (!this.suspiciousText || !this.suspiciousText.trim()) {
					uni.showToast({
						title: '请输入要分析的文本',
						icon: 'none'
					});
					return;
				}

				const url = `/pages/fraud-detection/fraud-detection?text=${encodeURIComponent(this.suspiciousText)}`;

				// 跳转到诈骗信息分析页面，并传递文本内容
				uni.navigateTo({
					url: url
				});
				
				// 跳转后立即清空输入框
				this.suspiciousText = '';
			}
		}
	}
</script>

<style scoped>
	.home-container {
		padding: 20rpx;
		background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
		min-height: 100vh;
	}

	/* 卡片通用样式 */
	.status-card,
	.stats-card,
	.action-section,
	.alerts-section {
		background-color: #ffffff;
		border-radius: 20rpx;
		padding: 30rpx;
		margin-bottom: 20rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
		animation: cardSlideIn 0.6s ease-out;
		transition: transform 0.3s ease, box-shadow 0.3s ease;
	}
	
	.status-card:active,
	.stats-card:active,
	.alerts-section:active {
		transform: scale(0.98);
	}
	
	@keyframes cardSlideIn {
		from {
			opacity: 0;
			transform: translateY(30rpx);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* 顶部状态卡片 */
	.status-card {
		color: #fff;
		background: linear-gradient(135deg, #4CAF50, #81C784, #66BB6A);
		background-size: 200% 200%;
		animation: gradientShift 4s ease-in-out infinite;
		position: relative;
		overflow: hidden;
	}
	
	@keyframes gradientShift {
		0%, 100% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
	}
    
	.status-card.warning {
		background: linear-gradient(135deg, #FF9800, #FFB74D, #FFA726);
		background-size: 200% 200%;
		animation: gradientShift 3s ease-in-out infinite;
	}

	.status-card.danger {
		background: linear-gradient(135deg, #F44336, #E57373, #EF5350);
		background-size: 200% 200%;
		animation: gradientShift 2s ease-in-out infinite, dangerPulse 1.5s ease-in-out infinite;
	}
	
	@keyframes dangerPulse {
		0%, 100% {
			box-shadow: 0 4rpx 12rpx rgba(244, 67, 54, 0.3);
		}
		50% {
			box-shadow: 0 8rpx 25rpx rgba(244, 67, 54, 0.5);
		}
	}

	.status-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20rpx;
	}

	.status-title {
		font-size: 36rpx;
		font-weight: bold;
		line-height: 1.1;
	}

	.last-scan-time {
		font-size: 24rpx;
		opacity: 0.8;
	}

	.status-indicator {
		text-align: center;
		padding: 40rpx 0;
		animation: bounce 2s ease-in-out infinite;
	}

	.status-text {
		font-size: 48rpx;
		font-weight: bold;
		text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.2);
		animation: textGlow 3s ease-in-out infinite;
	}
	
	@keyframes bounce {
		0%, 20%, 50%, 80%, 100% {
			transform: translateY(0);
		}
		40% {
			transform: translateY(-10rpx);
		}
		60% {
			transform: translateY(-5rpx);
		}
	}
	
	@keyframes textGlow {
		0%, 100% {
			text-shadow: 0 2rpx 8rpx rgba(255, 255, 255, 0.3);
		}
		50% {
			text-shadow: 0 4rpx 16rpx rgba(255, 255, 255, 0.6);
		}
	}
	
	.scan-summary {
		text-align: center;
		font-size: 26rpx;
		opacity: 0.9;
	}

	/* 风险统计卡片 */
	.stats-title {
		font-size: 30rpx;
		font-weight: bold;
		margin-bottom: 20rpx;
	}

	.stats-content {
		display: flex;
		align-items: center;
	}

	.chart-container {
		width: 180rpx;
		height: 180rpx;
		margin-right: 40rpx;
		position: relative;
	}

	.risk-chart-canvas {
		width: 100%;
		height: 100%;
		/* 添加willReadFrequently属性，避免Canvas警告 */
		will-change: transform;
	}

	.chart-center-text {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		text-align: center;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	.chart-total {
		font-size: 32rpx;
		font-weight: bold;
		color: #333;
		line-height: 1;
		animation: numberCount 1s ease-out;
	}
	
	@keyframes numberCount {
		from {
			opacity: 0;
			transform: scale(0.5);
		}
		to {
			opacity: 1;
			transform: scale(1);
		}
	}

	.chart-label {
		font-size: 22rpx;
		color: #666;
		margin-top: 4rpx;
	}

	.stats-legend .legend-item {
		display: flex;
		align-items: center;
		font-size: 26rpx;
		margin-bottom: 10rpx;
		padding: 8rpx 12rpx;
		border-radius: 8rpx;
		transition: all 0.3s ease;
		animation: fadeInLeft 0.5s ease-out;
	}
	
	.stats-legend .legend-item:nth-child(1) { animation-delay: 0.1s; }
	.stats-legend .legend-item:nth-child(2) { animation-delay: 0.2s; }
	.stats-legend .legend-item:nth-child(3) { animation-delay: 0.3s; }
	.stats-legend .legend-item:nth-child(4) { animation-delay: 0.4s; }
	
	.stats-legend .legend-item:active {
		background-color: #f8f9fa;
		transform: scale(1.05);
	}

	.legend-dot {
		width: 16rpx;
		height: 16rpx;
		border-radius: 50%;
		margin-right: 15rpx;
		animation: dotPulse 2s ease-in-out infinite;
	}
	
	@keyframes fadeInLeft {
		from {
			opacity: 0;
			transform: translateX(-20rpx);
		}
		to {
			opacity: 1;
			transform: translateX(0);
		}
	}
	
	@keyframes dotPulse {
		0%, 100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.2);
		}
	}

	.legend-item.high-risk .legend-dot { background-color: #F44336; }
	.legend-item.medium-risk .legend-dot { background-color: #FF9800; }
	.legend-item.low-risk .legend-dot { background-color: #2196F3; }
	.legend-item.safe .legend-dot { background-color: #4CAF50; }

	/* 诈骗信息智能识别 */
	.fraud-detection-section {
		padding: 30rpx;
		background-color: #ffffff;
		border-radius: 20rpx;
		margin-bottom: 20rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
	}

	.section-title {
		font-size: 30rpx;
		font-weight: bold;
		margin-bottom: 20rpx;
		text-align: center;
	}

	.detection-input-area {
		display: flex;
		align-items: center;
		gap: 20rpx; /* 新增flex gap */
		padding: 20rpx;
		background-color: #fff;
		border-radius: 15rpx;
		border: 1rpx solid #eee;
	}

	.detection-input {
		flex: 1;
		padding: 15rpx 20rpx;
		font-size: 28rpx;
		border: none;
		border-radius: 10rpx;
		background-color: #f7f7f7;
	}

	.detection-button {
		flex-shrink: 0;
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #3498db, #2980b9);
		color: #fff;
		font-size: 28rpx;
		font-weight: bold;
		border-radius: 12rpx;
		padding: 15rpx 30rpx;
		line-height: 1.5;
		margin: 0;
		border: none;
		box-shadow: 0 4rpx 12rpx rgba(52, 152, 219, 0.3);
		transition: all 0.3s ease;
		animation: buttonGlow 2s ease-in-out infinite;
	}
	
	.detection-button:active {
		transform: scale(0.95);
		box-shadow: 0 2rpx 8rpx rgba(52, 152, 219, 0.4);
	}
	
	@keyframes buttonGlow {
		0%, 100% {
			box-shadow: 0 4rpx 12rpx rgba(52, 152, 219, 0.3);
		}
		50% {
			box-shadow: 0 6rpx 20rpx rgba(52, 152, 219, 0.5);
		}
	}
	
	.detection-button::after {
		border: none;
	}
	
	.button-icon {
		font-size: 50rpx;
		margin-bottom: 10rpx;
	}

	/* 最近预警 */
	.alerts-title {
		font-size: 30rpx;
		font-weight: bold;
		margin-bottom: 20rpx;
	}

	.alert-item {
		padding: 20rpx 0;
		border-bottom: 1rpx solid #eee;
	}
	
	.alert-item:last-child {
		border-bottom: none;
	}
	
	.alert-item:active {
		background-color: #f9f9f9;
	}

	.alert-header {
		display: flex;
		align-items: center;
		margin-bottom: 10rpx;
	}

	.alert-tag {
		font-size: 22rpx;
		padding: 4rpx 12rpx;
		border-radius: 8rpx;
		color: #fff;
		margin-right: 10rpx;
	}
	
	.high-risk-tag { background-color: #F44336; }
	.medium-risk-tag { background-color: #FF9800; }
	.low-risk-tag { background-color: #2196F3; }
	.safe-tag { background-color: #4CAF50; }
	
	.alert-sender {
		font-size: 28rpx;
		font-weight: bold;
		color: #333;
	}
	
	.alert-time {
		font-size: 24rpx;
		color: #999;
		margin-left: auto;
	}
	
	.alert-content {
		font-size: 26rpx;
		color: #666;
		line-height: 1.5;
		overflow: hidden;
		text-overflow: ellipsis;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
	}

	.empty-alerts {
		text-align: center;
		padding: 40rpx 0;
		color: #999;
		font-size: 28rpx;
	}

	.view-all-alerts {
		text-align: center;
		padding: 20rpx 0;
		color: #666;
		font-size: 26rpx;
		border-top: 1rpx solid #eee;
		margin-top: 10rpx;
	}

	.view-all-alerts text {
		color: #007bff;
	}
</style> 