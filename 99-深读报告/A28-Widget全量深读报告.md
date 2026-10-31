# A28 深读报告 · Widget 域签名级/节选 72 文件升为全文深读

> 任务: 把 09a 中全部〔签〕与〔节〕行升级为全文深读并回写。日期: 2026-10-31。
> 源码: E:\SurvivalcraftAPIProject\Survivalcraft\Widget\（只读，未做任何修改）。

## 一、统计

- 本轮全文实读 **72 个文件**（69 个〔签〕+ 3 个〔节〕：GamesWidget/ViewWidget/RichTextWidget）。任务书写的"71 签"与 09a 实际行数（69）略有出入——旧状态行"32深+3节+71签=106"本身与逐行标注（34 深+3 节+69 签）不一致；升级后全部归〔深〕，总数 106/106 不变，账目差随旧状态行一并消除。
- 总实读源码行数 **约 15,900 行**（09a 全文 + 00-规则 另计）；最大单件 HtmlToWidgetsBuilder.cs 3490 行逐行读完，其次 GamesWidget 836、RichTextWidget 746、HtmlSpanParser 622、ModelWidget 601、RichContentImageLoader 576。
- 09a 重写：72 行全部升级为真实行号级要点（关键方法+行号、默认值陷阱、坐标系/焦点/输入坑），列结构与十节行序不变；状态行改"全读(全文深读106/106；A28 将 71 签名级+3 节选升为全文)"。09 主页状态行同步（外科手术式单行）。
- 新增 09 主页回填：坑与对策 +3、原版范例 +2（见第三节），并修正"MarkdownTableWidget 瀑布削峰列协商"过时表述（现为 TablePanelWidget 底座协商+超宽切滚动，`MarkdownTableWidget.cs:24` 文件头自述）。

## 二、新发现机制/坑 Top 清单（按重要性）

