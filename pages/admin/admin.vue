<template>
	<view class="admin-container">
		<view class="header">
			<view class="back-button" @click="goBack">
				<text class="icon">←</text>
			</view>
			<view class="title">后台管理</view>
		</view>

		<view class="table-selector">
			<button :class="['table-button', currentView === 'user' ? 'active' : '']" @click="switchView('user')">用户表</button>
			<button :class="['table-button', currentView === 'sms_record' ? 'active' : '']" @click="switchView('sms_record')">记录表</button>
			<button :class="['table-button', currentView === 'case_serial' ? 'active' : '']" @click="switchView('case_serial')">编号表统计</button>
			<button :class="['table-button', currentView === 'report_record' ? 'active' : '']" @click="switchView('report_record')">举报管理</button>
		</view>

		<!-- 用户表 -->
		<view class="content-area" v-if="currentView === 'user'">
			<view v-if="isLoading" class="loading-tip">正在加载...</view>
			<view v-else-if="tableData.length === 0" class="empty-tip">没有数据</view>
			
			<scroll-view scroll-x="true" class="table-wrapper" v-if="tableData.length > 0">
				<table class="data-table">
					<thead>
						<tr>
							<th v-for="header in tableHeaders" :key="header">{{ header }}</th>
							<th>操作</th>
						</tr>
					</thead>
					<tbody>
						<tr v-for="row in tableData" :key="row.id || row.category">
							<td v-for="header in tableHeaders" :key="header">{{ row[header] }}</td>
							<td>
								<button class="delete-button" @click="confirmDelete(row)">删除</button>
							</td>
						</tr>
					</tbody>
				</table>
			</scroll-view>
		</view>

		<!-- 编号表统计 (新图表 + 表格切换) -->
		<view class="content-area" v-if="currentView === 'case_serial'">
			<view class="view-toggle">
				<button class="toggle-button" @click="toggleCaseSerialView">
					{{ caseSerialViewMode === 'chart' ? '查看表格数据' : '查看图表统计' }}
				</button>
				<!-- 新增：重置数据按钮 -->
				<button class="reset-button" @click="confirmResetData">清空所有记录</button>
			</view>

			<view v-if="isLoading" class="loading-tip">正在加载...</view>
			<view v-else-if="!chartData.categories || chartData.categories.length === 0" class="empty-tip">没有数据</view>
			<template v-else>
				<!-- 图表视图 -->
				<qiun-data-charts 
					v-if="caseSerialViewMode === 'chart'"
					type="column"
					:opts="chartOpts"
					:chartData="chartData"
					canvas-id="CaseSerialChart"
				/>
				<!-- 表格视图 -->
				<scroll-view v-if="caseSerialViewMode === 'table'" scroll-x="true" class="table-wrapper" style="margin-top: 20rpx;">
					<table class="data-table">
						<thead>
							<tr>
								<th v-for="header in tableHeaders" :key="header">{{ header }}</th>
								<th>操作</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="row in tableData" :key="row.category">
								<td v-for="header in tableHeaders" :key="header">{{ row[header] }}</td>
								<td>
									<!-- 修改按钮文字和功能 -->
									<button class="reset-counter-button" @click="confirmResetCounter(row)">重置</button>
								</td>
							</tr>
						</tbody>
					</table>
				</scroll-view>
			</template>
		</view>

		<!-- 记录表 (新逻辑) -->
		<view class="content-area" v-if="currentView === 'sms_record'">
			<!-- 1. 统计仪表盘 -->
			<view class="stats-dashboard">
				<view class="stat-card">
					<view class="stat-value">{{ stats.today_new_records }}</view>
					<view class="stat-label">今日新增</view>
				</view>
				<view class="stat-card">
					<view class="stat-value">{{ stats.total_fraud_records }}</view>
					<view class="stat-label">诈骗总数</view>
				</view>
				<view class="stat-card">
					<view class="stat-value wide">{{ stats.top_fraud_type.type }} ({{stats.top_fraud_type.percentage}}%)</view>
					<view class="stat-label">高发类型</view>
				</view>
			</view>
			
			<!-- 2. 搜索与筛选 -->
			<view class="filter-section">
				<input class="search-input" v-model="filters.search_keyword" placeholder="搜短信内容/用户名" @confirm="applyFilters" />
				<picker mode="selector" :range="fraudTypeOptions" @change="onFraudTypeChange">
					<view class="picker">
						{{ filters.fraud_type || '所有类型' }}
					</view>
				</picker>
				<button class="filter-button" @click="applyFilters">筛选</button>
			</view>

			<!-- 3. 增强版表格 -->
			<scroll-view scroll-y="true" class="record-table-wrapper">
				<view v-if="isLoading" class="loading-tip">正在加载...</view>
				<view v-else-if="recordsData.length === 0" class="empty-tip">没有符合条件的记录</view>
				<view v-else class="record-list">
					<view v-for="record in recordsData" :key="record.id" :class="['record-item', record.is_fraud === 'True' ? 'is-fraud' : '']">
						<view class="record-row">
							<text class="record-username">{{ record.username }}</text>
							<text class="record-fraud-type">{{ record.fraud_type }}</text>
							<text class="record-time">{{ record.created_at }}</text>
						</view>
						<view class="record-text" @click="showFullText(record.sms_text)">
							{{ truncate(record.sms_text) }}
						</view>
						<button class="delete-button record-delete" @click="confirmDelete(record)">删除</button>
					</view>
				</view>
			</scroll-view>
			
			<!-- 4. 分页 -->
			<view class="pagination" v-if="pagination.total > 0">
				<text @click="changePage(pagination.current_page - 1)" :disabled="pagination.current_page <= 1">上一页</text>
				<text>第 {{ pagination.current_page }} / {{ pagination.pages }} 页</text>
				<text @click="changePage(pagination.current_page + 1)" :disabled="pagination.current_page >= pagination.pages">下一页</text>
			</view>

		</view>

		<!-- 举报管理 -->
		<view class="content-area" v-if="currentView === 'report_record'">
			<!-- 状态筛选和统计 -->
			<view class="report-controls">
				<view class="status-filter">
					<text class="filter-label">状态筛选：</text>
					<picker mode="selector" :value="reportStatusIndex" :range="reportStatusOptions" 
							range-key="label" @change="onReportStatusChange">
						<button class="filter-button">{{ reportStatusOptions[reportStatusIndex].label }}</button>
					</picker>
				</view>
				
				<view class="report-stats">
					<view class="stat-item pending">
						<text class="stat-number">{{ reportStats.pending }}</text>
						<text class="stat-label">待处理</text>
					</view>
					<view class="stat-item processing">
						<text class="stat-number">{{ reportStats.processing }}</text>
						<text class="stat-label">处理中</text>
					</view>
					<view class="stat-item resolved">
						<text class="stat-number">{{ reportStats.resolved }}</text>
						<text class="stat-label">已处理</text>
					</view>
				</view>
			</view>

			<!-- 举报列表 -->
			<view v-if="isLoading" class="loading-tip">正在加载...</view>
			<view v-else-if="reportData.length === 0" class="empty-tip">暂无举报记录</view>
			
			<view v-else class="report-list">
				<view v-for="report in reportData" :key="report.id" class="report-card">
					<view class="report-header">
						<view class="report-info">
							<text class="report-id">ID: {{ report.id }}</text>
							<text class="report-type">{{ getReportTypeLabel(report.report_type) }}</text>
						</view>
						<view :class="['status-badge', report.status]">
							{{ getStatusLabel(report.status) }}
						</view>
					</view>
					
					<view class="report-content">
						<view class="content-row">
							<text class="label">举报用户：</text>
							<text class="value">{{ report.username }}</text>
						</view>
						<view class="content-row">
							<text class="label">来源信息：</text>
							<text class="value">{{ report.source_info || '未提供' }}</text>
						</view>
						<view class="content-row">
							<text class="label">举报内容：</text>
							<text class="value content-text">{{ report.content }}</text>
						</view>
						<view class="content-row">
							<text class="label">提交时间：</text>
							<text class="value">{{ report.created_at }}</text>
						</view>
						<view class="content-row" v-if="report.updated_at !== report.created_at">
							<text class="label">更新时间：</text>
							<text class="value">{{ report.updated_at }}</text>
						</view>
					</view>
					
					<view class="report-actions">
						<button v-if="report.status === 'pending'" 
								class="action-btn start-btn" 
								@click="updateReportStatus(report.id, 'processing')">
							开始处理
						</button>
						<button v-if="report.status === 'processing'" 
								class="action-btn complete-btn" 
								@click="updateReportStatus(report.id, 'resolved')">
							标记完成
						</button>
						<button v-if="report.status === 'resolved'" 
								class="action-btn reopen-btn" 
								@click="updateReportStatus(report.id, 'pending')">
							重新打开
						</button>
						<button class="action-btn delete-btn" @click="confirmDeleteReport(report)">
							删除
						</button>
					</view>
				</view>
			</view>

			<!-- 分页 -->
			<view class="pagination" v-if="reportPagination.pages > 1">
				<button class="page-btn" :disabled="reportPagination.current_page <= 1" 
						@click="loadReportPage(reportPagination.current_page - 1)">上一页</button>
				<text class="page-info">{{ reportPagination.current_page }} / {{ reportPagination.pages }}</text>
				<button class="page-btn" :disabled="reportPagination.current_page >= reportPagination.pages" 
						@click="loadReportPage(reportPagination.current_page + 1)">下一页</button>
			</view>
		</view>
		
		<!-- 全文弹窗 -->
		<view v-if="fullText" class="modal-overlay" @click="fullText = ''">
			<view class="modal-content" @click.stop>
				<scroll-view scroll-y="true" style="height: 100%;">
					<text selectable>{{ fullText }}</text>
				</scroll-view>
			</view>
		</view>
	</view>
