<template>
	<view class="detail-container">
		<view class="header">
			<view class="sender-info">
				<text class="label">发件人</text>
				<text class="sender">{{ sms.sender || '未知' }}</text>
			</view>
			<view class="time-info">
				<text class="label">时间</text>
				<text class="time">{{ formattedTime }}</text>
			</view>
		</view>
		<scroll-view scroll-y class="content-scroll-view">
			<view class="content-body">
				<text class="content-text" user-select>{{ sms.body || '无内容' }}</text>
			</view>
		</scroll-view>
		<view class="footer-actions">
			<button class="action-button" @click="copyContent">复制短信内容</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				sms: {} // 用于存储从列表页传来的短信对象
			};
		},
		computed: {
			formattedTime() {
				if (!this.sms.date) return '未知';
				const date = new Date(this.sms.date);
				const year = date.getFullYear();
				const month = (date.getMonth() + 1).toString().padStart(2, '0');
				const day = date.getDate().toString().padStart(2, '0');
				const hours = date.getHours().toString().padStart(2, '0');
				const minutes = date.getMinutes().toString().padStart(2, '0');
				return `${year}-${month}-${day} ${hours}:${minutes}`;
			}
		},
		onLoad(options) {
			if (options.sms) {
				try {
					// 从URL参数中解析出完整的短信对象
					this.sms = JSON.parse(decodeURIComponent(options.sms));
				} catch (e) {
					console.error("解析短信数据失败", e);
					uni.showToast({
						title: '加载失败，请重试',
						icon: 'none'
					});
					this.sms = {
						sender: '错误',
						body: '无法加载短信内容。'
					};
				}
			}
		},
		methods: {
			copyContent() {
				uni.setClipboardData({
					data: this.sms.body,
					success: () => {
						uni.showToast({
							title: '已复制',
							icon: 'success'
						});
					},
					fail: () => {
						uni.showToast({
							title: '复制失败',
							icon: 'none'
						});
					}
				});
			}
		}
	}
</script>

<style scoped>
	.detail-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background-color: #f4f6f9;
	}

	.header {
		background-color: #fff;
		padding: 30rpx;
		border-bottom: 1rpx solid #eee;
	}

	.sender-info {
		margin-bottom: 20rpx;
	}

	.label {
		font-size: 26rpx;
		color: #999;
		display: block;
		margin-bottom: 5rpx;
	}

	.sender {
		font-size: 36rpx;
		font-weight: bold;
		color: #333;
	}

	.time {
		font-size: 28rpx;
		color: #666;
	}

	.content-scroll-view {
		flex: 1;
		height: 0;
	}

	.content-body {
		background-color: #fff;
		padding: 30rpx;
		margin: 20rpx;
		border-radius: 16rpx;
	}

	.content-text {
		font-size: 32rpx;
		line-height: 1.8;
		color: #333;
		white-space: pre-wrap; /* 保留换行和空格 */
		word-break: break-all; /* 允许长单词或URL换行 */
	}

	.footer-actions {
		padding: 20rpx 30rpx;
		background-color: #fff;
		border-top: 1rpx solid #eee;
		padding-bottom: constant(safe-area-inset-bottom);
		padding-bottom: env(safe-area-inset-bottom);
	}
	
	.action-button {
		background-color: #007aff;
		color: white;
		border-radius: 40rpx;
	}
</style> 