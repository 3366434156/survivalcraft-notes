# A17 原始报告 · SC Screen 屏幕族全量深读

> 任务: 把 SC 引擎 Screen 屏幕族深读到全量级并回写 17/17a 页。日期: 2026-10-31。
> 源码: E:\SurvivalcraftAPIProject\Survivalcraft\Screen\（只读，未做任何修改）；ScreensManager.cs（Managers\，属 01 页域，本次实读作交叉验证）一并实读。

## 一、统计

- 目录构成：根目录 47 个 .cs + Community 19 + OriginalCommunity 4 + Shared 1 = **71 个 .cs**，与任务预估一致。
- 深读方式：**71/71 全读**——〔深〕全文深读 64 个（最大全文 WorldOptionsScreen.cs 590 行、LoadingScreen.cs 757 行分两段整读）；〔节〕节选深读 7 个（ModsManageContentScreen.Community.cs 859、ModpacksManageContentScreen.cs 939、PostTreePresenter.cs 757、OriginalCommunityContentManager.cs 481 读头段+全签名；ModpackIconLoader/Manager、PostIconLoader 读头段+签名）。无 >2000 行文件。全目录约 1.49 万行。
- 基类形态：`Screen : CanvasWidget`（Screen.cs:2-6）**只有两个虚方法** `Enter(object[])`/`Leave()`；Update/Draw/Input/Measure 全部继承自 Widget 层（09 页域）。"Screen 契约"=Enter/Leave 两个钩子 + Widget 全套逐帧管线。
- 屏幕总数：LoadingScreen.InitScreens 注册 40 个命名屏（LoadingScreen.cs:609-650），外加启动屏 "Loading"（ScreensManager.cs:205-208）= 41 个注册键；另有 1 个未注册直切实例屏（LoadingFailedScreen）。
- 非 Screen 文件 16 个：枚举 2（ScreenLayout/ScreenshotSize）+ 接口 1（IWorldOptionsScreen）+ 粒子渲染器 1 + 原版社区服务/DTO/枚举 3 + 社区共享工具 9（presenter/loader/缓存/格式化/DTO）。
- 死文件 1 个：ManageUserScreen.cs 整文件注释，头行 `//abandoned`。

## 二、家族分类（12 族 × 71 文件）

| 家族 | 数 | 文件 |
|---|---|---|
| 基础设施 | 4 | Screen、ScreenLayout、ScreenshotSize、IWorldOptionsScreen |
| 启动加载与游戏内 | 4 | LoadingScreen、GameLoadingScreen、LoadingFailedScreen、GameScreen |
| 主菜单与世界流 | 5 | MainMenuScreen、PlayScreen、NewWorldScreen、ModifyWorldScreen、WorldOptionsScreen |
| 玩家管理 | 2 | PlayersScreen、PlayerScreen |
| 设置 | 8 | SettingsScreen + Performance/Graphics/Ui/Compatibility/Audio/Controls/Font |
| 输入映射与摄像机 | 4 | KeyboardMappingScreen、GamepadMappingScreen、VrControllerMappingScreen、CameraManageScreen |
| 图鉴与帮助 | 7 | Recipaedia×3、Bestiary×2、Help×2 |
| 内容管理 | 6 | ContentScreen、ExternalContentScreen、ManageContentScreen、ModsManageContentScreen(+Community partial)、ModpacksManageContentScreen |
| 中文社区 | 8 | CommunityScreen(+Auth/Featured/Posts/Ui)、CommunitySettingsScreen、CommunityMyPublishedScreen、CommunityScreenBase |
| 原版社区 | 4 | OriginalCommunityContentScreen/Manager/Entry、OriginalExternalContentType |
| 杂项单屏 | 6 | NagScreen、TrialEndedScreen、ModSettingsScreen、ReleasesScreen、ManageClassSubstitutesScreen、ManageUserScreen(死) |
| 共享工具/渲染 | 13 | ScreenSpaceFireRenderer、PostTreePresenter、PostIconLoader、EvictableTextureCache、HtmlTextUtils、PostDetailsHeaderBuilder、CommunityVersionDetail/CompatibilityFormatter、CommunityTimeFormatter、ModpackIconLoader/Manager、Models×2 |

## 三、机制发现（按重要性）

### 1. Screen 屏=Widget：栈上只有"一层壳"

