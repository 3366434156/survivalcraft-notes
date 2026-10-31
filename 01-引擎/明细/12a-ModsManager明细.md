# ModsManager 域明细（一行一文件）

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(72/72 文件, 16,876 行)
> 主页: 01-引擎\12-ModAPI与加载链.md。行号以 2026-10-31 源码为准。行数=总行数；ModLoader.cs >2000 行分段读完，其余全文读。

## 顶级目录（E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\，24 文件）

| 文件 | 行数 | 职责与实读要点 |
|---|---|---|
| ModsManager.cs | 1426 | 全域静态门面：常量(API 1.9.5.1/游戏 2.4.0.0)、钩子表(:111,133-214)、DeserializeJson(:219)、拓扑排序(:543)、RescanModsAsync(:644)、TryCreateModEntity(:806)、CombineClo/Cr/DataBase(:938/:969/:1083)、ClassSubstitutes(:1049-1212)、TryParseVersionRange(:1214)、加固包(:1291-1399) |
| ModLoader.cs | 2338 | 抽象 Loader，236 个 public virtual 成员；主 Loader 专属拦截 GetModFiles/GetModFile(:31-46)；VitalStats 六连钩子(:2138-2250)；屏幕/对话框替换 OnSwitchScreen/OnShowDialog(:2257/:2264)；字体链三钩子(:2324-2337) |
| ModEntity.cs | 562 | 模组实体：InitResources 五道禁用判定(:233-269)、icon 两段加载(:70-91)、GetFiles/GetFile 拦截管线(:98-160)、HandleAssembly 四类发现(:406-442)、CheckDependencies 依赖环双杀(:486-492)、Equals=包名+版本(:548) |
| SurvivalCraftModEntity.cs | 159 | 原版实体：注册 19 个 IContentReader(:13-40)、Content.zip 外置 app:/Content.zip 优先否则内嵌资源(:50-58)、LoadOrder=int.MinValue(:68)、原版 Block 必须有 public static int Index(:100-114)、LoadOrder 后注册 14 个方块分类(:143-158) |
| FastDebugModEntity.cs | 129 | 散文件虚拟模组：包名 ctor 里 "debug"/默认 "fastdebug"(:11/:127)；递归收 Mods/ 下全部非 .scmod 文件(:36-51)；SafeMode 只出默认 modinfo(:17-19) |
| SurvivalCraftModLoader.cs | 253 | 原版自身 Loader：__ModInitialize 注册 9 钩子(:15-26)、InitKeyCompatibleGroups 5 组(:28-39)、GetCameraList 调试相机(:41-47)、ManageCameras 挂条件委托(:49-61)、玩家名牌矢量字体绘制(:130-210)、TextBoxWidget Overdraw 层调整(:233-245) |
| ModInfo.cs | 94 | modinfo 模型：LoadOrder 枚举 Survivalcraft=int.MinValue/ThemeMod=-16384/Default=0/HelpfulMod=16384(:5-10)、DependencyDetails 富信息(:53)、RawSettings 延迟解析(:76)、GetHashCode=Name+PackageName+Version(:78) |
| ModDisableReason.cs | 9 | 禁用原因枚举：Unknown/Manually/NoModInfo/DependencyError/Duplicated/InvalidPackageName |
| ModSettingsManager.cs | 454 | ModSettings.xml 存取；Combined*Settings 三表合并(:42-84)；LoadModSettings 灌键位/手柄/相机(:86-164)；数据驱动 Get/TryGet/Set→OnModSettingChanged 精准分发(:232-324)；RegisterAllDataDriven(:332)；s_loaded 竞态门闩(:39-40,:169) |
| ModSettingsParser.cs | 165 | Settings JSON→描述符：Page/Item/Separator/Label 判定(:31-53)、ResolveType 简单名补 Game. 前缀(:93-102)、GetDefaultWidgetType 按值类型选 Widget(:23-29)、ResolveWidget 5 内置+全限定名自定义(:133-148) |
| ModSettingElement.cs | 31 | 四描述符类：ModSettingPage/ModSettingItem/ModSettingSeparator/ModSettingLabel；Item.CachedPath=包名/Id链(:22) |
| ModSettingItemWidgetFactory.cs | 41 | Widget 实例化→Supports 校验→回退默认→双双失败跳过+Log(:10-23) |
| ModSettingLocalizer.cs | 62 | 文案四档：整体[]token→id链默认键→Id 兜底→字面量(:12-36)；enum 成员键 ModSettings.包名.枚举名.成员名(:41-47) |
| LanguageControl.cs | 473 | loadJson 深合并(:180-238)、Get 回退英文表(:266-282)、TryGetBlock 支持 Name:data 回退 Name:0(:350-361)、ChangeLanguage 全屏重建+CraftingRecipesManager.Initialize 重跑(:371-406)、GetEnumDisplayName 统一键 Enums.枚举名.成员名(:340) |
| JsInterface.cs | 616 | Jint AllowClr+DebugMode(:33-38)、app:init.js 外置优先(:41-48)、handlers 数组约定(keyDown/keyUp/frame/:70-102)、HTTP 远程控制 DEBUG 28256 全卡/RELEASE 回环随机口(:228-240)、iOS 分支 JSContext(:347-616) |
| JsModLoader.cs | 186 | JS 钩子桥：C# 分支桥 8 钩子(OnMinerDig/OnMinerPlace/OnPlayerSpawned/OnPlayerDead/ProcessAttackment/CalculateCreatureInjuryAmount/OnProjectLoaded/OnProjectDisposed)(:9-94) |
| JsonModelReader.cs | 344 | **Load 抛"JsonModel功能暂时下线"**(:98)，正文全为注释遗留实现；JsonModel 类带 FirstPerson/InHand 偏移字段(:335-344) |
| ObjModelReader.cs | 234 | .obj→Model：mtllib 经 ContentManager(:102)、usemtl 定贴图(:129)、f 面强制三角(:141-143)、法线→CellFace 决定绕序(:157-158)、AppendMesh 逐 Mesh 建骨(:169-215) |
| MtllibStruct.cs | 30 | .mtl 解析：newmtl+map_Kd→材质名→贴图路径表 |
| OnlineJsonReader.cs | 22 | 静态 HttpClient，GetJsonFromUrlAsync(url)→JsonDocument |
| APIUpdateManager.cs | 248 | AtomGit release 查最新 API 版本(:94-102)、版本比较=点分 uint(:68-86)、DTO 字段名反序列化敏感三连警告(:126-248) |
| CommunityServerManager.cs | 208 | 社区服务器注册表：DefaultOriginal(scresdir.appspot.com)/DefaultChinese(api.survivalcraft.cn)、CurrentApiBaseUrl 归一化唯一读取口(:126-145)、切服清缓存+AuthSessionManager.OnServerSwitched(:179-189) |
| FileAssociationManager.cs | 143 | Windows 文件关联：.scworld/.scbtex/.scskin/.scfpack/.scmod 五扩展 ProgId 注册表写入/校验/注销(:31-138) |
| StandardCreatureSpawnRule.cs | 111 | CreatureType 封装：构造签名 (SubsystemCreatureSpawn, ValuesDictionary) 即注册协议(:34)；条件=温度/湿度/AboveTopBlock/海岸距离/脚下方块类型(:61-107)；Blocks 分号分隔按短类名解析(:51-56) |

