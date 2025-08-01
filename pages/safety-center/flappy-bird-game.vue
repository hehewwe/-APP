<template>
	<view class="game-container">
		<!-- 游戏标题 -->
		<view class="game-header" v-if="!gameStarted">
			<text class="game-title">🐦 防诈小鸟飞飞飞</text>
			<text class="game-subtitle">点击屏幕让小鸟飞起来，避开诈骗陷阱！</text>
		</view>

		<!-- 游戏分数 -->
		<view class="score-display" v-if="gameStarted">
			<text class="current-score">得分: {{ score }}</text>
			<text class="knowledge-count">防诈知识: {{ knowledgeCount }}</text>
		</view>

		<!-- 游戏画布 -->
		<canvas 
			canvas-id="gameCanvas" 
			class="game-canvas"
			@touchstart="handleTouch"
			@touchend="handleTouchEnd"
		></canvas>

		<!-- 开始游戏按钮 -->
		<view class="start-screen" v-if="!gameStarted && !gameOver">
			<button class="start-btn" @click="startGame">🐦 开始游戏</button>
			<view class="instructions">
				<text class="instruction-text">📱 点击屏幕控制小鸟飞行</text>
				<text class="instruction-text">💰 收集防诈知识金币</text>
				<text class="instruction-text">⚠️ 避开诈骗陷阱管道</text>
			</view>
		</view>

		<!-- 游戏结束界面 -->
		<view class="game-over-screen" v-if="gameOver">
			<view class="game-over-content">
				<text class="game-over-title">游戏结束！</text>
				<text class="final-score">本次得分: {{ score }}</text>
				<text class="high-score">历史最高: {{ highScore }}</text>
				<text class="knowledge-gained">学到防诈知识: {{ knowledgeCount }} 条</text>
				
				<!-- 防诈知识提示 -->
				<view class="knowledge-tip" v-if="currentKnowledge">
					<text class="tip-title">💡 防诈小贴士</text>
					<text class="tip-content">{{ currentKnowledge }}</text>
				</view>
				
				<view class="game-over-buttons">
					<button class="restart-btn" @click="restartGame">🔄 再来一次</button>
					<button class="home-btn" @click="goHome">🏠 返回主页</button>
				</view>
			</view>
		</view>

		<!-- 暂停界面 -->
		<view class="pause-screen" v-if="gamePaused">
			<view class="pause-content">
				<text class="pause-title">游戏暂停</text>
				<button class="resume-btn" @click="resumeGame">▶️ 继续游戏</button>
			</view>
		</view>

		<!-- 暂停按钮 -->
		<button class="pause-btn" v-if="gameStarted && !gameOver" @click="pauseGame">⏸️</button>
	</view>
</template>