</template>

<script>
	import config from '@/utils/config.js';
	// 引入图表组件，如果您的项目结构不同，请检查路径
	import qiunDataCharts from '@/uni_modules/qiun-data-charts/components/qiun-data-charts/qiun-data-charts.vue';

	export default {
		components: {
			qiunDataCharts
		},
		data() {
			return {
				currentView: 'user', // user, sms_record, case_serial
				isLoading: false,
				// 旧版表格数据
				tableHeaders: [],
				tableData: [],
				// 编号表视图切换
				caseSerialViewMode: 'chart', // 'chart' or 'table'
				// 图表数据
				chartData: {},
				chartOpts: {
					color: ["#1890FF"],
					padding: [15,15,30,5], // 增加底部边距
					xAxis: {
						disableGrid: true,
						rotateLabel: true // 开启标签旋转
					},
					yAxis: {
						data: [{
							min: 0,
							// 强制Y轴刻度为整数
							tofix: 0,
							// 建议分割段数，u-charts会尽量接近这个值来生成整数刻度
							splitNumber: 5 
						}]
					},
					extra: {
						column: {
							width: 20
						}
					}
				},
				// 新版记录表数据
				stats: { today_new_records: 0, total_fraud_records: 0, top_fraud_type: { type: 'N/A', percentage: 0 } },
				filters: { search_keyword: '', fraud_type: '' },
				fraudTypeOptions: ['全部类型', '刷单返利类', '虚假网络投资理财类', '冒充电商物流客服类', '贷款、代办信用卡类', '网络游戏产品虚假交易类', '虚假购物、服务类', '冒充公检法及政府机关类', '虚假征信类', '冒充领导、熟人类', '冒充军警购物类诈骗', '网络婚恋、交友类', '网黑案件', '正常信息'],
				recordsData: [],
				pagination: { total: 0, pages: 1, current_page: 1, per_page: 10 },
				fullText: '',
				// 举报管理数据
				reportData: [],
				reportPagination: { total: 0, pages: 1, current_page: 1, per_page: 10 },
				reportStats: { pending: 0, processing: 0, resolved: 0 },
				reportStatusIndex: 0,
				reportStatusOptions: [
					{ label: '全部状态', value: '' },
					{ label: '待处理', value: 'pending' },
					{ label: '处理中', value: 'processing' },
					{ label: '已处理', value: 'resolved' }
				]
			};
		},
		onLoad() {
			this.switchView('user'); // 默认加载用户表
		},
		methods: {
			toggleCaseSerialView() {
				this.caseSerialViewMode = this.caseSerialViewMode === 'chart' ? 'table' : 'chart';
			},
			truncate(text, length = 30) {
				if (text.length > length) {
					return text.substring(0, length) + '... [查看详情]';
				}
				return text;
			},
			showFullText(text) {
				this.fullText = text;
			},
			goBack() {
				uni.navigateBack();
			},
			switchView(view) {
				this.currentView = view;
				if (view === 'user') {
					this.fetchSimpleTable(view);
				} else if (view === 'sms_record') {
					this.fetchStats();
					this.applyFilters();
				} else if (view === 'case_serial') {
					this.fetchChartData();
					this.fetchSimpleTable(view); // 同时获取表格数据
				} else if (view === 'report_record') {
					this.fetchReportData();
					this.fetchReportStats();
				}
			},
			// --- 新增：图表方法 ---
			fetchChartData() {
				this.isLoading = true;
				uni.request({
					url: `${config.BASE_URL}/admin/data/case_serial`,
					success: (res) => {
						if (res.statusCode === 200 && res.data.data.length > 0) {
							// 格式化数据以适应图表库
							let categories = [];
							let seriesData = [];
							// 添加一个映射，将类别代码转换为可读的名称
							const categoryMap = {
								'a': '刷单', 'b': '理财', 'c': '客服', 'd': '贷款', 'e': '游戏', 'f': '购物',
								'g': '公检法', 'h': '征信', 'i': '熟人', 'j': '军警', 'k': '婚恋', 'l': '网黑', 'z': '未知'
							};
							res.data.data.forEach(item => {
								categories.push(categoryMap[item.category] || item.category);
								// Y轴显示案件总数 = next_val - 1
								seriesData.push(parseInt(item.next_val) - 1);
							});
							this.chartData = {
								categories: categories,
								series: [{
									name: "案件数量",
									data: seriesData
								}]
							};
						}
					},
					fail: () => uni.showToast({ title: '图表数据加载失败', icon: 'none' }),
					complete: () => this.isLoading = false
				});
			},
			// --- 新版记录表方法 ---
			fetchStats() {
				uni.request({
					url: `${config.BASE_URL}/admin/stats`,
					success: (res) => {
						if (res.statusCode === 200) this.stats = res.data;
					}
				});
			},
			applyFilters() {
				this.pagination.current_page = 1;
				this.fetchRecords();
			},
			onFraudTypeChange(e) {
				const selectedType = this.fraudTypeOptions[e.detail.value];
				// 如果选择的是“全部类型”，则清空筛选条件
				if (selectedType === '全部类型') {
					this.filters.fraud_type = '';
				} else {
					this.filters.fraud_type = selectedType;
				}
				this.applyFilters(); // 自动应用筛选
			},
			changePage(page) {
				if (page > 0 && page <= this.pagination.pages) {
					this.pagination.current_page = page;
					this.fetchRecords();
				}
			},
			fetchRecords() {
				this.isLoading = true;
				let params = `?page=${this.pagination.current_page}&per_page=${this.pagination.per_page}`;
				if (this.filters.search_keyword) params += `&search_keyword=${this.filters.search_keyword}`;
				if (this.filters.fraud_type) params += `&fraud_type=${this.filters.fraud_type}`;

				uni.request({
					url: `${config.BASE_URL}/admin/sms_records${params}`,
					success: (res) => {
						if (res.statusCode === 200) {
							this.recordsData = res.data.data;
							this.pagination.total = res.data.total;
							this.pagination.pages = res.data.pages;
						} else {
							uni.showToast({ title: '加载记录失败', icon: 'none' });
						}
					},
					fail: () => uni.showToast({ title: '网络错误', icon: 'error' }),
					complete: () => this.isLoading = false
				});
			},
			// --- 旧版通用表格方法 ---
			fetchSimpleTable(tableName) {
				this.isLoading = true;
				this.tableData = [];
				this.tableHeaders = [];
				uni.request({
					url: `${config.BASE_URL}/admin/data/${tableName}`,
					method: 'GET',
					success: (res) => {
						if (res.statusCode === 200) {
							this.tableData = res.data.data;
							if (this.tableData.length > 0) {
								this.tableHeaders = Object.keys(this.tableData[0]);
							}
						} else {
							uni.showToast({ title: res.data.msg || '加载失败', icon: 'none' });
						}
					},
					fail: () => uni.showToast({ title: '网络错误', icon: 'error' }),
					complete: () => this.isLoading = false
				});
			},
			confirmDelete(row) {
				const pkName = (this.currentView === 'case_serial') ? 'category' : 'id';
				const pkValue = row[pkName];
				uni.showModal({
					title: '确认删除',
					content: `确定要删除这条 ${pkName}=${pkValue} 的记录吗？`,
					success: (res) => {
						if (res.confirm) this.deleteItem(pkValue);
					}
				});
			},
			// --- 新增：重置分类计数器方法 ---
			confirmResetCounter(row) {
				const category = row.category;
				uni.showModal({
					title: '确认操作',
					content: `确认后将该类别 (${category}) 计数器归1`,
					success: (res) => {
						if (res.confirm) {
							this.resetCounter(category);
						}
					}
				});
			},
			resetCounter(category) {
				uni.showLoading({ title: '正在重置...' });
				uni.request({
					url: `${config.BASE_URL}/admin/reset_category/${category}`,
					method: 'POST',
					success: (res) => {
						if (res.statusCode === 200) {
							uni.showToast({ title: '计数器已归1', icon: 'success' });
							// 刷新图表和表格
							this.fetchChartData();
							this.fetchSimpleTable(this.currentView);
						} else {
							uni.showToast({ title: res.data.msg || '操作失败', icon: 'none' });
						}
					},
					fail: () => uni.showToast({ title: '网络错误', icon: 'error' }),
					complete: () => uni.hideLoading()
				});
			},
			// --- 新增：重置数据方法 ---
			confirmResetData() {
				uni.showModal({
					title: '⚠️ 危险操作确认',
					content: '此操作将永久删除所有分析记录，并将所有案件编号计数器归零。此操作不可撤销，确定要继续吗？',
					confirmColor: '#e53935',
					success: (res) => {
						if (res.confirm) {
							this.resetAllData();
						}
					}
				});
			},
			resetAllData() {
				uni.showLoading({ title: '正在重置数据...' });
				uni.request({
					url: `${config.BASE_URL}/admin/reset_data`,
					method: 'POST',
					success: (res) => {
						if (res.statusCode === 200) {
							uni.showToast({ title: '数据已成功重置', icon: 'success' });
							// 刷新当前视图和记录表视图
							this.fetchChartData();
							this.fetchSimpleTable(this.currentView);
							this.fetchStats(); // 确保记录表的统计也更新
						} else {
							uni.showToast({ title: res.data.msg || '重置失败', icon: 'none' });
						}
					},
					fail: () => uni.showToast({ title: '网络错误', icon: 'error' }),
					complete: () => uni.hideLoading()
				});
			},
			deleteItem(pkValue) {
				uni.showLoading({ title: '删除中...' });
				uni.request({
					url: `${config.BASE_URL}/admin/data/${this.currentView}/${pkValue}`,
					method: 'DELETE',
					success: (res) => {
						if (res.statusCode === 200) {
							uni.showToast({ title: '删除成功', icon: 'success' });
							if (this.currentView === 'sms_record') this.fetchRecords();
							else if (this.currentView === 'case_serial') {
								this.fetchChartData();
								this.fetchSimpleTable(this.currentView); // 删除后同时刷新图表和表格
							}
							else this.fetchSimpleTable(this.currentView);
						} else {
							uni.showToast({ title: res.data.msg || '删除失败', icon: 'none' });
						}
					},
					fail: () => uni.showToast({ title: '网络错误', icon: 'error' }),
					complete: () => uni.hideLoading()
				});
			},
			
			// --- 举报管理方法 ---
			fetchReportData(page = 1) {
				this.isLoading = true;
				const statusFilter = this.reportStatusOptions[this.reportStatusIndex].value;
				
				uni.request({
					url: `${config.BASE_URL}/admin/reports`,
					data: {
						page: page,
						per_page: 10,
						status: statusFilter
					},
					success: (res) => {
						if (res.statusCode === 200) {
							this.reportData = res.data.data;
							this.reportPagination = {
								total: res.data.total,
								pages: res.data.pages,
								current_page: res.data.current_page,
								per_page: 10
							};
						} else {
							uni.showToast({ title: res.data.msg || '获取举报数据失败', icon: 'none' });
						}
					},
					fail: () => uni.showToast({ title: '网络错误', icon: 'error' }),
					complete: () => this.isLoading = false
				});
			},
			
			fetchReportStats() {
				// 统计各状态的数量
				uni.request({
					url: `${config.BASE_URL}/admin/reports`,
					data: { per_page: 1000 }, // 获取所有数据来统计
					success: (res) => {
						if (res.statusCode === 200) {
							const allReports = res.data.data;
							this.reportStats = {
								pending: allReports.filter(r => r.status === 'pending').length,
								processing: allReports.filter(r => r.status === 'processing').length,
								resolved: allReports.filter(r => r.status === 'resolved').length
							};
						}
					}
				});
			},
			
			onReportStatusChange(e) {
				this.reportStatusIndex = e.detail.value;
				this.fetchReportData(1);
			},
			
			loadReportPage(page) {
				this.fetchReportData(page);
			},
			
			updateReportStatus(reportId, newStatus) {
				uni.showLoading({ title: '更新中...' });
				
				uni.request({
					url: `${config.BASE_URL}/admin/reports/${reportId}/status`,
					method: 'PUT',
					data: { status: newStatus },
					success: (res) => {
						if (res.statusCode === 200) {
							uni.showToast({ title: '状态更新成功', icon: 'success' });
							this.fetchReportData(this.reportPagination.current_page);
							this.fetchReportStats();
						} else {
							uni.showToast({ title: res.data.msg || '更新失败', icon: 'none' });
						}
					},
					fail: () => uni.showToast({ title: '网络错误', icon: 'error' }),
					complete: () => uni.hideLoading()
				});
			},
			
			confirmDeleteReport(report) {
				uni.showModal({
					title: '确认删除',
					content: `确定要删除举报ID: ${report.id} 吗？此操作不可撤销。`,
					success: (res) => {
						if (res.confirm) {
							this.deleteReport(report.id);
						}
					}
				});
			},
			
			deleteReport(reportId) {
				uni.showLoading({ title: '删除中...' });
				
				// 由于后端暂时没有删除接口，这里可以先用通用删除接口
				// 后期可以添加专门的举报删除接口
				uni.request({
					url: `${config.BASE_URL}/admin/data/report_record/${reportId}`,
					method: 'DELETE',
					success: (res) => {
						if (res.statusCode === 200) {
							uni.showToast({ title: '删除成功', icon: 'success' });
							this.fetchReportData(this.reportPagination.current_page);
							this.fetchReportStats();
						} else {
							uni.showToast({ title: res.data.msg || '删除失败', icon: 'none' });
						}
					},
					fail: () => uni.showToast({ title: '网络错误', icon: 'error' }),
					complete: () => uni.hideLoading()
				});
			},
			
			getReportTypeLabel(type) {
				const typeMap = {
					'a': '刷单返利类',
					'b': '虚假网络投资理财类',
					'c': '冒充电商物流客服类',
					'd': '贷款、代办信用卡类',
					'e': '网络游戏产品虚假交易类',
					'f': '虚假购物、服务类',
					'g': '冒充公检法及政府机关类',
					'h': '虚假征信类',
					'i': '冒充领导、熟人类',
					'j': '冒充军警购物类诈骗',
					'k': '网络婚恋、交友类',
					'l': '网黑案件'
				};
				return typeMap[type] || type;
			},
			
			getStatusLabel(status) {
				const statusMap = {
					'pending': '待处理',
					'processing': '处理中',
					'resolved': '已处理'
				};
				return statusMap[status] || status;
			}
		}
	}
