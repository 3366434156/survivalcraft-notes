# A9 原始报告 · SC Widget 域全量深读

> 任务: 把 SC 引擎 UI Widget 域深读到全量级并回写 09/09a 页。日期: 2026-10-31。
> 源码: E:\SurvivalcraftAPIProject\Survivalcraft\Widget\（只读，未做任何修改）。

## 一、统计

- 目录构成：根目录 76 个 .cs + Community 11 + Html 9 + Markdown 4 + RichText 6 = **106 个 .cs**（此前页面按 80 计，系漏数子目录）。
- 深读方式：全文深读 32（含前轮 8：Widget/ContainerWidget/CanvasWidget/InventorySlotWidget/ClickableWidget/GameWidget/ListPanelWidget/ScrollPanelWidget，本轮 24）、节选深读 3（GamesWidget、ViewWidget、RichText/RichTextWidget）、签名级扫描 71（grep 提取类声明/继承/public 方法+行号，逐文件落到 09a）。
- 全目录覆写统计：`override void Update` 34 处、`MeasureOverride` 45+、`ArrangeOverride` 20+、`UpdateCeases` 6、`Overdraw` 2（GamesWidget、TextBoxWidget）。
- 继承根分布：直接 `: Widget` 31；`: CanvasWidget` 34；`: ContainerWidget` 12；其余经 ButtonWidget/FontTextWidget/ScrollPanelWidget/TouchInputWidget/FixedSizePanelWidget/StackPanelWidget 中转；特例 `SubsystemGameWidgets : Subsystem`（非 Widget）。

## 二、机制发现（按重要性）

### 1. WidgetInput 统一输入抽象（WidgetInput.cs，1096 行，全读）

- 与 Widget 平行的非部件类；Screen/GameWidget 持有。按 `WidgetInputDevice` 位标志（WidgetInputDevice.cs:3-25：Keyboard/Mouse/Touch/GamePad1-4/VrControllers + Multi1-4 组合位）决定启用哪些设备轮询。
- 产物字段（:58-92）：`Press`（按住中）、`Tap`（按下瞬间）、`Click`（Segment2(按下点,抬起点)，:806-820）、`SpecialClick`（右键抬起或 Shift+左键，:809-819）、`Drag`（位移 > `SettingsManager.MinimumDragDistance×Widget.GlobalScale`，:836；`DragMode` 左键=AllItems 右键=SingleItem，:838）、`Hold`+`HoldTime`（> `MinimumHoldDuration`，:841）、`Scroll`(Vector3 含滚轮刻度/120)、`ScrollX`、方向键布尔 Left/Right/Up/Down（Repeat 级）。
- `Clear()`(:671-681) 置 `m_isCleared`，此后一切 getter 返回 null/0——控件处理完输入必须调 `Clear()` 吞事件，否则同输入会继续传给后续部件（SliderWidget.cs:159-161 是标准吞法）。
- 手柄鼠标替身：PadCursorPosition 由左摇杆积分（:929-936），软光标 PowSign(1.25) 加速曲线（:852-856）；VR 触控板射线与 quad 平面求交（:995-1007）。
- 键盘转发 `IsKeyDown/Once/Repeat`（:313-356）与映射名查询 `IsKeyOrMouseDown("xxx")`（:363-390，走 SettingsManager）。

### 2. Measure/Arrange 容器差异全链（全部 9 个布局容器全读）

