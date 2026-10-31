# UI 与 Widget 体系

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 抽样(深读8/80，Widget目录全ls)

## 一句话定位

反射式 XML→Widget、两遍布局、Layer 定序绘制、逆序命中测试与 Screen/Dialog 切换的完整机制。

## 目录地图

| 符号(类/文件) | 绝对路径 | 职责 |
|---|---|---|
| `Widget` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\Widget.cs | 全部部件基类：XML 解析、布局、命中、绘制管线 |
| `ContainerWidget` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\ContainerWidget.cs | 抽象容器；对齐算术 `ArrangeChildWidgetInCell` |
| `CanvasWidget` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\CanvasWidget.cs | 绝对定位画布，`Size`/`CanvasWidget.Position` |
| `ScreensManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\ScreensManager.cs | 换屏、淡入淡出、每帧布局+绘制入口 |
| `Screen` | E:\SurvivalcraftAPIProject\Survivalcraft\Screen\Screen.cs | `CanvasWidget` + `Enter/Leave` 两个虚方法 |
| `DialogsManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\DialogsManager.cs | 模态框、遮罩 `CoverWidget` |
| `GameWidget` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\GameWidget.cs | 每玩家视口根：相机 + HUD(GuiWidget) |
| `ComponentGui` | E:\SurvivalcraftAPIProject\Survivalcraft\Component\ComponentGui.cs | HUD 归属、模态面板槽 `ModalPanelWidget` |
| `WidgetsList` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\WidgetsList.cs | `Children` 实现；`Find` 深度优先 |
| `ContentManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\ContentManager.cs | XML/纹理解析与缓存（共享实例） |
| `HumanReadableConverter` | E:\SurvivalcraftAPIProject\Engine\Engine.Serialization\HumanReadableConverter.cs | 属性字符串→值转换，找不到转换器即抛 |
| `InventorySlotWidget` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\InventorySlotWidget.cs | 物品格：交互、拖放全部内联在 `Update/MeasureOverride` |
| `ClickableWidget` | E:\SurvivalcraftAPIProject\Survivalcraft\Widget\ClickableWidget.cs | 最小可点部件，`Update` 轮询置位 |
| `BlendState` | E:\SurvivalcraftAPIProject\Engine\Engine.Graphics\BlendState.cs | `AlphaBlend` 通道定义（预乘语义） |

## 核心机制

### 部件清单（抽样：80 个文件，深读 8 个）

`Survivalcraft\Widget\` 共 80 文件，深读：Widget、ContainerWidget、CanvasWidget、InventorySlotWidget、ClickableWidget、GameWidget、ListPanelWidget(读)、ScrollPanelWidget(读)；其余按用途分组（未深读，定义行号见各文件第 4~8 行的 class 声明）：

| 组 | 部件 | 用途 / XML 常用属性 |
|---|---|---|
| 容器 | CanvasWidget(561次)、StackPanelWidget(381)、UniformSpacingPanelWidget(110)、GridPanelWidget(19)、ScrollPanelWidget(28)、ListPanelWidget(17)、FixedSizePanelWidget、DragHostWidget | `Size`(Vector2 逗号分隔)、`Direction`(默认 Horizontal)、`ColumnsCount`+`GridPanelWidget.Cell="x,y"`、`ScrollPosition`/`ScrollSpeed` |
| 按钮类 | BevelledButtonWidget(276)、BitmapButtonWidget(15)、CheckboxWidget(21)、SliderWidget(39)、LinkWidget(18) | `Text`、`Size`、`Style="{Styles/ButtonStyle_*}"`、`IsChecked`、`MinValue/MaxValue/Value` |
| 文本 | LabelWidget(538)、TextBoxWidget(42)、FontTextWidget | `Text`、`FontScale`、`Color`、`WordWrap`、`MaximumLength` |
| 图元 | RectangleWidget(67)、BevelledRectangleWidget(132)、PanoramaWidget(35)、ValueBarWidget(13)、BusyBarWidget | `Size`、`Subtexture="{Textures/Atlas/x}"`、`FillColor/OutlineColor`、`BevelSize` |
| 游戏 | BlockIconWidget(6)、InventorySlotWidget(10)、ShortInventoryWidget、VitalStatsWidget、ChestWidget/FurnaceWidget | `Value`+`Contents`+`Light`、`HideBlockIcon` 等 6 个 Hide*、`ProcessingOnly` |
| 禁用标签 | ButtonWidget/ContainerWidget(abstract)、ClickTextWidget(无无参构造) | 当 XML 标签会直接抛 |

### XML 解析：标签名=类名，属性名=属性名

调用链：`LoadWidget` → `Activator.CreateInstance(FindTypeFromXmlName(...))` → `Children.Add` → `LoadContents`（`Widget\Widget.cs:491-503`）。

- `FindTypeFromXmlName`（`Widget.cs:797-805`）：scheme 必须 `runtime-namespace`，类型名 = `xmlns路径.标签名`（即 `Game.LabelWidget`）；**无 xmlns 直接抛**。
- `LoadProperties`（`Widget.cs:519-585`）按**书写顺序**逐属性反射赋值；未知属性名只 `Log.Warning` 后跳过（`Widget.cs:558-562`），值转换失败才抛（`Engine\Engine.Serialization\HumanReadableConverter.cs`）。
- `Style` 属性（`Widget.cs:464-466`）只写、setter 就是 `LoadContents(null, value)`——在 `Style=` 那一刻重入解析，**写在 Style 之前的内联属性会被样式覆盖**。
- `LoadChildren`（`Widget.cs:587-608`）：子元素带 `Name` 且 `Children.Find` 命中已有实例 → **合并属性而不是新建**（`Widget.cs:597-600`），这是给原版界面打补丁的官方机制。
- 内容引用 `{Textures/Atlas/Tick}` 取不到只 `Log.Error`，属性保持默认。

### 布局：两遍测量

每帧顺序：`ScreensManager.Update()`（先跑全部部件 `Update`）→ `LayoutAndDrawWidgets()`（`Managers\ScreensManager.cs:447-483`）= 整树 `Measure`（`Widget.cs:629`）→ 整树 `Arrange`（`Widget.cs:651`）→ `DrawWidgetsHierarchy`（`Widget.cs:755`）。**改属性要放在 Update 里，同帧生效**。

- 设计宽 = `850 / clamp(UIScale,0.5,1.2)`，Y 向下；像素↔UI 单位乘 `ScreensManager.FinalUiScale`（`ScreensManager.cs:451-467`）。
- 对齐：`ContainerWidget.ArrangeChildWidgetInCell`（`ContainerWidget.cs:68-113`）——Near 左上贴 margin；Center 居中**忽略 margin**；Far 只吃远端 margin；Stretch 吃格子减 margin。`DesiredSize` 默认正无穷（`Widget.cs:483`），无穷被夹成整格 → 没实现 MeasureOverride 的部件会被拉满。
- 容器差异：CanvasWidget 绝对定位（`CanvasWidget.cs:33-64`，`Size` 默认 -1=自适应，`CanvasWidget.cs:7`）；StackPanel 沿 Direction 累加、隐藏孩子跳过；Grid 列宽取最大、隐藏孩子**仍撑宽**；ScrollPanel 不是栈（每孩子摆同一格，内容长取 Max），初始 `ScrollPosition=12, ScrollSpeed=-70` 会自动滚。

### 绘制：Layer 决定 Z 序

`DrawContext` 五步：清空 → `CollateDrawItems`（`Widget.cs:42-93`）→ `AssignDrawItemsLayers`（`Widget.cs:98`）→ 渲染 → 回收。只有 `IsDrawRequired=true` 的部件生成绘制任务（`Widget.cs:65-70`）；层号两两比较重叠后 `+1` 再 `Sort`，O(n²) 每帧；`Widget.LayersLimit`（`Widget.cs:274`）设 ≥0 可裁剪渲染层（排错开关）。

- **自绘部件必须在 `MeasureOverride` 里置 `IsDrawRequired = true`**，否则永远不画。
- `InventorySlotWidget.MeasureOverride` 在 base 调用**前**把 `IsDrawRequired` 重置为 `m_inventoryDragData != null`（`InventorySlotWidget.cs:407-408`）——子类设 true 必须写在 `base.MeasureOverride()` 之后，否则被抹掉。

### 命中测试：倒序、命中即返

`HitTestGlobal`（`Widget.cs:808-828`）按 `Children` **逆序**深度优先，第一个满足条件的即返回；父 `IsHitTestVisible=false` 只排除自己不屏蔽子级。`ClickableWidget.Update` 与 `InventorySlotWidget.m_focus` 都用 `HitTestGlobal(point) == this` 判定 → 任一子部件可命中，父部件永远收不到点击。构造函数默认 `IsHitTestVisible=false` 的部件（已核）：RectangleWidget、BevelledRectangleWidget、FontTextWidget、ClearWidget、BlockIconWidget、ValueBarWidget、BusyBarWidget、ArrowLineWidget、DragHostWidget、ModelWidget、PlayerModelWidget。

### Update 覆写与 base

| 情形 | 依据 |
|---|---|
| 子类化 `ClickableWidget` / `InventorySlotWidget` 时漏调 `base.Update()` = 交互机被拔掉 | `ClickableWidget.Update` 置 IsClicked 等（`ClickableWidget.cs:22-45`）；`InventorySlotWidget.Update` 装着点击/长按/拖拽全部逻辑（`InventorySlotWidget.cs:201-329`） |
| `Widget`/`CanvasWidget`/`ButtonWidget`/`StackPanelWidget` 没有 Update 覆写，base 可省 | grep `override void Update` 计数 0 |
| `MeasureOverride` 相反：基类结尾会重置 IsDrawRequired，`IsDrawRequired=true` 要写在 base 之后 | `InventorySlotWidget.cs:407-408` |

### Screens 体系

- `Screen : CanvasWidget`，仅 `Enter(object[])`/`Leave()`（`Screen\Screen.cs:2-5`）。原版 41 个界面在加载队列里注册：`LoadingScreen.InitScreens`（`Screen\LoadingScreen.cs:609-651`）逐个 `AddScreen`；`LoadingScreen.Enter` 每次先把字典里**除自己外的全部 Screen 移除**（`:673-683`）——模组在 `__ModInitialize` 里 AddScreen 进一次加载页就没了，注册动作应塞进 `OnLoadingFinished`。
- 切屏：`ScreensManager.SwitchScreen`（`ScreensManager.cs:51`）先发 `OnSwitchScreen` 钩子（可换目标）；三阶段动画 `UpdateAnimation`（`:273-331`）：Factor<0.5 淡出旧屏，跨 0.5 那一帧才 `Leave()→移除→Insert(0,新屏)→Enter()`（`:305-321`），>0.5 淡入。动画期间 `RootWidget.IsUpdateEnabled=false`，整树不更新。
- 界面 XML 读取在各 Screen 构造函数：`ContentManager.Get<XElement>("Screens/Xxx")` → `LoadContents(this, node)`。`ContentManager` 缓存同一 XElement 实例，改它=全局持久。
- Dialog：`Dialog` 只是 CanvasWidget+IsHitTestVisible+Size=∞；`ShowDialog` 先派 `OnShowDialog` 钩子再 `Dispatcher.Dispatch` 挂树，`CoverWidget` 遮罩 (0,0,0,192) 先于对话框挂入（`Managers\DialogsManager.cs:46-77`）。

### 注入原版界面的方式（时机钩子）

| 钩子 | 派发点 | 能做什么 |
|---|---|---|
| `OnWidgetConstruct(ref Widget)` | `Widget.cs:495-501` | 换实例；此时 Name 尚未赋值 |
| `OnWidgetContentsLoaded(Widget)` | `Widget.cs:509-515` | 按名字判断+加子部件的正确位置 |
| `BeforeWidgetUpdate` / `AfterWidgetUpdate` | `Widget.cs:849-855` / `:857-863` | 每帧每部件；清 IsClicked 拦截按钮 |
| `OnMainMenuScreenCreated` | `Screen\MainMenuScreen.cs:46-52` | 直接往左右底栏 AddChildren |
| `ManageCameras(GameWidget)` | `Widget\GameWidget.cs:77-84` | 相机之外也是塞 HUD 的合法窗口 |
| `OnModalPanelWidgetSet` | `Component\ComponentGui.cs:169-174` | 工作台/箱子面板被设置时 |

Name 合并打补丁：补丁节点带 `Name="原版部件名"`（`Children.Find` 递归匹配，`WidgetsList.cs`），叠加属性；同名劫持 `Children.Insert(0, ...)` 可抢原版按钮的 `Find`（风险大）。

### 预乘 alpha

`BlendState.AlphaBlend` = Color/Alpha 双通道 `One / InverseSourceAlpha`（`Engine\Engine.Graphics\BlendState.cs:27-33`），**不做预乘**：自绘顶点色 RGB 必须先乘 A，否则半透明浅色变加色发光。引擎另备 `NonPremultiplied`（`:35-41`）但 UI 管线用的是 AlphaBlend。

## 坑与对策

- **属性名拼错**：只 `Log.Warning("Property \"X\" not found in widget of type \"Y\".")`（`Widget.cs:558-562`），界面静默用默认值 → 照日志类型全名查属性归属。
- **枚举/布尔值写错**：枚举大小写敏感（`HorizontalAlignment="center"` 抛）、bool 只认 True/False、Vector2 用逗号 → 值错是抛异常，整个界面建不出来。
- **abstract 当标签**：`<ButtonWidget>`、`<ContainerWidget>`、`<ClickTextWidget>` 抛异常 → 用 BevelledButtonWidget/BitmapButtonWidget/CanvasWidget。
- **子部件抢命中**：父 ClickableWidget/InventorySlotWidget 点不动 → 查子树里谁 `IsHitTestVisible` 为 true（图元类默认 false，容器默认 true）。
- **自绘不显示**：没置 `IsDrawRequired`；或设了但被 `base.MeasureOverride` 重置（InventorySlotWidget 系）。
- **加的 Screen 消失**：`LoadingScreen.Enter` 清字典（`LoadingScreen.cs:673-683`）→ 在 `OnLoadingFinished` 排动作注册。
- **切语言界面重建**：`LanguageControl.ChangeLanguage` 反射 new 全部 Screen → 自定义 Screen 必须有无参构造，注入代码必须可重入。
- **Style 覆盖内联**：`Style=` 之前的同名属性被样式盖掉 → 要生效的属性写在 Style 之后。

## 快查路由

| 我想… | 去/看 |
|---|---|
| 查某部件有哪些 XML 属性 | 对应 `E:\SurvivalcraftAPIProject\Survivalcraft\Widget\<名>.cs` 的 public 属性；拿不准看日志 `Property not found` 的类型全名 |
| 让自绘部件画出来 / 定位 Z 序 | `IsDrawRequired`（Widget.cs:65-70）与 Layer 排序（Widget.cs:98）；`Widget.LayersLimit` 调试 |
| 给主菜单/HUD 加部件 | `OnMainMenuScreenCreated`（MainMenuScreen.cs:46）或 `ManageCameras`（GameWidget.cs:77） |
| 改原版界面某个控件 | Name 合并机制（Widget.cs:587-608）+ `ContentManager.Get<XElement>` 共享缓存 |
| 界面整体切换/弹窗 | `ScreensManager.cs:51`（切屏）、`DialogsManager.cs:46`（弹窗） |
| 半透明发白/发光 | BlendState.cs:27 预乘 alpha，顶点色 RGB×A |
| 物品格交互/拖放规则 | `InventorySlotWidget.cs:201-329`（Update）与 `:569`（HandleDragDrop） |
| 界面进不去/白屏 | 检查 xmlns、abstract 标签、值转换异常；另见 12-ModAPI与加载链.md 的失败出口 |
