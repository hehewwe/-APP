<template>
	<view class="alert-detail-container">
		<!-- 风险等级顶栏 -->
		<view :class="['risk-header', getRiskLevelClass(alert.riskLevel)]">
			<view class="risk-title">{{ getRiskLevelText(alert.riskLevel) }}</view>
			<view class="risk-type">{{ alert.reason || '未知类型' }}</view>
		</view>

		<scroll-view scroll-y class="content-scroll-view">
			<!-- 发件人与时间 -->
			<view class="info-card">
				<view class="info-item">
					<text class="label">发件人</text>
					<text class="value sender">{{ alert.sender || '未知' }}</text>
				</view>
				<view class="info-item">
					<text class="label">时间</text>
					<text class="value">{{ formatTimestamp(alert.date) }}</text>
				</view>
			</view>

			<!-- 短信原文 -->
			<view class="info-card">
				<view class="info-item">
					<text class="label">短信原文</text>
					<view class="sms-body-box">
						<text class="content-text" user-select>{{ alert.body || '无内容' }}</text>
					</view>
				</view>
			</view>

			<!-- AI建议 -->
			<view class="info-card suggestion-card" v-if="alert.reason">
				<view class="info-item">
					<text class="label suggestion-label">🚨 AI分析结果</text>
					<view class="suggestion-box">
						<text class="suggestion-text">{{ alert.reason }}</text>
					</view>
				</view>
			</view>

		</scroll-view>

		<!-- 底部操作按钮 -->
		<view class="footer-actions">
			<button class="action-button delete" @click="deleteAlert">删除此预警</button>
		</view>
	</view>
</template>

<script>
	import alertManager from '@/utils/alert-manager.js';

	export default {
		data() {
			return {
				alert: {}
			};
		},
		onLoad(options) {
			if (options.alert) {
				try {
					this.alert = JSON.parse(decodeURIComponent(options.alert));
				} catch (e) {
					// handle error
				}
			}
		},
		methods: {
			getRiskLevelClass(level) {
				if (level >= 3) return 'high';
				if (level === 2) return 'medium';
				return 'low';
			},
			getRiskLevelText(level) {
				if (level >= 3) return '高风险警告';
				if (level === 2) return '中风险提醒';
				return '低风险提醒';
			},
			formatTimestamp(timestamp) {
				if (!timestamp) return '未知时间';
				const date = new Date(timestamp);
				return date.toLocaleString().replace(/\//g, '-');
			},
			deleteAlert() {
				uni.showModal({
					title: '确认删除',
					content: '您确定要删除这条预警吗？',
					success: (res) => {
						if (res.confirm) {
							if (alertManager.removeAlertById(this.alert.id)) {
								uni.$emit('risk-alert-deleted');
								uni.navigateBack();
							}
						}
					}
				});
			}
		}
	}
</script>

<style scoped>
	.alert-detail-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background-color: #f4f6f9;
	}

	.risk-header {
		padding: 40rpx 30rpx;
		color: #fff;
		text-align: center;
	}

	.risk-header.high {
		background: linear-gradient(45deg, #F44336, #E57373);
	}

	.risk-header.medium {
		background: linear-gradient(45deg, #FF9800, #FFB74D);
	}

	.risk-header.low {
		background: linear-gradient(45deg, #2196F3, #64B5F6);
	}

	.risk-title {
		font-size: 48rpx;
		font-weight: bold;
		margin-bottom: 10rpx;
	}

	.risk-type {
		font-size: 32rpx;
		opacity: 0.9;
	}

	.content-scroll-view {
		flex: 1;
		height: 0;
	}

	.info-card {
		background-color: #fff;
		margin: 20rpx 20rpx 0;
		padding: 30rpx;
		border-radius: 16rpx;
	}

	.info-item {
		display: flex;
		flex-direction: column;
		margin-bottom: 20rpx;
	}
	
	.info-item:last-child {
		margin-bottom: 0;
	}

	.label {
		font-size: 26rpx;
		color: #999;
		margin-bottom: 10rpx;
	}

	.value {
		font-size: 32rpx;
		color: #333;
	}

	.value.sender {
		font-weight: bold;
	}

	.sms-body-box {
		margin-top: 10rpx;
	}

	.content-text {
		font-size: 32rpx;
		line-height: 1.8;
		color: #333;
		white-space: pre-wrap;
		word-break: break-all;
	}

	.suggestion-card {
		border-left: 6rpx solid #FF9800;
	}

	.suggestion-label {
		color: #FF9800;
		font-weight: bold;
	}

	.suggestion-box {
		margin-top: 10rpx;
	}

	.suggestion-text {
		font-size: 30rpx;
		line-height: 1.7;
		color: #555;
	}

	.footer-actions {
		display: flex;
		padding: 20rpx 30rpx;
		background-color: #ffffff;
		border-top: 1rpx solid #eee;
		padding-bottom: constant(safe-area-inset-bottom);
		padding-bottom: env(safe-area-inset-bottom);
	}

	.action-button.delete {
		flex: 1;
		border-radius: 40rpx;
		font-size: 30rpx;
		margin: 0;
		background-color: #f56c6c;
		color: white;
		border: none;
	}
</style> 