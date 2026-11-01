# Widget 生命周期与自定义控件

> 域: SC引擎 · 更新: 2026-11-01 · 状态: 全读(Widget.cs/WidgetInput.cs/ContainerWidget/Canvas/Stack/Grid/Clickable/StarRating/Fire/BlockIcon/ValueBar/BusyBar/ScrollPanel/TextBox/GameWidget 全文，FlexPanel 表头+关键段)

## 一句话定位

自己写一个 Widget 类时的完整契约：帧内五步全序（输入→Update→Measure→Arrange→Draw）、两遍布局规则、点击从 Screen 流到控件的链路、以及最短可照抄的自定义控件模板。

源码树按新约定写仓库相对路径（根 = SurvivalcraftAPIProject 仓库根）。

## 帧内生命周期全序（带行号）

驱动方在主循环：`Game/Program.cs:298` 调 `ScreensManager.Update()`，`Game/Program.cs:328` 调 `ScreensManager.Draw()`。屏幕树根 `ScreensManager.RootWidget`（CanvasWidget）在 `Managers/ScreensManager.cs:196-201` 初始化时挂上全局唯一 `WidgetInput`。

一帧五步，全部外部驱动，**任何一步都不会自动发生**：

| 步 | 入口 | 做什么 |
|---|---|---|
| 1 输入采集 | `ScreensManager.Update` → `Widget.UpdateWidgetsHierarchy(RootWidget)`（`Managers/ScreensManager.cs:228`；`Survivalcraft/Widget/Widget.cs:742-748`） | 根 WidgetInput.Update() 汇总键鼠/触/手柄/VR 成 Press/Tap/Click/Drag/Hold/Scroll |
| 2 Update | 同上遍历内（`Widget.cs:830-868`） | 每个可见启用部件的 `Update()`（子先父后，见下） |
| 3 Measure | `ScreensManager.Draw` → `LayoutAndDrawWidgets`（`Managers/ScreensManager.cs:447-483`）→ `Widget.LayoutWidgetsHierarchy`（`Widget.cs:750-753`） | `root.Measure(availableSize)` 自顶向下递归算 DesiredSize |
| 4 Arrange | 同上 `root.Arrange(Vector2.Zero, availableSize)` | 自顶向下递归定 ActualSize + GlobalTransform/GlobalBounds |
| 5 Draw | `Widget.DrawWidgetsHierarchy`（`Widget.cs:755-763`） | Collate→分层→渲染（见下） |

`UpdateWidgetsHierarchy` 每部件精确顺序（`Widget.cs:830-868`）：
1. 门槛：`!IsVisible || !IsUpdateEnabled || !IsEnabled` 直接跳过整棵子树（831-834）。
2. 有自己的 `WidgetsHierarchyInput` 就先 `WidgetInput.Update()`（836-838，GameWidget/Screen 根才挂）。
3. **子件逆序**递归（840-847，`for num = Count-1 → 0`）：最后一个子件（绘制在最上层）最先 Update。
4. `BeforeWidgetUpdate` 钩子 → `widget.Update()` → `AfterWidgetUpdate` 钩子（848-864）；`Update1` 委托非空则整体替代（865-867）。

推论：**子件 Update 先于父件 Update**——父件 Update 里读子件状态（如 ScrollPanel 读子件 Measure 结果、面板读槽位状态）拿到的是本帧新值；但父件想让子件看到的变化要等下一帧（或直接改子件属性）。

### Update 契约（对 09 页契约的精确化）

`Widget.Update()` 是**空虚方法**（`Widget.cs:681`），子件递归由外部静态遍历驱动——**不调 `base.Update()` 不会断任何链**（原版 `ClickableWidget.cs:22`、`InventorySlotWidget.cs:201` 都不调；全目录仅 6 处调 base.Update()）。真正的“必调 base”只有两处：
- `MeasureOverride`/`ArrangeOverride`：base 实现（`ContainerWidget.cs:46-66`）才是子件递归本身，容器子类不调 base 也不手写子件 Measure/Arrange，子件就量不到摆不上。
- `UpdateCeases`：`ContainerWidget.cs:22-26` 向子件传播；重置一次性状态（`ClickableWidget.cs:15-20` 清 IsPressed/IsClicked/IsTapped）必须调。

`UpdateCeases` 触发时机：`IsVisible=false`（`Widget.cs:359-365`）、`IsEnabled=false`（368-378）、`ChangeParent(null)`（620-627）——隐藏/禁用即收尾，读它做状态复位与资源释放（`PlayerModelWidget.cs:166-174` 清皮肤缓存）。

