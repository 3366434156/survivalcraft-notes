# A30 · Game 根 226 文件深度补全报告

> 批次: A30a · 日期: 2026-10-31 · 对象: `E:\SurvivalcraftAPIProject\Survivalcraft\Game\` 根目录 226 文件（16a 明细页）；不涉 Community 72 文件（16b）。

## 一、分类方法与结果

184 个非★▲行（实数 186，原台账标 ★38/▲4 与逐行实数差 1+1，实为 ★37+▲3+空 186）逐行 grep 全库核实归属，分两类：

- **(a) 指针族 = 108 文件**：行内/表头明确"归 NN 页"且目标页确实覆盖（grep 命中文件名或家族机制）。
- **(b) 真签名级 = 78 文件（共 7836 行）**：无归属，或归属页经 grep 证实未覆盖——全部逐文件全文实读并升级为 ★。

补全后 16a 状态：★115（原 37 + 补 78）+ ▲3 + 指针族 108 = 226。

## 二、(a) 指针族清单（108，含指针修正）

| 家族 | 文件 | 归属（核实结果） |
|---|---|---|
| 弹射物 1 | ProjectileStoppedAction | 13 页:73 ✓ |
| 相机 13 | Camera 及 12 相机子类 | 10/10a 页 ✓ 全部点名 |
| 粒子 28 | ParticleSystem 族（除 PrecipitationShaftInfo） | 07/07a 页 ✓ 全部点名 |
| 地形/生成器 19 | Terrain/TerrainChunk/TerrainChunkState/TerrainUpdater/TerrainBrush/ITerrainContentsGenerator/TerrainGenerationMode/Generator21-24/Flat/ChunkGenerationStep | 05/05a 页 ✓ |
| 区块序列化 4 | TerrainSerializer129/14/22/23 | **修正：05a 页点名（原写 11 页错误，11 页 0 命中）** |
| 版本转换 12 | VersionConverter + 11 个 XToY | 11 页 ✓（链机制 :64/:98/:129，范例 21To22；10To14/21To22/22To23 另在 05 页 :118-119 点名；其余 8 个为链成员，结构同范例） |
| 实体引用 1 | EntityReferenceHumanReadableConverter | **修正：11 页:124（原写 03 页，03 页 0 命中）** |
| 渲染 10 | ModelShader/ShaderCodeManager/ICustomModelRenderer→06；TextureAtlas/TextureAtlasManager/Subtexture→20/22/09a；BlockColorsMap→04a；GlowPoint→15/03a；ICustomModelWidgetRenderer→09 | 各自专页 ✓（原表头只写 06 页，已按实际改） |
| 电学 6 | ElectricConnection/Path/ConnectorDirection/ConnectorType/MemoryBankData/TruthTableData | 15/15a 页 ✓ |
| 寻路 1 | CreatureCategory | 03 页 ✓（仅此一个） |
| 输入设备 4 | TouchInput/TouchInputType→10/10a；VrEye→10a/19a；LayoutDirection→09a | ✓ |
| 方块射线 1 | BodyRaycastResult | 13 页 ✓ |
| 基础设施 12 | Program/GameLogSink→01；Progress/CancellableProgress/ZipArchive/FileAlreadyExistsException/ExternalContentType→12/18/20/17a 等；CharacterSkinsCache→09a；HelpTopic→17；UpdateOrder/IUpdateable/INoiseListener→02/03/02a | ✓ |

## 三、(b) 真签名级清单（78 文件 7836 行，全部全文实读升级 ★）

| 家族 | 文件（行数） | 定性 |
|---|---|---|
| 玩家会话枚举 6 | AimState(6)/LookControlMode(6)/MoveControlMode(5)/VrLookControlMode(6)/VrMoveControlMode(6)/BreathingMode(5) | 无归属（表头自称"本页深读"却未读） |
| 伤害结算 2 | TypedInjury(57)/IInjurable(13) | 无归属 |
| 家具 1 | FurnitureInteractionMode(8) | 无归属 |
| 世界设置 2 | GameplayImpactLevel(31)/PrecipitationType(5) | 前者无归属；后者归 14 页但 14 页 0 命中 |
| 寻路 5 | AStar(200)/IAStarStorage(8)/IAStarWorld(12)/PathfindingResult(14)/PathRenderer(657) | 归 03 页但 03 页 0 命中（"寻路/A*"零出现） |
| 地形几何 6 | TerrainChunkGeometry(28)/TerrainChunkSliceGeometry(66)/TerrainGeometry(106)/TerrainGeometryDynamicArray(17)/TerrainGeometrySubset(25)/TerrainVertex(23) | 归 05 页但 05/05a 均未点名这 6 个 |
| 粒子 1 | PrecipitationShaftInfo(8) | 07/07a 均未点名 |
| 渲染 14 | BlockGeometryGenerator(2471)/BlockMesh(771)/BevelledShapeRenderer(491)/SkyShader(80)/SkyPrimitiveRender(94)/BlocksTexturesCache(23)/DrawBlockEnvironmentData(32)/BlockMeshVertex(14)/InstancedModelData(15)/SkyRenderingMode(6)/DrawBlockMode(7)/GeometrySubsetType(6)/ModelRenderingMode(7)/GlowPointType(7) | 归 06 页但 06 页只覆盖 ModelShader 等 4 个；两个巨型文件全库（除 16a/16 自身与 A2 报告一笔带过）零覆盖 |
| 电学 1 | PistonMode(6) | 15/15a 页 0 命中 |
| 数学工具 15 | SimplexNoise(783)/StringUtils(199)/SortedMultiCollection(191)/ArrayCache(126)/Random(117)/CellFace(163)/StateMachine(79)/CollectionUtils(80)/EnumUtils(63)/Segment2(74)/Segment3(52)/FloatCurve(41)/RunningAverage(30)/MatrixUtils(23)/IntervalUtils(14) | 无归属 |
| 输入设备 4 | DeviceManager(15)/GuiSize(8)/TextOrientation(5)/ResolutionMode(6) | 归 10/09 页但 0 命中（DeviceManager 仅 16 页自表） |
| 方块支撑 7 | BlockDropValue(20)/FluidInfo(17)/BlockPlacementData(14)/BlockAllocateData(8)/BlockDigMethod(7)/TreeType(9)/RaycastMode(6) | 归 04/13 页但 0 命中（04 页:39 命中的是 Managers 里同名 Comparer） |
| 基础设施 14 | Profiler(167)/CommunityContentEntry(38)/ZipArchiveEntry(28)/DataSizeFormatter(29)/DebugMenuItemAttribute(11)/UserInfo(11)/ExternalContentEntry(12)/DebugItemAttribute(9)/ActiveExternalContentInfo(8)/CommunityContentMode(7)/FloatListDebugMenuItemAttribute(13)/DebugInfo(7)/DebugItemsContainerAttribute(5)/BuildConfiguration(5) | 归 01/12 页但这些文件 0 命中（03a:78 命中的 DebugInfo 是 Behavior 字段） |

**总实读行数：7836 行（78 文件全文）**；另核实性抽查若干专页与 grep 定位。

## 四、新发现 Top 机制（本次深读产出的实质结论）

1. **BlockGeometryGenerator（2471 行）是方块→顶点的真正中央工厂**：6 面×(4 顶点+6 索引)标准立方、四角高度版（任一 height<1 强制画顶面 :1096-1110）、UV 旋转版三重载；X 形植物 2 面片且 UV 按坐标奇偶随机镜像(:155-365)；顶点光照=该面 2×2 邻域 4 格取 max 光再减阴影/7(:2138-2240)；电线顶点逐连接画线段、贴实心面时伪随机抖动防穿模(:1956-1961)；平滑光照版 GenerateShadedMeshVertices 用 6 面×8 角缓存+三线性插值（API 扩展）。
2. **BlockMesh（771 行）是模型/图像→CPU 网格的烘焙器**：AppendModelMeshPart 烘模型部件时非发光顶点乘 `LightingManager.CalculateLighting`、Face 由法线最大点积决定；`ReadInternalVertices` 双路径支持 glTF 蒙皮顶点布局（按偏移提取，失败抛异常而非跳过，注释明说理由）；BlendBlockMesh 等顶点数 Lerp 是弩 16 档拉弓动画的实现；GetVertexData/GetIndexData 硬性要求 VB/IB.Tag 存原始 byte[]。
3. **A* 族 03 页从未覆盖**：泛型 AStar<T>（节点池+二叉堆+maxPositionsToCheck 限步回退 H 最小节点）+PathRenderer（2D 描边路径渲染器，BevelledShapeRenderer 的底座）全在 Game 根；已改由 16a 承载并回填 16 页范例。
4. **两个死文件**：TerrainChunkSliceGeometry 全类被注释（"From original game, not used in API"，API 用 TerrainGeometry 替代）；DeviceManager 全文注释（Android 设备信息）。另 SkyShader.cs 的命名空间是 Engine.Graphics 而非 Game。
5. **SimplexNoise 不带世界种子**：m_permutations 是 512 项硬编码表，种子化靠生成器做坐标偏移；2D 输出≈[0,1]（35f 缩放+0.5），3D 同理（16f+0.5）；OctavedNoise 有 ridged 脊状模式。
6. **SortedMultiCollection.Find 是"找最后一个匹配键"**（注释 "Edited by Deepseek" :164）——重复键语义与常规字典不同；未命中返回 ~插入点。
7. **TerrainGeometry 的 API 扩展**：7 子集协议（0-3 侧 Opaque/4 顶 Opaque/5 AlphaTest/6 Transparent）+按纹理分 Draws 字典（GetGeometry 惰性建子几何）；TerrainGeometryDynamicArray 的顶点数组全部走静态 ArrayCache 池（2^n 桶，双阈值 0.66/60s、0.33/5s 自动清池，Window.LowMemory 联动）。
8. **GameplayImpactLevel 是 mod 平衡性五档协议**（Cosmetic/Assist/Turbo/Break/Godmode，中文 XML 注释），由 ModInfo 标注、GameMenuDialog/PlayerStats/ModsManager 消费——本 API 项目的 mod 分级元数据。
9. **IInjurable 接口含 5 类韧性**（虚空/溺水/熔岩/挤压/尖刺/爆炸），是 ComponentHealth 的契约面；TypedInjury 6 子类里 BlockInjury 的 BlockValue 惰性回读地形、SuicideInjury 第 4 参 true 标自杀。
10. **小坑集**：DataSizeFormatter <1024 字节显示"1KB"；StringUtils.AppendNumber 负数占位 padding-1、float 超 1E19 显示"NumberTooLarge"；AStar ctor 校验 ClosedStorage 的 if 复制粘贴误判 OpenStorage(:53-55)；PistonMode 有第三档 StrictPulling；CellFace 面协议 0..5=+Z,+X,-Z,-X,+Y,-Y（GetHashCode 位混淆 (X<<11)+(Y<<7)+(Z<<3)+Face）。

## 五、页面改动

1. **`01-引擎\明细\16a-Game明细.md`**：整体重写一次写回。列结构与行序保持；78 个 (b) 行升级为 ★+行号级要点；指针修正 3 处（TerrainSerializer×4 → 05a；EntityReference 族 → 11 页；渲染表头按实际覆盖拆分到 06/20/22/09/04a/15）；各家族表头括注同步实际覆盖；状态行改"全读(226/226：★115+▲3+指针族 108；A30a 补全)"。
2. **`01-引擎\16-玩法物品与背包.md`**（外科手术式 3 处）：状态行同步（根目录 226 全补：★115+▲3+指针族 108）；家族表"寻路 A*"归属改 16a（03 页不覆盖）、"实体引用"归属改 11 页(:72/:124)；原版范例表回填 1 行"给生物接自定义 A* 寻路"（AStar.cs:43-118 + IAStarWorld/IAStarStorage/PathfindingResult）。
3. **`99-深读报告\A30-Game根深度补全报告.md`**：本报告。

## 六、遗留

1. **16b（Community 72 文件）未动**：本批次范围仅 Game 根；16b 状态行未核实未改。
2. **版本转换 8 个链成员（20To21/23To24/112To113/113To114/120To121/121To122/126To127/128To129，约 680 行）未逐个全文读**：11 页已覆盖链机制且结构同 21To22 范例（SourceVersion/TargetVersion/Transform 三件套），16a 行保持指针族并注明；如需逐个行号级可开 A30b。
3. **相机 13 文件仅在 10/10a 有行**，本次未复核 10a 每行质量（grep 确认点名即通过）。
4. 16 页"分工边界"一行仍写"地形/生成器/区块序列化 → 05/05a"，与 16a 修正一致，未再改动。
5. 源码零写入，全程只读；未执行任何 git 写命令。
