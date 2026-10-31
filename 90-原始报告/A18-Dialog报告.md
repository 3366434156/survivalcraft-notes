# A18 原始报告 · SC Dialog 对话框族全量深读

> 任务: 把 SC 引擎 Dialog 对话框族深读到全量级并回写 18/18a 页。日期: 2026-10-31。
> 源码: E:\SurvivalcraftAPIProject\Survivalcraft\Dialog\（只读，未做任何修改）；管理器 DialogsManager.cs 与 XML 模板目录一并实读。

## 一、统计

- 目录构成：根目录 43 个 .cs + Community 子目录 14 个 = **57 个 .cs**，与任务预估一致。
- 深读方式：**57/57 全文深读**（最大 GameMenuDialog.cs 542 行，无 >2000 行文件，全部整读）；另实读 `Managers\DialogsManager.cs`（149 行全文）、`Content\Assets\Dialogs\MessageDialog.xml`、主循环调用点 `Game\Program.cs:299`。
- XML 模板：`Content\Assets\Dialogs\` 下 48 个 .xml，与 .cs 大体一一对应；4 个对话框无 XML 全代码构建（EditColorDialog、EditMemoryBankDialogAPI、LoginDialog、EditPaletteDialog 的行构建段）。
- 继承根分布：直接 `: Dialog` 53；二级继承 `: ListSelectionDialog` 3（SelectGameMode/SelectExternalContentProvider/SelectExternalContentType）；非类文件 2（SureDialog 空壳 + MessageDialogButton 枚举）。
- 编译开关特例：RemoteControlDialog 在 IOS/BROWSER 下编译为空壳类（RemoteControlDialog.cs:85-91）；RunJsDialog/ViewGameLogDialog 内有 `#if !BROWSER` 段与整段注释死码（上传旧云盘接口，ViewGameLogDialog.cs:87-133）。

## 二、家族分类（10 家族 × 57 文件）

| 家族 | 数 | 文件 |
|---|---|---|
| 基元骨架 | 3 | Dialog、SureDialog、MessageDialogButton |
| 消息/确认 | 8 | MessageDialog、BulletinDialog、LevelFactorDialog、CommunityImportOverwriteDialog、RestartConfirmDialog、CommunityModpackFileConflictDialog、CommunityDownloadFailureDialog、EditCommunityServerInfoDialog |
| 列表选择 | 7 | ListSelectionDialog(+3 子类 SelectGameMode/Provider/Type)、SelectCommunityServerDialog、SelectDownloadSourceDialog、SelectClassSubstituteDialog |
| 文本输入 | 4 | TextBoxDialog、DownloadContentFromLinkDialog、ExternalContentLinkDialog、EditWorldSeedDialog |
| 进度/忙碌 | 3 | BusyDialog、CancellableBusyDialog、CommunityDownloadDialog |
| 电元件编辑器 | 9 | EditSign/EditMemoryBank/EditMemoryBankAPI/EditTruthTable/EditVoltageLevel/EditPiston/EditAdjustableDelayGate/EditColor/EditPalette |
| 游戏内大面板 | 2 | GameMenuDialog、BuildFurnitureDialog |
| 帮助/加载 | 3 | KeyboardHelp、GamepadHelp、SpawnDialog |
| 工具/调试 | 2 | RunJsDialog、ViewGameLogDialog |
| 社区/内容管理 | 16 | LoginDialog、CommunityLogin、MoreCommunityLink、PublishCommunityLink、Rate、Report、ModDetails、ModpackDetails、CommunityDownloadQueue、CommunityFilters、CommunityMissingDependencies、CommunityModReview、CommunityModVersions、CommunityPostDetails、EditDownloadSourceInfo、RemoteControl |

## 三、机制发现（按重要性）

### 1. 对话框 = CanvasWidget + 遮罩 + 进出场动画（DialogsManager 全读）

- `Dialog : CanvasWidget` ctor 仅设 `IsHitTestVisible=true` 与 `Size=∞`（Dialog.cs:4-9）——∞ 尺寸吃满父格使整屏可命中挡输入，真实尺寸由 XML 根 CanvasWidget 定（MessageDialog.xml:1 `Size="600, 250" ClampToBounds="true"`）；ctor 的 size 参数 ≥0 才覆盖（MessageDialog.cs:27）。
- `ShowDialog`（DialogsManager.cs:46-77）五步：`OnShowDialog` 钩子（loader 可换 parent/dialog，置 null 即取消）→ `Dispatcher.Dispatch` 异步主线程 → `Contains` 防重入 → 遮罩 `CoverWidget`(0,0,0,192) 先挂 → 对话框后挂（后挂=绘制在上）→ `Input.Clear()` 吞残留输入。
- `HideDialog`（:79-100）不摘树：仅移出 m_dialogs 并置 `Direction=-1`；`Update()`（Program.cs:299 每帧）推 Factor ±6/秒，≤0 才把对话框与遮罩同时摘树（:109-131）。动画 = 中心缩放 0.75→1 + alpha（UpdateDialog :133-148）。从弹出到可点最长延迟约 1/6 秒 + Dispatcher 队列。
- parent=null → `ScreensManager.CurrentScreen ?? RootWidget`（:60-62）；parent=this → 嵌套叠框（EditColorDialog.cs:140 先例）；每框独立遮罩，嵌套会叠暗。

