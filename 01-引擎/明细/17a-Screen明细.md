# Screen 明细（71 文件全量一行表）

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(71/71，全文实读)
>
> 父页: 17-Screen屏幕族.md。每行 = 一个 .cs 文件。路径前缀统一为 `E:\SurvivalcraftAPIProject\Survivalcraft\Screen\`（表中只写相对路径）；行号以 2026-10-31 源码为准。

## 一、根目录（47）

### 基础设施（4）

| 文件(行) | 级 | 职责/关键行号 | 备注 |
|---|---|---|---|
| 〔深〕Screen.cs(6) | Screen:CanvasWidget | 全族基类：仅虚 `Enter(object[])`:3 / `Leave()`:5；Update/Draw/Input 全部继承自 Widget | 契约极薄，屏=一个全屏 Widget |
| 〔深〕ScreenLayout.cs(13) | enum | 分屏布局 10 值：Single/Double*3/Triple*4/Quadruple*2 | 供 PlayersScreen 选单 |
| 〔深〕ScreenshotSize.cs(6) | enum | 截图尺寸：ScreenSize/FullHD/Custom | 设置 UI 屏消费 |
| 〔深〕IWorldOptionsScreen.cs(5) | interface | 空标记接口；注释明示"模组调整世界设置的界面需要继承" | WorldOptionsScreen 实现；New/ModifyWorld 借它免重置设置 |

### 启动加载与游戏内（4）

| 文件(行) | 级 | 职责/关键行号 | 备注 |
|---|---|---|---|
| 〔深〕LoadingScreen.cs(757) | Screen | 启动总控：静态 DisplayLog 日志列表(:42-65)；`InitActions`:158-607 全队列(内容→mod 程序集→语言→字体→数据库→方块→各 Manager→注册屏→末步切 MainMenu/Play/重启直达:593-606)；`InitScreens`:609-650 注册 40 屏；`Enter`:673-687 清空其余屏(总复位点)；`Update`:689-729 每帧 100ms 预算泵+Back=退出确认(:690-693)；`Add(LogType)` 经 Dispatcher 回主线(:140-156) | 程序集加载失败→`SwitchScreen(new LoadingFailedScreen(...))`:309-321(未注册直切唯一例) |
| 〔深〕GameLoadingScreen.cs(110) | Screen | 进世界状态机：WaitingForFadeIn/Upgrading(Task.Run RepairAndUpgradeWorld:42-52)/Loading(LoadProject+SwitchScreen("Game"):64-73)/RestoringSnapshot(:74-83)；Update 异常→PreviousScreen+ViewGameLogDialog(:86-96)；Enter 收 (WorldInfo,snapshot):98-109；顺带清原版社区列表缓存(:103-108) | Upgrading 在后台线程，完成标志轮询回主线 |
| 〔深〕LoadingFailedScreen.cs(49) | Screen | 纯代码构建错误屏(无 XML)：标题红+异常明细+解决方案+SafeMode 按钮(:9-41)；点击 SafeMode→SettingsManager.SafeMode=true+提示重启(:43-48) | 构造器带参，实例即用即弃 |
| 〔深〕GameScreen.cs(69) | Screen | 游戏内屏：ctor 挂 Window.Deactivated→SaveProject、Closed→DisposeProject(:13-14)；Enter 解除音频 Mute(:17-23)；Leave=Mute+`SaveProject(true,true)`(:25-32)；Update=300s 自动存档(:37-41)+试玩 19min 踢出(:42-47)+`UpdateProject` 驱动 tick(:48)+光标显隐(:50-55)；Draw 高分辨率非动画期清屏(:58-63) | 全游戏唯一常驻世界屏 |

### 主菜单与世界流（5）

| 文件(行) | 级 | 职责/关键行号 | 备注 |
|---|---|---|---|
| 〔深〕MainMenuScreen.cs(180) | Screen | 主菜单：Enter=Mix.Menu+Motd 重启+隔离存储迁移(:55-74)+`OnMainMenuScreenCreated` 钩子(:46-52)+刘海留白(:68-69)；Update=版本串/Buy 可见/Logo 呼吸动画/更新检查图标旋转(:99-116)/四主按钮切屏(:128-139)/Back 退出策略(:168-175) | SafeMode 提示、禁用 mod 弹窗都在 Enter 一次性 |
| 〔深〕PlayScreen.cs(356) | Screen | 世界列表：Enter=BusyDialog+Task.Run 刷列表+Dispatcher 回填(:82-118)，支持参数[0]=目录名直达进世界(:102-113)；`WorldInfoWidget`:27-58 带 `LoadWorldInfoWidget` 钩子(:50-56)；`Play`:178-275 读世界 UsedMods 比对 mod 缺失/版本不符弹确认；`GameLoad`:277-289=`BeforeGameLoading` 钩子(可换目标)→GameLoading；`ShowTips`:291-327 mod 公告 | MaxWorlds=300 上限(:14) |
| 〔深〕NewWorldScreen.cs(122) | Screen | 新建世界：Enter 仅当来路非 IWorldOptionsScreen 才重置 WorldSettings(:49-56)；种子弹 EditWorldSeedDialog/模式弹 SelectGameModeDialog(:59-90)；Play→ValidateWorldName→CreateWorld→GameLoading(:108-115)；WorldOptions 传 (settings,false)(:106) | 非创造模式 ResetOptionsForNonCreativeMode(:110-112) |
| 〔深〕ModifyWorldScreen.cs(195) | Screen | 改世界：Enter 收 (目录名,WorldSettings) 并快照原值(:57-67)；Apply 按钮=值有变才可用，落盘 ChangeWorld(:141-150)；Delete 支持"必须输 yes"硬确认(TextBoxDialog,:94-114)；返回时有未存变更弹确认(:156-171)；`CompareValueDictionaries`:177-194 | Cruel 世界禁改模式(:65) |
| 〔深〕WorldOptionsScreen.cs(590) | Screen,IWorldOptionsScreen | 世界选项大杂烩：地形模式/岛尺寸/平地参数/海平线/温度湿度/群系尺寸/生成器版本(:427-438)/材质包/调色板/超自然生物/友伤/昼夜/四季年日(:491-502)/天气/冒险重生；面板可见性按模式与是否现存世界逐帧刷(:517-526)；生成器版本按钮被挂 `TerrainContentsGenerator24Initialize` 钩子的 mod 锁死(:233-237) | 滑块值↔预设数组 FindNearestIndex:581-589 |

### 玩家管理（2）

| 文件(行) | 级 | 职责/关键行号 | 备注 |
|---|---|---|---|
| 〔深〕PlayersScreen.cs(166) | Screen | 玩家列表(世界内)：Enter 收 SubsystemPlayers 并订阅 PlayerAdded/Removed(:22-27)，Leave 退订+清缓存(:29-35)；加人走 PlayerScreen(Add 模式)(:77)；分屏布局按人数给可选 ScreenLayout(:80-148)；Back 固定回 "Game"(:149-153) | Cruel/Adventure 禁加人(:40-63) |
| 〔深〕PlayerScreen.cs(292) | Screen | 单玩家编辑：Mode.Initial/Add/Edit 三态按钮布局(:87-116)；职业切换换肤+重命名(:145-151)；皮肤/输入设备 ListSelectionDialog(:152-202)，输入设备占用互斥清除(:193-198)；AddAnother 手动 Leave+Enter 复用实例(:230-236)；Back 按 Mode 分流(Initial=存档退世界回主菜单:239-243) | `VerifyName`:273-291 弹错不通过 |

### 设置（8）

| 文件(行) | 级 | 职责/关键行号 | 备注 |
|---|---|---|---|
| 〔深〕SettingsScreen.cs(116) | Screen | 设置枢纽：ctor 跑 `OnSettingsScreenCreated` 钩子收 mod 按钮(:32-43)；`AddSettingButton(button/text,action)`:86-115 奇偶分列到左右 StackPanel；Update 路由 7 个子设置屏(:47-67)+GoBack(:73-77) | m_previousScreen 字段已 [Obsolete](:6-7) |
| 〔深〕SettingsPerformanceScreen.cs(229) | Screen | 性能：分辨率模式/可视距离(26 档:8-35,警告文案 7 档:147-177)/地形 mipmap/天空渲染/阴影/帧率(PresentationInterval 2/1/0:6)/FPS 显示/低帧减速(LowFPSToTimeDeceleration:133-135)/动画纹理刷新上限；Back 时若调大可视距离且>128 弹提醒(:204-227) | 记 Enter 时可视距离比对(:96-98) |
| 〔深〕SettingsGraphicsScreen.cs(68) | Screen | 画质：亮度/视角滑块双向同步(:31-39)；VR 开关 StartVr/StopVr(:40-53) | VR 面板仅 WINDOWS |
| 〔深〕SettingsUiScreen.cs(208) | Screen | 界面：窗口模式/语言/字体入口(:112-114)/UI 缩放(SlidingCompleted 才写:103-105)/VR GUI/倒置布局/刘海适应(联动 TopBar 边距:135-143)/截图 UI/截图尺寸+自定义宽高比(:156-173)/删世界需输 yes/原版社区模式 | Enter 按平台显隐窗口/刘海容器(:90-93) |
| 〔深〕SettingsCompatibilityScreen.cs(142) | Screen | 兼容：查看/打开/分享 GameLog(:58-96,分享走 Task.Run+Dispatcher:86-95)/报告链接/Windows 文件关联(:101-112)/类替换管理入口(:113-115)/安全模式开关+警告(:116-124)/32 位索引(:125-128) | MultithreadedTerrainUpdate 已废只剩恢复默认钮(:129-135) |
| 〔深〕SettingsAudioScreen.cs(34) | Screen | 音量双滑块(IsSliding 写/否则回读同步:17-27)+Back 回 PreviousScreen | 全族最小样板 |
| 〔深〕SettingsControlsScreen.cs(215) | Screen | 操控：移动/视角模式枚举切换(:80-87)/左右手/翻转Y/自动跳/创造飞行等布尔(:88-108)/灵敏度×2+手柄×3+创造挖时/触及/长按/拖距/虚拟键边距滑块(:109-143)/四个映射子屏入口(:145-156)/VR 面板可见性(:171-208) | Back 固定回 "Settings"(:212) |
| 〔深〕SettingsFontScreen.cs(384) | Screen | 字体 8 槽位(FontSlot 枚举:7-23)：Enter 预热样式面探测(:67-75)；联动禁用/锁定(:168-179,270-281)；导入在 Task.Run 校验+Dispatcher 回主(:293-342)；应用=存档→RebuildChains→全屏重建(:227-285)；RebuildScreens=preserve GameScreen 的 RebuildAllScreens(:378-382) | BROWSER 借点击手势扫系统字体(:243-260)；Enter 扫描曾在重建后成环(注释:70-72) |

### 输入映射与摄像机（4）

| 文件(行) | 级 | 职责/关键行号 | 备注 |
|---|---|---|---|
| 〔深〕KeyboardMappingScreen.cs(167) | Screen | 键盘改键：列表 ItemFactory 补 Name 属性后 LoadWidget(:8-22)；等待按键态扫全部 Key/MouseButton(:95-117)；冲突标红(KeyCompatibleGroupsManager.HasConflict:70-73)；Enter 清单+按 `ModSettingsManager.CombinedKeyboardMappingSettings` 填充(:133-140)；游戏内来路才显 Help 钮(:134) | 等待态吞 Back(:95-101) |
| 〔深〕GamepadMappingScreen.cs(216) | Screen | 手柄改键：**复用 KeyboardMappingScreen 的 XML**(:59)；组合键=肩键/扳机按住+动作键合成 ValuesDictionary(:129-158)；其余同键盘屏 | fName 指向 KeyboardMappingScreen 名(:46)以复用翻译键 |
| 〔深〕VrControllerMappingScreen.cs(262) | Screen | VR 改键：15 动作+2 兼容组(:20-30)；左右手柄轮询 SetVrMapping(:141-167)；冲突按 (手柄,键) 聚合(:194-214) | 列表项带 VrMappingItem 包装区分表头(:252-260) |
| 〔深〕CameraManageScreen.cs(149) | Screen | 摄像机启用/排序：值=顺序序号，-1=禁用(:70)；禁用保底留 2 台(:56-59)；上移/下移=相邻序号互换+列表重选(:78-103)；RefreshList 重排序号防空洞(:135-148) | 数据源 ModSettingsManager.CombinedCameraManageSettings(可被 mod 扩) |

### 图鉴与帮助（7）

| 文件(行) | 级 | 职责/关键行号 | 备注 |
|---|---|---|---|
| 〔深〕RecipaediaScreen.cs(151) | Screen | 方块图鉴主页：分类翻页+按 DisplayOrder 填列表(:132-150)；点条目**整替注册表** `m_screens["RecipaediaDescription"]=block.GetBlockDescriptionScreen(value)`(:41,:116)与 Recipes(:122)——方块可自带屏子类；Enter 记来路且从子屏回来不覆盖(:73-78) | 虚方法 OnBlocksListItemClicked 可被 mod 重写(:31-36) |
| 〔深〕RecipaediaDescriptionScreen.cs(200) | Screen | 方块详情：左右翻 m_valuesList；`GetBlockProperties`:73-164 汇聚发光/燃料/堆叠/易燃/营养/腐坏/挖掘/爆炸/近战/穿戴等全部 Block 属性+`EditBlockDescriptionScreen` 钩子(:153-162)；静态 Default 属性(:30) | |
| 〔深〕RecipaediaRecipesScreen.cs(78) | Screen | 配方页：Enter 按 ResultValue 过滤 CraftingRecipesManager(:27-33)；热/熔炼两种控件切换(:39-50)；`EditRecipeScreenWidget` 钩子(:56-62)；静态 Default(:16) | |
| 〔深〕BestiaryScreen.cs(216) | Screen | 生物图鉴：ctor 全量扫 EntitiesValuesDictionaries 组装 BestiaryCreatureInfo(蛋序排序:45-147)；`SetupBestiaryModelWidget`:165-198 模型取景盒自适应(供详情屏复用)；`LoadCreatureInfoInBestiaryScreen` 钩子(:35-41) | 女性实体攻击/防×0.8 速×1.03(:133-139) |
| 〔深〕BestiaryDescriptionScreen.cs(164) | Screen | 生物详情：属性双列+掉落面板重清重建(:114-150，从 ComponentLoot 解析)；`UpdateCreaturePropertiesInBestiaryDescriptionScreen` 钩子(:151-161) | |
| 〔深〕HelpScreen.cs(132) | Screen | 帮助主页：条目从 `LanguageControl.jsonNode["Help"]` 解析(DisabledPlatforms 过滤:48-57,索引排序:84-85)；ShowTopic 分流键盘/手柄直接切映射屏(:121-131)；ListPanel ItemWidgetFactory 模板(:36-42) | m_previousScreen 逻辑全注释(:88-96) |
| 〔深〕HelpTopicScreen.cs(33) | Screen | 帮助正文：Enter 收 HelpTopic 填题/文+滚动复位(:19-24)；Back 回 PreviousScreen(:26-32) | Enter 参数强转失败即崩——参数协议硬约束 |

### 内容管理（6）

| 文件(行) | 级 | 职责/关键行号 | 备注 |
|---|---|---|---|
| 〔深〕ContentScreen.cs(195) | Screen | 内容中心枢纽：外部导入(Storage.ChooseFile 异步+Dispatcher 弹果:69-141)/社区入口弹 SelectCommunityServerDialog(:142-143)/链接导入(RemoteImportManager:177-179)/三管理入口(:180-188)；admin 可见"用户管理"(:35-61) | Back 固定回 MainMenu(:189-193) |
| 〔深〕ExternalContentScreen.cs(343) | Screen | 外部内容浏览器(本地盘/登录网盘)：SetPath 归一(:213-229)；UpdateList 异步列举(:231-258)；DownloadEntry→`PrepareExternalContent` 冲突检测+覆盖/改名确认(:260-309)；ImportPrepared 后 RequiresRestart 弹重启确认(:311-340)；换提供者若带专属屏名直接跳屏(:115-134) | busy 弹窗必须每分支 Hide(:276-278 注释)，残留锁输入 |
| 〔深〕ManageContentScreen.cs(422) | Screen | 本机材质/皮肤/家具/字体管理：ItemFactory 按 ExternalContentType 五分支(:54-158)；UseCount=被世界/槽位引用数(:313-377)；删除确认文案按类型(:207-259)；Mod 项删除转跳 ModsManageContent(:220-222) | Leave 清双缓存(:185-188) |
| 〔深〕ModsManageContentScreen.cs(405) | partial | 模组管理：Enter 订阅 ModListRescanned+`RescanModsAsync`(:133-140)；Leave 取消在途网络+作废 TaskSlot(:142-151)；启停=DisabledMods 增删+需重启标记(:230-260)；上移/下移维护 LoadAfter 链且依赖者禁越过(:351-393)；返回时需重启弹三选(重启/稍后)(:186-220)；状态标签优先级 FileDeleted>PendingRestart>Disabled>Update(:263-306) | ModEntity 重写 Equals→列表定位必须 ReferenceEquals(:352) |
| 〔深〕ModsManageContentScreen.Community.cs(859) | partial | 模组管理社区侧：静态门闩 s_autoUpdateScanLaunched 发起时置位失败不重扫(:83-84)；EntityReferenceComparer 引用比较器(:21-24，ModEntity 重写 Equals 的一一映射前提)；六动作入口 CheckModUpdate:186/OpenModVersions:222/LookupModDependencies:239/LookupSingleModDependency:266/OpenModReview:307/HasMissingDependencies:228(静态)；TryGuardLocalModNetworkStart:314 同任务在跑弹「请稍候」；EnsurePublishedPostThen:648 放行门(reviewKey 命中 PostId>0 直回调:651)；评分统一提交入口 StartLocalScore:829；GetChinesePublishPostUrl:291 截 WebsiteUrl authority 重拼 `/#/publish/post` | 结果落地三缓存 LocalModStateStore:145-156+陈旧 key 清理:159；发布检查 TaskSlot onFaulted 记日志不冒泡 Update:733-741 |
| 〔深〕ModpacksManageContentScreen.cs(939) | CommunityScreenBase | 整合包管理屏：静态共享 s_iconLoader:15/s_fileInfoManager:26（屏随换语言重建，缓存不丢）；选中代次计数 m_selectionVersion 防陈旧回写(:38-39)；启用链四段 ModpackDecision 门：忙:306/他包激活:310/文件信息在途:324/无管理 mod:328→缺嵌入列表框:350→缺下载确认:367→ImportEmbeddedItemsAndEnable:510(customFileBackupPreparer=ModpackDataFiles.PrepareForActivation:523，失败 TryRestoreBackups:535)；停用链三失败分支:597-611；TryDeleteModpack:651 激活中禁删+返回 true=点击已处理；补装 mod 默认禁用:729；GetModpackItemDisplayName:710 文件名→fileId→目录→路径→包名 | Leave 顺序不可换 DisposeRetired 在 ClearItems 后(:80-85)+ClearPending 兜底；Dispose 确定性退订静态事件(:89-95)；下载完成回调查缓存未命中同步重读防空列表误清选中:195；RestartConfirmDialog 回调内不得再调 Window.Restart:631 |

