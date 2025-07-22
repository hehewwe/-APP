<template>
	<view class="alerts-container">
		<!-- 顶部摘要 -->
		<view class="summary-header">
			<view class="summary-title">风险预警中心</view>
			<view class="summary-stats">
				<text class="stat-item high">高风险: {{ highRiskCount }} 条</text>
				<text class="stat-item medium">中风险: {{ mediumRiskCount }} 条</text>
				<text class="stat-item low">低风险: {{ lowRiskCount }} 条</text>
			</view>
		</view>

		<!-- 预警列表 -->
		<scroll-view scroll-y class="alerts-scroll-view">
			<view class="alerts-list">
				<view v-if="alerts.length === 0" class="empty-list">
					<text class="empty-text">太棒了！</text>
					<text class="empty-text">当前没有发现风险短信。</text>
				</view>

				<uni-swipe-action>
					<uni-swipe-action-item v-for="(alert, index) in alerts" :key="alert.id" :right-options="swipeOptions"
						@click="handleSwipeClick($event, alert)">
						<view :class="['alert-card', alert.riskLevel]" @click="viewAlertDetail(alert)">
							<view class="card-left-bar"></view>
							<view class="card-main-content">
								<view class="card-header">
									<view class="risk-info">
										<text :class="['risk-level-text', alert.riskLevel]">{{ formatRiskLevel(alert.riskLevel) }}</text>
										<text class="risk-type"> · {{ alert.riskType }}</text>
									</view>
									<text class="timestamp">{{ formatAlertTime(alert.date) }}</text>
								</view>
								<view class="sender-info">
									<text class="sender-label">发件人: </text>
									<text class="sender-name">{{ alert.sender }}</text>
								</view>
								<view class="alert-content">
									<text>{{ alert.body }}</text>
								</view>
								<view class="card-actions">
									<!-- 阻止事件冒泡，防止点击按钮时触发卡片的点击事件 -->
									<button class="action-btn delete" @click.stop="deleteAlert(alert.id)">删除</button>
								</view>
							</view>
						</view>
					</uni-swipe-action-item>
				</uni-swipe-action>
			</view>
		</scroll-view>
	</view>
</template>

<script>
	import alertManager from '@/utils/alert-manager.js';

	export default {
		data() {
			return {
				alerts: [],
				swipeOptions: [{
					text: '删除',
					style: {
						backgroundColor: '#dd524d'
					}
				}]
			};
		},
		onShow() {
			this.loadAlerts();
			uni.$on('risk-alert-deleted', this.loadAlerts);
		},
		onUnload() {
			uni.$off('risk-alert-deleted', this.loadAlerts);
		},
		computed: {
			highRiskCount() {
				return this.alerts.filter(a => a.riskLevel === 'high').length;
			},
			mediumRiskCount() {
				return this.alerts.filter(a => a.riskLevel === 'medium').length;
			},
			lowRiskCount() {
				return this.alerts.filter(a => a.riskLevel === 'low').length;
			}
		},
		methods: {
			loadAlerts() {
				this.alerts = alertManager.getRiskAlerts();
			},
			handleSwipeClick(e, alert) {
				// 只有一个删除选项，所以直接处理
				if (e.index === 0) {
					this.deleteAlert(alert.id);
				}
			},
			deleteAlert(id) {
				if (alertManager.removeAlertById(id)) {
					this.loadAlerts();
				}
			},
			viewAlertDetail(alert) {
				uni.navigateTo({
					url: '/pages/alert-detail/alert-detail?alert=' + encodeURIComponent(JSON.stringify(alert))
				});
			},
			formatRiskLevel(level) {
				const riskMap = {
					'high': '高风险警告',
					'medium': '中风险提醒',
					'low': '低风险提醒'
				};
				return riskMap[level] || '未知风险';
			},
			formatAlertTime(timestamp) {
				if (!timestamp) return '';
				const date = new Date(timestamp);
				const month = date.getMonth() + 1;
				const day = date.getDate();
				const hours = date.getHours().toString().padStart(2, '0');
				const minutes = date.getMinutes().toString().padStart(2, '0');
				return `${month}/${day} ${hours}:${minutes}`;
			},
			getRiskLevelClass(level) {
				if (level >= 3) return 'high';
				if (level === 2) return 'medium';
				return 'low';
			},
			formatTimestamp(timestamp) {
				if (!timestamp) return '未知时间';
				const date = new Date(timestamp);
				const now = new Date();
				const diff = (now.getTime() - date.getTime()) / 1000;
				if (diff < 3600) {
					return `${Math.floor(diff / 60)}分钟前`;
				} else if (diff < 86400) {
					return `${Math.floor(diff / 3600)}小时前`;
				} else {
					return `${Math.floor(diff / 86400)}天前`;
				}
			}
		}
	}