- 帧序不变式：ScreensManager.Update（全树 Update）→ 整树 Measure（Widget.cs:629）→ 整树 Arrange（Widget.cs:651）→ DrawWidgetsHierarchy（Widget.cs:755）。改属性放 Update 同帧生效。
- StackPanelWidget：fill 件（DesiredSize=∞）在 Measure 计数 `m_fillCount`，Arrange 平分 `ActualSize−m_fixedSize`（:55-57）；只要有 fill 件，主轴 DesiredSize=∞（:43-47）——StackPanel 嵌套 StackPanel 同轴时外层拿到 ∞，是"拉满格子"的根源。
- UniformSpacingPanelWidget：主轴 DesiredSize **恒 ∞**（:51-53），只能被外部 Size 锚定。
- FixedSizePanelWidget：忽略 ∞ 期望取有限最大（:10-15），每件摆满整格（:21-25）——可当"叠层容器"用。
- GridPanelWidget：Measure **不看 IsVisible**（:72-73），隐藏孩子仍撑宽列/行；`SetCell` 附着属性语法 `GridPanelWidget.Cell="x,y"`（:57-59）；cell 无效（越界）时摆满全格（:107）。
- TablePanelWidget（949 行全读）：TableRowWidget 行壳空实现 Measure/Arrange（:21-23）压掉 ContainerWidget 默认布局，布局权全在表容器；流水线 CollectRows(:533)→ExpandSlots(:608，rowspan 占位表+列数=自然列上限，超限 colspan 被钳)→两遍列宽（span cell 均摊到未饱和列 SpreadToColumns:753）→列下限=2 汉字宽（:146-151）→NegotiateColumns(:779-806) CSS auto 三态→高度轮(:815) rowspan 差值按行高比例摊→Arrange 摊余(:884)→Draw(:234) 单 FlatBatch(layer -1) 四层（表底/行底/cell底/格线，被 span 跨越的线段跳过）。
- **高危结论**：对 cell 直调 `Measure(Vector2(0,∞))` 会让 LabelWidget.UpdateLines 零推进死循环 OOM 崩游戏——TablePanelWidget.cs:653-656 注释点名此协议（"严禁"），FontTextWidget.cs:748-749 用断点钳 1 兜底。
- FlexPanelWidget（488 行全读）：Direction 为 Flags（`Vertical|Reverse`≡`VerticalReverse`，:10-17）；Wrap 均衡断行=贪心行数与 LineCount 取大后二分最小化最大行宽（CountLines:257 + BreakBalanced:279），行数不足拆最宽行；Grow/Shrink/Basis 存 ConditionalWeakTable（:64），XML 写 `FlexPanelWidget.Grow="1"`；摆位 ArrangeRow(:337)：grow 件**无条件吃满分配区间**（:450 growFills），shrink 按 shrink×basis 加权扣、每件下限 0；JustifyContent 六种（:384-409）；AlignItems 只在子件交叉轴对齐为 Near（enum 默认）时生效（:433-435 哨兵）——想被子容器统一对齐就不要显式写 Near。

### 3. Update 覆写全景与 base 清单（核全）

- `Widget.Update/UpdateCeases/Draw/Overdraw` 全部是空虚方法（Widget.cs:679-685）；CanvasWidget/ContainerWidget/ButtonWidget 无 Update 覆写。
- 全目录 34 处 `override void Update` 中，**带逻辑、会被子类继承的基类只有 ClickableWidget（:22-45）与 InventorySlotWidget（:201-329）**；其余 32 处均为叶子控件自有逻辑（清单见 09 页表格）。因此"子类化必须调 base.Update"仅对这两个成立；MeasureOverride 相反，InventorySlotWidget 在 base 调用**前**重置 IsDrawRequired（:407-408），自绘子类置 true 要写在 base 之后。
- InventorySlotWidget 的父是 **CanvasWidget + IDragTargetWidget**（:7），不是 ClickableWidget。
- UpdateCeases（部件因 Screen 切换/树摘除停更）覆写处：TextBoxWidget:828（关输入法）、PlayerModelWidget:166、HtmlWidget:101、MarkdownWidget:91。

### 4. 命中测试与拖放

- HitTestGlobal(:808-828) 逆序 DFS；**有谓词重载**：`HitTestGlobal(pos, w => w is IDragTargetWidget)`（DragHostWidget.cs:42 先例），可做"只命中某类部件"的定点查询。
- 拖放三件套：IDragTargetWidget（接口 DragOver/DragDrop）+ DragHostWidget（BeginDrag 把拖件改挂自己、Update 每帧定位+派发、Input.Drag 消失即 DragDrop+finally EndDrag，:39-55）+ 数据对象（InventoryDragData 等）。ViewWidget.DragDrop 把物品按屏幕射线抛进世界（:53-75，SubsystemPickables.AddPickable）；FurnitureSetItemWidget 是非物品类实现者（:24-35）。
- 拖动期间被拖件实际还挂在 DragHost 里渲染（Arrange 在指针下居中，:57-64），原位置控件自己隐藏。
- TextBoxWidget 焦点：static FocusedTextBox 全局唯一（:346）；点击框内要求**首尾两个命中都是自己**（:841-842，多行滚动区两侧不误触）；点击框外立即失焦+关输入法（:869-873）；光标点击定位=advance 半宽判定（CalculateClickedCharacterIndex:1085-1129，注释强调行进量必须与 EndOfLineDrawItem 一致否则多行深处点击漂移）。

### 5. 文本管线（FontTextWidget 811 行全读 + TextBoxWidget 2133 行全读）