### 杂项单屏（6）

| 文件(行) | 级 | 职责/关键行号 | 备注 |
|---|---|---|---|
| 〔深〕NagScreen.cs(33) | Screen | 试玩推销：Enter 设 `Keyboard.BackButtonQuitsApp=true`(:12-17) Leave 复位(:19-21)；Buy→商店；Quit/Back→Window.Close(:28-31) | |
| 〔深〕TrialEndedScreen.cs(34) | Screen | 试玩结束：Buy/Quit/NewWorld 三钮(:19-33)；由 GameScreen 试玩超时切入 | 控件可能缺→全可空判(:14-16) |
| 〔深〕ModSettingsScreen.cs(264) | Screen | 模组设置(声明式)：root 聚合各 mod 顶层 Page(:75-126)；页内 Item 经 ModSettingItemWidgetFactory 造控件(:185-201)，ValueChanged→ModSettingsManager.Set；`ModSettingsManager.SettingChanged` 订阅回写控件(:34-57)；内部页面栈 Back 逐级 Pop(:233-262) | 单实例复用：同屏重入禁令的官方绕法(注释:6-8) |
| 〔深〕ReleasesScreen.cs(204) | Screen | 发布版浏览(Atomgit)：Enter 存 URL+BusyDialog+Task 拉 JSON(:57-77)；版本列表+Markdown 正文+资产下载钮(:114-174)；MarkdownWidget.LinkClicked 过滤 # 锚点(:38-42) | |
| 〔深〕ManageClassSubstitutesScreen.cs(151) | Screen | 类替换管理：内嵌 SubstitutesGroupWidget/SubstituteWidget 双层 StackPanel(:7-118)；Back 时把变更 guid 写回 DatabaseNode 并 `LoadDataBaseFromXml`(:134-150) | 选中态存 ModsManager.SelectedClassSubstitutes |
| 〔深〕ManageUserScreen.cs(386) | — | **整文件被注释，标记 //abandoned**(:1-386 全在 /* */) | 死文件；中文管理后台用户管理遗留 |

