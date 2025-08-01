<template>
	<view class="safety-center-container">
		<scroll-view scroll-y class="scroll-view">
			<!-- 本周焦点 -->
			<view class="section-container focus-section" @click="openArticle(featuredArticle)">
				<view class="section-title">本周焦点</view>
				<view class="featured-card">
					<image class="featured-image" :src="featuredArticle.thumbnail" mode="aspectFill"></image>
					<view class="featured-content">
						<text class="featured-title">{{ featuredArticle.title }}</text>
						<text class="featured-excerpt">{{ featuredArticle.excerpt }}</text>
					</view>
				</view>
			</view>

			<!-- 防诈小游戏 -->
			<view class="section-container">
				<view class="section-title">🎮 防诈小游戏</view>
				<view class="game-cards">
					<view class="game-card quiz-game" @click="startQuizGame">
						<view class="game-icon">🐦</view>
						<view class="game-info">
							<text class="game-title">小鸟飞飞飞</text>
							<text class="game-desc">避开诈骗陷阱，收集防诈知识</text>
						</view>
						<view class="game-score">最高得分: {{flappyHighScore}}</view>
					</view>
					
					<view class="game-card judge-game" @click="startJudgeGame">
						<view class="game-icon">🎮</view>
						<view class="game-info">
							<text class="game-title">更多游戏</text>
							<text class="game-desc">敬请期待更多有趣小游戏</text>
						</view>
						<view class="game-score">即将推出</view>
					</view>
				</view>
			</view>

			<!-- 快速举报 -->
			<view class="section-container">
				<view class="section-title">🚨 快速举报</view>
				<view class="report-card" @click="openReportPage">
					<view class="report-icon">📱</view>
					<view class="report-content">
						<text class="report-title">发现可疑信息？</text>
						<text class="report-desc">一键举报，帮助他人避免受骗</text>
					</view>
					<view class="report-arrow">›</view>
				</view>
			</view>

			<!-- 防骗视频课 -->
			<view class="section-container">
				<view class="section-title">📺 防骗视频课</view>
				<scroll-view scroll-x class="video-scroll-view">
					<view class="video-list">
						<view v-for="video in videoList" :key="video.id" class="video-card" @click="openArticleById(video.id)">
							<image class="video-thumbnail" :src="video.thumbnail" mode="aspectFill"></image>
							<view class="play-icon">▶</view>
							<text class="video-title">{{ video.title }}</text>
						</view>
					</view>
				</scroll-view>
			</view>

			<!-- 安全知识库 -->
			<view class="section-container">
				<view class="section-title">安全知识库</view>
				<view class="article-list">
					<view v-for="article in articleList" :key="article.id" class="article-item" @click="openArticle(article)">
						<view class="article-info">
							<text class="article-title">{{ article.title }}</text>
							<text class="article-excerpt">{{ article.excerpt }}</text>
						</view>
						<text class="arrow">›</text>
					</view>
				</view>
			</view>

		</scroll-view>
	</view>
</template>

<script>
	import { database } from './content-database.js';

	export default {
		data() {
			return {
				featuredArticle: {},
				videoList: [],
				articleList: [],
				// 游戏数据
				flappyHighScore: 0
			};
		},
		created() {
			this.featuredArticle = database.getFeaturedArticle();
			this.videoList = database.getVideoList();
			this.articleList = database.getArticleList();
			this.loadGameScores();
		},
		methods: {
			openArticle(article) {
				if (!article || !article.id) return;
				uni.navigateTo({
					url: '/pages/safety-center/article-detail?id=' + article.id
				});
			},
			openArticleById(id) {
				if (!id) return;
				uni.navigateTo({
					url: '/pages/safety-center/article-detail?id=' + id
				});
			},
			// 加载游戏成绩
			loadGameScores() {
				this.flappyHighScore = uni.getStorageSync('flappy_bird_high_score') || 0;
			},
			// 开始小鸟飞飞飞游戏
			startQuizGame() {
				uni.navigateTo({
					url: '/pages/safety-center/flappy-bird-game'
				});
			},
			// 开始真假快判游戏（暂时跳转到小鸟游戏）
			startJudgeGame() {
				uni.showToast({
					title: '更多游戏即将推出',
					icon: 'none',
					duration: 2000
				});
			},
			// 打开举报页面
			openReportPage() {
				uni.navigateTo({
					url: '/pages/safety-center/report-page'
				});
			}
		},
		// 页面显示时刷新游戏成绩
		onShow() {
			this.loadGameScores();
		}
	}