- FontTextWidget 默认走**矢量字体链**（ctor 挂 FontManager.DefaultChain，:224-225，注释标明"回滚点=本行"），null 回退位图 FontBatch2D；两条路径行列表同源（UpdateLines）。
- 断行：TextWordBreak 四模式=CSS word-break 子集（:7-16）；FindLineBreakPosition(:648-663) 词边界回退+CJK 字间断点+行首/行尾禁则字表（:700-702）；BreakWord 无断点紧急强拆 fitCount-1（历史行为），Normal/KeepAll 纯溢出。
- 缓存失效模型：所有外观属性 setter 置 `m_linesSize=null`；`UpdateLines` 顶部有 ±0.1 容差短路（:705-715）。
- 装饰分层：背景/下划线 batch layer −1 垫底、删除线 layer 2 压字上（避免字形黑描边切缝，:237-242）；竖排不施装饰。
- 矢量路径 UI 缩放补偿：字形按屏上实际像素栅格化（gtScale=GlobalTransform.M11，:437-441），sink 出 quad 时除回 widget 空间；行宽必须与绘制同字号量测再 ÷gt（:445-451，"ModSettingsScreen Description 不居中根因"注释）。
- LabelWidget.Text 支持 `[Content:Name]` 与 `[Usual:Key]` 本地化（:14-30）；TextBoxWidget.Title/Description 同款（:53-85）。
- TextBoxWidget：静态 IME 接线（WINDOWS，:676-778，Ctrl+C/A/V/X 走控制字符分支）；TasksQueue 每帧任务模式（:306，光标位置同步防抖）；Draw_ 捕获全部异常只 Log（:1865-1872）防文本崩溃炸界面；底色批用 NonPremultiplied（:1889）；候选窗在 Overdraw 画并临时改 ScissorRectangle（:1775-1863）。

### 6. 复合控件模板模式（五件套）

BevelledButtonWidget/BitmapButtonWidget/CheckboxWidget/SliderWidget/LinkWidget 同构：ctor 里 `ContentManager.Get<XElement>("Widgets/XxxContents")` → `LoadChildren` → `Children.Find<T>("Xxx.Part")` 缓存内部件 → `LoadProperties(this, node)`（BevelledButtonWidget.cs:75-86 等）。外观状态机写在 MeasureOverride：按下/选中 bevel 取 −0.5×BevelSize 内凹（BevelledButtonWidget.cs:92）；禁用统一灰 (112,112,112)（:90-91、CheckboxWidget.cs:68）。这是做自定义复合控件的最短路径。

### 7. 富内容管线（Markdown/HTML→Widget 树）

- 抽象 RichContentBuilder（RichContentBuilder.cs:9）+ 两个实现：MarkdownToWidgetsBuilder（:18，Build:27）与 HtmlToWidgetsBuilder（:10，3490 行，BuildHtml:48，含 CSS 子集解析三件套）。
- 行内样式归 TextSpan；块级壳三层：HtmlBlockSizerWidget（宽/百分比）、HtmlStyleBoxWidget（盒模型/边框/圆角，Draw:41）、HtmlTransformBoxWidget（ArrangeOverride:27 施 transform 矩阵）。
- 表格：HTML 路径走 TablePanelWidget（列宽偏好 px/% 附着属性），Markdown 路径走 MarkdownTableWidget（:24，列协商 Measure:101）。图片异步：RichContentImageLoader.CreateImageBlock(:95) 先占位、加载后 RefitFrame(:76) 重适配、ResolvePendingWidths(:215) 收尾。
- RichTextWidget：dirty-flag 模式——就地改 Spans 列表内容（引用不变）必须手动 MarkLayoutDirty()（:56-58）；链接命中 FindLinkAtPoint(:706)。

### 8. 其它值得记的实现

