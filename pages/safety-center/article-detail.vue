<template>
	<view class="article-detail-container" v-if="article">
		<scroll-view scroll-y class="scroll-view">
			<image class="article-thumbnail" :src="article.thumbnail" mode="aspectFill"></image>
			<view class="article-content">
				<text class="article-title">{{ article.title }}</text>
				<view class="divider"></view>
				<!-- 使用rich-text渲染带有换行和样式的content -->
				<rich-text :nodes="formattedContent"></rich-text>
			</view>
		</scroll-view>
	</view>
	<view class="loading-container" v-else>
		<text>加载中...</text>
	</view>
</template>

<script>
	import { database } from './content-database.js';

	export default {
		data() {
			return {
				article: null
			};
		},
		onLoad(options) {
			const articleId = options.id;
			if (articleId) {
				// 如果ID是数字，先尝试转为数字类型
				const id = /^\d+$/.test(articleId) ? parseInt(articleId) : articleId;
				this.article = database.getArticleById(id);
			}
		},
		computed: {
			formattedContent() {
				if (!this.article || !this.article.content) {
					return '';
				}
				// 将纯文本中的换行符 \n 转换为 <br> 标签，并处理加粗
				return this.article.content
					.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // 将 **text** 转换为 <strong>text</strong>
					.replace(/\n/g, '<br/>');
			}
		}
	}
</script>

<style scoped>
	.article-detail-container {
		height: 100vh;
	}
	.scroll-view {
		height: 100%;
	}
	.article-thumbnail {
		width: 100%;
		height: 400rpx;
	}
	.article-content {
		padding: 40rpx;
	}
	.article-title {
		font-size: 44rpx;
		font-weight: bold;
		line-height: 1.4;
	}
	.divider {
		height: 1rpx;
		background-color: #e0e0e0;
		margin: 30rpx 0;
	}
	/* rich-text内的样式无法直接在这里定义，
	   但可以通过string style或class的方式传入，
	   为了简单起见，我们主要依赖<br>和<strong> */
	.loading-container {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 100vh;
		color: #999;
	}
</style> 