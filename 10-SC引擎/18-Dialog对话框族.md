# Dialog 对话框族

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(57/57 全文深读，最大 542 行)

## 一句话定位

Dialog 目录级域：模态对话框容器（遮罩/动画/生命周期）、消息/列表/文本输入/进度框与各编辑器的构造与关闭约定。

**分工边界**：本页只写 `E:\SurvivalcraftAPIProject\Survivalcraft\Dialog\` 目录（含 Community 子目录，共 57 个 .cs）与其管理器 `DialogsManager`。部件级机制（布局/命中/XML 解析/文本管线）全在 `09-UI与Widget体系.md`；Screens 切屏在 09 页"Screens 体系"节。

## 目录地图

| 符号(类/文件) | 绝对路径 | 职责 |
|---|---|---|
| `Dialog` | E:\SurvivalcraftAPIProject\Survivalcraft\Dialog\Dialog.cs | 全部对话框基类：CanvasWidget + 全屏命中 + Size=∞ |
| `DialogsManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\DialogsManager.cs | 静态管理：挂树/遮罩/进出场动画/每帧更新 |
| `MessageDialog` | E:\SurvivalcraftAPIProject\Survivalcraft\Dialog\MessageDialog.cs | 两按钮消息/确认框（全族最常用） |
| `ListSelectionDialog` | E:\SurvivalcraftAPIProject\Survivalcraft\Dialog\ListSelectionDialog.cs | 通用列表选择框（3 个 Select 系对话框的基类） |
| `TextBoxDialog` | E:\SurvivalcraftAPIProject\Survivalcraft\Dialog\TextBoxDialog.cs | 单行文本输入框（确定/取消回调 string） |
| `BusyDialog` / `CancellableBusyDialog` | E:\SurvivalcraftAPIProject\Survivalcraft\Dialog\BusyDialog.cs / CancellableBusyDialog.cs | 忙碌提示 / 可取消进度（配 CancellableProgress） |
| XML 模板目录 | E:\SurvivalcraftAPIProject\Survivalcraft\Content\Assets\Dialogs\ | 48 个对话框 XML（根 CanvasWidget 定尺寸） |

逐文件一行表 → `18a-Dialog明细.md`。

## 家族概览（根 43 + Community 14 = 57 个 .cs）

| 家族 | 文件数 | 成员 |
|---|---|---|
| 基元骨架 | 3 | Dialog、SureDialog(空壳，XML 占位)、MessageDialogButton(枚举) |
| 消息/确认 | 8 | MessageDialog、BulletinDialog(滚到底才出确认)、LevelFactorDialog、CommunityImportOverwriteDialog(三按钮)、RestartConfirmDialog、CommunityModpackFileConflictDialog(五按钮)、CommunityDownloadFailureDialog、EditCommunityServerInfoDialog |
| 列表选择 | 7 | ListSelectionDialog(基类)、SelectGameModeDialog、SelectExternalContentProviderDialog、SelectExternalContentTypeDialog(:5 三者 : ListSelectionDialog)、SelectCommunityServerDialog、SelectDownloadSourceDialog、SelectClassSubstituteDialog |
| 文本输入 | 4 | TextBoxDialog、DownloadContentFromLinkDialog、ExternalContentLinkDialog、EditWorldSeedDialog |
| 进度/忙碌 | 3 | BusyDialog、CancellableBusyDialog、CommunityDownloadDialog(ValueBar 进度) |
| 电元件编辑器 | 9 | EditSignDialog、EditMemoryBankDialog、EditMemoryBankDialogAPI、EditTruthTableDialog、EditVoltageLevelDialog、EditPistonDialog、EditAdjustableDelayGateDialog、EditColorDialog、EditPaletteDialog |
| 游戏内大面板 | 2 | GameMenuDialog(暂停菜单+统计，542 行)、BuildFurnitureDialog(家具编辑) |
| 帮助/加载 | 3 | KeyboardHelpDialog、GamepadHelpDialog、SpawnDialog(出生进度) |
| 工具/调试 | 2 | RunJsDialog(JsInterface 控制台)、ViewGameLogDialog(日志查看+过滤+复制) |
| 社区/内容管理 | 16 | LoginDialog(尸体类)、CommunityLoginDialog、MoreCommunityLinkDialog、PublishCommunityLinkDialog、RateCommunityContentDialog、ReportCommunityContentDialog、ModDetailsDialog、ModpackDetailsDialog、CommunityDownloadQueueDialog、CommunityFiltersDialog、CommunityMissingDependenciesDialog、CommunityModReviewDialog、CommunityModVersionsDialog、CommunityPostDetailsDialog(Html+自动翻译)、EditDownloadSourceInfoDialog、RemoteControlDialog |