## 二、Community/（19）

### 屏与屏基类（8）

| 文件(行) | 级 | 职责/关键行号 | 备注 |
|---|---|---|---|
| 〔深〕CommunityScreenBase.cs(90) | Screen,IRemoteImportHost | 四社区屏公共基类：ctor 订阅 AuthSessionManager.LoginStateChanged→**Dispose 确定性退订**(换语言重建不调 Leave,:16-25)；InstallDownloadFlowCallbacks/AcquireRemoteImportHost/Release 三段 Enter-Leave 配对(:53-89) | "单槽委托只在自己仍持有时清空"纪律(:5-8 注释) |
| 〔深〕CommunityScreen.cs(267) | CommunityScreenBase(partial) | 社区浏览主屏：Enter 先搭骨架让 2 帧再拉数据(:130-134)；分页/筛选/排序/搜索(0.4s 防抖:108-128)经 PostTreePresenter；四 TaskSlot(列表/详情/弹窗/精选:52-55)；Dispose→presenter.Detach(:261-266) | ctor 注册 RemoteImportManager 宿主(:118) |
| 〔深〕Community.Auth.cs(51) | partial | CommunityScreen 筛选默认值存取(CommunityModSettingsState) | |
| 〔深〕Community.Featured.cs(81) | partial | 精选/新动态版块：LoadFeaturedAsync+渲染空/错/数据三态(:6-80)，服务端 null PostItem 防线(:70-72) | |
| 〔深〕Community.Posts.cs(308) | partial | 帖子列表主逻辑：LoadCommunityPosts 组请求(含版本目录缓存:26-34)；下载/详情钮四态签名省赋值(:91-115)；详情弹窗两路(帖子/版本:139-264)；FindMatchingPostVersion(:284-307) | |
| 〔深〕Community.Ui.cs(167) | partial | 交互：筛选/排序对话框、GetEffectiveSection(搜索词强制回列表:61-65)、分页按钮 busy 语义修正注释(:148-152)、登录态刷新(:159-166) | |
| 〔深〕CommunitySettingsScreen.cs(200) | CommunityScreenBase | "More"设置屏：登录/我的发布/导入/下载队列/当前服务器(仅选不导航:85-89)/下载源模式/默认线路/翻译开关；静态 s_current+s_sharedStatus 跨实例状态(:5-6,113-121)；Leave 单槽定向释放(:53-62) | 动态文案钮逐帧守卫刷新(:130-144) |
| 〔深〕CommunityMyPublishedScreen.cs(372) | CommunityScreenBase | 我的发布(终端屏)：未登录 Enter 即弹登录，取消=GoBack(:84-88,100-116)；"只看未发布"走 /upload/list 平铺(:237-271)；类型切换/翻页必回第 1 页(:308-315)；分享链复制(:357-364) | Page/开关跨 Enter 残留→Enter 显式重置(:71-77) |