## Community 根（E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\Community\，7 文件）

| 文件 | 行数 | 职责与实读要点 |
|---|---|---|
| CommunityFramePump.cs | 31 | Window.Frame 全局帧泵：驱动 Auth/Download 轮询；LoadingScreen 期不泵；逐轮询自兜异常(:26-30) |
| CommunityToastManager.cs | 64 | 全局 Toast 单例 widget 挂当前屏，切屏自动摘挂(:12-38) |
| IRemoteImportHost.cs | 8 | 远程导入宿接口：HasExactLocalContent/IsModpackDataFilePresent/ImportModpackDataFileSafe |
| RemoteImportManager.cs | 799 | 链接导入三路：单资源(ExternalContentManager 决策树)、直链 zip 落 ModpackRegistry、清单整合包(RemoteModpackInstaller)；requestId 防陈旧(:127-203/:569-599) |
| RemoteImportManager.Request.cs | 43 | URL 校验+先解码再取文件名防 %2E%2E 路径穿越(:18-29)、类型按扩展名识别 Unknown 留待响应头定型 |
| TransactionalFileReplacement.cs | 311 | 备份-替换-回滚事务：备份名 <原名>.-backup-<32hex>(:7)；启动 RecoverLeftoverBackups 扫描回滚(:12-49)；Replace 先移旧后落新 finally 回滚(:155-189)；OverwriteWithRollback 覆盖导入(:214-246) |
| PlayedTimeTracker.cs | 453 | 游玩时长：按自动保存(300s)结算、间隔封顶 2×周期(:17)、键=包名\n版本\n文件名(:164-169)、待上报队列落盘+整批成功才出队(:355-409)、读取失败跳过保存防空台账覆盖(:33-34,:232-238) |

