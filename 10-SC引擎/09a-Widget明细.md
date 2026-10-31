# Widget 明细（106 文件全量一行表）

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(全文深读32、节选抽读3、签名级71)
>
> 父页: 09-UI与Widget体系.md。每行 = 一个 .cs 文件。格式：文件 | 继承 | 职责/关键成员+行号 | 坑。
> 路径前缀统一为 `E:\SurvivalcraftAPIProject\Survivalcraft\Widget\`（下表"路径"列只写文件名）；行号以 2026-10-31 源码为准。
> 标注：〔深〕=全文深读；〔节〕=节选深读；〔签〕=签名级扫描。

## 一、根与基础（7）

| 文件 | 继承 | 职责/关键成员 | 坑 |
|---|---|---|---|
| 〔深〕Widget.cs | — | 部件基类全管线：虚方法簇 `Update/UpdateCeases/Draw/Overdraw` 全空(`:679-685`)、`MeasureOverride:649`、`ArrangeOverride:677`、`ChangeParent:620`；XML 装载 `:491-608`；Layer 收集 `:42-98`；`HitTestGlobal:808`；钩子 `:849-863` | DesiredSize 默认 ∞(`:483`) |
| 〔深〕WidgetsList.cs | IEnumerable | Children 实现；`Insert:69` 防重复+ChangeParent；`Find:128-145` 递归深度优先按名/类型 | Find 命中即返，同名取先挂者 |
| 〔深〕WidgetAlignment.cs | enum | Near=0/Center/Far/Stretch | Center 忽略 margin |
| 〔深〕WidgetInput.cs | — | 统一输入聚合：`Click:806`(Segment2 首尾)、`Drag:836` 阈值、`Hold:841`、`Clear:671`、四设备 Update `:683-703`、软光标 Draw `:705-740`、映射名查询 `:363-449` | 读完必 Clear() 吞事件 |
| 〔深〕WidgetInputDevice.cs | enum(Flags) | 键/鼠/触/4手柄/VR + Multi* 组合位(`:3-25`) | All 不含 Multi* |
| 〔深〕ContainerWidget.cs | Widget | abstract；`ArrangeChildWidgetInCell:68-113` 对齐算术；`WidgetAdded/Removed:42-44` 虚钩 | 直接 Measure 全部孩子 |
| 〔深〕CanvasWidget.cs | ContainerWidget | 绝对定位画布：`Size:7`(-1=自适应)、Measure/Arrange `:33-66`、`SetWidgetPosition` | 无 Update 覆写 |

## 二、布局容器族（9）

| 文件 | 继承 | 职责/关键成员 | 坑 |
|---|---|---|---|
| 〔深〕StackPanelWidget.cs | ContainerWidget | 沿 Direction 累加；`MeasureOverride:13-48`(m_fixedSize/m_fillCount)、`ArrangeOverride:50-90` fill 件平分剩余(`:55-57`)；`IsInverted:11` 反向 | 有 fill 件主轴 DesiredSize=∞ |
| 〔深〕UniformSpacingPanelWidget.cs | ContainerWidget | 每可见件均分一格；`ArrangeOverride:14-30`(ActualSize/m_count)、`MeasureOverride:32-54` | 主轴 DesiredSize 恒 ∞(`:51-53`) |
| 〔深〕FixedSizePanelWidget.cs | ContainerWidget | 全孩子给满可用宽取有限最大(`:5-19`)，每件摆满整格(`:21-25`) | 忽略 ∞ 期望，可叠层 |
| 〔深〕GridPanelWidget.cs | ContainerWidget | `ColumnsCount/RowsCount:23-41`、附着 `SetCell:57`、`MeasureOverride:65-92`(列宽=最大含margin)、`ArrangeOverride:94-110`(无效cell摆全格`:107`)、内类 Column/Row `:5-15` | Measure 不看 IsVisible(`:73`)，隐藏孩子仍撑宽 |
| 〔深〕TablePanelWidget.cs | ContainerWidget | CSS table：`TableRowWidget:13-24`(空 Measure/Arrange 压默认)、`MeasureOverride:109`、CollectRows`:533`、ExpandSlots`:608`、`MeasureCellExtents:656`、`MeasureSpansMinWidth:708`、SpreadToColumns`:753`、`NegotiateColumns:779`、高度轮`:815`、`ComputeArrangedWidths:884`、`Draw:234`(layer -1 四层) | 严禁对 cell 测 (0,∞)→Label 零推进 OOM(`:653-656`) |
| 〔深〕FlexPanelWidget.cs | ContainerWidget | CSS flex：`FlexDirection/Wrap/Justification:10/24/37`(Flags)、Grow/Shrink/Basis 附着`:80-98`、`GreedyBreak:236`、`BreakBalanced:279`(二分)、`ArrangeRow:337`(grow吃满`:450`、Justify分布`:384`)、AlignItems Near哨兵`:433`、`IsInsideFlex:164` | Reverse 仅 Wrap 时生效(`:210-214`) |
| 〔深〕ScrollPanelWidget.cs | ContainerWidget | 视口滚动：Update/Measure/Arrange `:42/56/72`、`CalculateScrollAreaLength` 虚可覆写 | 初始 ScrollPosition=12/Speed=-70 自动滚 |
| 〔深〕ListPanelWidget.cs | ScrollPanelWidget | 条目化滚动列表；覆写 Update/Arrange `:182/200/219` | — |
| 〔深〕DragHostWidget.cs | ContainerWidget | 拖动宿主：`BeginDrag:17`(改挂孩子)、`EndDrag:27`、`Update:39-55`(谓词命中IDragTarget`:42`、finally收尾)、摆位指针居中`:57-64` | ctor IsHitTestVisible=false |

## 三、交互族（11）

| 文件 | 继承 | 职责/关键成员 | 坑 |
|---|---|---|---|
| 〔深〕ClickableWidget.cs | Widget | 最小可点件：`Update:22-45` 轮询置 IsClicked/IsTapped/IsPressed | 子类漏调 base.Update=交互失效 |
| 〔深〕ButtonWidget.cs | CanvasWidget | **abstract** 按钮接口：IsClicked/IsChecked/Text/Font/Color 纯抽象(`:5-17`) | 当 XML 标签抛 |
| 〔深〕BevelledButtonWidget.cs | ButtonWidget | 复合模板件：ctor 装配 "Widgets/BevelledButtonContents"(`:75-86`)；按下/选中 bevel 内凹(`:92`)；禁用灰(`:90-91`) | Size 不设 DesiredSize=∞ |
| 〔签〕BitmapButtonWidget.cs | ButtonWidget | 图片按钮模板件；MeasureOverride `:59` | 同上 |
| 〔深〕CheckboxWidget.cs | CanvasWidget | 复合模板件("Widgets/CheckboxContents" `:49-58`)；`Update:60-64` 自动取反 IsChecked；勾图显隐在 Measure(`:71`) | — |
| 〔深〕SliderWidget.cs | CanvasWidget | 滑杆：Min/Max/Granularity 联动钳制(`:29-61`)；`Update:127-162`(HitTestGlobal==tab、Input.Clear 吞输入、音效)；`ArrangeOverride:107` 摆 tab；`SlidingCompleted:90` | LayoutDirection 竖排时 label 位置不同 |
| 〔深〕LinkWidget.cs | FixedSizePanelWidget | 链接=模板件("Widgets/LinkContents" `:93-100`)全转 发 Label 属性；`Update:102-106` 点击 LaunchBrowser | Url 空串不响应 |
| 〔深〕ClickTextWidget.cs | CanvasWidget | 纯代码构造点击文本：`ctor:13`(要求参数，无无参构造)、`Update:54-60` 自画边框 | XML 不可用 |
| 〔签〕StarRatingWidget.cs | Widget | 星级评分：`Update:28` Input.Click 命中算星、`Draw:36`、`Measure:71` | — |
| 〔深〕TouchInputWidget.cs | Widget | 单指手势：`Update:38-91` 产出 Tap/Hold/Move 结构体，TotalMoveLimited 按 `Radius:22` 限位 | 只跟踪一个 touchId |
| 〔深〕IDragTargetWidget.cs | interface | `DragOver/DragDrop:2-6` | 无 data 类型约束 |

## 四、文本族（4）

| 文件 | 继承 | 职责/关键成员 | 坑 |
|---|---|---|---|
| 〔深〕FontTextWidget.cs | Widget | 文本核心：`TextWordBreak:7-16`、矢量链默认开(`:224-225`)、`Draw:228`(装饰分层`:240-242`)、`UpdateLines:704-809`(缓存+省略号+MaxLines)、`FindLineBreakPosition:648`、CJK 禁则`:685-702`、`MeasureOverride:603`、`CalculateLineHeight:621`、VectorGlyphSink`:537` | 可用宽 0 零推进死循环(断点钳1`:748`) |
| 〔深〕LabelWidget.cs | FontTextWidget | 文本标签：`Text:14-30` 支持 `[Content:Name]`/`[Usual:Key]` 本地化；默认 Pericles→FontManager(`:5-12`) | 本地化格式仅识别方括号整串 |
| 〔深〕TextBoxWidget.cs | Widget | API 增补多行文本框(2133行)：静态焦点 `FocusedTextBox:346`、`Update:834-1062`(点击选字`:841`、Tab切换`:1030`、快捷键)、IME 静态接线`:676-778`、`EnterCharacter:457`、`MeasureOverride:1996`(AutoSize)、`ArrangeOverride:2008`(滚动钳制)、`Draw_:1874`(NonPremultiplied`:1889`)、候选窗 Overdraw`:1775`、事件 FocusLost/OnFocus/Enter/Escape/TextChanged `:1725-1767` | MaximumLength<0 抛(`:1231`)；Scroll setter 直接赋字段防递归(`:1371`) |
| 〔签〕LegacyTextBoxWidget.cs | Widget | 旧版单行文本框：`Update:139`、`MoveNext:268`(Tab 轮转)、`Draw:297` | 新代码用 TextBoxWidget |

## 五、富文本与富内容族（22）

### RichText（6）

| 文件 | 继承 | 职责/关键成员 | 坑 |
|---|---|---|---|
| 〔节〕RichText/RichTextWidget.cs | Widget | 多 span 富文本：`MarkLayoutDirty:56`、`Update:266`、`Draw:277`、`MeasureOverride:656`、`FindLinkAtPoint:706`、VectorFont/MonoVectorFont(`:75/86`) | 就地改 Spans 必须手动置脏 |
| 〔签〕RichText/RichTextLayout.cs | — | span 排版引擎：`Layout:67-330`、`MeasureRunWidth:330`、`HasSpanDecoration:374` | — |
| 〔签〕RichText/TextSpan.cs | — | 行内片段：文本/色/字号/粗斜体/边框/链接/等宽 | — |
| 〔签〕RichText/TextLine.cs | — | `TextRun:3`/`TextLine:17` 排版产物 | — |
| 〔签〕RichText/SpanBorder.cs | — | span 边框规格(Widths 四向) | — |
| 〔签〕RichText/RichContentPalette.cs | static | 代码/链接/kbd/高亮默认配色(`:6-22`) | — |

### Html（9）

| 文件 | 继承 | 职责/关键成员 | 坑 |
|---|---|---|---|
| 〔签〕Html/HtmlWidget.cs | StackPanelWidget | HTML 入口控件：`MeasureOverride:62`、`UpdateCeases:101`、`TryScrollToAnchor:112` | — |
| 〔签〕Html/HtmlToWidgetsBuilder.cs | RichContentBuilder | HTML+CSS 子集→Widget 树(3490行)：`BuildHtml:48`/`BuildHtmlInto:55` | 重量级，解析深递归有 depth 参数 |
| 〔签〕Html/HtmlBlockSizerWidget.cs | StackPanelWidget | 块级尺寸壳(百分比/显式宽)：`MeasureOverride:73` | — |
| 〔签〕Html/HtmlStyleBoxWidget.cs | StackPanelWidget | margin/padding/边框/圆角壳：`Measure:36`、`Draw:41` | — |
| 〔签〕Html/HtmlTransformBoxWidget.cs | StackPanelWidget | css transform 壳：`ArrangeOverride:27` 施矩阵 | — |
| 〔签〕Html/HtmlSpanParser.cs | static | 行内 HTML→TextSpan：`ParseFragment:14`、内联标签`:425`、CSS opacity`:298` | — |
| 〔签〕Html/CssColorParser.cs | static | CSS 颜色：`TryParse:165` | — |
| 〔签〕Html/CssStyleParser.cs | static | style 声明解析：`ParseDeclarations:18`、盒`:71`、边框`:314`、圆角`:434` | — |
| 〔签〕Html/CssTransformParser.cs | static | transform 函数：`TryParseTransform:32`、origin`:262` | — |

### Markdown（4）

| 文件 | 继承 | 职责/关键成员 | 坑 |
|---|---|---|---|
| 〔签〕Markdown/MarkdownWidget.cs | StackPanelWidget | Markdown 入口：`MeasureOverride:51`、`UpdateCeases:91` | — |
| 〔签〕Markdown/MarkdownToWidgetsBuilder.cs | RichContentBuilder | MdBlock→Widget 树：`Build:27`、`BuildBlocks:34` | — |
| 〔签〕Markdown/MarkdownSpanParser.cs | static | 行内标记→TextSpan：`Parse:72`；`MarkdownSpanStyle:20`/`TextTransform:9` | — |
| 〔签〕Markdown/MarkdownTableWidget.cs | ContainerWidget | MD 表格：`AddRow:65`、列协商 `Measure:101`/`Arrange:127`、GridLineColor`:26` | TablePanelWidget 的原型 |

### RichContent 公共（3）

| 文件 | 继承 | 职责/关键成员 | 坑 |
|---|---|---|---|
| 〔签〕RichContentBuilder.cs | — | abstract 富内容构建器基(`:9`) | — |
| 〔签〕RichContentPanel.cs | StackPanelWidget | 内容面板+壳分类 `ShellKind:5`：`MeasureOverride:52` | — |
| 〔签〕RichContentImageLoader.cs | — | 图片异步加载：`CreateImageBlock:95`(占位)、`RefitFrame:76`(重适配)、`ResolvePendingWidths:215`、`ReleaseTextures:186` | 纹理要手动释放 |

## 六、图元显示族（11）

| 文件 | 继承 | 职责/关键成员 | 坑 |
|---|---|---|---|
| 〔深〕RectangleWidget.cs | Widget | 矩形/纹理矩形：`Size:76` 默认∞、`Draw:86-182`(贴图坐标/翻转/OutlineThickness逐px线`:164-181`)、`Measure:184-187` | ctor IsHitTestVisible=false |
| 〔深〕BevelledRectangleWidget.cs | Widget | 凸起面板：批缓存(`:40-44`，属性+GlobalScale 失效`:188-195`)、`Draw:178`、`PremultiplyAlpha:286`、默认圆角6/斜面2(`:162-176`)、静态 QueueBevelledRectangle`:308` | 低 alpha 观感受预乘改变(注释`:179-182`) |
| 〔深〕ValueBarWidget.cs | Widget | 分格值条：`Flash:81`、`Draw:85-204`(BarBlending插值/HalfBars/LitBarColor2渐变/闪白衰减`:203`)、`Measure:206-211` | ctor IsHitTestVisible=false |
| 〔签〕BusyBarWidget.cs | Widget | 忙碌动画条：`Measure:26`、`Draw:31` | — |
| 〔深〕BlockIconWidget.cs | Widget | 3D 方块图标：`Value:20-34` setter 重建视线矩阵(GetIconViewOffset)、Contents/Light/Data 分解`:36-49`、`Draw:63-78`(正交投影+DrawBlock UI 模式) | ctor Light=15；IsHitTestVisible=false |
| 〔签〕ClearWidget.cs | Widget | 清屏图元：`Measure:28`、`Draw:32` | — |
| 〔签〕ArrowLineWidget.cs | Widget | 折线箭头：`Draw:63`、`ParsePoints:86` | — |
| 〔签〕PanoramaWidget.cs | Widget | 主菜单全景：`DrawImage:19`(滚动平铺)、`DrawSquares:49`、TexturePath`:6` | — |
| 〔签〕ModelWidget.cs | Widget | UI 内 3D 模型容器：`AddModel:138`、`PlayAnimation:178-207`、`GetBoneTransform:239`、`Draw:245`、`Update:530`(动画推进)、`ProcessBoneHierarchy:576`、静态 CustomRenderer`:134` | IsHitTestVisible=false |
| 〔签〕ModelWidgetRenderContext.cs | — | 自定义模型渲染辅助：纹理/关矩阵/着色器参数(`:37-53`) | 配合 CustomRenderer |
| 〔签〕MoveRoseWidget.cs | Widget | 触屏方向罗盘：`Update:31`、`Draw:79`、GetSubtextureCoords`:219` | — |

## 七、HUD/视口/屏内显示族（10）

| 文件 | 继承 | 职责/关键成员 | 坑 |
|---|---|---|---|
| 〔深〕GameWidget.cs | CanvasWidget | 每玩家视口根(`:17`)：ManageCameras 钩子`:77-84`、GuiWidget HUD 槽、Update `:184/241`；同文件 `VrGuiRootWidget:13` | — |
| 〔节〕GamesWidget.cs | ContainerWidget | 分屏容器：`Measure:9-12`(孩子>1 置 IsOverdrawRequired)、`ArrangeOverride:14-60`(1/2/4 布局、刘海 insets`:17-19`、LayoutTransform 缩放`:48`)、`Overdraw:545` | 直接改孩子 GuiWidget margin |
| 〔节〕ViewWidget.cs | TouchInputWidget+IDragTarget | 3D 视口：`ChangeParent:24-32` 强制父=GameWidget、`Draw:39`、`DragDrop:53-75`(物品抛世界)、`SetupScalingRenderTarget:77`(分辨率三档) | 挂错父直接抛 |
| 〔签〕VitalStatsWidget.cs | CanvasWidget | 生命/物品栏状态条：`Update:69` | — |
| 〔签〕PlayerWidget.cs | CanvasWidget | 玩家状态面板：`Update:25` | — |
| 〔签〕PlayerModelWidget.cs | CanvasWidget | 玩家模型预览：`Update:78`、`UpdateCeases:166`、ViewMode enum`:6` | — |
| 〔签〕FireWidget.cs | CanvasWidget | 火焰指示：`Measure:14`、`Draw:19`、`Update:23` | — |
| 〔签〕MessageWidget.cs | StackPanelWidget | 飘字消息队列：`DisplayMessage:61/67`、`Update:72`、`RemoveOldMessages:89`、内类 Message`:8` | — |
| 〔签〕MotdWidget.cs | CanvasWidget | 公告滚动：`Update:32`、`GotoLine:104`、`Restart:114`、`ParseLine:135` | — |
| 〔签〕SubsystemGameWidgets.cs | Subsystem | 持有 GamesWidget+每玩家 GameWidget：`Update:34`(UpdateOrder.Views`:19`)、`AddGameWidgetForPlayer:63`、距离查询`:21-32` | — |

## 八、物品与功能方块面板族（14）

| 文件 | 继承 | 职责/关键成员 | 坑 |
|---|---|---|---|
| 〔深〕InventorySlotWidget.cs | CanvasWidget+IDragTarget | 物品格全能件：`Update:201-329`(点击/长按/拖拽)、Measure `:331/407`(base 前重置 IsDrawRequired)、HandleDragDrop`:569` | 子类设 IsDrawRequired 写 base 之后 |
| 〔签〕ShortInventoryWidget.cs | CanvasWidget | 快捷栏：`AssignComponents:22`、`Measure:29` | — |
| 〔签〕FullInventoryWidget.cs | CanvasWidget | 整背包面板(纯 XML 装配，无覆写) | — |
| 〔签〕ChestWidget.cs | CanvasWidget | 箱子面板：`Update:38`(绑定 ComponentChest) | ProcessingOnly 模式 |
| 〔签〕FurnaceWidget.cs | CanvasWidget | 熔炉面板：`Update:56` | — |
| 〔签〕CraftingTableWidget.cs | CanvasWidget | 工作台面板：`Update:46` | — |
| 〔签〕CraftingRecipeWidget.cs | CanvasWidget | 配方展示：`Measure:56`、`UpdateWidgets:63` | — |
| 〔签〕CraftingRecipeSlotWidget.cs | CanvasWidget | 配方格：`SetIngredient:23`、`SetResult:29`、`Measure:35` | — |
| 〔签〕SmeltingRecipeWidget.cs | CanvasWidget | 熔炼配方：`Measure:59`、`UpdateWidgets:66` | — |
| 〔签〕CreativeInventoryWidget.cs | CanvasWidget | 创造背包分类：内类 Category`:7`、`Update:77`、GetCategoryName`:75` | — |
| 〔签〕DispenserWidget.cs | CanvasWidget | 发射器面板：`Update:53` | — |
| 〔签〕ClothingWidget.cs | CanvasWidget | 衣物栏：`Update:70` | — |
| 〔签〕FurnitureDesignWidget.cs | Widget | 家具设计 3D 编辑器：`Draw:44-223`、`Update:224`、`Rotate:257`、DrawDebugFurniture`:28` | — |
| 〔签〕FurnitureSetItemWidget.cs | CanvasWidget+IDragTarget | 家具套装格：`DragDrop:24`、`DragOver:32`、`GetFurnitureDesign:51` | — |

## 九、手持武器族（3）

| 文件 | 继承 | 职责/关键成员 | 坑 |
|---|---|---|---|
| 〔签〕BowWidget.cs | CanvasWidget | 拉弓视图：`Update:40`(按拉距摆模型) | — |
| 〔签〕CrossbowWidget.cs | CanvasWidget | 弩视图：`Update:44`、`SetDraw:95`、`DrawToPosition/PositionToDraw:102-104`(拉量↔位置换算) | — |
| 〔签〕MusketWidget.cs | CanvasWidget | 火枪视图：`Update:40` | — |

## 十、树形与模组/社区管理族（15）

| 文件 | 继承 | 职责/关键成员 | 坑 |
|---|---|---|---|
| 〔签〕TreeViewWidget.cs | ScrollPanelWidget | 树形列表：`UpdateNodes:56`、`AddNodeToWidget:63`、`CalculateScrollAreaLength:103`(覆写滚动长度)、`AddRoot/RemoveRoot/RemoveAtTag/Clear:105-124`；TreeViewNode`:143`(Init:222/EnsureVisible:291)；TreeViewNodeContentItem`:351`(Update:390) | 每次全量重建行 |
| 〔签〕ModDependencyInfoWidget.cs | FixedSizePanelWidget | 依赖信息行(`:9`) | — |
| 〔签〕ModSettingItemWidget.cs | 多类 | 模组设置项框架：接口`:14`、基类 UniformSpacingPanelSettingWidget`:39`、Bool`:117`/EnumDialog`:159`/EnumSlider`:199`/Number`:256` | Supports(Type) 分派 |
| 〔签〕ModsManageContentItemWidget.cs | StackPanelWidget | 模组管理列表项(`:5`) | — |
| 〔签〕Community/CommunityDownloadQueueItemWidget.cs | CanvasWidget | 下载队列行：`ApplySelection:20` | — |
| 〔签〕Community/CommunityMissingDependencyDisplayData.cs | — | 3 个 sealed 显示数据类(`:2/10/20`) | 纯数据 |
| 〔签〕Community/CommunityMissingDependencyFileWidget.cs | FixedSizePanelWidget | 缺失依赖文件行(`:4`) | — |
| 〔签〕Community/CommunityMissingDependencyGroupWidget.cs | FixedSizePanelWidget | 缺失依赖分组：`Update:30` | — |
| 〔签〕Community/CommunityMissingDependencyPackageHeaderWidget.cs | StackPanelWidget | 包头行(`:4`) | — |
| 〔签〕Community/CommunityMissingDependencyPackageWidget.cs | StackPanelWidget | 包行(`:4`) | — |
| 〔签〕Community/CommunityModVersionData.cs | — | 版本显示数据(`:4/28`) | 纯数据 |
| 〔签〕Community/CommunityModVersionFileWidget.cs | FixedSizePanelWidget | 版本文件行(`:4`) | — |
| 〔签〕Community/CommunityModVersionWidget.cs | FixedSizePanelWidget | 版本块：`SetExpanded:57` | — |
| 〔签〕Community/CommunityToastWidget.cs | CanvasWidget(内部sealed) | 提示气泡：`Show:32`、`Hide:78`、`Update:88` | internal，外部不可直接 new |
| 〔签〕Community/CommunityTreeViewWidget.cs | TreeViewWidget | 社区页树：`UpdateNodes:52`、`InvalidateRows:66` | — |

## 快查路由

| 我想… | 去/看 |
|---|---|
| 找某控件属于哪家族/继承谁 | 本页十节小标题 + 每行"继承"列 |
| 查布局算法细节 | 二、布局容器族各行 → 09 页"布局"节 |
| 查输入/命中/拖放 | 三、交互族 + 09 页"命中测试与输入抽象全链"节 |
| 查文本断行/本地化 | 四、文本族 FontTextWidget 行 |
| 查富内容（MD/HTML）入口 | 五、RichContent 公共 + 09 页"富内容管线"节 |
| 查物品面板绑定哪个组件 | 八族各行 Update 行号 → 对应 Component*（跨域另见 10-SC引擎其它页） |