### Draw 契约：裁剪与混合状态谁管

- **要不要画由 `IsDrawRequired` 决定**（`Widget.cs:65-70`），默认 false——这就是“自绘不显示”的根源。惯例在 `MeasureOverride` 里置 true（每帧重设，如 `StarRatingWidget.cs:72`、`FireWidget.cs:15`、`BusyBarWidget.cs:27`、`BlockIconWidget.cs:81`）。`IsOverdrawRequired`（79-85）走 `Overdraw`（`Widget.cs:685`，画在自己子件之上）。
- **裁剪**：`ClampToBounds=true` 时 CollateDrawItems 用 GlobalBounds 与父 scissor 求交生成 scissor DrawItem（`Widget.cs:52-64`），子树继承缩小后的 scissor（71-78 只在 `isWidgetInBound || !ClampToBounds` 时递归）；切 scissor 靠插入 DrawItem 并提升 Layer 实现（98-120），渲染时 `Display.ScissorRectangle` 逐项设置（168）。
- **混合/深度/采样状态**：框架不管全局状态，**控件自选**——建批时传参：`dc.PrimitivesRenderer2D.FlatBatch(0, DepthStencilState.None)` / `TexturedBatch(texture, false, 0, DepthStencilState.None, null, null, SamplerState.X)`（`ValueBarWidget.cs:86-97`、`RectangleWidget.cs:90`）。批次按 Layer 分层 Flush（124-136），同层同状态批合并。
- **颜色**：`ColorTransform` 沿树相乘成 `GlobalColorTransform`（Arrange 时，`Widget.cs:659`），自绘末尾一律 `色 * GlobalColorTransform`，换屏淡入淡出（ColorTransform 透明渐变）才对自绘生效。
- 顶点全部入 `dc.PrimitivesRenderer2D/3D` 批后 `TransformTriangles(GlobalTransform, count)`（`StarRatingWidget.cs:68`），不要用 Display 级变换。3D 内容进 UI 用 `dc.PrimitivesRenderer3D`（`BlockIconWidget.cs:77`、`ModelWidget.cs:245`）。
- 钩子：`BeforeWidgetDrawItemRender` 可整替原版绘制（`Widget.cs:140-156`），`OnDrawItemAssigned`（113-119）。

### HitTest 与 IsClicked 的关系

- `HitTest(point)`（`Widget.cs:687-695`）默认实现 = 屏幕点经 `InvertedGlobalTransform` 逆变换回控件局部，落在 `[0,0]-[ActualSize]` 内即命中。要非矩形命中就 override 它（如按纹理 alpha）。
- `HitTestGlobal(point[, predicate])`（`Widget.cs:808-828`）：从根深度优先、**子件逆序**（最上层先），`ClampToBounds` 的父不命中则整棵子树跳过（811），自身需 `IsHitTestVisible`（构造默认 true，`Widget.cs:481`）。
- **没有全局“IsClicked”事件**。点击判定 = 各控件在 `Update()` 里轮询共享 `WidgetInput` 的 `Click`（**Segment2：按下点→抬起点**，`WidgetInput.cs:806-820`）+ 两端 `HitTestGlobal==this`（`ClickableWidget.cs:35-38`）。`IsClicked/IsTapped/IsPressed` 是 `ClickableWidget` 自己的轮询结果属性（`ClickableWidget.cs:5-9`），不是基类机制。消费输入防穿透用 `Input.Clear()`（`ScrollPanelWidget.cs:138`、`SliderWidget.cs:127-162` 先例）。

## 布局两阶段

测量父→子传“可用空间”，摆放父→子传“矩形格”。`DesiredSize` 构造默认 `Vector2(∞)`（`Widget.cs:483`）——“想占满”；`ParentDesiredSize` 是 Measure 后换算给父看的值（`Widget.cs:637-646`）。

