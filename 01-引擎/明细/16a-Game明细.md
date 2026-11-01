# Game 域明细（根目录 226 文件）

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(226/226：★全文深读 127 + ▲头部 3 + 指针族 96 归属专页；A30a/A32 补全)；逐文件一行。主页面另见 16-玩法物品与背包.md；Community 子域 72 文件另见 16b-Game明细2.md。
>
> 前缀：目录 `E:\SurvivalcraftAPIProject\Survivalcraft\Game\`（下表省略）。"声明"=public 类型声明行号。★=深读全文(127，其中 78 行为 A30a 补读、12 行为 A32 补读)，▲=深读头部/关键段(3)，空=指针族——A30a 已逐页 grep 核实归属专页确实覆盖(96)。指针家族的逐行职责以对应专页为准。

## 玩家会话与输入（11，本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `PlayerData.cs` | 703 | ★ | 玩家会话：5 态出生状态机 FirstUpdate→PrepareSpawn→WaitForTerrain→Playing⇄PlayerDead(:142-343)；出生点评分(:420-533)；SpawnPlayer 建实体+默认衣物+初始物品(:553-665)；Save/Load 键表(:376-398) | :7 |
| `PlayerInput.cs` | 73 | ★ | 每 tick 语义输入 struct：Look/Move/Jump/Dig/Hit/Aim/Interact/Drop 等 24 字段 + ValuesDictionaryForMods | :5 |
| `PlayerStats.cs` | 186 | ★ | 玩家统计：30+ 个 [Stat] 反射持久化字段(:61-133)；DeathRecord "日,x,y,z,因" CSV(:11-57)；ValuesDictionaryForMods 扩展 | :8 |
| `PlayerInfo.cs` | 4 | ★ | 世界信息里的玩家占位（仅 CharacterSkinName） | :2 |
| `PlayerClass.cs` | 5 | ★ | 枚举 Male=0/Female=1（决定实体模板 MalePlayer/FemalePlayer） | :2 |
| `AimState.cs` | 6 | ★ | 瞄准状态枚举：InProgress=0/Cancelled=1/Completed=2 | :2 |
| `LookControlMode.cs` | 6 | ★ | 视角控制模式：Pad=0/EntireScreen=1/SplitTouch=2（触摸视角三方案） | :2 |
| `MoveControlMode.cs` | 5 | ★ | 移动控制模式：Pad=0/Buttons=1 | :2 |
| `VrLookControlMode.cs` | 6 | ★ | VR 视角模式：Smooth=0/Snap=1 | :2 |
| `VrMoveControlMode.cs` | 6 | ★ | VR 移动模式：Smooth=0/Teleport=1 | :2 |
| `BreathingMode.cs` | 5 | ★ | 呼吸/憋气模式枚举：Air=0/Water=1（溺水系统用） | :2 |

## 伤害结算（6，本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `Attackment.cs` | 264 | ★ | 一次攻击全链：ProcessAttackment(:213-263)→护甲→韧性→扣血/扣 hitpoints→冲量+眩晕；CalculateInjuryAmount(:82-111)；ArmorProtectionDivision 除数(:71)；类名拼写错误故意保留(:7-11) | :12 |
| `MeleeAttackment.cs` | 29 | ★ | 近战冲量：ImpulseFactor=5.5×saturate(质量比^0.5×攻击力系数)，眩晕 0.25s×系数 | :5 |
| `ProjectileAttackment.cs` | 22 | ★ | 弹射物命中：ImpulseFactor=2、零伤不冲不晕、携带 Projectile 引用 | :5 |
| `Injury.cs` | 68 | ★ | 伤害记录基类：Amount/Attacker/Cause；Process() 走 CalculateCreatureInjuryAmount 钩子后 Injured 事件 | :4 |
| `TypedInjury.cs` | 57 | ★ | 6 个 Injury 子类：AttackInjury(:2，携 Attackment，Attacker 实体找 ComponentCreature)/FireInjury(:11，死因取 LanguageControl ComponentHealth:5)/ExplosionInjury(:20)/BlockInjury(:24，CellFace+SubsystemTerrain，BlockValue 惰性回读地形 :31-43)/VitalStatsInjury(:51)/SuicideInjury(:55，第 4 参 true=自杀，死因 VitalStatsWidget"Choked") | :2 |
| `IInjurable.cs` | 13 | ★ | 可受伤接口：Health/VoidDamageFactor(虚空高差伤害系数)/AirLackResilience(溺水)/MagmaResilience(熔岩)/CrushResilience(挤压)/SpikeResilience(尖刺)/ExplosionResilience(爆炸)/LastHealth + Injure/Die；ComponentHealth 实现 | :2 |

## 库存与物品（7，本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `IInventory.cs` | 30 | ★ | 库存槽位契约 10 成员：SlotsCount/VisibleSlotsCount/ActiveSlotIndex/GetSlot{Value,Count,Capacity,ProcessCapacity}/Add/Process/RemoveSlotItems/DropAllItems | :5 |
| `InventoryDragData.cs` | 8 | ★ | 拖拽状态：Inventory+SlotIndex+DragMode | :2 |
| `DragMode.cs` | 6 | ★ | 拖拽模式枚举 | :2 |
| `ScannedItemData.cs` | 18 | ★ | 扫描结果项：Container/IndexInContainer/Value/Count + mod 扩展袋 | :4 |
| `IEditableItemData.cs` | 8 | ★ | 可编辑物品数据接口（MemoryBank/TruthTable 实现） | :2 |
| `CreativeInventoryPanel.cs` | 97 | ★ | 创造目录面板：槽 0-9 手部、10+ 目录，按 Block.GetCategory 过滤分页(:54-90) | :5 |
| `FurnitureInventoryPanel.cs` | 407 | ★ | 家具集合面板：按 FurnitureSet 过滤 227 号方块槽分页(:196-225)；新建/重命名/删除/移动/导入导出 .scfpack(:227-406)；集合上限 32(:100) | :5 |

## 世界掉落物（2，本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `WorldItem.cs` | 35 | ★ | 掉落物/弹射物共同基类：Value/Position/Velocity/Creator/IsFireProof/MaxTimeExist/ExplosionMass + mod 数据袋；非实体，由 Subsystem 列表管理 | :5 |
| `Pickable.cs` | 563 | ★ | 掉落物：寿命随场上数量(:174-196)；手写移动/反弹/浮力(:198-424)；StuckMatrix 钉住(:315-329)；火/岩浆连锁 TryExplodeBlock(:330-405)；UnderExplosion 转弹射物(:441-476)；Save 写类名多态(:549) | :7 |

## 弹射物弹道（2 → 13-物理与碰撞.md）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `Projectile.cs` | 702 | ▲ | 弹射物：Rotation/AngularVelocity/IsInFluid/TrailParticleSystem/Gravity/Damping 等参数 + 飞行模拟 | :7 |
| `ProjectileStoppedAction.cs` | 6 | | 弹射物停止后行为枚举（13 页:73 覆盖：转 Pickable 或消失） | :2 |

## 合成（1，本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `CraftingRecipe.cs` | 27 | ★ | 配方记录：9 格 string 配料 Ingredients + Result/Remains + RequiredHeatLevel/RequiredPlayerLevel + DisplayOrder(:26) | :2 |

## 食物（1，本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `FoodType.cs` | 9 | ★ | 枚举 None/Meat/Fish/Fruit/Grass/Bread（营养系统分类） | :2 |

## 服装（2，本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `ClothingData.cs` | 238 | ★ | 单件衣物运行数据：XML 属性解析(:11-53)；护甲吸收公式 ApplyArmorProtection(:122-167)；随时间磨损(:175-218)；OnClotheSet 聚合保温/密度(:224-228) | :8 |
| `ClothingSlot.cs` | 58 | ★ | 衣物部位注册表：Head/Torso/Legs/Feet 基础保温(:35-38)；mod 可 AddClothingSlot(:14)；切语言重入只补缺(:22-30) | :2 |

## 家具（4）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `FurnitureDesign.cs` | 1201 | ▲ | 家具设计：体素数组 m_values+分辨率(:47-49)；上限 8192(:25)；LinkedDesign 链(:170)；Hash 去重(:77)；旋转/镜像点变换(:1158-1177)；GC 标记(:43) | :8 |
| `FurnitureSet.cs` | 6 | ★ | 家具集合：Name + ImportedFrom | :2 |
| `FurnitureGeometry.cs` | 17 | ★ | 家具网格容器：6 面×3 透明度 BlockMesh 数组 + 按自定义纹理分组 | :4 |
| `FurnitureInteractionMode.cs` | 8 | ★ | 家具交互模式：None=0/Multistate=1/ElectricButton=2/ElectricSwitch=3/ConnectedMultistate=4 | :2 |

## 世界设置/信息/模式（15，本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `WorldSettings.cs` | 165 | ★ | 世界参数全集：字段表(:5-62)；双模式 Save——live 参数恒存、种子/地形仅建档写(:134-163)；ResetOptionsForNonCreativeMode 强校验(:64-101) | :5 |
| `WorldInfo.cs` | 16 | ★ | 世界信息袋：目录名/大小/最后保存/序列化+API版本/WorldSettings/PlayerInfos | :2 |
| `WorldPalette.cs` | 96 | ★ | 世界调色板：16 色默认表(:10-27)；Save 只存非默认项(:65-75)；颜色名校验(:82-95) | :6 |
| `GameMode.cs` | 9 | ★ | 枚举 Creative0/Harmless1/Survival2/Challenging3/Cruel4/Adventure5（顺序即难度协议） | :2 |
| `EnvironmentBehaviorMode.cs` | 5 | ★ | 枚举 Living0/Static1（环境是否活跃） | :2 |
| `TimeOfDayMode.cs` | 8 | ★ | 枚举 Changing/Day/Night/Sunrise/Sunset | :2 |
| `Season.cs` | 7 | ★ | 枚举 Summer0/Autumn1/Winter2/Spring3 | :2 |
| `StartingPositionMode.cs` | 6 | ★ | 枚举 Easy/Medium/Hard（初始装备档次） | :2 |
| `GameplayImpactLevel.cs` | 31 | ★ | 玩法影响等级 5 档（mod 平衡性标注）：Cosmetic=0 纯装饰/Assist=1 轻辅助(小地图等)/Turbo=2 强辅助(一键撸树等)/Break=3 规则破坏(飞行等)/Godmode=4 上帝；ModInfo 标注，GameMenuDialog/PlayerStats/ModsManager 消费 | :5 |
| `SpawnChunk.cs` | 12 | ★ | 出生区块记录：Point/IsSpawned/LastVisitedTime/SpawnsData | :4 |
| `SpawnEntityData.cs` | 14 | ★ | 出生实体项：TemplateName/Position/ConstantSpawn/Data/EntityId | :4 |
| `SpawnLocationType.cs` | 6 | ★ | 枚举 Surface/Cave/Water | :2 |
| `BestiaryCreatureInfo.cs` | 34 | ★ | 图鉴生物条目：属性面板(Mass/AttackResilience/AttackPower/速度/跳跃)+Loot 列表 | :4 |
| `SignData.cs` | 9 | ★ | 告示牌内容：4 行文本+4 色+Url | :3 |
| `PrecipitationType.cs` | 5 | ★ | 降水类型：Rain=0/Snow=1（14 页未覆盖，A30a 改本页深读）；配 PrecipitationShaftInfo(:2) 使用 | :2 |

## 寻路（6：CreatureCategory → 03 页，其余 5 文件本页深读；03 页不覆盖 A* 族）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `AStar.cs` | 200 | ★ | 泛型 A*：Node{Position,PreviousPosition,F,G,H}(:5-15)；FindPath(:43-118) 带 maxPositionsToCheck 上限，超限回退 H 最小节点当目标(:97-100)；Cost=∞ 剪枝(:92)；节点对象池 NewNode(:188-199)；二叉堆 Enqueue/Dequeue/Update(:120-186，Update 线性找位)；坑：ctor 校验 ClosedStorage 的 if 复制粘贴误判 OpenStorage(:53-55) | :4 |
| `IAStarStorage.cs` | 8 | ★ | A* 存储接口 3 成员：Clear/Get/Set（开放/关闭集抽象） | :2 |
| `IAStarWorld.cs` | 12 | ★ | A* 世界接口 4 成员：Cost/Neighbors/Heuristic/IsGoal | :4 |
| `PathfindingResult.cs` | 14 | ★ | 后台寻路结果：volatile IsCompleted + IsInProgress + PathCost + PositionsChecked + Path(DynamicArray\<Vector3\>) | :4 |
| `PathRenderer.cs` | 657 | ★ | 2D 描边路径渲染器（生物路径/调试线框，BevelledShapeRenderer 的底座）：Point 双侧内外半径+颜色 struct(:6-67)；TrimPathStart/End 视野裁剪（Ray2 求交 :75-129)；GeneratePathNormals miter 法线(:131-175)；QueuePath FlatBatch2D/TexturedBatch2D 双族重载(:177-417)；MiterLimit 超限退化直法线(:443-448)；Normal2 长度=tan((π-夹角)/2)(:652-656) | :5 |
| `CreatureCategory.cs` | 9 | | 生物类别枚举（03 页覆盖） | :3 |

## 实体引用（2 → 11-存档持久化.md；03 页不覆盖，A30a 已核实）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `EntityReference.cs` | 180 | ▲ | 实体引用 struct：null:/local:/id:N:name:S 四种字符串协议(:19-35)；GetEntity/GetComponent 解析(:39-72)；存档语义见 11 页:72 | :5 |
| `EntityReferenceHumanReadableConverter.cs` | 9 | | EntityReference 的人类可读序列化适配器（11 页:124 覆盖：双向各一行注册） | :5 |

## 相机（13 → 10-输入与相机.md，10a 逐行）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `Camera.cs` | 58 | | 抽象相机基类 | :5 |
| `BasePerspectiveCamera.cs` | 242 | | 透视相机中层基类 | :5 |
| `FppCamera.cs` | 39 | | 第一人称相机 | :4 |
| `TppCamera.cs` | 153 | | 第三人称相机（含遮挡处理） | :4 |
| `DeathCamera.cs` | 82 | | 死亡视角相机 | :4 |
| `DebugCamera.cs` | 136 | | 调试自由相机 | :6 |
| `FixedCamera.cs` | 37 | | 固定机位相机 | :4 |
| `FlyCamera.cs` | 66 | | 飞行相机 | :5 |
| `IntroCamera.cs` | 55 | | 开场运镜相机 | :4 |
| `LoadingCamera.cs` | 18 | | 加载画面相机 | :4 |
| `OrbitCamera.cs` | 169 | | 环绕相机 | :4 |
| `RandomJumpCamera.cs` | 43 | | 随机跳切相机 | :4 |
| `StraightFlightCamera.cs` | 24 | | 直线飞行相机 | :4 |

## 粒子（29 → 07-粒子系统.md；唯 PrecipitationShaftInfo 07 页未列，本页深读）

| 文件 | 行 | 职责 | 声明 |
|---|---|---|---|
| `ParticleSystem.cs` | 165 | 泛型粒子系统基类（T:Particle） | :5 |
| `ParticleSystemBase.cs` | 81 | 粒子系统抽象基类 + 批次需求结构 | :6 |
| `Particle.cs` | 28 | 粒子基类 | :4 |
| `ParticleBillboardingMode.cs` | 7 | 广告牌模式枚举 | :2 |
| `ITrailParticleSystem.cs` | 8 | 拖尾粒子接口 | :4 |
| `PrecipitationShaftInfo.cs` | 8 | ★ 降水柱参数 struct：Type(PrecipitationType)/Intensity/YLimit；SubsystemWeather 与 PrecipitationShaftParticleSystem/篝火/地毯 BlockBehavior/ComponentLevel 消费 | :2 |
| `PrecipitationShaftParticleSystem.cs` | 358 | 雨雪柱系统（独立于泛型基类） | :6 |
| `BlockDebrisParticleSystem.cs` | 111 | 方块碎屑 | :5 |
| `BurntDebrisParticleSystem.cs` | 94 | 烧焦碎屑 | :5 |
| `ExplosionParticleSystem.cs` | 83 | 爆炸闪光 | :5 |
| `FireParticleSystem.cs` | 88 | 火焰 | :5 |
| `FireworksParticleSystem.cs` | 230 | 烟花 | :5 |
| `FireworksTrailParticleSystem.cs` | 66 | 烟花拖尾 | :5 |
| `FuseParticleSystem.cs` | 77 | 引信火花 | :5 |
| `GunSmokeParticleSystem.cs` | 95 | 枪口烟 | :5 |
| `HitValueParticleSystem.cs` | 112 | 伤害飘字 | :6 |
| `KillParticleSystem.cs` | 66 | 击杀特效 | :5 |
| `LeavesParticleSystem.cs` | 142 | 落叶 | :5 |
| `MagmaSplashParticleSystem.cs` | 106 | 岩浆飞溅 | :5 |
| `OnFireParticleSystem.cs` | 87 | 燃烧附着 | :5 |
| `PaintParticleSystem.cs` | 101 | 刷漆粒子 | :4 |
| `PukeParticleSystem.cs` | 114 | 呕吐 | :5 |
| `RainSplashParticleSystem.cs` | 107 | 雨点水花 | :5 |
| `ShapeshiftParticleSystem.cs` | 74 | 变身特效 | :5 |
| `SmokeTrailParticleSystem.cs` | 92 | 烟雾拖尾 | :5 |
| `SnowSplashParticleSystem.cs` | 73 | 雪花水花 | :5 |
| `SoundParticleSystem.cs` | 77 | 声音可视化粒子 | :5 |
| `WaterSplashParticleSystem.cs` | 130 | 入水水花（带帧配额 TryBeginInstantiation） | :5 |
| `WhalePlumeParticleSystem.cs` | 88 | 鲸喷水柱 | :5 |

## 地形/区块/生成器/序列化（25：地形/生成器/区块序列化 → 05/05a 页；几何 6 文件本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `Terrain.cs` | 359 | | 世界地形运行时 + ChunksStorage（05 页） | :5 |
| `TerrainChunk.cs` | 248 | | 单区块数据 + BrushPaint（05 页） | :4 |
| `TerrainChunkState.cs` | 13 | | 区块十态状态机枚举（05 页） | :2 |
| `TerrainChunkGeometry.cs` | 28 | ★ | 区块 GPU 几何句柄：TerrainChunk 引用 + 内嵌 Buffer(VertexBuffer/IndexBuffer/Texture + 7 子集起止下标表 :15-21)；Dispose 释放两 buffer(:23-26) | :5 |
| `TerrainChunkSliceGeometry.cs` | 66 | ★ | 死文件：首行注释"From original game, not used in API"，全类被注释——API 用 TerrainGeometry 替代 | :2 |
| `TerrainGeometry.cs` | 106 | ★ | 地形几何容器 7 子集：0-3=四侧 Opaque 面、4=Opaque 通用、5=AlphaTest、6=Transparent(:36-47)；API 扩展按纹理分 Draws 字典(:29-34)，GetGeometry 惰性建子几何(:49-57)，ClearGeometry 递归清后重建默认区(:59-76)；旧 ctor `Obsolete"此方法将弃用"`(:24) | :5 |
| `TerrainGeometryDynamicArray.cs` | 17 | ★ | 地形顶点/索引动态数组：Allocate/Free 接静态 ArrayCache 池（2^n 桶 4..2^33，双阈值 0.66/60s、0.33/5s :16） | :4 |
| `TerrainGeometrySubset.cs` | 25 | ★ | 几何子集：Vertices(TerrainVertex 动态数组)+Indices+Tag 挂钩 object；Dispose=清空（数组回池不释放） | :2 |
| `TerrainVertex.cs` | 23 | ★ | 地形 GPU 顶点 20 字节：Vector3 位置+NormalizedShort2 UV+NormalizedByte4 Color（光/湿/温打包进 Color 通道）；VertexDeclaration(:18-22) | :5 |
| `TerrainUpdater.cs` | 1339 | | 后台逐区块生成推进调度（05 页） | :5 |
| `TerrainRenderer.cs` | 463 | | 地形绘制（06/21 页点名） | :5 |
| `TerrainRaycastResult.cs` | 25 | | 地形射线结果（13 页点名） | :5 |
| `TerrainBrush.cs` | 390 | | 地形笔刷（编辑/生成共用，05 页点名） | :4 |
| `ITerrainContentsGenerator.cs` | 26 | | 生成器接口（05/05a 页） | :4 |
| `TerrainGenerationMode.cs` | 7 | | 地形生成模式枚举（05 页） | :2 |
| `TerrainContentsGenerator21.cs` | 2627 | | v2.1 生成器（05/05a 页） | :5 |
| `TerrainContentsGenerator22.cs` | 2365 | | v2.2 生成器（CavePoint 洞穴，05/05a 页） | :4 |
| `TerrainContentsGenerator23.cs` | 2469 | | v2.3 生成器（05/05a 页） | :4 |
| `TerrainContentsGenerator24.cs` | 2437 | | v2.4 生成器（05/05a 页） | :4 |
| `TerrainContentsGeneratorFlat.cs` | 161 | | 平地生成器（05/05a 页） | :4 |
| `ChunkGenerationStep.cs` | 25 | | 区块生成阶段描述（05/05a 页） | :2 |
| `TerrainSerializer129.cs` | 212 | | v1.2.9 区块序列化（05a 页点名；非 11 页） | :4 |
| `TerrainSerializer14.cs` | 189 | | v1.4 区块序列化（05/05a 页点名） | :4 |
| `TerrainSerializer22.cs` | 213 | | v2.2 区块序列化（05a 页点名） | :4 |
| `TerrainSerializer23.cs` | 783 | | v2.3 区块序列化（IStorage 抽象，05a 页点名） | :7 |

## 存档版本转换（12，本页深读 ★ A32 补全；链机制/反射收集另见 11-存档持久化.md :64/:98/:129；10To14/21To22/22To23 另在 05 页点名）

| 文件 | 行 | 职责 | 声明 |
|---|---|---|---|
| `VersionConverter.cs` | 186 | ★ 抽象基类：SourceVersion/TargetVersion 抽象(:7-9)；ConvertProjectXml 默认仅改 Version 属性(:12-14)；ConvertWorld 默认=读 Project.xml→ConvertProjectXml→写回(:16-26)；文件尾另含 21 个"空转"升档器（只改版本号零改值，补全链空档：14To15:62/111To112:104/114To115:110/119To120:140/122To123:146/125To126:164/127To128:170/129To130:176/130To20:182 等），全链 1.0→2.4 无断档；GenericVersionConverter 已整段注释弃用(:29-61) | :6 |
| `VersionConverter10To14.cs` | 70 | ★ 1.0→1.4：Chunks/ 逐块散文件合并为单文件 Chunks.dat——预写 65537 条空 TOC(:20-22)，逐文件拆名得 cx/cz(:30-32)，TerrainSerializer14.WriteChunkHeader+块体+回填 TOC 偏移(:41-44)，上限 65536 块抛异常(:27-29)，单块失败 Log.Error 跳过(:48-50)；Project.xml 改版本(:55-63)；最后删全部旧块文件与 Chunks 目录(:64-68) | :7 |
| `VersionConverter20To21.cs` | 102 | ★ 2.0→2.1：TerrainGenerationMode "Normal"→"Continent"(:20-22)；从 GameInfo 抠 CharacterSkinName 缺省 "$Male1"(:24-33)；Player 子系统→改名 Players 并重排 Values/Players/1 三层+注入 CharacterSkinName(:34-56)+NextPlayerIndex=2(:57-59)；PlayerStats 旧 Values 套入新 Stats 容器并更名"1"(:61-75)；Name 以 Player 开头的实体统一改 MalePlayer+固定 Guid(:76-81)；删全部实体的 SpawnPool 值(:82-88) | :6 |
| `VersionConverter21To22.cs` | 248 | ★ 2.1→2.2（11 页:129 范例）：TerrainGenerationMode "Flat"→"FlatContinent"(:21-23)；Pickables/Projectiles/CollapsingBlockBehavior 的 Value(:26-73)、6 容器(Inventory/CreativeInventory/CraftingTable/Chest/Furnace/Dispenser :93) 的 Contents(:94-111)、实体 Clothing 分号串(:74-92)全走 ConvertValue(:214-220：10 位 contents/4 位 light 重排 data<<14)；ConvertContentsLightData(:222-247)：contents 30/32/33/34/35→29（旧元件归并）、170→169；ConvertChunks(:153-212)：Chunks32.dat(129 格式 132112B/块)→Chunks32h.dat.new(22 格式 262144B 块体，l>127 层写 0 :183-203)，空间预检 2×文件+50MB(:156-159)；事务化 ConvertWorld(.new 落盘→.old 清理，失败回滚还原再 rethrow :114-138) | :7 |
| `VersionConverter22To23.cs` | 86 | ★ 2.2→2.3（05 页:119 点名：TS22 读→TS23 写）：Project.xml 仅改版本号(:11-13)；ConvertChunks(:70-85)=TerrainSerializer22(null,dir) 逐块 LoadChunk→空 TerrainChunk→TerrainSerializer23(dir,".new").SaveChunkData（IStorage 抽象直读写），空间预检 文件/10+50MB(:71-74)；事务化(:15-55)且自本档起 .new/.old 同时覆盖文件与目录两形态(:24-34, :42-52) | :6 |
| `VersionConverter23To24.cs` | 37 | ★ 2.3→2.4：GameInfo 注入四季系统两新值——AreSeasonsChanging=false(:16-19)、TimeOfYear=IntervalUtils.Midpoint(SubsystemSeasons.SummerStart,AutumnStart)(:20-23) | :6 |
| `VersionConverter112To113.cs` | 43 | ★ 1.12→1.13（Source/Target 实为 "1.12"/"1.13"，主.次协议）：ProcessNode 全树递归属性(:28-35)，把任意 Value="Dangerous" 改 "Normal"(:37-42)（移除危险等级选项） | :6 |
| `VersionConverter113To114.cs` | 43 | ★ 1.13→1.14：与 112To113 完全同构——全树 Value="Dangerous"→"Normal"(:28-42) | :6 |
| `VersionConverter120To121.cs` | 53 | ★ 1.20→1.21：全实体 Body/Frame 值组的 LocalMatrix 经 Matrix.Decompose 拆成 Position(Vector3)+Rotation(Quaternion) 两值(:13-39，Decompose :23-24)并删原矩阵(:35) | :6 |
| `VersionConverter121To122.cs` | 43 | ★ 1.21→1.22：CreatureSpawn 值组改名 Spawn(:17)，其下 CreaturesData→SpawnsData(:21)、CreaturesGenerated→IsSpawned(:26) | :6 |
| `VersionConverter126To127.cs` | 114 | ★ 1.26→1.27：全树 Value 的 Type 命名空间迁移 Microsoft.Xna.Framework.*→Engine.*（Vector2/3/4、Quaternion、Matrix、Point→Point2、Color、Game.Point3→Engine.Point3 共 8 种 :62-92）；另附 1.26 旧数据迁移工具 MigrateDataFromIsolatedStorageWithDialog(:28-60，!ANDROID)：app:/.config/.isolated-storage 递归 MigrateFolder 复制到 data:(:94-107)，完成后重载 SettingsManager.LoadSettings(:51) | :6 |
| `VersionConverter128To129.cs` | 246 | ★ 1.28→1.29：同 21To22 五处目标(Pickables/Projectiles/CollapsingBlockBehavior :14-61、Clothing :62-80、6 容器 Contents :81-99)全走 ConvertValue(:177-183：旧 8 位 contents+light<<8 → 新 10 位 contents+light<<10+data<<14)；ConvertContentsLightData(:185-245)：133-136 归并为 133 且子型挪 data 高 4 位、152/182/185 data 位重排、139 湿度入 data、旧 id 归并 128→21/163→3/164→73/165→67（data<<1|1）；ConvertChunks(:119-175)：Chunks.dat(14 格式 2B/格 65536)→Chunks32.dat(129 格式 4B/格 131072)，l<127 且本格 id 18/92 与上格不同置 0x40000 标记(:149-157) | :7 |

## 渲染/网格/着色器（24：Shader/接口 → 06 页；TextureAtlas 族 → 20/22 页；BlockColorsMap → 04a；GlowPoint → 15/03a；ICustomModelWidgetRenderer → 09 页；其余 14 文件本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `BlockGeometryGenerator.cs` | 2471 | ★ | 方块→TerrainVertex 中央生成器：SetupCornerVertex 亮度=LightIntensityByLightValueAndFace `light+16×face`(:75-98)，SetupVertex UV 编码 short×32767(:140-153)；GenerateCubeVertices 3 重载——标准(:367-795，邻块同 contents 且!GenerateFacesForSameNeighbors 剔除+ShouldGenerateFace)、四角高度版(:797-1238，任一 height<1 强制画顶面 :1096-1110，overrideTopTextureSlot)、UV 旋转版(:1240-1671)；GenerateCrossfaceVertices X 形植物 2 面片 8 顶点，UV 按坐标奇偶镜像(:155-365)；GenerateFlatVertices 单面片(:1673-1739)；GenerateMeshVertices 烘 BlockMesh（IsEmissive 免光照 :1762，Sides 驱动三角级剔除 :1787-1803）；GenerateShadedMeshVertices 平滑光照版（CalculateCornerLights 6 面×8 角缓存 :2401-2453 + 三线性插值 :2455-2470 + facesMap 重映射）；GenerateWireVertices 电线逐连接画线段、In 型接中心偏移、实心面伪随机抖动(:1882-2136, GetRandomWireOffset :2392-2399)；顶点光=2×2 邻域 4 格 max 光−阴影/7(:2138-2240, CombineLightAndShadow :2148) | :4 |
| `BlockMesh.cs` | 771 | ★ | CPU 侧静态网格：Vertices(BlockMeshVertex)+Indices+Sides(每三角面号 sbyte)；AppendImageExtrusion 2D 图沿 Z 挤出（前后盖+四向扫描侧壁 :44-255；带 alphaThreshold 重载按 1px 条带切 :562-671）；AppendModelMeshPart 模型部件烘焙（mod 钩子 OnFirstPersonModelDrawing 可跳原版 :264-285；非发光乘 CalculateLighting :309；Face=Vector3ToFace :312；doubleSided/flipWindingOrder :316-334）；ReadInternalVertices 兼容 glTF 蒙皮顶点按偏移提取(:347-408)；AppendBlockMesh 合并网格(:410-431)；BlendBlockMesh 等顶点数 Lerp 动画(:433-442，弩 16 档用)；Transform*/Set*/ModulateColor 全带 facesMask 位掩码(:444-474)；GenerateSidesData 逐三角按坐标归面 0-5（-1=不贴合 :476-505）；GetVertexData/GetIndexData 要求 VB/IB.Tag 存原始 byte[](:515-549) | :7 |
| `BlockMeshVertex.cs` | 14 | ★ | 网格 CPU 顶点：Position+UV+Color+byte Face+IsEmissive（发光标记→GenerateMeshVertices 免光照） | :4 |
| `BevelledShapeRenderer.cs` | 491 | ★ | 2D 圆角斜面形状渲染器（UI 面板/电路线框底妆，依赖 PathRenderer）：Point{Position,RoundingRadius,RoundingCount}(:6-20)；QueueShape 圆角化→斜边带（光源方向(-1,-2)，bevelSize<0 反向 :64）→Triangulate 耳切填充(:319-353)→抗锯齿内外渐变圈(:95-131)；QueueShapeShadow(:164-197)；Textured 版转 UV(:199-236)；QueueQuad 圆角矩形(:238-304)；RoundCorner 半径=min(邻边×0.49,radius)，count<0 按 0.25px 精度自动分段上限 50(:446-490)；LightPoints 方向光+环境光(:355-394) | :5 |
| `ModelShader.cs` | 224 | | 实体模型着色器（06 页） | :6 |
| `SkyShader.cs` | 80 | ★ | 注意命名空间是 Engine.Graphics：天空图元着色器:TransformedShader；5 参数 WVP/texture/samplerState/color/alphaThreshold(:45-51)；PrepareForDrawingOverride 更新 WVP(:53-56)；宏 USE_VERTEXCOLOR/USE_TEXTURE/USE_ALPHATHRESHOLD(:58-79) | :2 |
| `SkyPrimitiveRender.cs` | 94 | ★ | 天空图元专用 flush：Textured_Flush 196605 三角分段(:12-34)；Flush 自排 Layer 后 TexturedBatch3D 走 SkyShader/AlphaTest 变体并挂 ModsManager.SetShaderParameter mod 钩子(:36-92)，其余走 baseBatch.Flush(:90) | :5 |
| `SkyRenderingMode.cs` | 6 | ★ | 天空渲染模式：Full=0/NoClouds=1/Disabled=2 | :2 |
| `ShaderCodeManager.cs` | 81 | | 着色器代码管理（06 页） | :5 |
| `TextureAtlas.cs` | 52 | | 纹理图集（20/22 页点名） | :6 |
| `TextureAtlasManager.cs` | 68 | | 图集管理（20/22 页点名） | :6 |
| `BlocksTexturesCache.cs` | 23 | ★ | 方块纹理名缓存：GetTexture 未命中走 BlocksTexturesManager.LoadTexture(:7-13)；Clear 只 Dispose 非 ContentManager 托管纹理(:15-22) | :4 |
| `BlockColorsMap.cs` | 86 | | 方块颜色映射（04a 页点名） | :4 |
| `Subtexture.cs` | 27 | | 图集子纹理（20/09a 页点名） | :5 |
| `DrawBlockEnvironmentData.cs` | 32 | ★ | 方块绘制环境参数：DrawBlockMode/SubsystemTerrain/InWorldMatrix/ViewProjectionMatrix?/BillboardDirection?/Humidity(默认15)/Temperature(默认8)/Light(默认15)/Owner Entity（渲染 InventorySlotWidget 与第一/三人称模型时可读拥有者，中文注释 :22）/EnvironmentTemperature? | :5 |
| `DrawBlockMode.cs` | 7 | ★ | 方块绘制模式：World=0/FirstPerson=1/ThirdPerson=2/UI=3 | :2 |
| `GeometrySubsetType.cs` | 6 | ★ | 几何子集类型：Opaque=0/AlphaTest=1/Transparent=2 | :2 |
| `ModelRenderingMode.cs` | 7 | ★ | 模型渲染模式：Solid=0/AlphaThreshold=1/TransparentBeforeWater=2/TransparentAfterWater=3（水体前后分层） | :2 |
| `ICustomModelRenderer.cs` | 43 | | 自定义模型渲染接口（06/02a 页） | :11 |
| `ICustomModelWidgetRenderer.cs` | 7 | | 自定义 Widget 模型渲染接口（09 页） | :2 |
| `IDrawable.cs` | 6 | | 可绘制对象接口（渲染排序用，02/03/06/15 页） | :2 |
| `GlowPoint.cs` | 22 | | 发光点数据（15/03a 页） | :4 |
| `GlowPointType.cs` | 7 | ★ | 发光点形状：Round=0/Square=1/HorizontalRectangle=2/VerticalRectangle=3 | :2 |
| `InstancedModelData.cs` | 15 | ★ | 实例化模型：顶点声明 Position+Normal+UV+Single Instance(:5-10) + VB/IB | :4 |

## 电学/机构数据（7：6 文件 → 15/15a 页；PistonMode 本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `ElectricConnection.cs` | 16 | | 元件间连接记录（15 页） | :2 |
| `ElectricConnectionPath.cs` | 28 | | 连接路径（15 页） | :2 |
| `ElectricConnectorDirection.cs` | 8 | | 连接器方向枚举（15 页） | :2 |
| `ElectricConnectorType.cs` | 6 | | 连接器类型枚举（15 页） | :2 |
| `PistonMode.cs` | 6 | ★ | 活塞动作模式：Pushing=0/Pulling=1/StrictPulling=2（活塞方块/PistonHead/EditPistonDialog 消费） | :2 |
| `MemoryBankData.cs` | 96 | | 记忆库内容数据（IEditableItemData，15/15a 页） | :5 |
| `TruthTableData.cs` | 60 | | 真值表数据（IEditableItemData，15/15a 页） | :4 |

## 数学/几何/通用工具（15，本页深读；A30a 补）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `CellFace.cs` | 163 | ★ | 格面 struct X/Y/Z/Face：face 协议 0..5=+Z,+X,-Z,-X,+Y,-Y(:15)；对面表(:13)/切向表(:21)；Point3ToFace 线性查找(:54)、Vector3ToFace 最大点积(:63)、FromAxisAndDirection(:76)；CalculatePlane 每面常数(:89-98)；GetFaceCenter/GetFourVertices/GetSixVertices(:100-138)；GetHashCode 位混淆 (X<<11)+(Y<<7)+(Z<<3)+Face(:140)；全引擎射线/交互基本单元 | :4 |
| `Segment2.cs` | 74 | ★ | 2D 线段：Distance 点到线段内外分类(:16-32)；Intersection 参数化求交（平行 false :34-54)；NearestPoint(:56-73) | :4 |
| `Segment3.cs` | 52 | ★ | 3D 线段：Distance(:16-32)/NearestPoint(:34-51)，无 Intersection | :4 |
| `MatrixUtils.cs` | 23 | ★ | 单方法 CreateScaleTranslation 2D 缩放平移矩阵(:5-22) | :4 |
| `Random.cs` | 117 | ★ | 自研 PRNG（s0/s1 双 uint 状态，State 打包 ulong :12-18）：Seed 走 MathUtils.Hash 混淆(:32-35)，静态 m_counter 保证实例种子不重复(:6)；UInt 核心(:43-50)；Int(bound)/Int(min,max) 按 2^31 缩放(:54-56)；Float(:58)；NormalFloat 有理近似逆正态(:62-74)；Vector2() 圆盘均匀采样拒绝法(:76-92)/Vector3() 球面均匀(:98-110)；Bool(probability)/Sign | :5 |
| `RunningAverage.cs` | 30 | ★ | 时间窗滑动平均：AddSample 累计，过 period 秒才结算清零(:19-29) | :4 |
| `FloatCurve.cs` | 41 | ★ | 分段线性曲线：Sample(x) 线性插值，右溢出回末值、左溢出回首值(:19-40)；内嵌 HumanReadableConverter '|' 分隔(:6-13) | :5 |
| `EnumUtils.cs` | 63 | ★ | 枚举名值互转：Cache 字典+lock(:11-41)；GetEnumName\<T\> 未命中回"<invalid enum>"(:49-52)；旧 Type 版全 [Obsolete] | :4 |
| `CollectionUtils.cs` | 80 | ★ | ElementAt 枚举器定位(:3)；RandomShuffle Fisher-Yates 逆序(:15-22)；FirstIndex 值/谓词(:24-44)；SelectNth 快速选择 partition(:46-79) | :2 |
| `StringUtils.cs` | 199 | ★ | 全引擎 UI 数字显示底层：m_digits 16 进制表(:5-22)；CalculateNumberLength 4 重载(:50-90)；AppendNumber 扩展方法——先填 padding 再从尾位回写，负数占位 padding-1(:92-152)；float 版 Infinity/NaN/NumberTooLarge(>1E19) 特判，precision<0 去尾零(:154-198) | :4 |
| `IntervalUtils.cs` | 14 | ★ | [0,1) 环形区间 6 方法：Normalize/Add/Interval/Distance(双向取最短 :9)/Midpoint/IsBetween；TimeOfYear 用 | :2 |
| `SortedMultiCollection.cs` | 191 | ★ | 排序多值 KV 数组：Add 二分定位+Copy 后移(:102-112)；Enumerator 版本校验(:26-28)；坑：Find 注释"Find the last one"——重复键返回最后一个匹配(:164-190)，未命中返回 ~插入点 | :2 |
| `ArrayCache.cs` | 126 | ★ | 分桶数组池：桶按容量升序(:6)；Rent 找首个容量足够的桶出栈，无匹配桶直接 new 不缓存(:16-42)；Return 回栈+刷新双阈值时间戳(:44-61)；CheckCache 自循环队列（周期=窗口/5 :71），缓存率低且超时→ClearCache；Window.LowMemory 也清空(:13)；全程 lock | :4 |
| `StateMachine.cs` | 79 | ★ | 通用状态机：State{Name,Enter,Update,Leave}；TransitionTo 同态不重入(:46-61)；FindState 未找到抛 InvalidOperationException(:70-78)；OnTransitionTo 事件(:37)；PlayerData 5 态机宿主 | :2 |
| `SimplexNoise.cs` | 783 | ★ | Simplex 噪声静态类：m_permutations 512 项硬编码表——噪声本身不随世界种子变化，种子化靠生成器坐标偏移(:18-531)；Noise 1D 值噪声 smoothstep(:542-549)；2D simplex 斜切 0.366/0.211、输出 35f 缩放+0.5≈`[0,1]`(:551-607)；3D simplex 斜切 1/3 与 355/(678π)、16f 缩放+0.5(:609-730)；OctavedNoise 1/2/3D 分频叠加归一化，ridged=true 脊状 1-\|2x-1\|(:732-782) | :2 |

## 输入设备/UI 支撑（8：TouchInput/TouchInputType/VrEye → 10 页，LayoutDirection → 09a 页；其余 4 本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `TouchInput.cs` | 26 | | 触摸输入 struct（10/09 页） | :5 |
| `TouchInputType.cs` | 7 | | 触摸类型枚举（10 页） | :2 |
| `DeviceManager.cs` | 15 | ★ | 死文件：全文被注释（Android Build.Model/VERSION.Release 取设备信息），未参与编译 | :7 |
| `LayoutDirection.cs` | 5 | | 布局方向枚举（09a 页） | :2 |
| `TextOrientation.cs` | 5 | ★ | 文字方向：Horizontal=0/VerticalLeft=1 | :2 |
| `GuiSize.cs` | 8 | ★ | 界面尺寸档：Smallest/Smaller/Normal/Large/Larger 五档 | :2 |
| `ResolutionMode.cs` | 6 | ★ | 分辨率档：Low=0/Medium=1/High=2 | :2 |
| `VrEye.cs` | 6 | | VR 眼枚举（10a/19a 页） | :3 |

## 方块支撑 + 物理射线（8：BodyRaycastResult → 13 页；其余 7 本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `BlockAllocateData.cs` | 8 | ★ | 方块注册分配数据：Block+ModEntity+Index+Allocated+StaticBlockIndex（BlocksManager 注册时的分配记录） | :2 |
| `BlockDigMethod.cs` | 7 | ★ | 挖掘方式：None=0/Shovel=1/Quarry=2/Hack=3 | :2 |
| `BlockDropValue.cs` | 20 | ★ | 方块掉落物 struct：Value+Count+ValuesDictionaryForMods 扩展袋 | :4 |
| `BlockPlacementData.cs` | 14 | ★ | 放置数据 struct：Value+CellFace+ValuesDictionaryForMods 扩展袋 | :4 |
| `FluidInfo.cs` | 17 | ★ | 流体信息 struct：FluidBlock Block+SurfaceHeight+Vector2 FlowSpeed+ValuesDictionaryForMods 扩展袋 | :5 |
| `TreeType.cs` | 9 | ★ | 树类型：Oak/Birch/Spruce/TallSpruce/Mimosa/Poplar 六种 | :2 |
| `BodyRaycastResult.cs` | 13 | | 实体射线结果（13 页） | :5 |
| `RaycastMode.cs` | 6 | ★ | 射线模式：Digging=0/Interaction=1/Gathering=2 | :2 |

## 基础设施/调试/内容（26：Program/GameLogSink/Progress 族/ZipArchive 族核心/外部内容枚举等 12 → 01/12 页另见；其余 14 本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `Program.cs` | 389 | | 进程入口/平台初始化（01 页） | :26 |
| `GameLogSink.cs` | 151 | | 游戏内日志接收器（01 页） | :8 |
| `Profiler.cs` | 167 | ★ | using 作用域剖析器 struct:IDisposable：Metric{Name,HitCount,TotalTicks,MaxTicks,双 RunningAverage(5s) :7-19}；静态字典+按名排序表，新 Metric 置 m_sortNeeded(:21-55)；Dispose 累加、未配对抛 InvalidOperationException(:64-74)；Sample() 每帧采样后清零(:76-85)；FormatTime s/ms/us/ns 全量级表(:125-166) | :6 |
| `DebugInfo.cs` | 7 | ★ | 性能计数器：Counter/TotalTicksCosted/MaxTicksCosted1/MaxTicksCosted2 | :2 |
| `DebugItemAttribute.cs` | 9 | ★ | [Conditional("DEBUG")]——Release 编译下整个消失；Precision=3/Unit | :5 |
| `DebugItemsContainerAttribute.cs` | 5 | ★ | 继承 DebugItemAttribute（调试物品容器标注） | :5 |
| `DebugMenuItemAttribute.cs` | 11 | ★ | 继承 DebugItemAttribute + Step（默认 1.0，调试菜单数值步进） | :5 |
| `FloatListDebugMenuItemAttribute.cs` | 13 | ★ | 继承 DebugMenuItemAttribute + Items float[]（浮点候选列表） | :5 |
| `BuildConfiguration.cs` | 5 | ★ | 构建配置：Debug=0/Release=1 | :2 |
| `Progress.cs` | 6 | | 进度基类（18/09a/20a 页） | :2 |
| `CancellableProgress.cs` | 15 | | 可取消进度（18/18a 页） | :2 |
| `ZipArchive.cs` | 394 | | 自实现 zip 读解压（.scmod 载体，12/20/23 页） | :5 |
| `ZipArchiveEntry.cs` | 28 | ★ | zip 中央目录条目 12 字段：Method/FilenameInZip/FileSize/CompressedSize/HeaderOffset/FileOffset/HeaderSize/Crc32/IsFilenameUtf8/ModifyTime/Comment/EncodeUTF8；ToString=文件名 | :2 |
| `FileAlreadyExistsException.cs` | 11 | | 文件已存在异常（12/12a 页） | :2 |
| `ActiveExternalContentInfo.cs` | 8 | ★ | 当前激活外部内容：Address/DisplayName/Type | :2 |
| `ExternalContentEntry.cs` | 12 | ★ | 外部内容树条目：Type/Path/Size/Time + ChildEntries 递归 | :2 |
| `ExternalContentType.cs` | 20 | | 外部内容类型枚举（世界/皮肤/纹理包/材质…，17a 页点名） | :2 |
| `CommunityContentEntry.cs` | 38 | ★ | 下载中心列表项 17 字段：Type/Name/Address/UserId/UserName/Boutique(精品)/IsShow/Size/ExtraText/RatingsAverage/IconSrc+Icon(Texture2D)/LinkedNode(TreeViewNode)/CollectionID/CollectionName/CollectionDetails/Index | :4 |
| `CommunityContentMode.cs` | 7 | ★ | 社区内容模式：Disabled=0/Strict=1/Normal=2/ShowAll=3 | :2 |
| `UserInfo.cs` | 11 | ★ | 用户信息：readonly UniqueId/DisplayName | :2 |
| `DataSizeFormatter.cs` | 29 | ★ | 数据量格式化：KB/MB/GB 三档；坑：<1024 字节直接显示"1KB"(:6-8)而非字节数；PrepareFormatString 按 Log10 算有效数字(:21-28) | :4 |
| `CharacterSkinsCache.cs` | 25 | | 皮肤缓存（09a 页） | :4 |
| `HelpTopic.cs` | 9 | | 帮助主题（17 页） | :2 |
| `UpdateOrder.cs` | 15 | | 更新顺序枚举（02/03/13/15 页） | :2 |
| `IUpdateable.cs` | 7 | | 可更新接口（02/03/07/15 页） | :2 |
| `INoiseListener.cs` | 6 | | 噪声监听接口（生物听觉，02a 页） | :4 |