### 共享工具（11）

| 文件(行) | 级 | 职责/关键行号 | 备注 |
|---|---|---|---|
| 〔深〕PostTreePresenter.cs(757) | —(Shared/) | 单棵帖子树 presenter：LazyTag 占位(:30)点击展开拉详情(:112)；LoadPostDetail:128 TryStart 防重；ApplyPostDetailResult:149 成功回填版本子树、空落"无资源"终态:182、失败重挂懒加载占位可重试:190；ApplyPostsResult:207 目录按来源服务器绑定:211+ref-snapshot 整表共享一次本地快照:222；节点工厂 CreatePostNode:379/CreateVersionNode:436/CreateFileNode:498/CreateUploadFileNode:524；分页状态机 HandlePaginationClicks:333 跳页钳 1..TotalPages；服务端脏数据防线：null version 返回 null:437、null file 跳过:483、数组全 null 落占位:411 | 分页协议坑：/user/posts total=页数 count=条数、/post/list 无 count(:234)；total 谎报弃用回退已加载口径 ResolveListTotals:743；ClearChildren(false) 不 Dispose 共享纹理:159；Detach:61 幂等退订防静态事件钉死 |
| 〔深〕PostIconLoader.cs(311) | static | 帖子图标进程级加载：EvictableTextureCache(128)+在途去重 s_iconRequests(:14-15)+IconUpdated/IconCleared 广播(:22,24)；反射写 TreeViewNode.m_subtexture(:17-21)；ApplyPostNodeIcon:30 先贴类型图标:246 再异步远程；GetPostIconUrl:75 只认服务器图标，不为缺图下载整包 .scmod(:76-77)；LoadNodeIconAsync:151 下载→512KB 上限:166→Task.Run 解码:178→Dispatcher 回主线；覆写先 IconCleared 摘旧引用再 IconUpdated:197-202、容量驱逐逐 key 广播:203 | 全树匹配按 Tag 重算 URL，事件低频不做节点级备忘(:104)；CropSubtextureToSquare:291 居中正方形 UV 裁剪(图集 UV 约定注释:285-290)；DisposeRetired:26 由列表 Clear 调 |
| 〔深〕EvictableTextureCache.cs(50) | — | 容量上限纹理缓存：被驱逐/覆写不立即 Dispose，入退休队列待 DisposeRetired(:24-49) | 防可见节点引用悬空 |
| 〔深〕ModpackIconLoader.cs(173) | — | 整合包图标加载：EvictableTextureCache(64)(:19)+缺失集合 m_missing:20+在途任务表 m_tasks:21；TryStartEmbedded:39 内嵌字节解码；TryStartRemote:50 远程下载 2MB 上限(:66)；TryTakeCompleted:74 每帧只取一个完成 key，失败/解码异常落 missing，Texture2D.Load 在游戏线程执行:100 | ClearPending:116 未完成任务挂 ContinueWith Dispose 防 Image 滞留进程退出；Decode 复用本体 PostIconDecoder.Decode(:146-151)；MakeEmbeddedKey:132 `embedded:{包路径}\|{图标路径}` |
| 〔深〕ModpackIconManager.cs(193) | — | 图标协调：m_waiters 等待名册(:12)；StartIconRequests:37 嵌入优先防同 widget 双 key 双注册(:33-36)；缓存命中即贴/missing 放行远程/注册 waiter(:62-73)；Update:105 TryTakeCompleted+ApplyReadyTexturesToWaiters:149 兜底扫描补同帧第二 key；ApplyReadyTexture:135 分离 widget 也先贴(Subtexture 纯字段赋值，滚回重挂即显示) | ResolveRemoteIconUrl:168 相对图标按 SourceUrl 解析、zip 包不给远程(:176)；MakeCacheKey:184 `路径\|图标\|最后写时间Ticks`；Clear:113 只清名册，loader 生命周期仍由屏驱动 |
| 〔深〕HtmlTextUtils.cs(128) | static | 帖子 HTML 纯函数：可见文本探测(:8-35)/纯文本列表行拆分(:39-58)/列表标记(type 属性+字母/罗马序号:62-127) | HtmlAgilityPack |
| 〔深〕PostDetailsHeaderBuilder.cs(164) | static | 详情弹窗 header 直产 widget(不经 HTML)：更新元信息(:22-55)/发布统计+30 天趋势+版本下载量(:58-134) | 不进自动翻译载荷(注释:6-8) |
| 〔深〕CommunityTimeFormatter.cs(26) | static | API 时间戳→本地文本唯一入口：解析固定 InvariantCulture+RoundtripKind 防波斯历劫持(:11-25) | 发送侧不用此类 |
| 〔深〕CommunityVersionDetailFormatter.cs(58) | static | 版本详情内容提取(Content/ExtensionData 五键回退:11-44)+标题/空值格式化 | |
| 〔深〕CommunityVersionCompatibilityFormatter.cs(88) | static | 版本兼容信息(ModCompatibility.Evaluate→文本/颜色:15-52)+当前版本判定(NuGet 解析，纯整数序号拒比:54-87) | 宁漏高亮不误命中(注释:60-63) |
| 〔深〕Models/CommunityLoadResults.cs(47) | — | 五个加载结果 DTO：Posts/PostDetail/PostDetailsDialog/Featured/UploadFiles(+RequestId) | TaskSlot 泛型载荷 |
| 〔深〕Models/ResourceSource.cs(7) | enum | 帖子来源：Local/Community/MyPublished | |