### 2. 输入模型：每帧轮询 + Dismiss 三件套 + 点外关闭

- 无窗口过程，逻辑全在 `Update()` 覆写。MessageDialog 样板（MessageDialog.cs:52-68）：Cancel→Button2（单按钮降级 Button1）、Ok/按钮1→Button1、按钮2→Button2。
- **Dismiss 三件套**：`AutoHide`（默认 true）→ `DialogsManager.HideDialog` → `m_handler?.Invoke(result)`（MessageDialog.cs:70-75）。
- **回调语义分叉**：ListSelectionDialog 仅 result!=null 才回调（ListSelectionDialog.cs:92-101）；TextBoxDialog 取消也回调 null（TextBoxDialog.cs:72-77）——handler 判空规则不同。
- **点外关闭**惯用法 `Input.Tap.HasValue && !HitTest(Input.Tap.Value)`：DownloadContentFromLinkDialog.cs:28-31 起 10+ 处沿用。
- 防重复触发：ListSelectionDialog `m_isDismissed` 一次性标志 + 选中延迟 50ms 再关（:14,82-88）。
- 强制等待：BusyDialog.Update `Input.Clear()` 吞 Back（BusyDialog.cs:34-38）；CancellableBusyDialog 同样吞 Cancel 但取消按钮走 `Progress.Cancel()`（CancellableBusyDialog.cs:73-84）。

### 3. 嵌套对话框的全局输入泄漏（社区框实战解法）

Input.Ok/Back 是全层级共享的边缘触发信号，子 ListSelectionDialog 消费按键后父框同帧再读会"一键连关两层"。CommunityFiltersDialog 的完整解法（CommunityFiltersDialog.cs:64-72,156-185）：子框存活期间跳过全局输入分支；存活判据 = 在 DialogsManager.Dialogs 中**且父链可达 RootWidget**（切屏后实例仍留在 Dialogs 但挂在死屏上，:166-185）。

### 4. 构造模式：XML 模板改装为主、全代码构建为辅

- XML 主流：`ContentManager.Get<XElement>("Dialogs/Xxx")` → `LoadContents(this,node)` → `Children.Find<T>("Xxx.部件名")` → 填数据（MessageDialog.cs:25-31 样板）。
- 全代码 4 例：EditColorDialog.cs:19-136（中心 Canvas + DialogArea 底板 + Stack 布局）、EditMemoryBankDialogAPI.cs:21-50、LoginDialog.cs:19-40、EditPaletteDialog.cs:23-61。
- 动态行样板：GameMenuDialog.AddStat（UniformSpacingPanel+3 FontTextWidget，:520-541）；Tuple<string,Action> 菜单（:475-482）。

### 5. 进度协作链（CancellableProgress → WebManager → 对话框）

CancellableBusyDialog 自建 Progress（:46）→ 传给 `WebManager.Post(...,progress,成功,失败)` → Update 每帧刷 `Completed/Total` 百分比到 SmallMessage（:70-72）→ 取消按钮 `Progress.Cancel()`，`autoHideOnCancel` 控制是否自动关。完成态把取消键文本改 "OK" 复用为确认（ViewGameLogDialog.cs:121-122）。社区新链路：`CommunityTransferProgress.Snapshot()` + SetProgress/SetCompleted/SetFailed/SetStopped 四态（CommunityDownloadDialog.cs:37-63），**终态 m_closable 才允许关闭且忽略迟到进度**（:39,74-77）。

### 6. 列表框的每帧同步细节（CommunityDownloadQueueDialog 全读）

ListPanelWidget 点击回调后无条件把选中指回点击行；"再点取消选择"用 `SelectedIndex` 每帧 Sync 覆盖（:91-96）。Provider 每帧返回新建条目实例：行数/Id 序列变了才 RebuildRows，否则 UpdateRowItems 原地换——必须同步直改 `m_taskList.m_items[i]`（ItemWidgetFactory 读它构建滚入行），否则滚入行永久旧文本（:178-193）。按钮启用 = 选中项能力位，无选中时按全行能力位 OR 聚合（:207-235）；禁用按钮不进 Update 天然无效。

### 7. CommunityPostDetailsDialog：HtmlWidget 生命周期管理（全读）

- 图片纹理由 HtmlWidget.UpdateCeases 级联释放；翻译重建时**只截 m_htmlWidget 之后的子件、不摘部件**（Children.RemoveAt 会 ChangeParent(null)→UpdateCeases→毁纹理缓存），`PreserveImagesOnRebuild=true` 让已加载图进缓存复用（:112-119）。
- 自动翻译：Task.Run + RequestId 防串号（:162-176,179-226）；标题/正文并行两请求（:289-294）；UpdateCeases 取消在途请求（:105-110）。
- # 开头链接 = 站内锚点走 `TryScrollToAnchor` 不外抛浏览器（:61-67）。