- 切屏本质是 RootWidget.Children 的增删：旧屏 `RootWidget.Children.Remove`（ScreensManager.cs:303）、新屏 `Children.Insert(0,…)`（:306）——插到最底，绘制顺序由动画 ColorTransform 控制。GameScreen.Draw 甚至反向利用这点：高分辨率且非动画期直接 `Display.Clear` 黑屏再画世界（GameScreen.cs:58-63）。
- HistoryStack 的"返回"实现极简：`screen == TopOfHistoryScreen → Pop`，否则 Push 旧当前屏（ScreensManager.cs:76-81）。`GoBack()`=切栈顶（:90）。栈里存的是**实例引用**，RebuildAllScreens 换语言后要整栈映射到新实例并保持底→顶原序（:136-147，注释详述 [.. Stack] LIFO 快照倒序回推）。
- PreviousScreen 是 API 侧新增直通字段（ScreensManager.cs:34），大量屏用它做"短路返回"（SettingsAudio/Graphics/Performance/Releases/RecipaediaDescription 等 10+ 处）；而图鉴主页仍自存 m_previousScreen——因为它是"从 A 进图鉴→子屏→回 A"的跨子屏来路，PreviousScreen 在进子屏那一刻已被覆盖。

### 2. Enter/Leave 的真实时机：动画过半，不是切换瞬间

- `SwitchScreen` 只建 AnimationData(Factor=0, Speed=4f)（ScreensManager.cs:68-70）；真正 `Leave()`/`OnScreenLeaved` 在 Factor≥0.5 的那一帧（:294-303），`Enter(parameters)`/`OnScreenEntered` 紧随（:305-317），随后才恢复 RootWidget 更新（:316）。同帧 `CurrentScreen` 已是新屏（:82）但 Enter 未跑——"切完就读"必拿旧态。
- 切换瞬间立即做的只有三件事：旧屏 `Input.Clear()`（:73，防残留点击打中新屏）、RootWidget 停更（:72）、HistoryStack 维护。
- 首屏（Loading）Speed=float.MaxValue（:69，CurrentScreen==null 时），即启动屏无淡出动画、Enter 立即执行。

### 3. 全屏注册表与三个特殊注册点

- 常规：LoadingScreen.InitScreens 逐屏 `AddLoadAction(delegate { AddScreen("名", new XxxScreen()) })`（LoadingScreen.cs:609-650）——注册本身就是加载队列的一步，发生在"内容管理器/数据库/方块"全部就绪之后（InitScreens 调用点在 Database/BlocksManager 步之后，:558）。
- 特殊点 A：LoadingScreen.Enter 先把 m_screens 里除自己外的键全删再重跑 InitActions（:675-685）——重进 Loading 屏=全屏表复位+全加载队列重跑，是"重启进程"之外的软复位通道。
- 特殊点 B：`SwitchScreen(Screen)` 接受任意实例不要求注册（ScreensManager.cs:51），原版唯一用例 LoadingFailedScreen（:309-321）——一次性的错误屏不占注册表。
- 特殊点 C：Recipaedia 运行时**整替注册表项**：`ScreensManager.m_screens["RecipaediaDescription"] = block.GetBlockDescriptionScreen(value)`（RecipaediaScreen.cs:41、:116），Recipes 同理（:122）——方块类可自带屏子类，这是"按数据替换屏实例"的官方机制（Block 虚方法）。

### 4. 屏层 mod 钩子共 11 处（全 Screen 目录扫描）

OnSwitchScreen（可改写 ref screen，ScreensManager.cs:52-58）、OnScreenLeaved/OnScreenEntered（:295-315）、OnLoadingStart（注入加载动作，LoadingScreen.cs:485-496）、OnSettingsScreenCreated（SettingsScreen.cs:32-43，还回收 mod 按钮 dict）、OnMainMenuScreenCreated（MainMenuScreen.cs:46-52）、LoadWorldInfoWidget（PlayScreen.cs:50-56，ref containerWidget 可整替）、BeforeGameLoading（PlayScreen.cs:278-284，可改写 item 即换世界）、EditRecipeScreenWidget（RecipaediaRecipesScreen.cs:56-62）、EditBlockDescriptionScreen（RecipaediaDescriptionScreen.cs:153-162，新旧双签名 :157-159）、LoadCreatureInfoInBestiaryScreen（BestiaryScreen.cs:35-41）、UpdateCreaturePropertiesInBestiaryDescriptionScreen（BestiaryDescriptionScreen.cs:151-161）。另 WorldOptionsScreen.cs:233-237 用 `ModsManager.ModHooks["TerrainContentsGenerator24Initialize"]` 检测有 mod 注册该钩子时锁死"生成器版本"按钮。

