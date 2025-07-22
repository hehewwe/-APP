<template>
	<view class="fraud-detection-container">
		<view class="header">
			<view class="back-button" @click="goBack">
				<text class="icon">←</text>
			</view>
			<view class="title">诈骗信息智能识别</view>
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
						text: this.textToAnalyze
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
			
		}
	}
</script>

<style>
	.fraud-detection-container {
		padding: 0;
		background-color: #f4f6f9;
		min-height: 100vh;
		display: flex;
		flex-direction: column;
        padding-top: 75rpx;
        padding-bottom: 100rpx;        
	}
	
	.header {
		display: flex;
		align-items: center;
		padding: 20rpx 30rpx;
		background-color: #ffffff;
		border-bottom: 1rpx solid #eee;
		position: relative;
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
		flex: 1;
		text-align: center;
		font-size: 34rpx;
		font-weight: bold;
	}
	
	.content {
		flex: 1;
		padding: 30rpx;
	}
	
	.input-section {
		background-color: #ffffff;
		border-radius: 20rpx;
		padding: 30rpx;
		margin-bottom: 30rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
	}
	
	.input-label {
		font-size: 30rpx;
		font-weight: bold;
		margin-bottom: 20rpx;
	}
	
	.input-area {
		width: 100%;
		height: 300rpx;
		padding: 20rpx;
		font-size: 28rpx;
		border: 1rpx solid #eee;
		border-radius: 10rpx;
		background-color: #f7f7f7;
		box-sizing: border-box;
	}
	
	.char-count {
		text-align: right;
		font-size: 24rpx;
		color: #999;
		margin-top: 10rpx;
	}
	
	.button-section {
		margin-bottom: 30rpx;
	}
	
	.analyze-button {
		
        border-left: 200rpx;
        border-right: 200rpx;
        border-top: 100rpx;
        border-bottom: 100rpx;
		flex-direction: row;
		align-items: center;
		justify-content: center;
		background-color: #007bff;
		color: #fff;
		font-size: 40rpx;
		border-radius: 20rpx;
		padding: 20rpx 0;
		width: 100%;
		margin: 0 auto;
		border: none;
	}
	
	.analyze-button[disabled] {
		background-color: #cccccc;
		color: #ffffff;
	}
	
	.analyze-button::after {
		border: none;
	}
	
	.button-icon {
		font-size: 36rpx;
		margin-right: 10rpx;
	}
	
	.result-section {
		background-color: #ffffff;
		border-radius: 20rpx;
		padding: 30rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
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
		background-color: #f7f7f7;
		padding: 20rpx;
		border-radius: 10rpx;
		font-size: 26rpx;
	}
</style> 