</script>

<style scoped>
	.safety-center-container {
		height: 100vh;
		background-color: #f4f6f9;
	}

	.scroll-view {
		height: 100%;
	}

	.section-container {
		margin-bottom: 30rpx;
		background-color: #fff;
		padding: 30rpx;
	}

	.section-title {
		font-size: 34rpx;
		font-weight: bold;
		margin-bottom: 20rpx;
	}
	
	/* 焦点区域 */
	.focus-section {
		padding: 0;
		background-color: transparent;
	}
	.focus-section .section-title {
		padding: 30rpx 30rpx 0;
	}
	.featured-card {
		margin: 20rpx 30rpx;
		border-radius: 20rpx;
		overflow: hidden;
		box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.1);
	}
	.featured-image {
		width: 100%;
		height: 350rpx;
	}
	.featured-content {
		padding: 25rpx;
		background-color: #fff;
	}
	.featured-title {
		font-size: 32rpx;
		font-weight: bold;
		color: #333;
		display: block;
		margin-bottom: 10rpx;
	}
	.featured-excerpt {
		font-size: 26rpx;
		color: #666;
	}

	/* 视频区域 */
	.video-scroll-view {
		white-space: nowrap;
	}

	.video-list {
		display: flex;
	}

	.video-card {
		display: inline-block;
		width: 300rpx;
		margin-right: 20rpx;
		position: relative;
	}
	.video-thumbnail {
		width: 300rpx;
		height: 180rpx;
		border-radius: 16rpx;
		background-color: #e0e0e0;
	}
	.play-icon {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -65%);
		font-size: 60rpx;
		color: rgba(255, 255, 255, 0.8);
		text-shadow: 0 0 10rpx rgba(0,0,0,0.5);
	}
	.video-title {
		display: block;
		font-size: 26rpx;
		margin-top: 10rpx;
		white-space: normal;
		line-height: 1.4;
	}

	/* 文章列表 */
	.article-list .article-item {
		display: flex;
		align-items: center;
		padding: 25rpx 0;
		border-bottom: 1rpx solid #f0f0f0;
	}
	.article-list .article-item:last-child {
		border-bottom: none;
	}
	.article-info {
		flex: 1;
	}
	.article-title {
		font-size: 30rpx;
		color: #333;
		display: block;
		margin-bottom: 5rpx;
	}
	.article-excerpt {
		font-size: 26rpx;
		color: #999;
	}
	.arrow {
		font-size: 40rpx;
		color: #ccc;
		font-weight: bold;
		margin-left: 20rpx;
	}

	/* 游戏卡片样式 */
	.game-cards {
		display: flex;
		gap: 20rpx;
	}
	
	.game-card {
		flex: 1;
		padding: 25rpx;
		border-radius: 16rpx;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		position: relative;
		overflow: hidden;
	}
	
	.judge-game {
		background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
	}
	
	.game-icon {
		font-size: 40rpx;
		margin-bottom: 10rpx;
	}
	
	.game-title {
		font-size: 28rpx;
		font-weight: bold;
		display: block;
		margin-bottom: 5rpx;
	}
	
	.game-desc {
		font-size: 22rpx;
		opacity: 0.9;
		display: block;
		margin-bottom: 15rpx;
	}
	
	.game-score {
		font-size: 20rpx;
		opacity: 0.8;
		background: rgba(255, 255, 255, 0.2);
		padding: 8rpx 12rpx;
		border-radius: 20rpx;
		text-align: center;
	}

	/* 举报卡片样式 */
	.report-card {
		display: flex;
		align-items: center;
		padding: 25rpx;
		background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
		border-radius: 16rpx;
		box-shadow: 0 4rpx 12rpx rgba(252, 182, 159, 0.3);
	}
	
	.report-icon {
		font-size: 40rpx;
		margin-right: 20rpx;
	}
	
	.report-content {
		flex: 1;
	}
	
	.report-title {
		font-size: 28rpx;
		font-weight: bold;
		color: #8b4513;
		display: block;
		margin-bottom: 5rpx;
	}
	
	.report-desc {
		font-size: 24rpx;
		color: #a0522d;
		opacity: 0.8;
	}
	
	.report-arrow {
		font-size: 40rpx;
		color: #8b4513;
		font-weight: bold;
	}
</style> 