<script>
export default {
	data() {
		return {
			// 游戏状态
			gameStarted: false,
			gameOver: false,
			gamePaused: false,
			score: 0,
			highScore: 0,
			knowledgeCount: 0,
			currentKnowledge: '',
			
			// 画布相关
			ctx: null,
			canvasWidth: 0,
			canvasHeight: 0,
			
			// 游戏对象
			bird: {
				x: 80,
				y: 200,
				width: 40,
				height: 30,
				velocity: 0,
				gravity: 0.8,
				jumpPower: -12
			},
			
			// 管道数组
			pipes: [],
			
			// 金币数组
			coins: [],
			
			// 游戏循环
			gameLoopTimer: null,
			
			// 防诈知识库
			antiScamKnowledge: [
				"公检法机关不会通过电话要求转账",
				"刷单返利都是诈骗，千万别信",
				"陌生链接不要随意点击",
				"个人信息要保护好，不要随意透露",
				"网恋交友要谨慎，涉及金钱要警惕",
				"中奖信息多为骗局，天下没有免费的午餐",
				"银行卡密码不要告诉任何人",
				"遇到可疑电话，挂断后拨打官方客服确认"
			]
		};
	},
	
	mounted() {
		this.initCanvas();
		this.loadHighScore();
	},
	
	beforeDestroy() {
		if (this.gameLoopTimer) {
			clearInterval(this.gameLoopTimer);
		}
	},
	
	methods: {
		// 初始化画布
		initCanvas() {
			const query = uni.createSelectorQuery().in(this);
			query.select('.game-canvas').boundingClientRect(rect => {
				this.canvasWidth = rect.width;
				this.canvasHeight = rect.height;
				
				this.ctx = uni.createCanvasContext('gameCanvas', this);
				this.drawBackground();
			}).exec();
		},
		
		// 绘制背景
		drawBackground() {
			if (!this.ctx) return;
			
			// 清空画布
			this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);
			
			// 绘制天空背景
			const gradient = this.ctx.createLinearGradient(0, 0, 0, this.canvasHeight);
			gradient.addColorStop(0, '#87CEEB');
			gradient.addColorStop(1, '#98FB98');
			this.ctx.fillStyle = gradient;
			this.ctx.fillRect(0, 0, this.canvasWidth, this.canvasHeight);
			
			// 绘制云朵
			this.drawClouds();
			
			this.ctx.draw();
		},
		
		// 绘制云朵
		drawClouds() {
			this.ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
			// 简单的云朵效果
			for (let i = 0; i < 3; i++) {
				const x = (this.canvasWidth / 4) * (i + 1);
				const y = 50 + Math.sin(Date.now() * 0.001 + i) * 10;
				this.ctx.beginPath();
				this.ctx.arc(x, y, 20, 0, Math.PI * 2);
				this.ctx.arc(x + 15, y, 25, 0, Math.PI * 2);
				this.ctx.arc(x + 30, y, 20, 0, Math.PI * 2);
				this.ctx.fill();
			}
		},
		
		// 开始游戏
		startGame() {
			this.gameStarted = true;
			this.gameOver = false;
			this.score = 0;
			this.knowledgeCount = 0;
			this.resetBird();
			this.pipes = [];
			this.coins = [];
			this.currentKnowledge = '';
			
			// 开始游戏循环
			this.gameLoopTimer = setInterval(() => {
				this.updateGame();
				this.drawGame();
			}, 16); // 约60FPS
		},
		
		// 重置小鸟
		resetBird() {
			this.bird.x = 80;
			this.bird.y = this.canvasHeight / 2;
			this.bird.velocity = 0;
		},
		
		// 处理触摸
		handleTouch() {
			if (!this.gameStarted || this.gameOver || this.gamePaused) return;
			this.bird.velocity = this.bird.jumpPower;
		},
		
		handleTouchEnd() {
			// 可以在这里添加触摸结束的逻辑
		},
		
		// 更新游戏状态
		updateGame() {
			if (!this.gameStarted || this.gameOver || this.gamePaused) return;
			
			// 更新小鸟
			this.bird.velocity += this.bird.gravity;
			this.bird.y += this.bird.velocity;
			
			// 检查小鸟边界
			if (this.bird.y <= 0 || this.bird.y >= this.canvasHeight - this.bird.height) {
				this.endGame();
				return;
			}
			
			// 生成管道
			if (this.pipes.length === 0 || this.pipes[this.pipes.length - 1].x < this.canvasWidth - 200) {
				this.createPipe();
			}
			
			// 更新管道
			this.pipes.forEach((pipe, index) => {
				pipe.x -= 2;
				if (pipe.x + pipe.width < 0) {
					this.pipes.splice(index, 1);
				}
			});
			
			// 更新金币
			this.coins.forEach((coin, index) => {
				coin.x -= 2;
				if (coin.x + coin.width < 0) {
					this.coins.splice(index, 1);
				}
			});
			
			// 检测碰撞
			this.checkCollisions();
		},
		
		// 创建管道
		createPipe() {
			const gapHeight = 120;
			const pipeWidth = 50;
			const minHeight = 50;
			const maxHeight = this.canvasHeight - gapHeight - minHeight;
			const topHeight = Math.random() * (maxHeight - minHeight) + minHeight;
			
			// 上管道
			this.pipes.push({
				x: this.canvasWidth,
				y: 0,
				width: pipeWidth,
				height: topHeight,
				type: 'top',
				scamType: this.getRandomScamType()
			});
			
			// 下管道
			this.pipes.push({
				x: this.canvasWidth,
				y: topHeight + gapHeight,
				width: pipeWidth,
				height: this.canvasHeight - (topHeight + gapHeight),
				type: 'bottom',
				scamType: this.getRandomScamType()
			});
			
			// 在管道间隙中间添加金币
			this.coins.push({
				x: this.canvasWidth + 25,
				y: topHeight + gapHeight/2 - 15,
				width: 30,
				height: 30,
				collected: false
			});
		},
		
		// 获取随机诈骗类型
		getRandomScamType() {
			const types = ['📞', '💳', '🎣', '📱', '💰'];
			return types[Math.floor(Math.random() * types.length)];
		},
		
		// 检测碰撞
		checkCollisions() {
			// 检测管道碰撞
			this.pipes.forEach(pipe => {
				if (this.bird.x < pipe.x + pipe.width &&
					this.bird.x + this.bird.width > pipe.x &&
					this.bird.y < pipe.y + pipe.height &&
					this.bird.y + this.bird.height > pipe.y) {
					this.endGame();
				}
				
				// 检测通过管道得分
				if (pipe.type === 'top' && pipe.x + pipe.width < this.bird.x && !pipe.scored) {
					pipe.scored = true;
					this.score += 10;
				}
			});
			
			// 检测金币收集
			this.coins.forEach((coin, index) => {
				if (!coin.collected &&
					this.bird.x < coin.x + coin.width &&
					this.bird.x + this.bird.width > coin.x &&
					this.bird.y < coin.y + coin.height &&
					this.bird.y + this.bird.height > coin.y) {
					
					coin.collected = true;
					this.score += 50;
					this.knowledgeCount++;
					this.coins.splice(index, 1);
					
					// 播放收集音效（可选）
					uni.vibrateShort();
				}
			});
		},
		
		// 绘制游戏
		drawGame() {
			if (!this.ctx) return;
			
			// 清空画布并绘制背景
			this.drawBackground();
			
			// 绘制管道
			this.pipes.forEach(pipe => {
				this.ctx.fillStyle = '#228B22';
				this.ctx.fillRect(pipe.x, pipe.y, pipe.width, pipe.height);
				
				// 绘制诈骗类型图标
				this.ctx.fillStyle = '#FF4500';
				this.ctx.font = '20px Arial';
				this.ctx.textAlign = 'center';
				this.ctx.fillText(pipe.scamType, pipe.x + pipe.width/2, pipe.y + pipe.height/2);
			});
			
			// 绘制金币
			this.coins.forEach(coin => {
				if (!coin.collected) {
					this.ctx.fillStyle = '#FFD700';
					this.ctx.beginPath();
					this.ctx.arc(coin.x + coin.width/2, coin.y + coin.height/2, coin.width/2, 0, Math.PI * 2);
					this.ctx.fill();
					
					// 绘制防诈标识
					this.ctx.fillStyle = '#FF6347';
					this.ctx.font = '12px Arial';
					this.ctx.textAlign = 'center';
					this.ctx.fillText('防', coin.x + coin.width/2, coin.y + coin.height/2 + 4);
				}
			});
			
			// 绘制小鸟
			this.ctx.fillStyle = '#FF6B6B';
			this.ctx.beginPath();
			this.ctx.arc(this.bird.x + this.bird.width/2, this.bird.y + this.bird.height/2, this.bird.width/2, 0, Math.PI * 2);
			this.ctx.fill();
			
			// 绘制小鸟的眼睛
			this.ctx.fillStyle = '#FFF';
			this.ctx.beginPath();
			this.ctx.arc(this.bird.x + this.bird.width/2 + 5, this.bird.y + this.bird.height/2 - 5, 5, 0, Math.PI * 2);
			this.ctx.fill();
			
			this.ctx.fillStyle = '#000';
			this.ctx.beginPath();
			this.ctx.arc(this.bird.x + this.bird.width/2 + 7, this.bird.y + this.bird.height/2 - 5, 2, 0, Math.PI * 2);
			this.ctx.fill();
			
			this.ctx.draw();
		},
		
		// 结束游戏
		endGame() {
			this.gameOver = true;
			this.gameStarted = false;
			
			// 清除游戏循环
			if (this.gameLoopTimer) {
				clearInterval(this.gameLoopTimer);
				this.gameLoopTimer = null;
			}
			
			// 更新最高分
			if (this.score > this.highScore) {
				this.highScore = this.score;
				this.saveHighScore();
			}
			
			// 显示随机防诈知识
			if (this.antiScamKnowledge.length > 0) {
				const randomIndex = Math.floor(Math.random() * this.antiScamKnowledge.length);
				this.currentKnowledge = this.antiScamKnowledge[randomIndex];
			}
		},
		
		// 重新开始游戏
		restartGame() {
			this.startGame();
		},
		
		// 暂停游戏
		pauseGame() {
			this.gamePaused = true;
		},
		
		// 继续游戏
		resumeGame() {
			this.gamePaused = false;
		},
		
		// 返回主页
		goHome() {
			uni.navigateBack();
		},
		
		// 加载最高分
		loadHighScore() {
			this.highScore = uni.getStorageSync('flappy_bird_high_score') || 0;
		},
		
		// 保存最高分
		saveHighScore() {
			uni.setStorageSync('flappy_bird_high_score', this.highScore);
		}
	}
};
</script>

