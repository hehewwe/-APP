<template>
	<view class="report-container">
		<view class="header">
			<text class="title">快速举报</text>
			<text class="subtitle" v-if="!preFilledData">发现可疑信息，帮助他人避免受骗</text>
			<text class="subtitle" v-if="preFilledData">基于AI检测结果自动填充，请确认信息后提交</text>
		</view>

		<view class="form-container">
			<!-- 举报类型选择 -->
			<view class="form-group">
				<text class="label">举报类型</text>
				<view class="type-options">
					<view v-for="type in reportTypes" :key="type.value" 
						  class="type-option" 
						  :class="{ active: selectedType === type.value }"
						  @click="selectType(type.value)">
						<text class="type-text">{{ type.label }}</text>
					</view>
				</view>
			</view>

			<!-- 可疑内容输入 -->
			<view class="form-group">
				<text class="label">可疑内容 *</text>
				<textarea 
					v-model="reportContent" 
					placeholder="请输入收到的可疑短信、电话内容或其他相关信息..."
					class="content-input"
					maxlength="500"
				></textarea>
				<text class="char-count">{{ reportContent.length }}/500</text>
			</view>

			<!-- 来源信息 -->
			<view class="form-group">
				<text class="label">来源信息</text>
				<input 
					v-model="sourceInfo" 
					placeholder="发送方号码/网址/联系方式（选填）"
					class="source-input"
				/>
			</view>


		</view>

		<!-- 提交按钮 -->
		<view class="submit-container">
			<button class="submit-btn" 
					:class="{ disabled: !canSubmit }"
					:disabled="!canSubmit"
					@click="submitReport">
				{{ isSubmitting ? '提交中...' : '提交举报' }}
			</button>
		</view>

		<!-- 温馨提示 -->
		<view class="tips-container">
			<text class="tips-title">温馨提示</text>
			<text class="tips-text">• 您的举报将帮助完善我们的防诈骗数据库</text>
			<text class="tips-text">• 我们会保护您的隐私，不会泄露个人信息</text>
			<text class="tips-text">• 如遇紧急情况，请直接拨打110报警</text>
		</view>
	</view>
</template>

<script>
import config from '../../utils/config.js';

export default {
	data() {
		return {
			selectedType: 'a',
			reportContent: '',
			sourceInfo: '',
			isSubmitting: false,
			preFilledData: false,
			reportTypes: [
				{ value: 'a', label: '刷单返利类' },
				{ value: 'b', label: '虚假网络投资理财类' },
				{ value: 'c', label: '冒充电商物流客服类' },
				{ value: 'd', label: '贷款、代办信用卡类' },
				{ value: 'e', label: '网络游戏产品虚假交易类' },
				{ value: 'f', label: '虚假购物、服务类' },
				{ value: 'g', label: '冒充公检法及政府机关类' },
				{ value: 'h', label: '虚假征信类' },
				{ value: 'i', label: '冒充领导、熟人类' },
				{ value: 'j', label: '冒充军警购物类诈骗' },
				{ value: 'k', label: '网络婚恋、交友类' },
				{ value: 'l', label: '网黑案件' }
			]
		};
	},
	onLoad(options) {
		// 处理从诈骗检测页面跳转过来的参数
		if (options.type) {
			this.selectedType = options.type;
			this.preFilledData = true;
		}
		if (options.content) {
			this.reportContent = decodeURIComponent(options.content);
		}
		if (options.source) {
			this.sourceInfo = decodeURIComponent(options.source);
		}
	},
	computed: {
		canSubmit() {
			return this.reportContent.trim().length > 0 && !this.isSubmitting;
		}
	},
	methods: {
		selectType(type) {
			this.selectedType = type;
		},
		async submitReport() {
			if (!this.canSubmit) return;
			
			this.isSubmitting = true;
			
			try {
				const reportData = {
					type: this.selectedType,
					content: this.reportContent.trim(),
					source: this.sourceInfo.trim(),
					timestamp: new Date().toISOString()
				};

				const response = await uni.request({
					url: config.BASE_URL + '/api/report/submit',
					method: 'POST',
					data: reportData,
					header: {
						'Content-Type': 'application/json'
					}
				});

				if (response.data && response.data.code === 200) {
					uni.showToast({
						title: '举报提交成功',
						icon: 'success',
						duration: 2000
					});
					
					// 清空表单
					this.resetForm();
					
					// 延时返回上一页
					setTimeout(() => {
						uni.navigateBack();
					}, 2000);
				} else {
					throw new Error(response.data?.msg || '提交失败');
				}
			} catch (error) {
				console.error('举报提交失败:', error);
				uni.showToast({
					title: '提交失败，请重试',
					icon: 'none',
					duration: 2000
				});
			} finally {
				this.isSubmitting = false;
			}
		},
		resetForm() {
			this.selectedType = 'a';
			this.reportContent = '';
			this.sourceInfo = '';
			this.preFilledData = false;
		}
	}
};
</script>