## Community\Authentication\（2 文件）

| 文件 | 行数 | 职责与实读要点 |
|---|---|---|
| AuthSessionManager.cs | 421 | 进程单例：per-URL 会话表(:42)、登录/登出任务轮询 Update(:219-309)、401/403 去重派发按 token 定位归属服(:377-419)、弱事件源 LoginStateChanged(:53-58)、对话框存活判据=在 Dialogs 且父链可达 RootWidget(:359-371) |
| AuthenticationSessionStore.cs | 27 | 凭据文件读写门面，实际落盘在 CommunityCredentialStore(sha256 命名 v4) |

## Community\Community\（10 文件）

| 文件 | 行数 | 职责与实读要点 |
|---|---|---|
| CommunityManager.cs | 14 | 静态门面：ApiClient/ModCatalog 两个单例接线 |
| CommunityManager.Browse.cs | 228 | /post/list 查询、用户帖、下载趋势（两种历史响应体按顶层 code 属性区分 :52-72） |
| CommunityManager.Catalog.cs | 60 | /version/list 目录查询 + CommunityModVersionSelector.FindBestMatch |
| CommunityManager.Details.cs | 43 | 帖子详情+趋势并行 Task.WhenAll |
| CommunityManager.Featured.cs | 64 | 精选两路并行、单侧失败降级空列表、双侧失败重抛(:8-30) |
| CommunityManager.Score.cs | 44 | /post/score 评分提交：空响应/业务码非 0/200 抛异常(:24-31) |
| CommunityManager.Uploads.cs | 35 | /upload/list 未发布资源查询(publishState=2) |
| PostQueryBuilder.cs | 26 | /post/list 查询串拼装（搜索时 ignoreOrder/ignoreFileType 语义） |
| ReviewSubmissionHandler.cs | 252 | 评分提交管线：busy/未登录守卫、TaskSlot 单飞、postId 缓存命中跳过解析(:195-243)、结果落地写 LocalModReviews |
| VersionCatalogCache.cs | 169 | 版本目录不可变快照缓存（BaseUrl 绑定防跨服复用 :146-149）、api 版本匹配负缓存(:33-39) |

## Community\Downloads\（5 文件）

| 文件 | 行数 | 职责与实读要点 |
|---|---|---|
| DownloadFlowManager.cs | 272 | 下载管线控制器单例：StartDownload 前置覆盖确认/同包名自动禁用旧版(挡 survivalcraft/fastdebug :155)、EnqueueFileDownload |
| DownloadFlowManager.Update.cs | 200 | 每帧收尾：文件下载任务/清单任务/子项任务三段完成处理，Faulted 降级为失败结果不冒泡 |
| DownloadFlowManager.QueueDialog.cs | 895 | 队列执行 ExecuteQueuedDownloadAsync(:806-890)：CT 取消 vs 超时 OCE 区分(:825-835)、FileAlreadyExistsException 类型化带路径(:873-876)、导入成功即时落盘标记(:50-57)、失联覆盖框每帧重挂(:231-261) |
| DownloadFlowManager.ModpackDownload.cs | 290 | 整合包下载编排：BuildModpackConfirmBody 三态子项清单(:115-148)、取消=清单照落盘(2026-09-24 用户裁定 :88-104)、GetPlatformName 稳定英文标识(:272-289) |
| CommunityDownloadSourceManager.cs | 157 | 下载线路注册表：DefaultCn(直连)+4 镜像+自建；名称即身份 Ordinal(:9-10) |

## Community\LocalResources\（14 文件）

