# Screen 屏幕族

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(71/71：全文深读64 + 节选深读7，无 >2000 行文件)

## 一句话定位

71 个 Screen 怎么组织、注册、切换、活死——01 页管切换器(ScreensManager)，09 页管控件(Widget)，本页管屏幕层本身。

## 目录地图

| 符号(类/文件) | 绝对路径 | 职责 |
|---|---|---|
| `Screen` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\Screen.cs | 基类：`: CanvasWidget`，仅虚 `Enter(object[])`/`Leave()` |
| `ScreensManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\ScreensManager.cs | 注册表/栈/动画/绘制（切换细节另见 01 页） |
| `LoadingScreen` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\LoadingScreen.cs | 启动加载队列 + 全屏注册表 InitScreens(:609-650) |
| `GameScreen` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\GameScreen.cs | 游戏内屏：自动存档/驱动 tick/进退世界挂钩 |
| `GameLoadingScreen` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\GameLoadingScreen.cs | 进世界状态机(WaitingForFadeIn→Upgrading→Loading/RestoringSnapshot) |
| `PlayScreen` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\PlayScreen.cs | 世界列表 + mod 兼容检查 + `BeforeGameLoading` 钩子 |
| `SettingsScreen` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\SettingsScreen.cs | 设置枢纽：`OnSettingsScreenCreated` 钩子 + `AddSettingButton` |
| `ModSettingsScreen` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\ModSettingsScreen.cs | 模组设置递归页（内部页面栈规避同屏重入） |
| `CommunityScreenBase` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\Community\CommunityScreenBase.cs | 四社区屏公共基类：Dispose 确定性退订纪律 |
| `RecipaediaScreen` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\RecipaediaScreen.cs | 图鉴：运行时整替 m_screens 里的描述/配方屏 |
| `WorldOptionsScreen` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\WorldOptionsScreen.cs | 世界选项：实现 `IWorldOptionsScreen`（屏保留协议） |
| 明细(一行一文件) | [17a-Screen明细](明细/17a-Screen明细.md) | 71 文件全量表 |

## 家族概览（12 族 = 71 文件）

| 族 | 数 | 文件 |
|---|---|---|
| 基础设施 | 4 | Screen.cs(6行基类)、ScreenLayout.cs(分屏枚举)、ScreenshotSize.cs(截图尺寸枚举)、IWorldOptionsScreen.cs(模组世界选项屏接口) |
| 启动加载与游戏内 | 4 | LoadingScreen、GameLoadingScreen、LoadingFailedScreen、GameScreen |
| 主菜单与世界流 | 5 | MainMenuScreen、PlayScreen、NewWorldScreen、ModifyWorldScreen、WorldOptionsScreen |
| 玩家管理 | 2 | PlayersScreen(分屏/加人)、PlayerScreen(Initial/Add/Edit 三模式) |
| 设置 | 8 | SettingsScreen + Performance/Graphics/Ui/Compatibility/Audio/Controls/Font |
| 输入映射与摄像机 | 4 | KeyboardMappingScreen、GamepadMappingScreen、VrControllerMappingScreen、CameraManageScreen |
| 图鉴与帮助 | 7 | Recipaedia/Description/Recipes、Bestiary/Description、Help/HelpTopic |
| 内容管理 | 6 | ContentScreen、ExternalContentScreen、ManageContentScreen、ModsManageContentScreen(+Community 分部)、ModpacksManageContentScreen |
| 中文社区 | 8 | CommunityScreen(+Auth/Featured/Posts/Ui 四分部)、CommunitySettingsScreen、CommunityMyPublishedScreen、CommunityScreenBase |
| 原版社区 | 4 | OriginalCommunityContentScreen/Manager/Entry、OriginalExternalContentType |
| 杂项单屏 | 6 | NagScreen、TrialEndedScreen、ModSettingsScreen、ReleasesScreen、ManageClassSubstitutesScreen、ManageUserScreen(整文件注释=死文件) |
| 共享工具/渲染 | 13 | ScreenSpaceFireRenderer、PostTreePresenter、PostIconLoader、EvictableTextureCache、HtmlTextUtils、PostDetailsHeaderBuilder、三个 Community*Formatter、CommunityTimeFormatter、ModpackIconLoader/Manager、Models×2 |

## 核心机制

### 1. 屏幕栈与切换协议（切换器本体另见 01 页，此处只列屏层要点）

- 注册：启动时只有 `"Loading"`（ScreensManager.cs:197-208）；其余 40 个命名屏全部由 `LoadingScreen.InitScreens` 以加载动作注册（LoadingScreen.cs:609-650），屏名=字符串键（"Game"/"MainMenu"/"Play"…），`AddScreen` 后 `SwitchScreen("名字")` 才能找到。
- 栈语义：`HistoryStack`(Stack\<Screen\>，ScreensManager.cs:36)。`SwitchScreen` 目标==栈顶 → Pop（这就是"返回"）；否则把旧当前屏 Push（:76-81）。`GoBack()`(:90)=切栈顶。屏自身**不用记来路**，但图鉴类屏仍自存 `m_previousScreen` 做跨子屏返回（RecipaediaScreen.cs:73-78——从 Recipes/Description 回来时不覆盖来路）。
- 同屏重入被禁：`screen == CurrentScreen` 直接 return（ScreensManager.cs:59-61）。需要"屏内再导航"的屏自建内部栈：ModSettingsScreen.cs:20,233-261（Push/Pop+重建内容）。
- **未注册也能切**：`SwitchScreen(Screen)` 直收实例——唯一原版用例 `SwitchScreen(new LoadingFailedScreen(...))`（LoadingScreen.cs:309-321），一次性错误屏不占注册表。
- 整表重建：`RebuildAllScreens`（ScreensManager.cs:100-159，换语言/字体热切换共用）逐屏 Activator 重建；preserve 谓词保命——`SettingsFontScreen.RebuildScreens` 保留 GameScreen（SettingsFontScreen.cs:378-382，世界绑定屏重建=空壳黑屏），被替换旧实例 Dispose 但**不调 Leave**（:148-158）。
- 重启直达：`RestartGameToScreen` 写 Settings.xml（ScreensManager.cs:166-172）→ 进程重启 → LoadingScreen 最后一步 `ConsumeRestartReturnScreen` 直达（LoadingScreen.cs:593-606）。
- LoadingScreen.Enter 是**总复位点**：清掉 m_screens 里除自己外的全部屏再重跑 InitActions（LoadingScreen.cs:675-685）。

### 2. Screen 生命周期钩子全链

```
new(ctor: ContentManager.Get<XElement>("Screens/名")→LoadContents→Children.Find 缓存控件→订阅事件)
 → Enter(params)(收参数/绑数据/清状态) → [动画 Factor≥0.5 才真进树：Children.Insert(0,screen)+Enter，ScreensManager.cs:305-317]
 → Update() 每帧(按钮轮询 IsClicked/设置回写/返回键) → Leave()(退订/清缓存/存档)
 → Dispose()(仅 RebuildAllScreens/关窗触发——静态事件退订必须放这里)