## 核心机制

### 生命周期：挂树即开、动画播完才摘

- **本体**：`Dialog : CanvasWidget`，ctor 只做两件事——`IsHitTestVisible = true`（挡住下层输入）+ `Size = new Vector2(1f / 0f)`（∞=吃满父格，`Dialog.cs:4-9`）；实际可见尺寸由 XML 根节点定（MessageDialog.xml:1 `Size="600, 250" ClampToBounds="true"`），ctor 的 size 参数 ≥0 才覆盖（`MessageDialog.cs:27`）。
- **ShowDialog**（`DialogsManager.cs:46-77`）：先派 `OnShowDialog` 钩子（模组可换 parent/dialog，返回 null 即取消弹窗，`:47-53`）→ `Dispatcher.Dispatch` 排主线程（**异步**，当帧 Children 里还没有）→ `Contains` 防重入 → `CoverWidget` 遮罩 (0,0,0,192) 先挂（`:65-67`）→ 对话框后挂（后挂者绘制在上）→ `dialog.Input.Clear()` 吞掉残留输入（`:73`）。
- **HideDialog**（`DialogsManager.cs:79-100`）：派 `OnHideDialog` 钩子 → 从 m_dialogs 移除 + `Direction = -1`，**不立即摘树**——出屏动画继续画。
- **每帧驱动**：`DialogsManager.Update()` 在主循环（`Game\Program.cs:299`）推进 Factor ±6/秒（约 1/6 秒播完，`:113-121`）；Factor≤0 才把对话框与遮罩同时从树上摘除（`:124-129`）。动画 = 中心缩放 0.75→1.0 + 颜色 alpha 渐入（`UpdateDialog`，`:133-148`）。
- **查询**：`DialogsManager.Dialogs`（快照列表）、`HasDialogs(parent)` / `HasDialogsOrAnimations(parent)`（`:23-44`，注意挂在死屏上的实例仍占位，见"坑"）。
- **parent 语义**：null = `ScreensManager.CurrentScreen ?? RootWidget`（`:60-62`）；传 `this` = 嵌套（对话框叠对话框，EditColorDialog.cs:140 先例）；每个对话框独立遮罩，多层嵌套遮罩会叠暗。

### 输入与关闭：每帧轮询而非事件

对话框没有窗口过程，全部逻辑写在 `Update()` 覆写里逐帧查输入。标准五件套（MessageDialog.cs:52-68 为样板）：

1. `Input.Cancel`（Back/Esc）→ Dismiss(Button2)，仅一个按钮时降级 Dismiss(Button1)。
2. `Input.Ok` / 按钮1 `IsClicked` → Dismiss(Button1)。
3. 按钮2 `IsClicked` → Dismiss(Button2)。
4. **点外关闭**：`Input.Tap.HasValue && !HitTest(Input.Tap.Value)`（DownloadContentFromLinkDialog.cs:28-31 先例，10+ 处沿用）。
5. **Dismiss 三件套**：`AutoHide`（默认 true）→ `DialogsManager.HideDialog(this)` → `m_handler?.Invoke(result)`（`MessageDialog.cs:70-75`）。

回调语义差异（易混）：`ListSelectionDialog.Dismiss` 仅 `result != null` 才回调（`ListSelectionDialog.cs:92-101`）；`TextBoxDialog.Dismiss(null)`（取消）**也会回调** handler 传 null（`TextBoxDialog.cs:72-77`）——handler 内必须判 null。防重复触发：ListSelectionDialog 用 `m_isDismissed` 一次性标志 + 选中后延迟 50ms 再关（给玩家按下反馈，`:14,82-88`）；防止滚动中误选则在 Update 里检查 `!m_listWidget.HitTest(Input.Tap.Value)`。

