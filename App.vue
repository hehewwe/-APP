<script>
	import smsClassifier from '@/utils/sms-classifier.js';
	import advancedAnalyzer from '@/utils/advanced-risk-analyzer.js';
	import alertManager from '@/utils/alert-manager.js';

	const MONITOR_LIMIT = 200; // 设置滚动监控的数量

	// 将receiver的定义移到外部，确保在App实例化之前plus对象可用
	var receiver = null;

	export default {
		onLaunch: function() {
			console.log('App Launch');
			// #ifdef APP-PLUS
			this.initSmsReceiver();
			this.checkAndSetupSmsListener();
			uni.$on('new-sms-received', this.handleNewSms);
			// #endif
		},
		onShow: function() {
			console.log('App Show');
			// #ifdef APP-PLUS
			// 添加延迟，避免与页面导航冲突
			setTimeout(() => {
				this.checkAndSetupSmsListener();
			}, 1000); // 延迟1秒执行
			// #endif
		},
		onHide: function() {
			console.log('App Hide');
			// #ifdef APP-PLUS
			this.unregisterSmsReceiver();
			// #endif
		},
		methods: {
			initSmsReceiver() {
				// #ifdef APP-PLUS
				receiver = plus.android.implements('io.dcloud.feature.internal.reflect.BroadcastReceiver', {
					onReceive: (context, intent) => {
						try {
							if (intent.getAction() === "android.provider.Telephony.SMS_RECEIVED") {
								const messages = intent.getSerializableExtra("pdus");
								const format = intent.getStringExtra("format");
								for (let i = 0; i < messages.length; i++) {
									const smsMessage = plus.android.invoke('android.telephony.SmsMessage', 'createFromPdu',
										messages[i], format);
									const sms = {
										id: `new_${Date.now()}_${i}`,
										sender: smsMessage.getOriginatingAddress(),
										body: smsMessage.getMessageBody(),
										date: smsMessage.getTimestampMillis()
									};
									uni.$emit('new-sms-received', sms);
								}
							}
						} catch (e) {
							console.error('onReceive error: ', e);
						}
					}
				});
				// #endif
			},
			handleNewSms(sms) {
				console.log(`[App.vue] 收到新的短信事件，发件人: ${sms.sender}`);
				this.updateMonitoredList([sms]);
				const category = smsClassifier.classify(sms);
				if (category === '其他' || category === '推广') {
					advancedAnalyzer.analyze([sms]).then(riskResults => {
						if (riskResults && riskResults.length > 0) {
							alertManager.storeRiskAlerts(riskResults);
							this.createLocalNotification(riskResults[0]);
						}
					});
				}
			},

			checkAndSetupSmsListener() {
				// #ifdef APP-PLUS
				console.log("开始检查短信权限...");
				const permission = 'android.permission.READ_SMS';
				plus.android.checkPermission(permission,
					(result) => {
						console.log(`权限检查结果: ${JSON.stringify(result)}`);
						if (result.granted) {
							console.log('权限已授予，准备启动服务。');
							this.registerSmsReceiver();
							this.performInitialScan();
						} else {
							// -1 表示 PERMISSION_DENIED (用户拒绝，且可能勾选了不再提示)
							// -2 表示 PERMISSION_DENIED_RAW (原生返回的权限值为-1，未通过转换)
							if(result.checkResult === -1 || result.checkResult === -2) {
								console.log('权限已被永久拒绝，引导用户去设置页。');
								this.showSettingsGuide(); 
							} else {
								console.log('权限未授予，发起请求。');
								this.requestPermission();
							}
						}
					},
					(error) => {
						console.error(`检查权限时发生系统错误: ${JSON.stringify(error)}`);
					}
				);
				// #endif
			},

			requestPermission() {
				// #ifdef APP-PLUS
				const permission = 'android.permission.READ_SMS';
				// 使用正确的 API: requestPermissions (复数)，并且传入一个数组
				plus.android.requestPermissions([permission],
					(result) => {
						console.log(`权限请求回调结果: ${JSON.stringify(result)}`);
						// 正确的检查方式：判断权限名是否在 granted 数组中
						if (result && result.granted && result.granted.indexOf(permission) !== -1) {
							console.log('用户已授权，启动服务。');
							this.registerSmsReceiver();
							this.performInitialScan();
						} else {
							console.log('用户拒绝了授权。');
							uni.showToast({
								title: '短信监控功能无法启动',
								icon: 'none',
								duration: 3000
							});
						}
					},
					(e) => {
						console.error(`请求权限时发生系统错误: ${JSON.stringify(e)}`);
						uni.showToast({
							title: '权限请求失败',
							icon: 'error'
						});
					}
				);
				// #endif
			},
			
			showSettingsGuide() {
				// #ifdef APP-PLUS
				uni.showModal({
					title: '权限申请',
					content: '应用需要短信读取权限才能正常工作。请前往系统设置页面手动授予。',
					showCancel: false, // 只显示一个按钮
					confirmText: '去设置',
					success: (res) => {
						if (res.confirm) {
							console.log('用户点击了“去设置”');
							const main = plus.android.runtimeMainActivity();
							const Intent = plus.android.importClass('android.content.Intent');
							const Settings = plus.android.importClass('android.provider.Settings');
							const Uri = plus.android.importClass('android.net.Uri');
							const intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
							const uri = Uri.fromParts("package", main.getPackageName(), null);
							intent.setData(uri);
							main.startActivity(intent);
						}
					}
				});
				// #endif
			},
			
			registerSmsReceiver() {
				// #ifdef APP-PLUS
				const main = plus.android.runtimeMainActivity();
				const filter = new(plus.android.importClass('android.content.IntentFilter'))();
				filter.addAction("android.provider.Telephony.SMS_RECEIVED");
				try {
					main.registerReceiver(receiver, filter);
					console.log('短信广播接收器已成功注册。');
				} catch (e) {
					console.log('短信广播接收器可能已注册，无需重复操作。');
				}
				// #endif
			},

			unregisterSmsReceiver() {
				// #ifdef APP-PLUS
				try {
					const main = plus.android.runtimeMainActivity();
					main.unregisterReceiver(receiver);
					console.log('短信广播接收器已成功注销。');
				} catch (e) {
					console.log('注销短信广播接收器时出错（可能未注册或已注销）。');
				}
				// #endif
			},
			
			async performInitialScan() {
				// #ifdef APP-PLUS
				console.log(`开始执行初始扫描，读取最近${MONITOR_LIMIT}条短信...`);
				const Uri = plus.android.importClass("android.net.Uri");
				const mainActivity = plus.android.runtimeMainActivity();
				const contentResolver = mainActivity.getContentResolver();
				const SMS_INBOX = Uri.parse("content://sms/");
				const projection = ["_id", "address", "body", "date", "type"];

				try {
					const cursor = plus.android.invoke(contentResolver, 'query', SMS_INBOX, projection, "type=1", null,
						`date desc LIMIT ${MONITOR_LIMIT}`);
					if (cursor) {
						const smsList = [];
						const idIndex = plus.android.invoke(cursor, 'getColumnIndex', '_id');
						const addressIndex = plus.android.invoke(cursor, 'getColumnIndex', 'address');
						const bodyIndex = plus.android.invoke(cursor, 'getColumnIndex', 'body');
						const dateIndex = plus.android.invoke(cursor, 'getColumnIndex', 'date');
						const typeIndex = plus.android.invoke(cursor, 'getColumnIndex', 'type');

						while (plus.android.invoke(cursor, 'moveToNext')) {
							smsList.push({
								id: plus.android.invoke(cursor, 'getString', idIndex),
								sender: plus.android.invoke(cursor, 'getString', addressIndex),
								body: plus.android.invoke(cursor, 'getString', bodyIndex),
								date: plus.android.invoke(cursor, 'getLong', dateIndex),
								type: plus.android.invoke(cursor, 'getInt', typeIndex)
							});
						}
						plus.android.invoke(cursor, 'close');
						console.log(`初始扫描完成，读取到${smsList.length}条短信。`);
						this.updateMonitoredList(smsList, true);
					}
				} catch (e) {
					console.error("初始扫描时发生错误: ", e);
				}
				// #endif
			},
			
			updateMonitoredList(newSmsItems, overwrite = false) {
				const currentList = overwrite ? [] : (uni.getStorageSync('monitoredSmsList') || []);
				const updatedList = [...newSmsItems, ...currentList];

				if (updatedList.length > MONITOR_LIMIT) {
					updatedList.splice(MONITOR_LIMIT);
				}

				uni.setStorageSync('monitoredSmsList', updatedList);
				console.log(`监控列表已更新，当前数量: ${updatedList.length}。发送全局通知...`);
				uni.$emit('monitored-sms-updated');
			},
			
			createLocalNotification(alert) {
				// #ifdef APP-PLUS
				const riskLevelMap = {
					high: '高',
					medium: '中',
					low: '低'
				};
				const riskLevelText = riskLevelMap[alert.riskLevel] || '未知';
				const title = `检测到${riskLevelText}风险短信`;
				const content = `来自 ${alert.sender} 的消息被判定为"${alert.riskType}"，请注意防范。`;
				plus.push.createMessage(content, {}, {
					title: title
				});
				// #endif
			}
		}
	}
</script>

<style>
	/*每个页面公共css */
	@import '@/uni.scss';
</style>