</script>

<style scoped>
	.alerts-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background-color: #f4f6f9;
	}

	.summary-header {
		background: #fff;
		padding: 30rpx;
		border-bottom: 1rpx solid #eee;
	}

	.summary-title {
		font-size: 36rpx;
		font-weight: bold;
		color: #333;
		margin-bottom: 15rpx;
	}

	.summary-stats {
		font-size: 28rpx;
	}

	.stat-item {
		margin-right: 30rpx;
	}

	.stat-item.high {
		color: #F44336;
	}

	.stat-item.medium {
		color: #FF9800;
	}

	.stat-item.low {
		color: #2196F3;
	}

	.alerts-scroll-view {
		flex: 1;
		height: 0;
	}

	.alerts-list {
		padding: 20rpx;
	}
	
	.empty-list {
		padding-top: 150rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		color: #999;
	}
	
	.empty-text {
		font-size: 30rpx;
		margin-bottom: 10rpx;
	}

	.alert-card {
		display: flex;
		background-color: #fff;
		border-radius: 16rpx;
		margin-bottom: 25rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.06);
		overflow: hidden; /* 让子元素的圆角生效 */
		transition: transform 0.2s;
	}
	.alert-card:active {
		transform: scale(0.98);
	}

	.card-left-bar {
		width: 12rpx;
	}

	.alert-card.high .card-left-bar {
		background-color: #F44336;
	}

	.alert-card.medium .card-left-bar {
		background-color: #FF9800;
	}

	.alert-card.low .card-left-bar {
		background-color: #2196F3;
	}

	.card-main-content {
		flex: 1;
		padding: 25rpx;
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20rpx;
	}

	.risk-info .risk-level-text {
		font-size: 30rpx;
		font-weight: bold;
	}
	
	.risk-level-text.high { color: #F44336; }
	.risk-level-text.medium { color: #FF9800; }
	.risk-level-text.low { color: #2196F3; }

	.risk-info .risk-type {
		font-size: 26rpx;
		color: #666;
	}
	
	.timestamp {
		font-size: 24rpx;
		color: #999;
	}
	
	.sender-info {
		font-size: 28rpx;
		margin-bottom: 15rpx;
	}
	.sender-label {
		color: #666;
	}
	.sender-name {
		color: #333;
		font-weight: 500;
	}

	.alert-content {
		font-size: 28rpx;
		color: #555;
		line-height: 1.6;
		padding-bottom: 20rpx;
		border-bottom: 1rpx solid #f0f0f0;
	}
	
	.card-actions {
		display: flex;
		justify-content: flex-end; /* 让删除按钮靠右 */
		margin-top: 20rpx;
	}
	
	.action-btn {
		padding: 8rpx 20rpx;
		font-size: 24rpx;
		border-radius: 30rpx;
		margin: 0;
	}
	.action-btn::after {
		border: none;
	}
	.action-btn.delete {
		background-color: #fef0f0;
		color: #f56c6c;
		border: 1rpx solid #fbc4c4;
	}
</style> 