| 容器 | 测量规则 | 摆放规则 |
|---|---|---|
| ContainerWidget 默认 | 子件各得 `parentAvailableSize - margin`（`ContainerWidget.cs:46-55`） | 全部塞进 `(0,0)-ActualSize` 格，对齐算术决定落点（57-66） |
| CanvasWidget | 子件各得 `可用 - Position - margin`；自身 DesiredSize = max(子 Position+Desired+margin)，`Size≥0` 时覆盖（`CanvasWidget.cs:33-64`） | 有 Position 的子件按位摆：有限 DesiredSize 原样，**∞ 则吃 `ActualSize - Position`**（66-79）；无 Position 走整格对齐 |
| StackPanelWidget | 有限子件累加 fixed、从可用里扣；**∞（fill）子件计入 m_fillCount**；无 fill 子件 → 主轴 DesiredSize=fixed，有 → **主轴=∞**（`StackPanelWidget.cs:13-48`） | fill 子件均分 `Actual - fixed`；每子件格 = 主轴区间 × **整条交叉轴**，再进对齐算术（50-90） |
| GridPanelWidget | 逐格取 `max(子 Desired+margin)` 定列宽行高，Position 累加，DesiredSize=总尺寸（`GridPanelWidget.cs:65-92`） | 格矩形 → 对齐算术（94-110）。注意测量不看 IsVisible，隐藏子件仍撑格（09 页已录） |
| FlexPanelWidget | 主轴期望恒有限（fill 件 Basis 0，空间分配交给 Grow）；交叉轴滤 ∞/NaN 子件（`FlexPanelWidget.cs:56-58` 头注） | grow 件无条件吃满分配区间，shrink 按 shrink×basis 加权（详见 09 页 flex 行） |

对齐与 Margin 的最终语义全在 `ArrangeChildWidgetInCell`（`ContainerWidget.cs:68-114`）：
- 目标尺寸先钳到 `格 - margin`（∞ 直接取格大小，73-80）。
- Near = 格首 + MarginLeft/Top，尺寸取 DesiredSize（81-84）；Center 居中（85-88）；Far = 格尾 − 尺寸 − MarginRight/Bottom（89-92）；**Stretch = 从格首+margin 铺满到格尾**（93-96），此时 margin 是两侧收缩量。
- `WidgetAlignment`：Near=0/Center=1/Far=2/Stretch=3（`WidgetAlignment.cs:3-6`）。
- Margin 是四向独立属性（`Widget.cs:419-441`），测量阶段即从可用空间扣除——它是“占位”，不是“外边距后仍参与 Stretch”。

## 输入路由链

```
OS事件 → Engine.Input.Keyboard/Mouse/Touch/GamePad
      → WidgetInput.Update()（每屏根一个，WidgetInput.cs:683-703，按 Devices 位分别汇入）
      → 语义事件: Press/Tap/Click(Segment2)/Drag/Hold/Scroll 挂在 WidgetInput 上（789-857, 939-990）
      → Widget.Input 属性沿父链上溯取最近 WidgetsHierarchyInput（Widget.cs:296-308）
      → 控件 Update() 轮询 Input.* + HitTestGlobal 自认命中（拉模型，无事件总线）
```

- 触屏直接带命中门槛：按下点须先过 `Widget.HitTest`（`WidgetInput.cs:942`，Widget = 挂输入的根）；鼠标无此门槛，命中判定全交给各控件。
- 谁挂 WidgetInput：菜单屏根（`ScreensManager.cs:199`）；游戏内 HUD 由 `GameWidget.Update` 按设备动态 new 挂到自己（`GameWidget.cs:215-231`），GuiWidget 靠父链拿到；VR 下 GuiWidget 被摘出树、由 GameWidget 手动 `UpdateWidgetsHierarchy(GuiWidget)` 驱动（169-190）。
- 模态拦截两条线：**对话框** `DialogsManager.ShowDialog` 把 Dialog 挂进屏（输入走父链共享，`Managers/DialogsManager.cs:63`），Hide 时挂 `WidgetInputDevice.None` 隔绝（94）；**游戏内模态面板** `ComponentGui.ModalPanelWidget` 非空或有对话框时，`ComponentInput` 停止把输入交给世界操作并强制显示鼠标（`Component/ComponentInput.cs:136-141`）。
- 键盘焦点没有树级焦点链：`TextBoxWidget` 用**静态 FocusedTextBox 单例**（`TextBoxWidget.cs:368-387`），被 Click（两端都在框内）命中即 `HasFocus=true` 并弹输入法（839-870），点框外失焦（871-875），`UpdateCeases` 收输入法（826-830）。有焦点后直接读 `Keyboard.*`（943-1000，不走 WidgetInput 语义层）。
- 滚轮：`Input.Scroll`（位置+格数）挂在指针处，`ScrollPanelWidget.Update` 用 `HitTestPanel`（`HitTestGlobal` + 谓词认领子树，`ScrollPanelWidget.cs:114-120, 166-176`）决定是否滚动并 Clear。