### 5. 生命周期契约的两个版本：Leave 型与 Dispose 型

- 常规屏：Enter 订阅/Leave 退订+清缓存（PlayersScreen.cs:22-35 是教科书）。但 **RebuildAllScreens（换语言/字体）只 Dispose 不调 Leave**（ScreensManager.cs:148-158）——凡订阅静态事件/单例事件的屏，退订必须放 `override Dispose`。CommunityScreenBase 把这条写成注释纪律并落地（CommunityScreenBase.cs:16-25）；CommunityScreen/CommunityMyPublishedScreen 的 Dispose→m_postsPresenter.Detach 解 PostIconLoader 静态事件（CommunityScreen.cs:261-266）。
- preserve 保命：SettingsFontScreen.RebuildScreens 传 `s => s is GameScreen`（SettingsFontScreen.cs:378-382）——GameScreen 经 Activator 重建=没加载世界的空壳，返回即黑屏无输入（ScreensManager.cs:93-98 注释明示）。
- GameScreen 自身生命周期与 Window 事件绑死：Deactivated→SaveProject、Closed→DisposeProject（GameScreen.cs:13-14）；Leave 再 SaveProject(true,true)（:28）。自动存档 300 真实秒（:37-41）；试玩 1140 秒游戏时间到点存档+踢到 TrialEnded（:42-47）。

### 6. 进世界链（屏视角补完 01 页）

PlayScreen.Play 读世界 UsedMods 节点逐 mod 比对（缺→modsNotLoaded、版本不符→modsVersionNotCapable，:187-225）→ 弹确认 → GameLoad → BeforeGameLoading 钩子可换 item → `SwitchScreen("GameLoading", item, null)`（:277-289）。GameLoadingScreen 四态：WaitingForFadeIn（等 IsAnimating==false，:24-35）→（有快照先 RestoringSnapshot :74-83）→ Upgrading（`Task.Run RepairAndUpgradeWorld`，完成标志/error 标志轮询，:36-63）→ Loading（主线 LoadProject+SwitchScreen("Game")，:64-73）。状态机任何异常→PreviousScreen+ViewGameLogDialog（:86-96）。NewWorld/ModifyWorld 进 WorldOptions 传 (WorldSettings, isExisting)，返回判定 `PreviousScreen is IWorldOptionsScreen` 决定是否重置 WorldSettings（NewWorldScreen.cs:49-56、ModifyWorldScreen.cs:57-67）——IWorldOptionsScreen 是"选项屏返回不丢数据"协议。

### 7. 屏内异步三模式（并存在同一目录里）

- 模式 1（老式）：BusyDialog + Task.Run + Dispatcher.Dispatch 回填（PlayScreen.Enter:82-118、SettingsCompatibilityScreen 分享日志:86-95）。
- 模式 2（新式）：TaskSlot<T>（Start/TryTake/Invalidate/IsRunning）+ Update 里 TryTake 消费（CommunityScreen 四槽:52-55,236-254；ModsManageContentScreen.Community 六槽；ModpacksManageContentScreen m_fileInfoSlot）。Leave 统一 Invalidate+Cancel（CommunityScreen.cs:203-215、ModsManageContentScreen.cs:142-151）。
- 模式 3（反例）：`Task.Delay(250).Wait()` 直接阻塞主线程（OriginalCommunityContentScreen.cs:198-203 长按强刷）——勿学。
- PostTreePresenter + PostIconLoader 是"屏内 MVP"：presenter 管树/分页/懒加载占位（Shared/PostTreePresenter.cs:12-23），图标进程级共享（128 容量 EvictableTextureCache+在途去重，PostIconLoader.cs:14-15），反射写 TreeViewNode.m_subtexture（:17-21）。

### 8. 单槽委托与跨屏共享单例