</script>

<style scoped>
/* 基本样式 */
.admin-container { background-color: #f4f6f9; min-height: 100vh; }
.header { display: flex; align-items: center; padding: 20rpx 30rpx; background-color: #fff; border-bottom: 1rpx solid #eee; position: relative; padding-top: var(--status-bar-height); }
.back-button { position: absolute; left: 30rpx; top: var(--status-bar-height); bottom: 0; display: flex; align-items: center; justify-content: center; }
.icon { font-size: 40rpx; font-weight: bold; }
.title { flex: 1; text-align: center; font-size: 34rpx; font-weight: bold; }
.table-selector { display: flex; justify-content: space-around; padding: 20rpx; background-color: #fff; border-bottom: 1rpx solid #eee; }
.table-button { font-size: 28rpx; margin: 0 10rpx; background-color: #eee; }
.table-button.active { background-color: #007bff; color: #fff; }
.content-area { padding: 20rpx; }
.loading-tip, .empty-tip { text-align: center; color: #999; padding: 100rpx 0; }
.view-toggle { display: flex; justify-content: space-between; margin-bottom: 20rpx; }
.toggle-button, .reset-button { font-size: 26rpx; }
.reset-button { background-color: #e53935; color: #fff; }

/* 旧版表格样式 */
.table-wrapper { width: 100%; }
.data-table { width: 100%; border-collapse: collapse; background-color: #fff; font-size: 24rpx; }
.data-table th, .data-table td { border: 1px solid #ddd; padding: 12rpx; text-align: left; white-space: nowrap; }
.data-table th { background-color: #f2f2f2; font-weight: bold; }
.delete-button { font-size: 24rpx; background-color: #e53935; color: white; padding: 5rpx 10rpx; border-radius: 5rpx; border: none; }
.reset-counter-button { font-size: 24rpx; background-color: #ff9800; color: white; padding: 5rpx 10rpx; border-radius: 5rpx; border: none; }

/* 编号表统计图表样式 */
.qiun-data-charts {
	width: 100%;
	height: 500rpx; /* 您可以根据需要调整高度 */
}

/* 新版记录表样式 */
.stats-dashboard { display: flex; justify-content: space-around; margin-bottom: 20rpx; gap: 15rpx; }
.stat-card { flex: 1; background-color: #fff; border-radius: 15rpx; padding: 20rpx; text-align: center; box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05); }
.stat-value { font-size: 40rpx; font-weight: bold; color: #007bff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.stat-value.wide { font-size: 28rpx; }
.stat-label { font-size: 24rpx; color: #666; margin-top: 5rpx; }

.filter-section { display: flex; gap: 15rpx; margin-bottom: 20rpx; }
.search-input { flex: 1; background-color: #fff; border-radius: 10rpx; padding: 15rpx; font-size: 28rpx; }
.picker { background-color: #fff; padding: 15rpx; border-radius: 10rpx; font-size: 28rpx; }
.filter-button { background-color: #007bff; color: #fff; font-size: 28rpx; }

.record-list { display: flex; flex-direction: column; gap: 15rpx; }
.record-item { background-color: #fff; border-radius: 15rpx; padding: 20rpx; position: relative; }
.record-item.is-fraud { border-left: 10rpx solid #e53935; }
.record-row { display: flex; justify-content: space-between; margin-bottom: 10rpx; font-size: 24rpx; color: #666; }
.record-username { font-weight: bold; }
.record-fraud-type { background-color: #eee; padding: 2rpx 10rpx; border-radius: 20rpx; }
.record-text { font-size: 28rpx; color: #333; line-height: 1.5; margin-bottom: 10rpx; }
.record-delete { position: absolute; right: 20rpx; bottom: 20rpx; }

.pagination { display: flex; justify-content: space-around; align-items: center; padding: 30rpx 0; font-size: 28rpx; }

/* 举报管理样式 */
.report-controls { 
	background-color: #fff; 
	padding: 20rpx; 
	border-radius: 15rpx; 
	margin-bottom: 20rpx; 
}

.status-filter { 
	display: flex; 
	align-items: center; 
	margin-bottom: 20rpx; 
}

.filter-label { 
	font-size: 28rpx; 
	margin-right: 15rpx; 
	color: #333; 
}

.filter-button { 
	background-color: #007bff; 
	color: #fff; 
	font-size: 26rpx; 
	padding: 10rpx 20rpx; 
	border-radius: 8rpx; 
}

.report-stats { 
	display: flex; 
	justify-content: space-around; 
}

.stat-item { 
	text-align: center; 
	padding: 15rpx; 
	border-radius: 10rpx; 
}

.stat-item.pending { background-color: #fff3cd; }
.stat-item.processing { background-color: #d4edda; }
.stat-item.resolved { background-color: #d1ecf1; }

.stat-number { 
	display: block; 
	font-size: 32rpx; 
	font-weight: bold; 
	color: #333; 
}

.stat-label { 
	display: block; 
	font-size: 24rpx; 
	color: #666; 
	margin-top: 5rpx; 
}

.report-list { 
	display: flex; 
	flex-direction: column; 
	gap: 15rpx; 
}

.report-card { 
	background-color: #fff; 
	border-radius: 15rpx; 
	padding: 20rpx; 
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1); 
}

.report-header { 
	display: flex; 
	justify-content: space-between; 
	align-items: center; 
	margin-bottom: 15rpx; 
	padding-bottom: 10rpx; 
	border-bottom: 1rpx solid #eee; 
}

.report-info { 
	display: flex; 
	gap: 15rpx; 
}

.report-id { 
	font-size: 24rpx; 
	color: #666; 
}

.report-type { 
	background-color: #e9ecef; 
	padding: 4rpx 12rpx; 
	border-radius: 12rpx; 
	font-size: 22rpx; 
	color: #495057; 
}

.status-badge { 
	padding: 8rpx 16rpx; 
	border-radius: 20rpx; 
	font-size: 22rpx; 
	color: #fff; 
	font-weight: bold; 
}

.status-badge.pending { background-color: #ffc107; }
.status-badge.processing { background-color: #28a745; }
.status-badge.resolved { background-color: #17a2b8; }

.report-content { 
	margin-bottom: 15rpx; 
}

.content-row { 
	display: flex; 
	margin-bottom: 8rpx; 
	font-size: 26rpx; 
}

.content-row .label { 
	width: 180rpx; 
	flex-shrink: 0; 
	color: #666; 
	font-weight: bold; 
}

.content-row .value { 
	flex: 1; 
	color: #333; 
}

.content-text { 
	line-height: 1.5; 
	word-break: break-all; 
}

.report-actions { 
	display: flex; 
	gap: 10rpx; 
	flex-wrap: wrap; 
}

.action-btn { 
	padding: 12rpx 20rpx; 
	border-radius: 8rpx; 
	font-size: 24rpx; 
	border: none; 
	color: #fff; 
}

.start-btn { background-color: #28a745; }
.complete-btn { background-color: #17a2b8; }
.reopen-btn { background-color: #ffc107; color: #212529; }
.delete-btn { background-color: #dc3545; }

.page-btn { 
	background-color: #007bff; 
	color: #fff; 
	padding: 12rpx 24rpx; 
	border-radius: 8rpx; 
	font-size: 26rpx; 
}

.page-btn:disabled { 
	background-color: #6c757d; 
	opacity: 0.6; 
}

.page-info { 
	font-size: 26rpx; 
	color: #666; 
}

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background-color: #fff; padding: 40rpx; border-radius: 15rpx; width: 80%; max-height: 70%; }
</style> 