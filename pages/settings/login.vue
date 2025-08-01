<template>
	<view class="login-container">
		<view class="header">
			<view class="back-button" @click="goBack">
				<text class="icon">←</text>
			</view>
			<view class="title">{{ isLoginMode ? '用户登录' : '用户注册' }}</view>
		</view>

		<view class="form-container">
			<view class="form-item">
				<text class="form-label">账号</text>
				<input class="form-input" type="number" v-model="username" placeholder="请输入手机号" />
			</view>
			<view class="form-item">
				<text class="form-label">密码</text>
				<input class="form-input" type="password" v-model="password" placeholder="请输入密码" />
			</view>
			<view class="form-item" v-if="!isLoginMode">
				<text class="form-label">确认密码</text>
				<input class="form-input" type="password" v-model="confirmPassword" placeholder="请再次输入密码" />
			</view>

			<button class="login-button" @click="handleSubmit">{{ isLoginMode ? '立即登录' : '立即注册' }}</button>
		</view>
		
		<view class="extra-links">
			<text class="link" @click="toggleMode">{{ isLoginMode ? '没有账号？立即注册' : '已有账号？立即登录' }}</text>
		</view>

		<view class="tips" v-if="isLoginMode">
			<text>管理员测试账号: 13800138000</text>
			<text>管理员测试密码: 123456</text>
		</view>
	</view>
</template>

<script>
	import config from '@/utils/config.js';
	
	export default {
		data() {
			return {
				username: '',
				password: '',
				confirmPassword: '',
				isLoginMode: true
			}
		},
		methods: {
			goBack() {
				uni.navigateBack();
			},
			toggleMode() {
				this.isLoginMode = !this.isLoginMode;
				this.password = '';
				this.confirmPassword = '';
			},
			handleSubmit() {
				if (this.isLoginMode) {
					this.handleLogin();
				} else {
					this.handleRegister();
				}
			},
			handleRegister() {
				if (!this.username || !this.password || !this.confirmPassword) {
					uni.showToast({ title: '请填写所有字段', icon: 'none' });
					return;
				}
				if (this.password !== this.confirmPassword) {
					uni.showToast({ title: '两次输入的密码不一致', icon: 'none' });
					return;
				}

				uni.showLoading({ title: '注册中...' });

				uni.request({
					url: `${config.BASE_URL}/register`,
					method: 'POST',
					data: {
						username: this.username,
						password: this.password
					},
					success: (res) => {
						if (res.statusCode === 200) {
							uni.showToast({
								title: '注册成功，请登录',
								icon: 'success'
							});
							// 注册成功后切换到登录模式
							this.toggleMode();
						} else {
							uni.showToast({
								title: res.data.msg || '注册失败',
								icon: 'none'
							});
						}
					},
					fail: (err) => {
						uni.showToast({
							title: '网络连接失败',
							icon: 'error'
						});
					},
					complete: () => {
						uni.hideLoading();
					}
				});
			},
			handleLogin() {
				if (!this.username || !this.password) {
					uni.showToast({
						title: '账号或密码不能为空',
						icon: 'none'
					});
					return;
				}

				uni.showLoading({
					title: '登录中...'
				});

				uni.request({
					url: `${config.BASE_URL}/try/login`,
					method: 'POST',
					data: {
						username: this.username,
						password: this.password
					},
					success: (res) => {
						if (res.statusCode === 200) {
							uni.showToast({
								title: '登录成功',
								icon: 'success'
							});
							
							// 触发一个全局事件，通知其他页面登录状态已改变
							uni.$emit('user-log-changed');

							// 延迟1秒后返回上一页
							setTimeout(() => {
								uni.navigateBack();
							}, 1000);

						} else {
							uni.showToast({
								title: res.data.msg || '登录失败',
								icon: 'none'
							});
						}
					},
					fail: (err) => {
						uni.showToast({
							title: '网络连接失败',
							icon: 'error'
						});
					},
					complete: () => {
						uni.hideLoading();
					}
				});
			}
		}
	}
</script>

<style scoped>
	.login-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background-color: #f4f6f9;
	}

	.header {
		display: flex;
		align-items: center;
		padding: 20rpx 30rpx;
		background-color: #ffffff;
		border-bottom: 1rpx solid #eee;
		position: relative;
		padding-top: var(--status-bar-height);
	}

	.back-button {
		position: absolute;
		left: 30rpx;
		top: var(--status-bar-height);
		bottom: 0;
		width: 60rpx;
		height: 88rpx;
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

	.form-container {
		padding: 60rpx 40rpx;
	}

	.form-item {
		display: flex;
		align-items: center;
		padding: 20rpx 0;
		border-bottom: 1rpx solid #e0e0e0;
		margin-bottom: 40rpx;
	}
	
	.form-label {
		width: 120rpx;
		font-size: 30rpx;
		color: #333;
	}
	
	.form-input {
		flex: 1;
		font-size: 30rpx;
	}

	.login-button {
		background-color: #007bff;
		color: #fff;
		font-size: 32rpx;
		border-radius: 50rpx;
		margin-top: 40rpx;
	}
	
	.extra-links {
		text-align: center;
		padding: 20rpx 40rpx 0;
	}
	
	.link {
		color: #007bff;
		font-size: 28rpx;
		cursor: pointer;
	}

	.tips {
		padding: 40rpx;
		text-align: center;
		color: #999;
		font-size: 26rpx;
		display: flex;
		flex-direction: column;
		gap: 10rpx;
	}
</style> 