DownloadFlowManager.Instance 的 StatusReporter/ManualSelectResolver/EffectiveSourceResolver 是共享单例上的单槽：三屏 ctor 都赋会互相覆盖 → 统一 Enter 安装/Leave 释放且"只在自己仍持有时清空"（CommunityScreenBase.cs:53-89、CommunityScreen.cs:77-79 注释、CommunitySettingsScreen.cs:53-62 定向判等释放）。

### 9. 同屏重入禁令与两条绕法

`screen == CurrentScreen` 直接 return（ScreensManager.cs:59-61）。绕法 A：屏内页面栈（ModSettingsScreen.cs:20 的 `Stack<(pkg,pageIds,title)>`+NavigateCurrent:59-73，注释明写"规避单实例 SwitchScreen 同实例重入限制"）。绕法 B：手动 Leave()+Enter() 复用实例（PlayerScreen.cs:230-236 AddAnother）。

### 10. 屏实例全局复用的状态残留

屏对象常驻（除非换语言重建）：Page/SelectedItem/搜索词/开关全部跨 Enter 存活。社区屏对策是 Enter 显式重置（CommunityScreen.cs:156-179 回第 1 页、CommunityMyPublishedScreen.cs:71-77 重置页码+未发布开关，注释解释"旧页码请求返回空列表"）。

## 四、坑实录（新页"坑与对策"素材来源）

- 切屏后同帧读新屏 Enter 结果拿不到（动画过半才跑，ScreensManager.cs:305-317）——01 页已录，屏层补实例：HelpTopicScreen.Enter 直接强转 parameters[0]，参数协议错误即崩（HelpTopicScreen.cs:19-24）。
- SwitchScreen(string) 未注册名抛 ArgumentNullException（ScreensManager.cs:62-64）——01 页已录；本次补充"未注册实例直切"合法（LoadingFailed 用例）。
- RebuildAllScreens 不调 Leave→Leave 退订=泄漏；GameScreen 不可重建（见机制 5）。
- 多屏 ctor 抢单槽委托后注册者赢（机制 8）。
- 等待改键态吞 Back：KeyboardMappingScreen.cs:95-101 vs :127-129 分层；Gamepad/VrControllerMapping 同构。
- Keyboard.BackButtonQuitsApp 谁置位谁复位：NagScreen.cs:12-21、MainMenuScreen.cs:76-81。
- busy 弹窗每个分支都要 Hide，残留全屏 Cover 锁输入（ExternalContentScreen.cs:276-278 注释原文）。
- GamepadMappingScreen 复用 KeyboardMappingScreen 的 XML 且 fName=typeof(KeyboardMappingScreen).Name（:46,:59）——翻译键挂错屏名时先查这里。
- OriginalCommunityContentScreen 长按强刷 Task.Delay().Wait() 阻塞 250ms（:198-203）。
- ModsManageContentScreen 上移/下移必须 ReferenceEquals（ModEntity 重写 Equals 基于包名+版本，:352 注释）。
- 分页按钮 busy 判断曾写反（==null 空闲时禁用）锁死翻页——Community.Ui.cs:148-152 注释留档。
- ManageUserScreen 整文件注释废弃（死文件，勿引用）。

## 五、原版范例候选（已选 10 条入 17 页）

SettingsAudioScreen（最小设置屏）、HelpTopicScreen（参数详情屏）、PlayScreen.Enter（异步列表）、GameLoadingScreen（状态机）、SettingsScreen:32-115（钩子+AddSettingButton）、RecipaediaScreen:36-44/116-123（方块专属屏整替）、WorldOptionsScreen（IWorldOptionsScreen 协议）、CommunityScreenBase（多屏公共基类）、ModSettingsScreen（单实例内部栈）、CommunityScreen:52-55/236-254（TaskSlot 异步）。

## 六、回写记录

- 新建 E:\数据\生存战争系列\SC完全学习笔记\10-SC引擎\17-Screen屏幕族.md（约 170 行：目录地图 12 符号、家族概览 12 族=71 文件、机制 4 节、坑 9、范例 10、路由 13）。
- 新建 E:\数据\生存战争系列\SC完全学习笔记\10-SC引擎\17a-Screen明细.md（71 行一表：〔深〕64/〔节〕7）。
- 未改动 01/09/18 页（ScreensManager 切换器、Widget 层、Dialog 层各归其位，本页只做"另见"）；未触碰 SC 库既有页面与库外私有笔记任何文件；SC 源码只读。
- 行号基准：2026-10-31 源码实测。