<style scoped>
.game-container {
	width: 100vw;
	height: 100vh;
	position: relative;
	background: linear-gradient(135deg, #87CEEB 0%, #98FB98 100%);
	overflow: hidden;
}

.game-header {
	position: absolute;
	top: 80rpx;
	left: 50%;
	transform: translateX(-50%);
	text-align: center;
	z-index: 100;
}

.game-title {
	font-size: 48rpx;
	font-weight: bold;
	color: #2c3e50;
	display: block;
	margin-bottom: 10rpx;
	text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.game-subtitle {
	font-size: 28rpx;
	color: #34495e;
}

.score-display {
	position: absolute;
	top: 40rpx;
	left: 30rpx;
	z-index: 100;
}

.current-score, .knowledge-count {
	display: block;
	font-size: 28rpx;
	font-weight: bold;
	color: #fff;
	text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
	margin-bottom: 10rpx;
}

.game-canvas {
	width: 100%;
	height: 100%;
}

.start-screen {
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	text-align: center;
	z-index: 200;
}

.start-btn {
	background: linear-gradient(135deg, #FF6B6B, #FF8E53);
	color: white;
	border: none;
	border-radius: 50rpx;
	padding: 20rpx 60rpx;
	font-size: 32rpx;
	font-weight: bold;
	margin-bottom: 40rpx;
	box-shadow: 0 8rpx 20rpx rgba(255, 107, 107, 0.4);
}

.instructions {
	background: rgba(255, 255, 255, 0.9);
	border-radius: 20rpx;
	padding: 30rpx;
}

.instruction-text {
	display: block;
	font-size: 26rpx;
	color: #2c3e50;
	margin-bottom: 10rpx;
	line-height: 1.4;
}

.game-over-screen {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.8);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 300;
}

.game-over-content {
	background: white;
	border-radius: 30rpx;
	padding: 50rpx;
	text-align: center;
	max-width: 600rpx;
}

.game-over-title {
	font-size: 40rpx;
	font-weight: bold;
	color: #e74c3c;
	display: block;
	margin-bottom: 20rpx;
}

.final-score, .high-score, .knowledge-gained {
	display: block;
	font-size: 28rpx;
	color: #2c3e50;
	margin-bottom: 15rpx;
}

.knowledge-tip {
	background: #f8f9fa;
	border-radius: 15rpx;
	padding: 25rpx;
	margin: 30rpx 0;
}

.tip-title {
	font-size: 26rpx;
	font-weight: bold;
	color: #e67e22;
	display: block;
	margin-bottom: 10rpx;
}

.tip-content {
	font-size: 24rpx;
	color: #2c3e50;
	line-height: 1.5;
}

.game-over-buttons {
	display: flex;
	gap: 20rpx;
	margin-top: 30rpx;
}

.restart-btn, .home-btn {
	flex: 1;
	height: 80rpx;
	border: none;
	border-radius: 40rpx;
	font-size: 28rpx;
	font-weight: bold;
}

.restart-btn {
	background: linear-gradient(135deg, #3498db, #2980b9);
	color: white;
}

.home-btn {
	background: linear-gradient(135deg, #95a5a6, #7f8c8d);
	color: white;
}

.pause-screen {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.6);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 250;
}

.pause-content {
	background: white;
	border-radius: 20rpx;
	padding: 40rpx;
	text-align: center;
}

.pause-title {
	font-size: 36rpx;
	font-weight: bold;
	color: #2c3e50;
	display: block;
	margin-bottom: 30rpx;
}

.resume-btn {
	background: linear-gradient(135deg, #27ae60, #229954);
	color: white;
	border: none;
	border-radius: 30rpx;
	padding: 15rpx 40rpx;
	font-size: 28rpx;
}

.pause-btn {
	position: absolute;
	top: 40rpx;
	right: 30rpx;
	background: rgba(255, 255, 255, 0.8);
	border: none;
	border-radius: 50%;
	width: 80rpx;
	height: 80rpx;
	font-size: 24rpx;
	z-index: 100;
}
</style>