## 三、OriginalCommunity/（4）

| 文件(行) | 级 | 职责/关键行号 | 备注 |
|---|---|---|---|
| 〔深〕OriginalCommunityContentScreen.cs(380) | Screen | 原版(官方)社区浏览：排序 6 档(:6-13)/过滤(类型|用户|URL)/搜索即时 PopulateList(:91-94)；列表 120s 缓存(:229-267)；长按顶部 2s 强刷(留 Task.Delay(250).Wait() 阻塞:198-203)；下载/删除/评分经 Manager | 被 GameLoadingScreen.Enter 清缓存(GameLoadingScreen.cs:103-108) |
| 〔深〕OriginalCommunityContentManager.cs(481) | static | 原版社区服务：XML 协议 POST {original ApiUrl}，List:42(Action=list，Cursor/Type/Moderation/Search/SortOrder 等 9 参数，响应 NextCursor+条目属性:76)；Download:108 GET→SHA1 内容哈希:126,423→PrepareExternalContent publiclyVisible 零拷贝:134→覆盖确认 CommunityImportOverwriteDialog:144；Publish:207 试玩禁发:215+VerifyLinkContent:340 先试导入 __Temp 再删；Feedback:370 统一反馈(Action=feedback+Success/ImportFailure/DownloadFailure/Rating/Report/PlayTime)，m_feedbackCache TryAdd 防重复、重复延迟 1.5s 报错:385-391 | id↔地址映射随四类 Deleted 事件清:19-28、Window.Deactivated 落盘:29；用户取消导入不计 Success 也不计 ImportFailure:153；Load/Save:429,457 XML 缓存 OriginalCommunityContentCachePath |
| 〔深〕OriginalCommunityContentEntry.cs(16) | — | 条目 DTO：Type/Name/Url/Version/Size/RatingsAverage | |
| 〔深〕OriginalExternalContentType.cs(9) | enum | 原版社区类型：Unknown/Directory/World/BlocksTexture/CharacterSkin/FurniturePack | 与 ExternalContentType 平行的一套 |

## 四、根目录独立工具（1）

| 文件(行) | 级 | 职责/关键行号 | 备注 |
|---|---|---|---|
| 〔深〕ScreenSpaceFireRenderer.cs(130) | — | 屏幕空间火焰粒子池(预分配+池化复用:54-88)；3×3 火焰帧图集动画(:109-129)；Update/Draw 与屏解耦 | 虽在 Screen 目录但非 Screen，是 UI 特效渲染器 |

## 速记

- 屏幕命名=注册键：类名去 "Screen" 后缀即注册名（LoadingScreen.cs:609-650 一一对应），`ScreensManager.GetScreenName` 反查(ScreensManager.cs:345-351)。
- 全目录 71 文件 ≈1.49 万行；最大 ModpacksManageContentScreen.cs 939 行，无 >2000 行文件。
- 另见：17-Screen屏幕族.md（机制与范例）、01-程序入口与主循环.md（ScreensManager/帧序）、09-UI与Widget体系.md（控件层）、18-Dialog对话框族.md（对话框层）。