1. **UniformSpacingPanel 竖排嵌竖排 StackPanel 崩整页**：主轴 DesiredSize=∞ 的容器放进竖排 StackPanel，上层经 layoutTransform 参与排列时算出 NaN 直接崩（`ModSettingItemWidget.cs:37-38` 选型注释 + `:272-274` NumberSlider 实证，"整个页面 widget 崩"）。引擎内所有"一行设置项"一律 Horizontal。已回填 09 坑与对策。
2. **富内容图片纹理生命周期全链**：widget 树无 Dispose 级联 → 持有 Texture2D 的部件必须在 `UpdateCeases` 释放；RichContentImageLoader 用代际计数（`m_generation`，`:39`）使 ReleaseTextures 后晚到的下载回调就地销毁新纹理（`:320-339`）、并发同 URL 后到者释放复用先到（`:340-355`）。纹理缓存比较器必须 Ordinal——base64 data URI 大小写敏感，IgnoreCase 会串图（`:30-33`）。已回填 09 坑与对策。
3. **TreeViewWidget 的重建时机在 Draw 不在 Update**：`m_widgetsDirty` 在 `Draw:48-54` 消费 → AddRoot/展开后下一帧才显示；且 ArrangeOverride 里 ActualSize 变化也置脏（`:90-93`）。节点模型增删改完全不自动重建，`CommunityTreeViewWidget.InvalidateRows:66-68` 是官方认可的补丁路径；`new SelectedNode:25-38` 因引擎 m_selectedNode 在 Clear 后不重置而按"仍可达"过滤。已回填 09 坑与对策。
4. **HtmlToWidgetsBuilder 的 ctx 传导体系**（3490 行核心架构）：8 路继承上下文参数族（对齐/wordBreak/nowrap/line-height×2/opacity/letter-spacing/font-size）随容器递归链透传；opacity 是叠乘语义（`ResolveOpacityMultiplier:3095`），word-break/line-height/letter-spacing 是替换语义，font-size 分绝对换底/相对乘（`ResolveFontScaleCtx:3102-3108`）。防双淡纪律：壳装饰色乘 v、文字走 ColorTransform=White×v，两路各恰一次（footer 行内形态 v² 教训 `:1272-1280`、img 分层落点 `:3273-3328`）。
5. **文本排版-绘制同源不变量**（RichTextLayout/RichTextWidget）：字符推进量唯一出处 `CharacterAdvance:388-396`；挂链字符矢量实测、缺字回退位图预算（粗体 ×GetBoldAdvanceScale 仅位图回退路径需要）。装饰 run（背景/边框/删除线/下划线/链接，`HasSpanDecoration:374-380`）矢量段改逐字符量测/定位，代价是丢段内 kerning——否则灰底右缘与后续文字间距随 run 长度累积漂移（实测 +5~6px/行）。"1.5rem" 以 em 结尾，rem 判定必须先于 em（三处独立注释：HtmlSpanParser:397、HtmlToWidgetsBuilder:2890、CssTransformParser 同型）。
6. **RichTextWidget 三批分层渲染**：背景/下划线/边框 FlatBatch layer=-1、文字 FontBatch layer=1、**删除线 layer=2 必须画在文字上**——Pericles 烘焙黑描边会把垫底的删除线切成暗缝（实测穿越处亮度 255→128，`:282-284`）。伪粗体=同串横偏 1×FontScale 双绘、伪斜体=12° 切变绕 em 中点（非基线，Pericles 未暴露基线）。文字像素整栅对齐：FontBatch 内部 Round 在局部空间、批末叠加 GlobalTransform 平移会落半像素相位 → 显式对齐+DisableSnapToPixels（`:348-364`）。
7. **HTML 表格列对齐 M1 模拟**：builder 侧逐格定列号必须照底座 ExpandSlots 口径模拟（cursor 跳过前行 rowspan 占格、span 展开钳自然列数，`:2431-2522`）——两侧任一单改即错列；col/colgroup 偏好按"活位 rank"落轨（死位后的位前移，`:2349-2428`）；colspan/rowspan 属性钳 1000 防 alignments 扩容+`new float[columns]` 双重内存爆炸（`:2703-2704`）。
8. **测量期回填的两条纪律**：RichContentPanel 无界分支（协商首遍 ∞ 探测）必须逐帧还原 shell 宽协商输入（CodeBlock=NaturalWidth、其余=−1），否则读到上帧回填值列宽逐帧缩至 50 保底的"棘轮"（`RichContentPanel.cs:89-93`）；HtmlBlockSizerWidget.ResolveAncestorCap 用静态栈池做父到子 cap 递推（每节点 margin 恰扣一次，`:41-56`）。宿主壳回填时 % 缩进分母防 ∞（availableWidth<1e7 才做基准，`RichTextWidget.cs:692`）。
9. **ModelWidget 暂停时动画照跑**：Update 由 UI 层级驱动且 `Time.FrameDuration` 是实时帧增量 → 暂停不暂停与 UI 预览无关（`:531-532` 注释）；controller 驱动前先清全骨骼 null（回退 rest pose），controller/player 双向互斥（AddModel(config) 移除 player、PlayAnimation 移除 controller）。glTF 蒙皮=整局部变换替换，DAE=保留平移只换旋转缩放（`ProcessBoneHierarchy:581-591`）。
10. **散点坑**：StarRatingWidget 点最左格也给 1 星（floor(5x/宽+1)）且不 Clear 吞点击；LegacyTextBoxWidget 桌面 Ctrl+V 是 `Text+=` 尾追加非插光标处、Obsolete 消息文案自引用错误；BusyBar 动画推进藏在 Draw（不画不动）；MoveRose 只支持 4 向无斜向且 Draw 内每帧 ContentManager.Get 两次；CraftingRecipeSlot 配料多命中按秒轮换；跨性/社区面板通用自毁模式 `!IsAddedToProject → ParentWidget.Children.Remove(this)`（Chest/Furnace/CraftingTable/Dispenser/Bow/Crossbow/Musket 共 7 处）；CommunityToast 隐藏位按当前高度算（固定 −48 多行滑不出屏）且 Hide 才触发 dismissAction（Reset 不触发）；FurnitureSetItemWidget 高亮消费在 Draw 期自清；width/height 声明 content-box 补偿=声明值+水平 pad/border（`ApplyBlockSizing:292`）。

## 三、回填 09 主页条目

坑与对策新增 3 条：①持有 Texture2D 部件泄漏纹理（UpdateCeases+代际计数）；②TreeViewWidget 改树不生效（Draw 期重建+手动置脏）；③UniformSpacingPanel 竖排嵌竖排 StackPanel 崩整页（layoutTransform NaN，一律 Horizontal）。

原版范例新增 2 行：①"UI 内异步加载图片（占位→下载→上屏）"→ RichContentImageLoader.cs:95-380；②"外部推值与用户操作双向同步（防回环）"→ ModSettingItemWidget.cs:88-108。

另修正 09 页"富内容管线"节一处过时表述（MarkdownTableWidget"瀑布削峰列协商"→"TablePanelWidget 底座列协商+超宽切横向滚动"，与 `MarkdownTableWidget.cs:12-23` 文件头自述一致）。

## 四、遗留问题

- 09a 旧状态行"签名级 71"与实际 69 行的差 2 无从追溯（本轮按实际行数升级），新状态行采用任务书给定文案，账目已闭合。
- HtmlToWidgetsBuilder 的格内（td）回填链依赖 RichContentPanel push/pop（`CreateHtmlCell:2583-2607`），嵌套表格 push/pop 顺序已核正确，但三层以上 td 套 td 的极端组合未逐路径验证（源码注释亦按"嵌套 push/pop 使上下文正确嵌套"口径留档）。
- `Known limitations` 类引擎自述留档（CSS overflow 圆角裁切、white-space pre/pre-wrap、baseline 对齐、text-align:justify、margin auto 单侧、flex order/align-self 等）均在 09a 对应行的"坑"列标注"留档/不做"，未展开成独立页面。
- 本轮未触碰 09 页"核心机制"其余段落与 02-范例配方.md（无新增跨域配方需求）。