| 文件 | 行数 | 职责与实读要点 |
|---|---|---|
| LocalResourceIdentity.cs | 45 | 评价 key（包名优先→文件路径→类型:名）、world key、自动更新扫描签名 |
| LocalReviewModels.cs | 43 | 发布检查/评分请求结果 DTO |
| LocalModReviewCache.cs | 30 | 评价字典 IO 包装 |
| LocalModReviewState.cs | 94 | postId 多键关联（key/显示名/文件名/无扩展名 :52-70） |
| LocalModStateStore.cs | 105 | 三屏共用状态门面；待重启计数跨线程必须 Dispatcher 封送(:41-55)；下载前兼容覆盖缓存(:57-79) |
| LocalModPendingActionStore.cs | 65 | 重启后再执行动作落盘；ClearPendingActions 只清启用/禁用保留删除(:49-64) |
| LocalModInstallStatus.cs | 197 | FindExactLocalDownloadFilePath 按类型查本地(:30-41)、GetCommunityLocalModSnapshot 主线程封送投影(:65-97)、安装/更新判定 NuGetVersion 语义(:99-196) |
| LocalModUpdateModels.cs | 129 | 更新检查 DTO；LocalModUpdateCheckResult setter 自动解析 NuGetVersion(:101-119) |
| LocalModPostResolver.cs | 140 | 文件名/包名→postId：包名命中后限流 3 并发解析文件名(:57-87)、/post/file/published 端点(:93-139) |
| LocalResourceCollection.cs | 300 | 扫描四类资源(家具/贴图/皮肤/模组)、ModEntity→LocalResourceItem 投影(兼容判定 ApiVersion 1.4-1.7 前缀直接判不兼容 :102-114)、依赖可用性快照(Loaded/Disabled/PendingRestart/Incompatible 四集合 :203-231) |
| LocalModNetworkManager.cs | 623 | 四类网络任务(单检查/批量扫描/版本列表/依赖查询)TaskSlot 单飞调度(:58-112)；批量扫描有界并发 4(:115-187)；Cancel 只 Cancel 不 Dispose CTS(:581-591) |
| LocalModNetworkManager.Dependencies.cs | 94 | 缺失依赖按包名并发查询限流 4，单项失败按缺失处理不拖垮整批(:23-78) |
| LocalModNetworkManager.UpdateCheck.cs | 75 | 社区源更新检查：postId→详情→兼容谓词选最新；不兼容时记 NoUpdateReason(:35-45) |
| LocalModNetworkManager.Versions.cs | 142 | 已发布版本列表装载+元数据回填(PostId/Type 继承 :85-108) |

## Community\Modpacks\（3 文件）

| 文件 | 行数 | 职责与实读要点 |
|---|---|---|
| ModpackManager.cs | 331 | 整合包激活/停用无 UI 决策器：激活=备份当前模组状态+按 BuildEnableChanges 批量 setDisabledState(:178-211)；停用=恢复备份文件+反写禁用状态(:213-249)；EvaluateEnable 七态判定(:306-328) |
| ModpackManifestLoadManager.cs | 164 | 本地清单缓存：同步回退/后台延迟装载双路、丢弃任务 Observe 防未观察异常(:142-163) |
| ModpackFileInfoManager.cs | 100 | fileId→PostFileItem 缓存 512 LRU、限流 6 并发(:14-40) |

## Community\Settings\（1 文件）

| 文件 | 行数 | 职责与实读要点 |
|---|---|---|
| CommunityModSettingsState.cs | 133 | 屏筛选状态(文件类型/排序/节)持久化 state.json；惰性门闩 EnsureLoaded(:80-95)；重启直达目标已改走 Settings.xml 不入此文件(:8-9) |

## Community\Transfers\（6 文件）

| 文件 | 行数 | 职责与实读要点 |
|---|---|---|
| TransferManager.cs | 34 | 传输静态域：下载器/上传提供者/队列持久化/反馈客户端/来源解析器；字段声明顺序即初始化顺序勿反转(:5-6) |
| DownloadQueueManager.cs | 272 | 队列状态机：Pending/Running/Pausing/Paused/AwaitingOverwriteConfirmation/Completed/Failed/Canceled；URL+文件名未完成项去重(:49-55)；旧格式明文 Token 检测即重写(:200-207)；读方法无锁依赖"变更全在主线程"约定(:82-85) |
| ModpackDownloader.cs | 234 | 子项批预取(4)串行导入：批大小=内存峰值设计(Android 约束 :3-5)；被取代请求 Interrupted 标记(:48-53)；撞本地同名跳过不计成败(:187-196) |
| RemoteModpackInstaller.cs | 227 | 清单整合包预检(冲突谈判 Skip/Overwrite/SkipAll/OverwriteAll :46-112)+导入两阶段；await 点后复查 isCurrentRequest(:177-182)；首因原则只留首个 LastError(:131/:144) |
| ModpackConflictManager.cs | 51 | 后台线程→主线程冲突对话框桥：TaskCompletionSource+TryMarkRequestDisplayed 防重复弹 |
| IDownloadFeedbackReporter.cs | 4 | 下载反馈上报接口 |