- BevelledRectangleWidget 顶点批缓存：任何外观 setter、GlobalScale、纹理缩放变化都失效重建（:188-195,291-306）；入口 PremultiplyAlpha(:286-289) 让调用方写直色。注释明确低透明度直色在 AlphaBlend 下会近似实心（:179-182）。
- ValueBarWidget：Flash(count) 触发闪白，衰减 4/s（:203）；BarBlending=false 时值取整格（MathF.Ceiling :120-122）。
- BlockIconWidget.Value setter 每次变值用 block.GetIconViewOffset 重建视线矩阵（:20-34）；Draw 走 PrimitivesRenderer3D + DrawBlockMode.UI（:63-78）。
- GamesWidget：1/2/4 分屏全在 ArrangeOverride（:14-60）；刘海屏 DisplayCutoutInsets×FinalUiScale 注入 GuiWidget margin（:17-19）；孩子>1 时置 IsOverdrawRequired（:9-12）。
- ViewWidget.ChangeParent 强制父必须为 GameWidget 否则抛（:24-32）；分辨率三档 0.5/0.75/1（SetupScalingRenderTarget:77-80）。
- ModelWidget：UI 内 3D 模型 + 动画控制器/骨变换（AddModel:138、PlayAnimation:178、ProcessBoneHierarchy:576）；静态 ICustomModelWidgetRenderer 钩子（:134）。
- TreeViewWidget 复用 ScrollPanelWidget：覆写 CalculateScrollAreaLength=可见行数×ItemSize（:103），UpdateNodes 全量重建（:56）；EnsureVisible 由节点自己算（TreeViewNode.cs:291）。
- SubsystemGameWidgets（非 Widget）：每玩家 GameWidget 的增删与距离查询（:21-77），UpdateOrder.Views。
- Widget.cs 内嵌类：DrawContext（:11）、DrawItem（:213，IComparable 按 Layer）。
- GameWidget.cs 同文件还有 VrGuiRootWidget : CanvasWidget（:13）。

## 三、新坑列表（本轮新增，未入旧页）

1. 测文字格禁 (0,∞)：Label/RichText 作 cell 时 Measure((0,∞)) → UpdateLines 零推进死循环 OOM（TablePanelWidget.cs:653-656；FontTextWidget.cs:748-749 钳 1 兜底）。
2. RichTextWidget 就地改 Spans 内容不置脏 → 排版不刷新；必须 MarkLayoutDirty()（RichTextWidget.cs:56-58）。
3. TextBoxWidget.VerticalScroll 钳制不能放 Update：首帧 ActualSize=0 会把滚动钉死错值；必须在 ArrangeOverride（TextBoxWidget.cs:2008-2022 注释）。
4. GridPanelWidget 隐藏孩子仍撑宽列（Measure 无 IsVisible 检查，GridPanelWidget.cs:72-73）；Table/Flex 均跳过隐藏件（TablePanelWidget.cs:541、FlexPanelWidget.cs:177-181）——要"隐藏即退布局"选 Table/Flex 或先 Remove。
5. UniformSpacingPanelWidget 主轴 DesiredSize 恒 ∞（:51-53），外层不锚定尺寸就吃满。
6. StackPanel 同轴嵌套：子 Stack 有期望 ∞ 的 fill 件时外层 DesiredSize=∞（StackPanelWidget.cs:43-47）。
7. FlexPanelWidget.AlignItems 仅对"子件对齐=Near(默认)"生效，显式写过对齐的子件不受容器 AlignItems 影响（FlexPanelWidget.cs:433-435）。
8. FlexPanelWidget.Reverse 只在 Wrap 开启时生效；NoWrap 单行忽略行序反转（:210-214）。
9. Grow 分配是"使用尺寸"：grow 件无条件吃满分配区间（CSS flex-grow 语义），不按 desired 缩（FlexPanelWidget.cs:450）。
10. TextBoxWidget.MaximumLength/MaximumLinesCount setter 传负数直接抛 InvalidOperationException（:1231/:1249）。
11. TextBoxWidget.LimitScrollValue 里赋值必须写字段 m_scroll 不能走 Scroll 属性（无限递归，:1371 注释）。
12. CommunityToastWidget 是 internal sealed，外部程序集不可直接构造（CommunityToastWidget.cs:5）。
13. ClickTextWidget 无无参构造且走纯代码构造（:13），XML 标签不可用（旧页已记，本轮补构造细节）。
14. ViewWidget 挂到非 GameWidget 父直接抛 InvalidOperationException（ViewWidget.cs:24-32）。
15. BevelledRectangleWidget 低 alpha 直色观感：入口已预乘，写值只降 A 不压 RGB，否则变暗（:179-189 注释）。
16. FontTextWidget 矢量链默认开启（ctor :224-225），位图路径是回退；指定位图观感需显式 VectorFont=null。

## 四、回写清单

- 09-UI与Widget体系.md：状态行改"全读(106/106)"；目录地图补 WidgetInput/FontText/Flex/Table；新增"布局容器差异全链"（表格+Table/Flex 两小节）、"Update 覆写全景"（34 处核全）、"文本管线"、"富内容管线"、"复合控件模板模式"；命中测试节并入 WidgetInput 全链；坑表 +5；原版范例 14 条；快查路由 19 条。
- 09a-Widget明细.md：新建，106 文件逐行（十家族），每行含继承/关键成员+行号/坑。
- 未动文件：SC库 README.md、45-SC原版范例菜谱.md、00-页面模板与规则.md、姊妹库一切文件（合规）。
