# UI 与 Widget 体系

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(106/106 全文深读；A28 将 71 签名级+3 节选升为全文)

## 一句话定位

反射式 XML→Widget、两遍布局、Layer 定序绘制、WidgetInput 统一输入与 Screen/Dialog 切换的完整机制；明细逐文件另见 09a。

## 目录地图

| 符号(类/文件) | 仓库路径 | 职责 |
|---|---|---|
| `Widget` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\Widget.cs | 全部部件基类：XML 解析、布局、命中、绘制管线 |
| `ContainerWidget` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\ContainerWidget.cs | 抽象容器；对齐算术 `ArrangeChildWidgetInCell` |
| `CanvasWidget` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\CanvasWidget.cs | 绝对定位画布，`Size`/`CanvasWidget.Position` |
| `WidgetInput` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\WidgetInput.cs | 键鼠/触屏/手柄/VR 统一输入抽象（Press/Tap/Click/Drag/Hold） |
| `FontTextWidget` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\FontTextWidget.cs | 文本渲染核心：断行/CJK 禁则/位图+矢量双路径 |
| `FlexPanelWidget` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\FlexPanelWidget.cs | CSS flexbox 布局容器（Grow/Shrink/Basis 附着属性） |
| `TablePanelWidget` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\TablePanelWidget.cs | CSS table 布局容器（ColSpan/RowSpan/列协商） |
| `ScreensManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\ScreensManager.cs | 换屏、淡入淡出、每帧布局+绘制入口 |
| `Screen` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\Screen.cs | `CanvasWidget` + `Enter/Leave` 两个虚方法 |
| `DialogsManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\DialogsManager.cs | 模态框、遮罩 `CoverWidget` |
| `GameWidget` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\GameWidget.cs | 每玩家视口根：相机 + HUD(GuiWidget)；同文件含 `VrGuiRootWidget`(:13) |
| `ComponentGui` | E:\SurvivalcraftAPIProject\Survivalcraft\Component\ComponentGui.cs | HUD 归属、模态面板槽 `ModalPanelWidget` |
| `ContentManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\ContentManager.cs | XML/纹理解析与缓存（共享实例） |
| `HumanReadableConverter` | E:\SurvivalcraftAPIProject\Engine\Engine.Serialization\HumanReadableConverter.cs | 属性字符串→值转换，找不到转换器即抛 |
| `BlendState` | E:\SurvivalcraftAPIProject\Engine\Engine.Graphics\BlendState.cs | `AlphaBlend` 通道定义（预乘语义） |

## 核心机制

### 部件全量清单（106 个 .cs，逐文件明细 → 09a-Widget明细.md）

`Widget\` 目录 = 根 76 + 子目录 30（Community 11、Html 9、Markdown 4、RichText 6）。十大家族：

| 家族 | 文件数 | 代表 |
|---|---|---|
| 根与基础 | 7 | Widget、WidgetsList、WidgetInput(+Device)、WidgetAlignment |
| 布局容器 | 9 | Stack/UniformSpacing/FixedSize/Grid/Table/Flex/Scroll/List/DragHost |
| 交互 | 11 | Clickable、Button(abstract)、BevelledButton、BitmapButton、Checkbox、Slider、Link、ClickText、StarRating、TouchInput、IDragTarget |
| 文本 | 4 | FontText、Label、TextBox、LegacyTextBox |
| 富文本/富内容 | 22 | RichText 系6、Html 系9、Markdown 系4、RichContentPanel/Builder/ImageLoader |
| 图元显示 | 11 | Rectangle、BevelledRectangle、ValueBar、BusyBar、BlockIcon、Clear、ArrowLine、Panorama、Model(+Context)、MoveRose |
| HUD/视口 | 10 | GameWidget、GamesWidget、ViewWidget、VitalStats、Player、PlayerModel、Fire、Message、Motd、SubsystemGameWidgets |
| 物品与功能方块面板 | 14 | InventorySlot、Short/FullInventory、Chest、Furnace、CraftingTable、CraftingRecipe(+Slot)、SmeltingRecipe、CreativeInventory、Dispenser、Clothing、FurnitureDesign(+SetItem) |
| 手持武器 | 3 | Bow、Crossbow、Musket |
| 树形与模组/社区 | 15 | TreeView(+Node)、ModSettingItem 系、ModsManageContentItem、Community 系11 |

### XML 解析：标签名=类名，属性名=属性名

调用链：`LoadWidget` → `Activator.CreateInstance(FindTypeFromXmlName(...))` → `Children.Add` → `LoadContents`（`Widget\Widget.cs:491-503`）。

- `FindTypeFromXmlName`（`Widget.cs:797-805`）：scheme 必须 `runtime-namespace`，类型名 = `xmlns路径.标签名`；**无 xmlns 直接抛**。
- `LoadProperties`（`Widget.cs:519-585`）按**书写顺序**逐属性反射赋值；未知属性名只 `Log.Warning` 后跳过（`Widget.cs:558-562`），值转换失败才抛（`HumanReadableConverter.cs`）。
- `Style` 属性（`Widget.cs:464-466`）setter 就是 `LoadContents(null, value)`——**写在 Style 之前的内联属性会被样式覆盖**。
- `LoadChildren`（`Widget.cs:587-608`）：子元素带 `Name` 且 `Children.Find` 命中 → **合并属性而不是新建**（`Widget.cs:597-600`），给原版界面打补丁的官方机制。
- 附着属性（attached property）XML 语法即 `类型.属性`：`GridPanelWidget.Cell="x,y"`、`FlexPanelWidget.Grow="1"`、`TablePanelWidget.ColSpan="2"`——静态 Set 方法挂到 `ConditionalWeakTable`（`FlexPanelWidget.cs:80-98`、`TablePanelWidget.cs:85-103`），本体 LoadProperties 原生支持。

### 布局：两遍测量与容器差异全链

每帧顺序：`ScreensManager.Update()`（全部部件 `Update`）→ `LayoutAndDrawWidgets()`（`Managers\ScreensManager.cs:447-483`）= 整树 `Measure`（`Widget.cs:629`）→ 整树 `Arrange`（`Widget.cs:651`）→ `DrawWidgetsHierarchy`（`Widget.cs:755`）。**改属性放 Update 里，同帧生效**。设计宽 = `850/clamp(UIScale,0.5,1.2)`；`DesiredSize` 默认正无穷（`Widget.cs:483`），没实现 MeasureOverride 的部件被拉满格子。对齐算术 `ContainerWidget.ArrangeChildWidgetInCell`（`ContainerWidget.cs:68-113`）。

| 容器 | 测量（MeasureOverride 行号） | 摆放（ArrangeOverride 行号） | 关键坑 |
|---|---|---|---|
| CanvasWidget | 不量孩子，`Size`-1=自适应（`CanvasWidget.cs:33-64,7`） | 绝对定位 | — |
| StackPanelWidget | `:13-48` 固定件累加 `m_fixedSize`；期望∞的件计入 `m_fillCount` | `:50-90` fill 件平分 `ActualSize-m_fixedSize`（`:55-57`） | 有 fill 件则主轴 DesiredSize=∞ |
| UniformSpacingPanel | `:32-54` 只数可见件 `m_count` | `:14-30` 每件均分 `ActualSize/m_count` | 主轴 DesiredSize 恒 ∞（`:51-53`） |
| FixedSizePanel | `:5-19` 全孩子给满可用宽，取有限最大 | `:21-25` 每件摆满整格 | 忽略 ∞ 期望，可叠放 |
| GridPanelWidget | `:65-92` **量全部孩子不看 IsVisible**（`:73`），列宽=最大 | `:94-110` 按 cell；无效 cell 摆满全格（`:107`） | 隐藏孩子仍撑宽列；`SetCell` 附着（`:57`） |
| TablePanelWidget | `:109-188` CSS auto 列协商 | `:195-225` 行壳摆满行带 | 见下"表格容器" |
| FlexPanelWidget | `:173-207` 断行+行宽行高 | `:209-231` grow/shrink+JustifyContent | 见下"flex 容器" |
| ScrollPanelWidget | 视口量；`CalculateScrollAreaLength` 可覆写（TreeViewWidget.cs:103 先例） | 内容按滚动区摆 | 初始 `ScrollPosition=12, ScrollSpeed=-70` 自动滚 |
| ListPanelWidget | ScrollPanel 子类，条目化 | 同上 | — |

**表格容器**（TablePanelWidget，949 行）：`TableRowWidget` 行壳**空实现** Measure/Arrange（`:21-23`，压掉 ContainerWidget 默认量子件），布局权全在表容器。流水线 `MeasureOverride`（`:109`）= CollectRows（`:533`，行壳或裸子件匿名行）→ ExpandSlots（`:608`，rowspan 占位表定列）→ 两遍列宽（span cell 均摊到未饱和列 `SpreadToColumns:753`）→ 列下限=2 汉字宽（`:146-151`）→ `NegotiateColumns`（`:779-806`，CSS auto 三态：Σmax≤可用 shrink-to-fit / Σmin>可用定格 / 线性插值）→ 高度轮 `MeasureRowHeights`（`:815`，rowspan 差值按行高比例摊）。Arrange 期 `ComputeArrangedWidths`（`:884`）摊余 Stretch 差值，Draw（`:234-398`）单 FlatBatch 画四层：表底→行底→cell 底→格线（layer -1 垫底）。

**flex 容器**（FlexPanelWidget，488 行）：`Direction` 是 Flags（`Vertical|Reverse` ≡ `VerticalReverse`，`:10-17`）；断行两算法：贪心 `GreedyBreak`（`:236-254`）、均衡 `BreakBalanced`（`:279-320`，二分最小化最大行宽+拆最宽行补行数）；Grow/Shrink/Basis 存 `ConditionalWeakTable`（`:64`）；摆位 `ArrangeRow`（`:337-423`）——grow 件**无条件吃满分配区间**（`:450`），shrink 按 `shrink×basis` 加权扣；`JustifyContent` 六种分布（`:384-409`）；交叉轴对齐用 Near 哨兵：子件 Near 才吃容器 `AlignItems`（`:433-435`）。

### 绘制：Layer 决定 Z 序

`DrawContext` 五步：清空 → `CollateDrawItems`（`Widget.cs:42-93`）→ `AssignDrawItemsLayers`（`Widget.cs:98`）→ 渲染 → 回收。只有 `IsDrawRequired=true` 的部件生成绘制任务（`Widget.cs:65-70`）；层号两两比较重叠后 `+1` 再 `Sort`，O(n²) 每帧；`Widget.LayersLimit`（`Widget.cs:274`）可裁剪渲染层。`Overdraw` 第二遍绘制（`Widget.cs:685`），由 `IsOverdrawRequired`（`Widget.cs:462`）触发（`Widget.cs:79`），GamesWidget 用它画多视口装饰（`GamesWidget.cs:9-12`）。文本装饰分层先例：背景/下划线 layer -1 垫底、删除线 layer 2 压字上（避免字形黑描边切缝，`FontTextWidget.cs:240-242`）。

- **自绘部件必须在 `MeasureOverride` 里置 `IsDrawRequired = true`**（FontTextWidget 还要 `Color.A != 0` 才画，`FontTextWidget.cs:604`）。
- `InventorySlotWidget.MeasureOverride` 在 base 前**重置** `IsDrawRequired`（`InventorySlotWidget.cs:407-408`）——子类设 true 必须写在 `base.MeasureOverride()` 之后。
- `BevelledRectangleWidget` 顶点批缓存：任何外观属性、`GlobalScale`、纹理缩放变化都置 `m_cachedBatchesValid=false` 重建（`:48-158,188-195,291-306`）；入口 `PremultiplyAlpha` 统一预乘（`:286-289`）。

### 命中测试与输入抽象全链

输入单源：`WidgetInput`（非 Widget，挂在 Screen/GameWidget 上）按 `WidgetInputDevice` 位标志（`WidgetInputDevice.cs:3-25`，键/鼠/触/4 手柄/VR + 多人 Multi*）聚合出：`Press`（按住点）、`Tap`（按下瞬间）、`Click`（**Segment2(按下点,抬起点)**，`WidgetInput.cs:806-820`）、`SpecialClick`（右键或 Shift+左键）、`Drag`（超 `SettingsManager.MinimumDragDistance×GlobalScale`，`:836`）、`Hold`+`HoldTime`（超 `MinimumHoldDuration`，`:841`）、`Scroll/ScrollX`。`Clear()`（`:671-681`）后全部属性返回 null——控件读完**必须 `Input.Clear()` 吞事件**（SliderWidget.cs:159-161 先例）。键盘走 `IsKeyDown/Once/Repeat` 转发（`:313-356`）。

命中判定：`HitTestGlobal(point)`（`Widget.cs:808-828`）按 `Children` **逆序**深度优先，第一个命中即返；带谓词重载 `HitTestGlobal(pos, w => w is IDragTargetWidget)`（`DragHostWidget.cs:42` 先例）。父 `IsHitTestVisible=false` 只排除自己不屏蔽子级。构造默认 `IsHitTestVisible=false` 的部件（已核）：RectangleWidget、BevelledRectangleWidget、FontTextWidget、ClearWidget、BlockIconWidget、ValueBarWidget、BusyBarWidget、ArrowLineWidget、DragHostWidget、ModelWidget、PlayerModelWidget、LinkWidget 外壳、图元容器。**子部件抢命中**：任一 `IsHitTestVisible=true` 的子件被命中时父 ClickableWidget/InventorySlotWidget 收不到点击。

消费者速查：Slider 拖 tab+吞输入（`SliderWidget.cs:127-162`）；ClickText 点击回调（`ClickTextWidget.cs:54-60`）；TouchInputWidget 单指手势 Tap/Hold/Move+`Radius` 限位（`TouchInputWidget.cs:38-91`）；DragHost 拖放（见下）；TextBox 焦点管理（见下）。

**拖放机制**：`IDragTargetWidget.DragOver/DragDrop`（`IDragTargetWidget.cs:2-6`）+ `DragHostWidget`（`:17-55`）——`BeginDrag` 把拖件改挂到 DragHost；Update 每帧谓词命中目标，`Input.Drag` 有值→`DragOver`，无值→`DragDrop` 后 **finally EndDrag**；`ArrangeOverride` 把拖件摆在指针下居中（`:57-64`）。`ViewWidget.DragDrop` 把物品抛进世界（`ViewWidget.cs:53-75`，SubsystemPickables）；`InventorySlotWidget`、`FurnitureSetItemWidget`（`:24-35`）实现该接口。

**文本框焦点**：`static TextBoxWidget.FocusedTextBox` 全局唯一焦点（`TextBoxWidget.cs:346`）；点击框内（首尾两 hit 都是自己，`:841-842`）→`HasFocus=true`+弹输入法，点击框外→失焦（`:869-873`）；光标点击定位=半字宽判定（`CalculateClickedCharacterIndex:1085-1129`）；Tab 切换递归收集全树 TextBox（`:1030-1040,1066-1083`）。

### Update 覆写全景（base 调用清单核全）

`Widget.Update/UpdateCeases/Draw/Overdraw` 全是**空虚方法**（`Widget.cs:679-685`）；`CanvasWidget`/`ContainerWidget`/`ButtonWidget` 无 Update 覆写。全目录 `override void Update` 共 34 处，**带逻辑的基类只有两个**：

| 基类 | 依据 |
|---|---|
| 子类化 `ClickableWidget`/`InventorySlotWidget` 必调 `base.Update()` | `ClickableWidget.cs:22-45`（置 IsClicked/IsTapped）；`InventorySlotWidget.cs:201-329`（点击/长按/拖拽全部） |
| 其余 32 处 Update 全是叶子控件自有逻辑，无 base 链 | Slider :127、TouchInput :38、DragHost :39、Link :102、ClickText :54、Message :72、Motd :32、Chest :38、Furnace :56、CraftingTable :46、Dispenser :53、CreativeInventory :77、VitalStats :69、Player :25、Fire :23、Clothing :70、Bow :40、Crossbow :44、Musket :40、FurnitureDesign :224、Model :530、PlayerModel :78、MoveRose :31、StarRating :28、RichText :266、LegacyTextBox :139、TextBox :834、Checkbox :60、CommunityToast :88 等 |
| `MeasureOverride` 相反：部分基类结尾重置 IsDrawRequired，`IsDrawRequired=true` 要写在 base 之后 | `InventorySlotWidget.cs:407-408`、`TextBoxWidget.MeasureOverride:1996`（先设 DesiredSize 再 AutoSize 重算） |
| `UpdateCeases`（部件停更时机）覆写要处理输入法/动画收尾 | `TextBoxWidget.cs:828-832`、`PlayerModelWidget.cs:166`、`HtmlWidget.cs:101`、`MarkdownWidget.cs:91` |

### 文本管线（FontTextWidget → Label/RichText）

`FontTextWidget`（811 行）双路径：**默认矢量链**（ctor 挂 `FontManager.DefaultChain`，`FontTextWidget.cs:224-225`，回滚点=该行），null 时回退位图 `FontBatch2D`。断行 `UpdateLines`（`:704-809`）带缓存（`m_linesSize`，任何属性 setter 置 null）；`TextWordBreak`（`:7-16`）= CSS word-break 子集，`FindLineBreakPosition`（`:648-663`）词边界回退+CJK 禁则（`CanBreakBeforeCjk:685`、行首/行尾禁则字表 `:700-702`）；可用宽≈0 时断点钳 1 防零推进死循环（`:748-749`，OOM 根因）。矢量路径按屏上实际像素栅格化再除回 widget 空间（GlobalTransform 缩放补偿，`:437-441`），行宽必须与绘制同字号量测（`:445-451`，UI 缩放≠1 时 Center/Right 锚点偏移根因）。`LabelWidget.Text` setter 支持 `[Content:Name]`/`[Usual:Key]` 本地化（`LabelWidget.cs:14-30`）。`RichTextWidget` 多 span 单批绘制，排版委托 `RichTextLayout.Layout`（`RichTextLayout.cs:67-330`），就地改 `Spans` 列表内容必须手动 `MarkLayoutDirty()`（`RichTextWidget.cs:56-58`）；链接命中 `FindLinkAtPoint`（`:706`）。

### 富内容管线（Markdown/HTML → Widget 树）

`RichContentBuilder`（抽象，`RichContentBuilder.cs:9`）两个实现：`MarkdownToWidgetsBuilder`（`MarkdownToWidgetsBuilder.cs:18`，`Build(markdown):27` 产出 StackPanelWidget 树）与 `HtmlToWidgetsBuilder`（`HtmlToWidgetsBuilder.cs:10`，3490 行，`BuildHtml:48`，内嵌 CSS 子集：CssStyleParser/CssColorParser/CssTransformParser）。行内样式归 `TextSpan`（`MarkdownSpanParser:72`/`HtmlSpanParser:14`）；块级用 `HtmlBlockSizerWidget`（百分比/显式尺寸壳）、`HtmlStyleBoxWidget`（margin/padding/边框/圆角壳）、`HtmlTransformBoxWidget`（css transform 壳，`ArrangeOverride:27` 施加矩阵）；表格走 `TablePanelWidget`（HTML 路径）或 `MarkdownTableWidget`（`MarkdownTableWidget.cs:24`，TablePanelWidget 底座列协商+超宽切横向滚动 `Measure:101`）；图片异步 `RichContentImageLoader`（`RichContentImageLoader.cs:20`，`CreateImageBlock:95` 占位→`RefitFrame:76` 应用态重适配→`ResolvePendingWidths:215`）。入口控件 `MarkdownWidget`/`HtmlWidget`（`HtmlWidget.cs:10`，`TryScrollToAnchor:112`）。

### Screens 体系

- `Screen : CanvasWidget`，仅 `Enter(object[])`/`Leave()`（`Screen\Screen.cs:2-5`）。原版 41 个界面在 `LoadingScreen.InitScreens`（`Screen\LoadingScreen.cs:609-651`）注册；`LoadingScreen.Enter` 每次先把字典里**除自己外的全部 Screen 移除**（`:673-683`）——注册动作应塞进 `OnLoadingFinished`。
- 切屏：`ScreensManager.SwitchScreen`（`ScreensManager.cs:51`）先发 `OnSwitchScreen` 钩子；三阶段动画（`:273-331`）跨 0.5 帧 `Leave()→移除→Insert(0,新屏)→Enter()`（`:305-321`）；动画期间 `RootWidget.IsUpdateEnabled=false`。
- 界面 XML 在各 Screen 构造函数 `ContentManager.Get<XElement>("Screens/Xxx")` → `LoadContents(this, node)`；`ContentManager` 缓存同一 XElement 实例，改它=全局持久。
- Dialog：`ShowDialog` 先派 `OnShowDialog` 钩子再挂树，`CoverWidget` 遮罩 (0,0,0,192) 先挂（`Managers\DialogsManager.cs:46-77`）。

### 注入原版界面的方式（时机钩子）

| 钩子 | 派发点 | 能做什么 |
|---|---|---|
| `OnWidgetConstruct(ref Widget)` | `Widget.cs:495-501` | 换实例；此时 Name 尚未赋值 |
| `OnWidgetContentsLoaded(Widget)` | `Widget.cs:509-515` | 按名字判断+加子部件的正确位置 |
| `BeforeWidgetUpdate` / `AfterWidgetUpdate` | `Widget.cs:849-855` / `:857-863` | 每帧每部件；清 IsClicked 拦截按钮 |
| `OnMainMenuScreenCreated` | `Screen\MainMenuScreen.cs:46-52` | 直接往左右底栏 AddChildren |
| `ManageCameras(GameWidget)` | `Widget\GameWidget.cs:77-84` | 相机之外也是塞 HUD 的合法窗口 |
| `OnModalPanelWidgetSet` | `Component\ComponentGui.cs:169-174` | 工作台/箱子面板被设置时 |
| `ICustomModelWidgetRenderer`（静态） | `Widget\ModelWidget.cs:134` | UI 内 3D 模型自渲染接管 |

Name 合并打补丁：补丁节点带 `Name="原版部件名"`（`WidgetsList.cs:128-145` 递归 Find），叠加属性。

### 预乘 alpha

`BlendState.AlphaBlend` = `One / InverseSourceAlpha`（`Engine\Engine.Graphics\BlendState.cs:27-33`），**不做预乘**：自绘顶点色 RGB 必须先乘 A。引擎内两处实证：`BevelledRectangleWidget.PremultiplyAlpha`（`BevelledRectangleWidget.cs:286-289`，调用方给直色、控件内预乘）；`TextBoxWidget.Draw_` 反例——其底色批直接用 `BlendState.NonPremultiplied`（`TextBoxWidget.cs:1889`），因为选区/光标矩形按直色语义画。UI 管线默认仍是 AlphaBlend。

### 复合控件模板模式（自装配子件）

BevelledButton/BitmapButton/Checkbox/Slider/Link 五件共用同一模式（照抄模板）：ctor 里 `ContentManager.Get<XElement>("Widgets/XxxContents")` → `LoadChildren(this, node)` → `Children.Find<T>("Xxx.Part")` 缓存内部件引用 → `LoadProperties(this, node)`（`BevelledButtonWidget.cs:75-86`、`CheckboxWidget.cs:49-58`、`SliderWidget.cs:92-100`、`LinkWidget.cs:93-100`）。外观状态机写在 `MeasureOverride`：按下/选中时 bevel 取负内凹（`BevelledButtonWidget.cs:92`）、禁用统一灰 (112,112,112)（`:90-91`、`CheckboxWidget.cs:68`）。该模式子件布局仍走 XML，改装点=Find 后的引用。

## 坑与对策

- **属性名拼错**：只 `Log.Warning`（`Widget.cs:558-562`），界面静默用默认值 → 照日志类型全名查属性归属。
- **枚举/布尔值写错**：枚举大小写敏感、bool 只认 True/False、Vector2 用逗号 → 值错是抛异常，整个界面建不出来。
- **abstract 当标签**：`<ButtonWidget>`、`<ContainerWidget>`、`<ClickTextWidget>`（无无参构造）抛异常 → 用 BevelledButtonWidget/BitmapButtonWidget/CanvasWidget。
- **子部件抢命中**：父 ClickableWidget/InventorySlotWidget 点不动 → 查子树里谁 `IsHitTestVisible=true`（图元类默认 false，容器默认 true）。
- **自绘不显示**：没置 `IsDrawRequired`；或设了但被 `base.MeasureOverride` 重置（InventorySlotWidget 系）。
- **测文字格不许 (0,∞)**：对 Label/RichText cell 直调 `Measure(Vector2(0,∞))` → `UpdateLines` 零推进死循环 OOM 崩游戏（`TablePanelWidget.cs:653-656` 注释、`FontTextWidget.cs:748-749` 钳 1 防护）→ 传 ∞ 或钳最小宽。
- **RichTextWidget 就地改 Spans 不生效**：列表引用没变引擎不感知 → 手动 `MarkLayoutDirty()`（`RichTextWidget.cs:56-58`）。
- **TextBoxWidget.VerticalScroll 在 Update 里钳会钉死**：首帧 ActualSize=0 → 钳制必须在 ArrangeOverride（`TextBoxWidget.cs:2008-2022` 注释）。
- **加的 Screen 消失**：`LoadingScreen.Enter` 清字典（`LoadingScreen.cs:673-683`）→ 在 `OnLoadingFinished` 排动作注册。
- **切语言界面重建**：`LanguageControl.ChangeLanguage` 反射 new 全部 Screen → 自定义 Screen 必须有无参构造，注入代码必须可重入。
- **Style 覆盖内联**：`Style=` 之前的同名属性被样式盖掉 → 要生效的属性写在 Style 之后。
- **Grid 隐藏孩子撑宽列**：GridPanelWidget.MeasureOverride 不看 IsVisible（`GridPanelWidget.cs:73`）→ 想让隐藏件退出布局要 Remove 或用 Table/Flex（两者都跳过隐藏件，`TablePanelWidget.cs:541`、`FlexPanelWidget.cs:177-181`）。
- **持有 Texture2D 的部件泄漏纹理**：widget 树无 Dispose 级联，异步加载的纹理句柄会累积 → 释放放 `UpdateCeases`（被移出更新树时级联调用），代际计数使晚到回调就地销毁（`HtmlWidget.cs:101-106`、`MarkdownWidget.cs:91-96`、`RichContentImageLoader.cs:186-211`）。
- **TreeViewWidget 改树不生效**：行重建的脏标记在 **Draw** 期消费（`TreeViewWidget.cs:48-54`）→ AddRoot/Clear 后下一帧才显示；节点增删改不自动置脏，须手动 `m_widgetsDirty=true`（`CommunityTreeViewWidget.cs:66-68` 封装先例）。
- **UniformSpacingPanel 竖排放进竖排 StackPanel 崩整页**：主轴 DesiredSize=∞ 污染上层期望、arrange 经 layoutTransform 算 NaN（`ModSettingItemWidget.cs:272-274` 注释实证）→ 均分行容器一律 Horizontal。

## 原版范例

| 我要做… | 照抄哪里 |
|---|---|
| 组合控件（按钮+字+图） | `BevelledButtonWidget.cs:75-86`——XML 模板装配+Find 改装+LoadProperties，复合控件标准流程 |
| 属性失效缓存的复杂自绘 | `BevelledRectangleWidget.cs:178-306`——cached batches + 属性 setter 置脏 + GlobalScale 失效 |
| 拖放目标与拖动宿主 | `DragHostWidget.cs:17-55` + `FurnitureSetItemWidget.cs:24-35`——BeginDrag/DragOver/DragDrop/finally EndDrag 全链 |
| 全局输入消费（防穿透） | `SliderWidget.cs:127-162`——HitTestGlobal==子件判定 + `Input.Clear()` 吞事件 |
| 带焦点的文本输入框 | `TextBoxWidget.cs:834-1062`——Focus 生命周期/TasksQueue 每帧任务/快捷键全集 |
| 血条式分格值条 | `ValueBarWidget.cs:85-211`——BarBlending/HalfBars/Flash 渐灭，值条样板 |
| 均衡断行（二分最小化最大行宽） | `FlexPanelWidget.cs:257-320`——CountLines 二分+拆最宽行补行数 |
| CSS auto 表格列协商 | `TablePanelWidget.cs:779-806`——min/max/插值三态，span 均摊 `:753-773` |
| Markdown/HTML 渲染成界面 | `MarkdownToWidgetsBuilder.cs:27-34` 起步，复杂照 `HtmlToWidgetsBuilder.cs:48` |
| UI 里挂 3D 模型+动画 | `ModelWidget.cs:136-243`——AddModel/PlayAnimation/GetBoneTransform，骨变换 `:576` |
| 分屏/刘海屏排布 | `GamesWidget.cs:14-60`——DisplayCutoutInsets×FinalUiScale + LayoutTransform 缩放 |
| 触摸手势解析（Tap/Hold/Move） | `TouchInputWidget.cs:38-91`——单指跟踪+Radius 限位输出 TouchInput |
| 树形列表（滚动面板复用） | `TreeViewWidget.cs:56-105`——覆写 CalculateScrollAreaLength+UpdateNodes 重建行 |
| 物品格拖抛进世界 | `ViewWidget.cs:53-75`——DragDrop 里算屏幕射线给 SubsystemPickables |
| UI 内异步加载图片（占位→下载→上屏） | `RichContentImageLoader.cs:95-380`——占位 frame+后台下载解码+Dispatcher 回主线程+代际守卫防晚到回调+宽未定挂起 `ResolvePendingWidths` 收口 |
| 外部推值与用户操作双向同步（防回环） | `ModSettingItemWidget.cs:88-108`——CommitValue 查 `m_applyingExternalValue` 守卫 + ApplyExternalValueCore 入口类型预检 |

## 快查路由

| 我想… | 去/看 |
|---|---|
| 查某部件有哪些 XML 属性 | `09a-Widget明细.md` 定位文件 → 该 .cs 的 public 属性；拼错看日志 `Property not found` |
| 找某家族有哪些控件可选 | 本页"部件全量清单"表 → 09a 对应家族节 |
| 让自绘部件画出来 / 定位 Z 序 | `IsDrawRequired`（Widget.cs:65-70）与 Layer 排序（Widget.cs:98）；`Overdraw`（Widget.cs:685） |
| 写自定义布局容器 | 照 Stack/FixedSize 最小实现 + `ArrangeChildWidgetInCell`（ContainerWidget.cs:68-113）；复杂照 Flex/Table |
| 弹性/换行/比例分配 | FlexPanelWidget（Grow/Shrink/Basis，FlexPanelWidget.cs:337） |
| 表格/跨行跨列/单元格底色 | TablePanelWidget（ColSpan/RowSpan/CellBackground 附着属性，:109） |
| 读输入（点击/拖/长按/滚轮/手柄/VR） | `WidgetInput.cs:58-92` 字段表；设备开关 `WidgetInputDevice.cs:3`；吞事件 `Clear()`（:671） |
| 做拖放 | `IDragTargetWidget` + `DragHostWidget.BeginDrag`（:17）；物品拖抛看 ViewWidget.cs:53 |
| 做文本输入/输入法 | `TextBoxWidget.cs`（Focus :346、Update :834、IME 静态接线 :676）；旧版 LegacyTextBoxWidget 只读兼容 |
| 富文本/Markdown/HTML 显示 | `MarkdownWidget`/`HtmlWidget` 入口；span 级样式 `TextSpan`；管线见"富内容管线"节 |
| 给主菜单/HUD 加部件 | `OnMainMenuScreenCreated`（MainMenuScreen.cs:46）或 `ManageCameras`（GameWidget.cs:77） |
| 改原版界面某个控件 | Name 合并机制（Widget.cs:587-608）+ `ContentManager.Get<XElement>` 共享缓存 |
| 界面整体切换/弹窗 | `ScreensManager.cs:51`（切屏）、`DialogsManager.cs:46`（弹窗） |
| UI 里显示方块/模型/生物 | `BlockIconWidget.cs:63`（3D 方块图标）、`ModelWidget.cs:245`（模型+动画） |
| 半透明发白/发光 | BlendState.cs:27 预乘 alpha，顶点色 RGB×A；控件内直色入口照 BevelledRectangleWidget.cs:286 |
| 物品格交互/拖放规则 | `InventorySlotWidget.cs:201-329`（Update）与 `:569`（HandleDragDrop） |
| 文字换行/CJK 禁则/省略号 | `FontTextWidget.cs:648-702`（FindLineBreakPosition/禁则表）、WordBreak 属性 |
| 界面进不去/白屏 | 检查 xmlns、abstract 标签、值转换异常；另见 12-ModAPI与加载链.md 的失败出口 |