### 构造模式：XML 模板改装 vs 全代码构建

- **XML 模板（主流）**：ctor 里 `ContentManager.Get<XElement>("Dialogs/Xxx")` → `LoadContents(this, node)` → `Children.Find<T>("Xxx.部件名")` 缓存引用 → 填数据。与 09 页"复合控件模板模式"同源，模板在 `Content\Assets\Dialogs\*.xml`（48 个，与 .cs 一一对应）。
- **全代码构建（4 例）**：EditColorDialog.cs:19-136、EditMemoryBankDialogAPI.cs:21-50、LoginDialog.cs:19-40、EditPaletteDialog 的行构建段。要点：中心 CanvasWidget 定尺寸 → `BevelledRectangleWidget { Style = ContentManager.Get<XElement>("Styles/DialogArea") }` 做底板（EditColorDialog.cs:25）→ StackPanel 填内容。适合条目数运行时才定的界面。
- **动态内容行**：GameMenuDialog 统计面板全代码 `AddStat`（UniformSpacingPanel + 3 个 FontTextWidget 一行，`GameMenuDialog.cs:520-541`）；"More"子菜单 = `ListSelectionDialog(Tuple<string,Action> 列表)`（`:475-482`）——运行时组装菜单的标准样板。

### 进度与取消：CancellableProgress 协作链

`CancellableBusyDialog` ctor 自建 `CancellableProgress`（`CancellableBusyDialog.cs:46`）；把 `dialog.Progress` 传给 `WebManager.Post(..., progress, 成功, 失败)`（ViewGameLogDialog.cs:114-120 注释段、PublishCommunityLinkDialog.cs:65-70 同构）。Update 每帧把 `Progress.Completed/Total` 百分比刷到 SmallMessage（`:70-72`）；取消按钮 → `Progress.Cancel()`，`autoHideOnCancel` 决定框是否自动关（`:73-78`）。完成后 `m_cancelButtonWidget.Text = "OK"` 变确认键（ViewGameLogDialog.cs:121-122）。社区新链路换用 `CommunityTransferProgress.Snapshot()` + `CommunityDownloadDialog.SetProgress/SetCompleted/SetFailed/SetStopped`（CommunityDownloadDialog.cs:37-63），**进入终态后忽略迟到进度事件且框才可关**（`m_closable`，`:39,74-77`）。

## 坑与对策

- **嵌套框同帧连关两层**：父框 Update 读 `Input.Ok/Back` 是全局共享的，子 ListSelectionDialog 消费同一按键后父框同帧又读到 → 社区筛选框的解法：子框存活期间跳过全局输入分支，且存活判据必须是"在 Dialogs 中**且父链可达 RootWidget**"（切屏后实例挂在死屏上仍留在 Dialogs，CommunityFiltersDialog.cs:64-72,156-185）。
- **ShowDialog 是异步的**：Dispatcher.Dispatch 排队（DialogsManager.cs:57-76），调用后当帧 `Children.Find` 找不到刚弹的框；连续 ShowDialog 两个框的叠放顺序也不保证按调用序。
- **HasDialogs 误判**：切屏不清理 m_dialogs 里的实例，"有没有对话框"要用 `HasDialogsOrAnimations` + 自己校验父链（DialogsManager.cs:23-44）。
- **BusyDialog 吃输入**：Update 里 `Input.Clear()` 吞掉 Back（BusyDialog.cs:34-38）——想强制等待就照抄；反之若自己的对话框用 BusyDialog 当子框，Back 已被它吞。
- **ListPanel 点击后强制重选**：ListPanelWidget 点击回调后无条件把 SelectedIndex 指回点击行；需要"再点一次取消选择"时用 SelectedIndex 每帧 Sync 覆盖 + 条目实例不稳定就直改 `m_items[i]`（CommunityDownloadQueueDialog.cs:91-96,178-193）。
- **ModEntity 按值相等**：ModDetailsDialog 删除条目必须按引用移除（Equals 基于包名+版本，同包同版会撞键，ModDetailsDialog.cs:237-239,328-334）。
- **UpdateCeases 清理**：对话框内启动的 Task/请求要在 `UpdateCeases` 取消（CommunityPostDetailsDialog.cs:105-110 取消在途翻译）；`AutoHide=false` 的框要自己记得 Hide，否则永久遮挡。
- **MessageDialog 至少一按钮**：两个按钮文本都空直接抛 InvalidOperationException（MessageDialog.cs:42-45）。