## 自定义控件最短全流程（照抄 StarRatingWidget）

1. **写类**：继承 `Widget`（纯自绘+自交互）或 `CanvasWidget`（要装子件）。构造函数设默认外观。
2. **override MeasureOverride**：置 `IsDrawRequired = true`（不画就永远不会画）+ 给有限 `DesiredSize`（`StarRatingWidget.cs:71-74`）。
3. **override Draw**：从 `dc.PrimitivesRenderer2D` 要批、Queue 顶点、`TransformTriangles(GlobalTransform, count)`、色乘 `GlobalColorTransform`（36-69）。
4. **override Update**：轮询 `Input.Press/Tap/Click` + `HitTestGlobal(...) == this` 判命中，改状态，需要独占就 `Input.Clear()`（28-34）。
5. **override UpdateCeases**：复位按下的瞬时状态（可选）。
6. **上屏**：代码 `parent.Children.Add(new XxxWidget())`；或 XML 直接写元素——`Widget.LoadWidget` 反射 `FindTypeFromXmlName` 构造（`Widget.cs:486-505`），带 `runtime-namespace:` 前缀可实例化任意程序集类型（797-806），`OnWidgetConstruct` 钩子可偷梁换柱（495-501）；属性按名反射赋值，`{资源名}` 走 ContentManager（564-574），`Type.Prop` 附着属性调静态 SetXxx（526-555）。
7. 之后每帧自动进入五步全序，无需再挂任何驱动代码。

原版最短完整范例：`Survivalcraft/Widget/StarRatingWidget.cs`（75 行，含测量/交互/自绘/命中全链）；纯交互范例 `ClickableWidget.cs`（47 行）；XML 组合外壳范例 `BitmapButtonWidget.cs`（ctor 加载 `Widgets/BitmapButtonContents` 后 `Children.Find<ClickableWidget>("Button.Clickable")`）。

## 原版范例表（它 override 了什么）

| 控件 | 基类 | override 点 | 学什么 |
|---|---|---|---|
| StarRatingWidget | Widget | Measure(置IsDrawRequired)、Update(轮询Press+HitTestGlobal)、Draw(双quad贴图) | 最小全周期模板 |
| ClickableWidget | Widget | Update(Press/Tap/Click 三态判定)、UpdateCeases(复位) | 点击判定标准写法 |
| ValueBarWidget | Widget | Measure、Draw(Flat/TexturedBatch 按状态传参) | 分段条、批状态选择 |
| BusyBarWidget | Widget | Measure、Draw(Time.RealTime 驱动动画) | 无状态自绘动画 |
| FireWidget | CanvasWidget | Measure(调base+置IsDrawRequired)、Update(粒子推进)、Draw(委托渲染器) | 装饰粒子+ClampToBounds 裁剪 |
| BlockIconWidget | Widget | Draw(PrimitivesRenderer3D + 投影进 GlobalTransform) | 3D 方块进 2D UI |
| PlayerModelWidget | CanvasWidget | Update(Press 拖转+Input.Clear)、UpdateCeases(释放缓存) | 3D 角色可交互 |
| ScrollPanelWidget | ContainerWidget | Measure/Arrange(自布局)、Update(Drag/Scroll+HitTestPanel 谓词+Clear)、Draw(滚动条) | 自定义布局+输入消费 |

## 快查路由

| 要做什么 | 照抄 | 关键行 |
|---|---|---|
| 自绘控件不显示 | 检查 MeasureOverride 是否置 IsDrawRequired | `StarRatingWidget.cs:72` |
| 控件点不到 | IsHitTestVisible / 父 ClampToBounds / 子件抢命中 | `Widget.cs:808-828` |
| 点击防穿透 | 判定成立后 `Input.Clear()` | `ScrollPanelWidget.cs:138` |
| 隐藏后状态残留 | override UpdateCeases + 调 base | `ClickableWidget.cs:15-20` |
| 让子件 ∞ 填满剩余 | StackPanel fill 机制 | `StackPanelWidget.cs:55-57` |
| 控件内 3D 内容 | dc.PrimitivesRenderer3D + GlobalTransform 换算 | `BlockIconWidget.cs:63-78` |
| XML 自定义控件元素 | runtime-namespace 类型名 | `Widget.cs:797-806` |
| 键盘输入进控件 | 静态 FocusedTextBox 模式 + Keyboard 直读 | `TextBoxWidget.cs:368,839-870` |