### 8. ModDetailsDialog/ModpackDetailsDialog：宿主屏委托模式（全读）

对话框持宿主 Screen 引用转发动作（ModDetailsDialog 转发 TriggerEnable/CheckModUpdate 等，:220-311）；依赖行逐条标注（快照分组 evaluate，:133-144）；"查看被禁用依赖"下钻 = 关自己开新 ModDetailsDialog（:296-303）。**ModEntity 重写 Equals（包名+版本）→ 列表删除必须 ReferenceEquals 按引用移除**（:237-239,328-334），否则同包同版撞键。ModpackDetailsDialog 用边沿轮询 busy/loading 变化恢复按钮文本（失败路径无回调，:118-127）。

### 9. GameMenuDialog：性能自诊断与统计面板（全读）

ctor 内根据 `PerformanceManager.LongTermAverageFrameTime`（<25ms 建议提画质 / >50ms 建议降画质）自动弹建议框，static 标志保证只弹一次（:8-10,26-45）。统计面板按存档版本分支：序列化版本 >"1.29" 才有完整统计与死亡记录（:222-364）。Quit = SaveProject(true,true)+DisposeProject+SwitchScreen("MainMenu")（:489-494）。

### 10. 其他实读要点

- EditWorldSeedDialog.SeedToTrueSeed：Σ(char×(1+29n))（EditWorldSeedDialog.cs:94-102）；真种子直改后字符串框清空（:50-58）。
- EditMemoryBankDialogAPI：供模组 API 的存储器重制界面，17×17 ClickTextWidget 网格全代码构建（:107-155），hex 字符串 Load/Save 与 MemoryBankData.m_hexChars 对齐（:67-105），脏标记 isclick 驱动整格重绘（:369-391）。
- ViewGameLogDialog：日志行上限 1000（:165-169）；过滤三级循环切换（:63-67）；行颜色钩子 ModifyLogColor（:149-155）；复制走 `GameLogSink.GetRecentLog(131072)`。
- SpawnDialog：出生进度框纯展示（ValueBar+季节上色，SpawnDialog.cs:13-19）。
- RemoteControlDialog：JsInterface.httpListener 开关 + 端口/密码编辑，配置落 ModsManager.SetConfig（:30-78）。
- SelectClassSubstituteDialog：模组类替换选择，选中即写 `ModsManager.SelectedClassSubstitutes[guid]` 与 XML Value 属性（:40-48）。

## 四、坑列表（新页已收录的主要条目）

1. 嵌套框同帧连关两层：全局 Input.Ok/Back 共享 → 子框存活期间跳过（CommunityFiltersDialog.cs:64-72）；存活判据要"父链可达 RootWidget"。
2. ShowDialog 异步（Dispatcher.Dispatch）：当帧 Children 找不到刚弹的框，连续弹框叠放序不保证（DialogsManager.cs:57-76）。
3. HasDialogs 把死屏挂载实例也算数：严格判定照 HasLiveListSelectionDialog 写法（CommunityFiltersDialog.cs:167-185）。
4. ListSelectionDialog 取消不回调、TextBoxDialog 取消回调 null：handler 判空规则不同（ListSelectionDialog.cs:96-99 vs TextBoxDialog.cs:72-77）。
5. BusyDialog/CancellableBusyDialog 吞 Back/Cancel：用它们当子框时父框收不到返回键（BusyDialog.cs:34-38）。
6. ListPanel 点击强制重选自身：取消选择需 SelectedIndex 每帧 Sync + 直改 m_items（CommunityDownloadQueueDialog.cs:91-96,186-193）。
7. ModEntity Equals 按值：删除必须 ReferenceEquals 按引用（ModDetailsDialog.cs:237-239）。
8. 对话框内 Task/请求要在 UpdateCeases 取消（CommunityPostDetailsDialog.cs:105-110）；HtmlWidget 重建不摘部件防纹理早释放（:112-119）。
9. MessageDialog 两按钮全空抛 InvalidOperationException（MessageDialog.cs:42-45）；多于两按钮须自建（CommunityImportOverwriteDialog 注释 :10-12）。
10. AutoHide=false 的框自己负责 Hide，否则永久遮挡（MessageDialog.cs:16,70-75）。
11. 上传日志走已死旧云盘接口（ViewGameLogDialog.cs:87-133 注释死码），勿照抄。
12. CommunityDownloadDialog 终态前不可关、终态后忽略迟到进度（CommunityDownloadDialog.cs:39,74-77）。

## 五、回写产物

- `10-SC引擎/18-Dialog对话框族.md`：新建主页（家族概览/生命周期/输入与关闭/构造模式/进度取消/坑/范例 12 条/路由 12 条）。
- `10-SC引擎/18a-Dialog明细.md`：新建明细页（57 行一行一文件 + XML 模板节）。
- 本报告：`90-原始报告/A18-Dialog报告.md`。
- 未触碰任何禁改文件；SC 源码项目零修改。