## 原版范例

| 我要做… | 照抄哪里 |
|---|---|
| 两按钮消息/确认框 | MessageDialog.cs:18-47——ctor 填 4 文本+handler，最通用样板 |
| 列表选择（含定制行） | ListSelectionDialog.cs:23-57 基类 + SelectGameModeDialog.cs:5-20（继承换条目工厂与 ContentSize） |
| 文本输入框 | TextBoxDialog.cs:19-34——HasFocus=true + Enter 提交，一行起 |
| 三按钮以上选择框 | CommunityImportOverwriteDialog.cs:19-49——MessageDialog 只有两按钮，多按钮自建 |
| 可取消进度框 | CancellableBusyDialog.cs:38-78——配 WebManager.Post 的 progress 参数 |
| 无 XML 全代码对话框 | EditColorDialog.cs:19-136——Canvas 定尺寸 + DialogArea 底板 + Stack 布局 |
| 运行时组装菜单/统计行 | GameMenuDialog.cs:475-482（Tuple 菜单）、:520-541（AddStat 动态行） |
| 嵌套对话框（框上弹框） | EditColorDialog.cs:139-166——`ShowDialog(this, new TextBoxDialog(...))` parent 传 this |
| 滚动到底才允许确认 | BulletinDialog.cs:58-63——ScrollPosition ≥ 80% 才显示 OK |
| 点框外关闭 | DownloadContentFromLinkDialog.cs:26-43——Tap 不在框内即关 |
| 每帧轮询的任务队列框 | CommunityDownloadQueueDialog.cs:72-96——IDownloadQueueDialogHost 抽象 + Refresh 全量刷 |
| 重启确认 + 静态便捷入口 | RestartConfirmDialog.cs:14-51——回调返回 true 才真重启（Window.Restart） |

## 快查路由

| 我想… | 去/看 |
|---|---|
| 弹个提示/确认 | `new MessageDialog(大字,小字,按钮1,按钮2,handler)` + `DialogsManager.ShowDialog(null, 框)` |
| 让玩家从列表选一项 | ListSelectionDialog（字符串行用第 2 ctor，定制行走 itemWidgetFactory） |
| 让玩家输入一段文字 | TextBoxDialog；取消时 handler 收 null 要判空 |
| 显示耗时操作进度 | CancellableBusyDialog + CancellableProgress；完成后把取消键文本改 OK |
| 拦截/监听所有弹窗 | `OnShowDialog`/`OnHideDialog` 钩子（DialogsManager.cs:47-53,80-86） |
| 自定义一个对话框 | 照"构造模式"节：XML 模板 + Find 改装，或照 EditColorDialog 全代码 |
| 关闭对话框 | `DialogsManager.HideDialog(dialog)`；自己框内用 `Dismiss()` 三件套 |
| 判断当前有没有模态框 | `DialogsManager.HasDialogsOrAnimations(parent)`；严格判定照 CommunityFiltersDialog.cs:167-185 |
| 做多按钮分支选择 | CommunityImportOverwriteDialog（三按钮）/ CommunityModpackFileConflictDialog（五按钮）模式 |
| 查某对话框类细节 | `18a-Dialog明细.md` 定位文件 → 直接跳源码 |
| 部件布局/输入/XML 属性 | 另见 `09-UI与Widget体系.md`（本页不重复） |
| GameMenu 加自己的菜单项 | GameMenuDialog.cs:379-483 的 ListSelectionDialog 菜单模式；钩子另见 09 页注入节 |
