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

			<!-- 防骗视频课 -->
			<view class="section-container">
				<view class="section-title">防骗视频课</view>
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
				articleList: []
			};
		},
		created() {
			this.featuredArticle = database.getFeaturedArticle();
			this.videoList = database.getVideoList();
			this.articleList = database.getArticleList();
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
			}
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
</style> 