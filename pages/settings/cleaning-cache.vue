<template>
	<view class="cleaning-container">
		<view class="progress-circle-container">
			<canvas canvas-id="progressCanvas" id="progressCanvas" class="progress-canvas"></canvas>

			<!-- 进度文字 -->
			<view class="progress-text" v-if="!isComplete">
				<view class="progress-percent">{{ percent.toFixed(0) }}%</view>
				<view class="progress-label">{{ statusText }}</view>
			</view>

			<!-- 火箭 -->
			<view class="rocket-container" :class="{ 'launch': isLaunching }">
				<text class="rocket-emoji">🚀</text>
			</view>
			
			<!-- 完成视图 -->
			<view class="completion-view" v-if="isComplete">
				<view class="completion-text">清理完成</view>
			</view>
		</view>

		<view class="cleaned-info">
			<text>已释放 {{ (cleanedSize * percent / 100).toFixed(2) }} MB 空间</text>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				percent: 0,
				cleanedSize: 0,
				statusText: '正在扫描...',
				isLaunching: false,
				isComplete: false,
				ctx: null,
				intervalId: null // 使用 setInterval 代替 requestAnimationFrame
			};
		},
		onReady() {
			this.$nextTick(() => {
				this.ctx = uni.createCanvasContext('progressCanvas', this);
				if (this.ctx) {
					this.cleanedSize = (Math.random() * 150) + 50;
					this.startAnimation();
				}
			});
		},
		onUnload() {
			// 在页面卸载时清除定时器，防止内存泄漏
			if (this.intervalId) {
				clearInterval(this.intervalId);
			}
		},
		methods: {
			startAnimation() {
				// 动画: 从 0% 到 100%
				this.animateTo(100, 3000, '正在扫描...', () => {
					// 动画完成后的回调
					this.isComplete = true;
					this.isLaunching = true;
					
					setTimeout(() => {
						uni.navigateBack();
					}, 1500); // 等待火箭飞出和文字动画完成
				});
			},
			animateTo(targetPercent, duration, statusText, callback) {
				const start = this.percent;
				const change = targetPercent - start;
				const startTime = Date.now();

				// 清除之前的定时器
				if (this.intervalId) clearInterval(this.intervalId);

				this.intervalId = setInterval(() => {
					const now = Date.now();
					const time = now - startTime;
					
					if (time >= duration) {
						clearInterval(this.intervalId);
						this.percent = targetPercent;
						this.drawProgress(this.percent);
						if (callback) callback();
						return;
					}
					
					this.percent = this.easeInOutQuad(time, start, change, duration);
					this.statusText = statusText;
					this.drawProgress(this.percent);
				}, 16); // ~60fps
			},
			drawProgress(percent) {
				const W = 150;
				const H = 150;
				this.ctx.clearRect(0, 0, W, H);

				// 底圆
				this.ctx.beginPath();
				this.ctx.arc(W / 2, H / 2, 60, 0, 2 * Math.PI, false);
				this.ctx.setStrokeStyle('#333');
				this.ctx.setLineWidth(10);
				this.ctx.stroke();

				// 进度圆
				if (percent > 0) {
					this.ctx.beginPath();
					this.ctx.arc(W / 2, H / 2, 60, -Math.PI / 2, (percent / 100) * 2 * Math.PI - Math.PI / 2, false);
					this.ctx.setStrokeStyle('#007aff');
					this.ctx.setLineWidth(10);
					this.ctx.setLineCap('round');
					this.ctx.stroke();
				}
				
				this.ctx.draw();
			},
			easeInOutQuad(t, b, c, d) {
				t /= d / 2;
				if (t < 1) return c / 2 * t * t + b;
				t--;
				return -c / 2 * (t * (t - 2) - 1) + b;
			}
		}
	}
</script>

<style scoped>
	.cleaning-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100vh;
		background-color: #1c1c1e;
		overflow: hidden;
	}

	.progress-circle-container {
		position: relative;
		width: 150px;
		height: 150px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.progress-canvas {
		width: 150px;
		height: 150px;
	}

	.progress-text {
		position: absolute;
		text-align: center;
		color: #fff;
	}

	.progress-percent {
		font-size: 36px;
		font-weight: bold;
	}

	.progress-label {
		font-size: 14px;
		color: #8e8e93;
		margin-top: 5px;
	}
	
	.cleaned-info {
		margin-top: 30px;
		font-size: 18px;
		color: #007aff;
		height: 25px; /* 占位防止跳动 */
	}
	
	/* 火箭初始状态在中心，透明 */
	.rocket-container {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%) scale(0.8);
		opacity: 0;
		transition: all 0.5s ease-out;
	}

	/* 火箭发射动画 */
	.rocket-container.launch {
		animation: launch-rocket 1s ease-in forwards;
	}

	.rocket-emoji {
		font-size: 50px;
		transform: rotate(-45deg);
		display: inline-block;
	}

	/* 完成视图 */
	.completion-view {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%) scale(0);
		opacity: 0;
		animation: pop-in 0.5s 0.2s forwards; /* 延迟0.2秒播放 */
		text-align: center;
		color: #fff;
	}
	
	.success-emoji {
		font-size: 50px;
	}
	
	.completion-text {
		font-size: 20px;
		font-weight: bold;
		margin-top: 10px;
		color: #007aff;
	}
	
	@keyframes pop-in {
		0% {
			transform: translate(-50%, -50%) scale(0);
			opacity: 0;
		}
		80% {
			transform: translate(-50%, -50%) scale(1.1);
			opacity: 1;
		}
		100% {
			transform: translate(-50%, -50%) scale(1);
			opacity: 1;
		}
	}
	
	@keyframes launch-rocket {
		0% {
			opacity: 1;
			transform: translate(-50%, -50%) scale(0.8);
		}
		20% {
			opacity: 1;
			transform: translate(-50%, -70%) scale(1);
		}
		100% {
			opacity: 0;
			transform: translate(-50%, -500px) scale(1.5);
		}
	}
</style> 