<template>
	<view class="analysis-container">
		<!-- 顶部搜索和筛选 -->
		<view class="filter-section">
			<view class="search-bar">
				<input class="search-input" placeholder="搜索关键词或发信人" v-model="searchText" />
			</view>
			<view class="filter-tabs">
				<text v-for="(tab, index) in filterTabs" :key="index"
					:class="['tab-item', { active: activeTabIndex === index }]" @click="changeTab(index)">
					{{ tab }}
				</text>
			</view>
		</view>

		<!-- 短信列表 -->
		<scroll-view scroll-y class="sms-list-scroll">
			<view class="sms-list">
				<view v-if="filteredSmsList.length === 0" class="empty-list">
					<text>没有找到相关短信</text>
				</view>
				<view v-for="sms in filteredSmsList" :key="sms.id" class="sms-item-card" @click="viewSmsDetail(sms)">
					<view class="card-header">
						<text class="sender">{{ sms.sender }}</text>
						<view :class="['category-tag', sms.category]">{{ sms.category }}</view>
					</view>
					<view class="card-content">
						<text class="content-preview">{{ sms.body }}</text>
					</view>
					<view class="card-footer">
						<text class="timestamp">{{ formatDisplayTime(sms.date) }}</text>
						<text class="view-detail-arrow">›</text>
					</view>
				</view>
			</view>
			
			<view class="clear-section" v-if="allSmsList.length > 0">
				<view class="bottom-divider">--- 到底了 ---</view>
				<button class="clear-button" @click="clearMessages">清除信息</button>
			</view>
		</scroll-view>
	</view>
</template>

<script>
	import smsClassifier from '@/utils/sms-classifier.js';

	export default {
		data() {
			return {
				searchText: '',
				activeTabIndex: 0,
				filterTabs: ['全部', '通知', '验证码', '推广', '其他'],
				allSmsList: []
			};
		},
		computed: {
			processedSmsList() {
				return this.allSmsList.map(sms => ({
					...sms,
					category: smsClassifier.classify(sms)
				}));
			},
			filteredSmsList() {
				const filter = this.filterTabs[this.activeTabIndex];
				let list = this.processedSmsList;
				if (filter !== '全部') {
					list = list.filter(sms => sms.category === filter);
				}
				if (this.searchText.trim()) {
					const searchLower = this.searchText.toLowerCase();
					list = list.filter(sms =>
						sms.sender.toLowerCase().includes(searchLower) ||
						sms.body.toLowerCase().includes(searchLower)
					);
				}
				return list;
			}
		},
		onLoad() {
			this.loadMessages();
			uni.$on('monitored-sms-updated', this.onSmsUpdate);
		},
		onUnload() {
			uni.$off('monitored-sms-updated', this.onSmsUpdate);
		},
		methods: {
			onSmsUpdate() {
				this.loadMessages();
			},
			loadMessages() {
				this.allSmsList = uni.getStorageSync('monitoredSmsList') || [];
			},
			changeTab(index) {
				this.activeTabIndex = index;
			},
			viewSmsDetail(sms) {
				const smsString = encodeURIComponent(JSON.stringify(sms));
				uni.navigateTo({
					url: '/pages/sms-detail/sms-detail?sms=' + smsString
				});
			},
			formatDisplayTime(timestamp) {
				if (!timestamp) return '';
				const date = new Date(timestamp);
				const month = date.getMonth() + 1;
				const day = date.getDate();
				const hours = date.getHours().toString().padStart(2, '0');
				const minutes = date.getMinutes().toString().padStart(2, '0');
				return `${month}/${day} ${hours}:${minutes}`;
			},
			clearMessages() {
				uni.showModal({
					title: '确认',
					content: '确定要清除所有监控的短信吗？',
					success: (res) => {
						if (res.confirm) {
							uni.setStorageSync('monitoredSmsList', []);
							this.loadMessages();
							uni.showToast({
								title: '信息已清除',
								icon: 'none'
							});
						}
					}
				});
			}
		}
	}
</script>

<style scoped>
	.analysis-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background-color: #f4f6f9;
		box-sizing: border-box;
	}
	.filter-section {
		padding: 20rpx;
		background-color: #ffffff;
		border-bottom: 1rpx solid #eee;
	}
	.search-bar {
		margin-bottom: 20rpx;
	}
	.search-input {
		background-color: #f0f0f0;
		border-radius: 30rpx;
		padding: 10rpx 30rpx;
		font-size: 28rpx;
	}
	.filter-tabs {
		display: flex;
		justify-content: space-around;
	}
	.tab-item {
		font-size: 28rpx;
		color: #666;
		padding: 10rpx 20rpx;
		border-radius: 30rpx;
	}
	.tab-item.active {
		background-color: #007aff;
		color: #fff;
		font-weight: bold;
	}
	.sms-list-scroll {
		flex: 1;
		height: 0;
	}
	.sms-list {
		padding: 20rpx;
	}
	.empty-list {
		text-align: center;
		color: #999;
		padding-top: 100rpx;
	}
	.sms-item-card {
		background-color: #ffffff;
		border-radius: 20rpx;
		padding: 25rpx;
		margin-bottom: 20rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
	}
	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 15rpx;
	}
	.sender {
		font-size: 32rpx;
		font-weight: bold;
		color: #333;
	}
	.category-tag {
		font-size: 24rpx;
		padding: 6rpx 15rpx;
		border-radius: 8rpx;
		color: #fff;
	}
	.category-tag.通知 { background-color: #2196F3; }
	.category-tag.验证码 { background-color: #4CAF50; }
	.category-tag.推广 { background-color: #FF9800; }
	.category-tag.其他 { background-color: #F44336; }
	.card-content { margin-bottom: 20rpx; }
	.content-preview {
		font-size: 28rpx;
		color: #555;
		line-height: 1.6;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 3;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.card-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		color: #999;
		font-size: 24rpx;
	}
	.view-detail-arrow {
		font-size: 40rpx;
		font-weight: bold;
		color: #ccc;
	}
	.clear-section {
		padding: 40rpx;
		text-align: center;
	}
	.bottom-divider {
		color: #bbb;
		font-size: 26rpx;
		margin-bottom: 20rpx;
	}
	.clear-button {
		background-color: #e5e5e5;
		color: #666;
		font-size: 28rpx;
		border-radius: 40rpx;
		width: 50%;
	}
</style> 