<style scoped>
.report-container {
	min-height: 100vh;
	background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
	padding: 30rpx;
}

.header {
	text-align: center;
	margin-bottom: 40rpx;
}

.title {
	font-size: 36rpx;
	font-weight: bold;
	color: #e74c3c;
	display: block;
	margin-bottom: 10rpx;
	text-shadow: 0 2rpx 4rpx rgba(231, 76, 60, 0.2);
}

.subtitle {
	font-size: 26rpx;
	color: #7f8c8d;
}

.form-container {
	background: white;
	border-radius: 20rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.1);
}

.form-group {
	margin-bottom: 35rpx;
}

.label {
	font-size: 28rpx;
	font-weight: bold;
	color: #2c3e50;
	display: block;
	margin-bottom: 15rpx;
}

/* 类型选择 */
.type-options {
	display: flex;
	flex-wrap: wrap;
	gap: 15rpx;
}

.type-option {
	flex: 1;
	min-width: 140rpx;
	padding: 20rpx 15rpx;
	border: 2rpx solid #e9ecef;
	border-radius: 12rpx;
	text-align: center;
	background: #f8f9fa;
	transition: all 0.3s;
	cursor: pointer;
}

.type-option:hover {
	border-color: #bbb;
	background: #e2e6ea;
}

.type-option.active {
	border-color: #3498db;
	background: linear-gradient(135deg, #ebf3fd, #d6eaff);
	color: #2980b9;
	box-shadow: 0 2rpx 8rpx rgba(52, 152, 219, 0.2);
}

.type-text {
	font-size: 22rpx;
	color: inherit;
	font-weight: 500;
}

/* 输入框样式 */
.content-input {
	width: 100%;
	min-height: 200rpx;
	padding: 20rpx;
	border: 2rpx solid #e9ecef;
	border-radius: 12rpx;
	font-size: 26rpx;
	line-height: 1.5;
	background: #f8f9fa;
	box-sizing: border-box;
}

.source-input {
	width: 100%;
	height: 80rpx;
	padding: 0 20rpx;
	border: 2rpx solid #e9ecef;
	border-radius: 12rpx;
	font-size: 26rpx;
	background: #f8f9fa;
	box-sizing: border-box;
}

.char-count {
	font-size: 22rpx;
	color: #6c757d;
	text-align: right;
	display: block;
	margin-top: 10rpx;
}

/* 提交按钮 */
.submit-container {
	margin-bottom: 30rpx;
}

.submit-btn {
	width: 100%;
	height: 88rpx;
	background: linear-gradient(135deg, #3498db, #2980b9);
	color: white;
	border: none;
	border-radius: 44rpx;
	font-size: 32rpx;
	font-weight: bold;
	display: flex;
	align-items: center;
	justify-content: center;
}

.submit-btn.disabled {
	background: #bdc3c7;
	color: #7f8c8d;
}

/* 提示区域 */
.tips-container {
	background: rgba(255, 255, 255, 0.9);
	border-radius: 16rpx;
	padding: 25rpx;
}

.tips-title {
	font-size: 26rpx;
	font-weight: bold;
	color: #f39c12;
	display: block;
	margin-bottom: 15rpx;
	border-left: 4rpx solid #f39c12;
	padding-left: 12rpx;
}

.tips-text {
	font-size: 24rpx;
	color: #7f8c8d;
	display: block;
	margin-bottom: 8rpx;
	line-height: 1.4;
}
</style>