```

- Enter/Leave **不随 SwitchScreen 同步执行**，等切换动画过半（ScreensManager.cs:294/:307）；切屏后头半帧两屏都不在更新中。切屏瞬间旧屏 Input 被清（:73）。
- Update 是 Widget 虚方法，由 `ScreensManager.Update → Widget.UpdateWidgetsHierarchy(RootWidget)` 驱动（ScreensManager.cs:210-215）；绘制走 `LayoutAndDrawWidgets`（:447-484，850 基准缩放）。
- 屏层 mod 钩子（HooksManager 可挂）：`OnSwitchScreen`(可改写 ref screen 换目标，ScreensManager.cs:52-58)、`OnScreenLeaved`/`OnScreenEntered`(:295-315)、`OnLoadingStart`(注入加载动作，LoadingScreen.cs:485-496)、`OnSettingsScreenCreated`(加设置钮，SettingsScreen.cs:32-43)、`OnMainMenuScreenCreated`(加底栏钮，MainMenuScreen.cs:46-52)、`LoadWorldInfoWidget`(改世界条目 UI，PlayScreen.cs:50-56)、`BeforeGameLoading`(改写要进的世界，PlayScreen.cs:278-284)、`EditRecipeScreenWidget`(RecipaediaRecipesScreen.cs:56-62)、`EditBlockDescriptionScreen`(RecipaediaDescriptionScreen.cs:153-162)、`LoadCreatureInfoInBestiaryScreen`/`UpdateCreaturePropertiesInBestiaryDescriptionScreen`(BestiaryScreen.cs:35-41/BestiaryDescriptionScreen.cs:151-161)。
- 标准返回写法四选一：`SwitchScreen(PreviousScreen)`（APIT 短路屏）、`GoBack()`（栈顶）、`SwitchScreen("固定屏")`（层级明确如 Play→MainMenu）、屏内自管栈（ModSettings）。

### 3. 屏幕与 World/Project 生命周期衔接

- 新建：NewWorldScreen.Play → `WorldsManager.CreateWorld` → `SwitchScreen("GameLoading", worldInfo, null)`（NewWorldScreen.cs:108-115）。修改：ModifyWorldScreen.Apply → `ChangeWorld` → 回 Play（ModifyWorldScreen.cs:141-150）。
- 进世界状态机（GameLoadingScreen.cs:21-96）：Enter 收 (WorldInfo, snapshotName) → WaitingForFadeIn（等 `ScreensManager.IsAnimating==false`）→ RestoringSnapshot(有快照先恢复) → Upgrading(`Task.Run RepairAndUpgradeWorld`，后台) → Loading(主线 `GameManager.LoadProject` + `SwitchScreen("Game")`)。任何状态抛异常 → 回 PreviousScreen + 弹 ViewGameLogDialog（:86-96）。
- PlayScreen 进世界前置：读世界 UsedMods 节点比对已装 mod（缺失/版本不符弹确认框，PlayScreen.cs:187-274）→ `GameLoad` → `BeforeGameLoading` 钩子（可换目标）→ GameLoading（:277-289）。
- 在世界内：GameScreen.Update 每 300 真实秒自动存档（GameScreen.cs:37-41）、`GameManager.UpdateProject()` 驱动 tick（:48）；Leave 时 `SaveProject(true,true)` + 音频 Mute（:25-32）；构造时挂 Window.Deactivated→存档、Window.Closed→DisposeProject（:13-14）。试玩版 19 分钟到点→TrialEnded（:42-47）。
- 退世界回 MainMenu：PlayerScreen.Initial 模式返回键 = `SaveProject(true,true)`+`DisposeProject`+`SwitchScreen("MainMenu")`（PlayerScreen.cs:239-243）；Program.Run 顶层异常兜底同链（另见 01 页）。
- 玩家分屏：PlayersScreen.Enter 订阅 `SubsystemPlayers.PlayerAdded/Removed`，Leave 必退订并清缓存（PlayersScreen.cs:22-35）；分屏布局枚举 ScreenLayout 按人数限制可选值（:80-148）。

### 4. 自定义屏幕最小集

1. 建类 `class MyScreen : Screen`，构造里 `ContentManager.Get<XElement>("Screens/MyScreen")` + `LoadContents(this, node)`（XML 布局可自备，也可纯代码建控件，样板见 LoadingFailedScreen.cs:7-41）；override `Enter/Leave/Update`。
2. 注册：mod 在 `OnLoadingStart` 钩子里拿 `actions` 列表加一条 `ScreensManager.AddScreen("MyScreen", new MyScreen())`（队列消费点 LoadingScreen.cs:481-496）。
3. 切换/返回：`SwitchScreen("MyScreen", 参数)`；参数经 `Enter(object[])` 收（装箱，多参按序取）；返回用 `GoBack()` 即可回上一屏。
4. 想把入口挂进设置页：`OnSettingsScreenCreated` 钩子里 `screen.AddSettingButton(text, action)`（SettingsScreen.cs:86-115，奇偶分左右两列）。
5. 想进世界选项页：实现 `IWorldOptionsScreen` 空标记接口（IWorldOptionsScreen.cs:5）——NewWorld/ModifyWorld 回跳时若 `PreviousScreen is IWorldOptionsScreen` 就**不重置** WorldSettings（NewWorldScreen.cs:49-56、ModifyWorldScreen.cs:57-67），这是"选项屏返回不丢数据"的官方协议。

## 坑与对策

- **同屏 SwitchScreen 无效**：目标是 CurrentScreen 直接 return（ScreensManager.cs:59-61）→ 屏内分级导航用内部栈（抄 ModSettingsScreen），别自己切自己。
- **Enter 里读不到切屏参数生效后的世界**：Enter 在动画过半才跑，同帧读 `CurrentScreen`/Project 拿到旧态 → 初始化放 Enter 内部完成，别在调用方切完就读。
- **换语言/字体屏被 Activator 重建**：字段状态全丢、ctor 重跑；订阅静态事件必须 `override Dispose` 退订（CommunityScreenBase.cs:16-25——RebuildAllScreens 不调 Leave，Leave 退订=泄漏）。
- **GameScreen 不可重建**：换字体屏 preserve 它（SettingsFontScreen.cs:381）；自己仿写 Rebuild 时照抄谓词，否则返回游戏=黑屏无输入。
- **屏实例全局复用**：Page/SelectedItem/筛选跨 Enter 存活 → 每次 Enter 显式重置（CommunityScreen.cs:156-179、CommunityMyPublishedScreen.cs:71-77，页码残留会请求到空列表）。
- **共享单例委托 ctor 赋值被覆盖**：多屏都给 DownloadFlowManager.StatusReporter 赋值时后注册者赢 → 用 Enter/Leave 配对安装/释放且"只在自己仍持有时清空"（CommunityScreen.cs:77-79、CommunitySettingsScreen.cs:53-62）。
- **Enter 里直接 Task.Run 回填列表**：必须 `Dispatcher.Dispatch` 回主线再碰控件（PlayScreen.cs:91-115 样板）；TaskSlot 模式（Start/TryTake）是社区屏的标准替代。
- **返回键被"等待按键"状态吞掉**：KeyboardMappingScreen 等待新键时 Input.Back 先被解释为取消改键（:95-101 vs :127-129）——做录入型屏要分层处理返回键。
- **Main 返回键语义随屏变**：NagScreen.Enter 设 `Keyboard.BackButtonQuitsApp=true` Leave 复位（NagScreen.cs:12-21）；MainMenu 每帧按试玩态写（MainMenuScreen.cs:81）。新屏若动这个标志必须 Leave 复位。

## 原版范例

| 我要做… | 照抄哪里 |
|---|---|
| 最小设置/子菜单屏（XML+滑块+返回） | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\SettingsAudioScreen.cs:5-34——40 行含全部样板：LoadContents、Find 缓存、IsSliding 双向同步、Back 三条件 |
| Enter 收参数填详情页 | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\HelpTopicScreen.cs:19-24——参数[0]强转填 Label+滚动复位 |
| 异步加载列表不卡帧 | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\PlayScreen.cs:82-118——BusyDialog+Task.Run+Dispatcher.Dispatch 回填，跨 Enter 保留选中项 |
| 进世界流程状态机 | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\GameLoadingScreen.cs:21-96——Engine.StateMachine 四态+异常落日志框 |
| 设置页加自定义按钮 | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\SettingsScreen.cs:32-43,86-115——钩子+AddSettingButton 奇偶分列 |
| 方块/生物专属图鉴页 | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\RecipaediaScreen.cs:36-44,116-123——Block.GetBlockDescriptionScreen/GetBlockRecipeScreen 整替注册表项 |
| 世界选项屏接入建/改世界 | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\WorldOptionsScreen.cs:7,250-254——实现 IWorldOptionsScreen，返回不重置 WorldSettings |
| 多屏共享行为基类 | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\Community\CommunityScreenBase.cs:9-90——ctor 订阅/Dispose 退订/单槽委托 Enter-Leave 配对 |
| 单实例多级导航 | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\ModSettingsScreen.cs:19-20,59-73,233-261——内部 (pkg,pageIds,title) 栈 |
| 屏内异步任务槽 | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\Community\CommunityScreen.cs:52-55,236-254——TaskSlot.Start 异步 + Update.TryTake 收结果 |

## 快查路由

| 我想… | 去/看 |
|---|---|
| 知道某屏的注册名/在哪注册 | LoadingScreen.cs:609-650（40 屏名字表）；"Loading" 在 ScreensManager.cs:205-208 |
| 切屏/返回/拦屏 | ScreensManager.cs:51-90（本体）、01-程序入口与主循环.md"屏幕切换机制" |
| 写一个新屏 | 本页"自定义屏幕最小集"4 步 + SettingsAudioScreen 样板 |
| 屏内做子页面导航 | ModSettingsScreen.cs:19-20（内部栈，规避同屏重入） |
| Enter/Leave/Dispose 各该做什么 | 本页机制 2 全链 + CommunityScreenBase.cs:16-25（退订纪律） |
| 加载动作/启动序列排队 | LoadingScreen.cs:158-607（InitActions 全队列）；另见 12-ModAPI与加载链 |
| 世界怎么进/退、存档谁调 | 本页机制 3 + GameScreen.cs:25-32, GameLoadingScreen.cs:64-73 |
| 给设置页/主菜单加入口 | SettingsScreen.cs:32-43 / MainMenuScreen.cs:46-52 两钩子 |
| 方块说明书/配方页自定义 | RecipaediaScreen.cs:41,122 + Block.GetBlockDescriptionScreen/GetBlockRecipeScreen |
| mod 设置页（声明式） | ModSettingsScreen.cs:75-204（ModSettingsManager 页树→控件） |
| 屏间共享数据/服务定位 | 无通用上下文对象：参数走 `Enter(object[])`，服务走静态 Manager（WorldsManager/ModsManager 等） |
| 查控件 Find 用法/XML 装载 | 09-UI与Widget体系.md（Widget 层）；本页只管屏级 |
| 71 文件逐个速查 | 17a-Screen明细.md |

另见：[01-程序入口与主循环.md](01-程序入口与主循环.md)（ScreensManager 切换动画/帧序）、[09-UI与Widget体系.md](09-UI与Widget体系.md)（控件层）、[12-ModAPI与加载链.md](12-ModAPI与加载链.md)（钩子与加载动作）、[18-Dialog对话框族.md](18-Dialog对话框族.md)（对话框叠在屏上，不占屏栈）。
