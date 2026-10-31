# Game 域明细（根目录 226 文件）

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全列(226/226)；逐文件一行。主页面另见 16-玩法物品与背包.md；Community 子域 72 文件另见 16b-Game明细2.md。
>
> 前缀：目录 `E:\SurvivalcraftAPIProject\Survivalcraft\Game\`（下表省略）。"声明"=public 类型声明行号。★=本次深读全文，▲=深读头部/关键段，空=签名级未深读。指针家族的逐行职责以对应专页为准。

## 玩家会话与输入（11，本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `PlayerData.cs` | 703 | ★ | 玩家会话：5 态出生状态机 FirstUpdate→PrepareSpawn→WaitForTerrain→Playing⇄PlayerDead(:142-343)；出生点评分(:420-533)；SpawnPlayer 建实体+默认衣物+初始物品(:553-665)；Save/Load 键表(:376-398) | :7 |
| `PlayerInput.cs` | 73 | ★ | 每 tick 语义输入 struct：Look/Move/Jump/Dig/Hit/Aim/Interact/Drop 等 24 字段 + ValuesDictionaryForMods | :5 |
| `PlayerStats.cs` | 186 | ★ | 玩家统计：30+ 个 [Stat] 反射持久化字段(:61-133)；DeathRecord "日,x,y,z,因" CSV(:11-57)；ValuesDictionaryForMods 扩展 | :8 |
| `PlayerInfo.cs` | 4 | ★ | 世界信息里的玩家占位（仅 CharacterSkinName） | :2 |
| `PlayerClass.cs` | 5 | ★ | 枚举 Male=0/Female=1（决定实体模板 MalePlayer/FemalePlayer） | :2 |
| `AimState.cs` | 6 | | 瞄准状态枚举 | :2 |
| `LookControlMode.cs` | 6 | | 视角控制模式枚举 | :2 |
| `MoveControlMode.cs` | 5 | | 移动控制模式枚举 | :2 |
| `VrLookControlMode.cs` | 6 | | VR 视角控制模式枚举 | :2 |
| `VrMoveControlMode.cs` | 6 | | VR 移动控制模式枚举 | :2 |
| `BreathingMode.cs` | 5 | | 呼吸/憋气模式枚举（溺水系统用） | :2 |

## 伤害结算（6，本页深读）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `Attackment.cs` | 264 | ★ | 一次攻击全链：ProcessAttackment(:213-263)→护甲→韧性→扣血/扣 hitpoints→冲量+眩晕；CalculateInjuryAmount(:82-111)；ArmorProtectionDivision 除数(:71)；类名拼写错误故意保留(:7-11) | :12 |
| `MeleeAttackment.cs` | 29 | ★ | 近战冲量：ImpulseFactor=5.5×saturate(质量比^0.5×攻击力系数)，眩晕 0.25s×系数 | :5 |
| `ProjectileAttackment.cs` | 22 | ★ | 弹射物命中：ImpulseFactor=2、零伤不冲不晕、携带 Projectile 引用 | :5 |
| `Injury.cs` | 68 | ★ | 伤害记录基类：Amount/Attacker/Cause；Process() 走 CalculateCreatureInjuryAmount 钩子后 Injured 事件 | :4 |
| `TypedInjury.cs` | 57 | | 伤害类型族：AttackInjury(:2)/FireInjury(:11) 等子类 | :2 |
| `IInjurable.cs` | 13 | | 可受伤接口 | :2 |

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
| `ProjectileStoppedAction.cs` | 6 | | 弹射物停止后行为枚举 | :2 |

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
| `FurnitureInteractionMode.cs` | 8 | | 家具交互模式枚举 | :2 |

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
| `GameplayImpactLevel.cs` | 31 | | 游戏影响等级枚举（世界对玩法系统的干预级别） | :5 |
| `SpawnChunk.cs` | 12 | ★ | 出生区块记录：Point/IsSpawned/LastVisitedTime/SpawnsData | :4 |
| `SpawnEntityData.cs` | 14 | ★ | 出生实体项：TemplateName/Position/ConstantSpawn/Data/EntityId | :4 |
| `SpawnLocationType.cs` | 6 | ★ | 枚举 Surface/Cave/Water | :2 |
| `BestiaryCreatureInfo.cs` | 34 | ★ | 图鉴生物条目：属性面板(Mass/AttackResilience/AttackPower/速度/跳跃)+Loot 列表 | :4 |
| `SignData.cs` | 9 | ★ | 告示牌内容：4 行文本+4 色+Url | :3 |
| `PrecipitationType.cs` | 5 | | 降水类型枚举（→14-光照天空与天气.md） | :2 |

## 寻路（6 → 03 页另见）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `AStar.cs` | 200 | | 通用 A* 算法：泛型 Node/开放集，与具体世界解耦 | :4 |
| `IAStarStorage.cs` | 8 | | A* 存储接口 | :2 |
| `IAStarWorld.cs` | 12 | | A* 世界接口（可通行/代价） | :4 |
| `PathfindingResult.cs` | 14 | | 寻路结果：路径点序列+状态 | :4 |
| `PathRenderer.cs` | 657 | | 路径渲染器：调试/生物路径可视化 | :6 |
| `CreatureCategory.cs` | 9 | | 生物类别枚举 | :3 |

## 实体引用（2 → 03 页另见）

| 文件 | 行 | 读 | 职责 | 声明 |
|---|---|---|---|---|
| `EntityReference.cs` | 180 | ▲ | 实体引用 struct：null:/local:/id:N:name:S 四种字符串协议(:19-35)；GetEntity/GetComponent 解析(:39-72) | :5 |
| `EntityReferenceHumanReadableConverter.cs` | 9 | | EntityReference 的人类可读序列化适配器 | :5 |

## 相机（13 → 10-输入与相机.md）

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

## 粒子（29 → 07-粒子系统.md）

| 文件 | 行 | 职责 | 声明 |
|---|---|---|---|
| `ParticleSystem.cs` | 165 | 泛型粒子系统基类（T:Particle） | :5 |
| `ParticleSystemBase.cs` | 81 | 粒子系统抽象基类 + 批次需求结构 | :6 |
| `Particle.cs` | 28 | 粒子基类 | :4 |
| `ParticleBillboardingMode.cs` | 7 | 广告牌模式枚举 | :2 |
| `ITrailParticleSystem.cs` | 8 | 拖尾粒子接口 | :4 |
| `PrecipitationShaftInfo.cs` | 8 | 降水柱参数 | :2 |
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

## 地形/区块/生成器/序列化（25 → 05/05a 页，序列化 → 11 页）

| 文件 | 行 | 职责 | 声明 |
|---|---|---|---|
| `Terrain.cs` | 359 | 世界地形运行时 + ChunksStorage | :5 |
| `TerrainChunk.cs` | 248 | 单区块数据 + BrushPaint | :4 |
| `TerrainChunkState.cs` | 13 | 区块十态状态机枚举 | :2 |
| `TerrainChunkGeometry.cs` | 28 | 区块几何容器 | :5 |
| `TerrainChunkSliceGeometry.cs` | 66 | 区块切片几何 | :4 |
| `TerrainGeometry.cs` | 106 | 地形顶点几何 | :5 |
| `TerrainGeometryDynamicArray.cs` | 17 | 几何动态数组 | :4 |
| `TerrainGeometrySubset.cs` | 25 | 几何子集 | :2 |
| `TerrainVertex.cs` | 23 | 地形顶点格式 | :5 |
| `TerrainUpdater.cs` | 1339 | 后台逐区块生成推进调度 | :5 |
| `TerrainRenderer.cs` | 463 | 地形绘制 | :5 |
| `TerrainRaycastResult.cs` | 25 | 地形射线结果 | :5 |
| `TerrainBrush.cs` | 390 | 地形笔刷（编辑/生成共用） | :4 |
| `ITerrainContentsGenerator.cs` | 26 | 生成器接口 | :4 |
| `TerrainGenerationMode.cs` | 7 | 地形生成模式枚举 | :2 |
| `TerrainContentsGenerator21.cs` | 2627 | v2.1 生成器 | :5 |
| `TerrainContentsGenerator22.cs` | 2365 | v2.2 生成器（CavePoint 洞穴） | :4 |
| `TerrainContentsGenerator23.cs` | 2469 | v2.3 生成器 | :4 |
| `TerrainContentsGenerator24.cs` | 2437 | v2.4 生成器 | :4 |
| `TerrainContentsGeneratorFlat.cs` | 161 | 平地生成器 | :4 |
| `ChunkGenerationStep.cs` | 25 | 区块生成阶段描述 | :2 |
| `TerrainSerializer129.cs` | 212 | v1.2.9 区块序列化 | :4 |
| `TerrainSerializer14.cs` | 189 | v1.4 区块序列化 | :4 |
| `TerrainSerializer22.cs` | 213 | v2.2 区块序列化 | :4 |
| `TerrainSerializer23.cs` | 783 | v2.3 区块序列化（IStorage 抽象） | :7 |

## 存档版本转换（12 → 11-存档持久化.md）

| 文件 | 行 | 职责 | 声明 |
|---|---|---|---|
| `VersionConverter.cs` | 186 | 抽象基类 + GenericVersionConverter(:30) | :6 |
| `VersionConverter10To14.cs` | 70 | 1.0→1.4 升档 | :7 |
| `VersionConverter20To21.cs` | 102 | 2.0→2.1 升档 | :6 |
| `VersionConverter21To22.cs` | 248 | 2.1→2.2 升档 | :7 |
| `VersionConverter22To23.cs` | 86 | 2.2→2.3 升档 | :6 |
| `VersionConverter23To24.cs` | 37 | 2.3→2.4 升档 | :6 |
| `VersionConverter112To113.cs` | 43 | 1.1.2→1.1.3 升档 | :6 |
| `VersionConverter113To114.cs` | 43 | 1.1.3→1.1.4 升档 | :6 |
| `VersionConverter120To121.cs` | 53 | 1.2.0→1.2.1 升档 | :6 |
| `VersionConverter121To122.cs` | 43 | 1.2.1→1.2.2 升档 | :6 |
| `VersionConverter126To127.cs` | 114 | 1.2.6→1.2.7 升档 | :6 |
| `VersionConverter128To129.cs` | 246 | 1.2.8→1.2.9 升档 | :7 |

## 渲染/网格/着色器（24 → 06-渲染管线与着色器.md，方块几何另见 04 页）

| 文件 | 行 | 职责 | 声明 |
|---|---|---|---|
| `BlockGeometryGenerator.cs` | 2471 | 方块→顶点几何的中央生成器（所有方块形状装配） | :4 |
| `BlockMesh.cs` | 771 | 静态网格构建/变换/合并 | :7 |
| `BlockMeshVertex.cs` | 14 | 网格顶点 struct | :4 |
| `BevelledShapeRenderer.cs` | 491 | 斜面体渲染（电路线框等） | :5 |
| `ModelShader.cs` | 224 | 实体模型着色器 | :6 |
| `SkyShader.cs` | 80 | 天空着色器 | :2 |
| `SkyPrimitiveRender.cs` | 94 | 天空图元绘制 | :5 |
| `SkyRenderingMode.cs` | 6 | 天空渲染模式枚举 | :2 |
| `ShaderCodeManager.cs` | 81 | 着色器代码管理 | :5 |
| `TextureAtlas.cs` | 52 | 纹理图集 | :6 |
| `TextureAtlasManager.cs` | 68 | 图集管理 | :6 |
| `BlocksTexturesCache.cs` | 23 | 方块纹理缓存 | :4 |
| `BlockColorsMap.cs` | 86 | 方块颜色映射 | :4 |
| `Subtexture.cs` | 27 | 图集子纹理 | :5 |
| `DrawBlockEnvironmentData.cs` | 32 | 方块绘制环境参数（光/湿度/温度/广告牌向） | :5 |
| `DrawBlockMode.cs` | 7 | 方块绘制模式枚举 | :2 |
| `GeometrySubsetType.cs` | 6 | 几何子集类型枚举 | :2 |
| `ModelRenderingMode.cs` | 7 | 模型渲染模式枚举 | :2 |
| `ICustomModelRenderer.cs` | 43 | 自定义模型渲染接口 | :11 |
| `ICustomModelWidgetRenderer.cs` | 7 | 自定义 Widget 模型渲染接口 | :2 |
| `IDrawable.cs` | 6 | 可绘制对象接口（渲染排序用） | :2 |
| `GlowPoint.cs` | 22 | 发光点数据 | :4 |
| `GlowPointType.cs` | 7 | 发光点类型枚举 | :2 |
| `InstancedModelData.cs` | 15 | 实例化模型数据 | :4 |

## 电学/机构数据（7 → 15/15a 页）

| 文件 | 行 | 职责 | 声明 |
|---|---|---|---|
| `ElectricConnection.cs` | 16 | 元件间连接记录 | :2 |
| `ElectricConnectionPath.cs` | 28 | 连接路径 | :2 |
| `ElectricConnectorDirection.cs` | 8 | 连接器方向枚举 | :2 |
| `ElectricConnectorType.cs` | 6 | 连接器类型枚举 | :2 |
| `PistonMode.cs` | 6 | 活塞动作模式枚举 | :2 |
| `MemoryBankData.cs` | 96 | 记忆库内容数据（IEditableItemData） | :5 |
| `TruthTableData.cs` | 60 | 真值表数据（IEditableItemData） | :4 |

## 数学/几何/通用工具（15）

| 文件 | 行 | 职责 | 声明 |
|---|---|---|---|
| `CellFace.cs` | 163 | 格面 struct（六向邻接/平面计算），全引擎射线/交互的基本单元 | :4 |
| `Segment2.cs` | 74 | 2D 线段 | :4 |
| `Segment3.cs` | 52 | 3D 线段 | :4 |
| `MatrixUtils.cs` | 23 | 矩阵工具 | :4 |
| `Random.cs` | 117 | 引擎随机数封装（Vector/Color 随机等） | :5 |
| `RunningAverage.cs` | 30 | 滑动平均 | :4 |
| `FloatCurve.cs` | 41 | 浮点曲线插值 + HumanReadableConverter(:7) | :5 |
| `EnumUtils.cs` | 63 | 枚举名值互转 | :4 |
| `CollectionUtils.cs` | 80 | 集合工具 | :2 |
| `StringUtils.cs` | 199 | 字符串工具 | :4 |
| `IntervalUtils.cs` | 14 | 区间归一化（TimeOfYear 用） | :2 |
| `SortedMultiCollection.cs` | 191 | 排序多值集合 | :2 |
| `ArrayCache.cs` | 126 | 数组池 | :4 |
| `StateMachine.cs` | 79 | 通用状态机（PlayerData 用） | :2 |
| `SimplexNoise.cs` | 783 | Simplex 噪声（地形生成用） | :2 |

## 输入设备/UI 支撑（8 → 10/09 页）

| 文件 | 行 | 职责 | 声明 |
|---|---|---|---|
| `TouchInput.cs` | 26 | 触摸输入 struct | :5 |
| `TouchInputType.cs` | 7 | 触摸类型枚举 | :2 |
| `DeviceManager.cs` | 15 | 显示设备管理 | :7 |
| `LayoutDirection.cs` | 5 | 布局方向枚举 | :2 |
| `TextOrientation.cs` | 5 | 文字方向枚举 | :2 |
| `GuiSize.cs` | 8 | 界面尺寸档枚举 | :2 |
| `ResolutionMode.cs` | 6 | 分辨率模式枚举 | :2 |
| `VrEye.cs` | 6 | VR 眼枚举 | :3 |

## 方块支撑 + 物理射线（8 → 04/13 页）

| 文件 | 行 | 职责 | 声明 |
|---|---|---|---|
| `BlockAllocateData.cs` | 8 | 方块分配数据 | :2 |
| `BlockDigMethod.cs` | 7 | 挖掘方式枚举 | :2 |
| `BlockDropValue.cs` | 20 | 方块掉落物 struct | :4 |
| `BlockPlacementData.cs` | 14 | 放置数据 struct | :4 |
| `FluidInfo.cs` | 17 | 流体信息 struct | :5 |
| `TreeType.cs` | 9 | 树类型枚举 | :2 |
| `BodyRaycastResult.cs` | 13 | 实体射线结果 | :5 |
| `RaycastMode.cs` | 6 | 射线模式枚举 | :2 |

## 基础设施/调试/内容（26 → 01/12 页另见）

| 文件 | 行 | 职责 | 声明 |
|---|---|---|---|
| `Program.cs` | 389 | 进程入口/平台初始化（另见 01 页） | :26 |
| `GameLogSink.cs` | 151 | 游戏内日志接收器 | :8 |
| `Profiler.cs` | 167 | 性能剖析 Metric | :6 |
| `DebugInfo.cs` | 7 | 调试信息开关 | :2 |
| `DebugItemAttribute.cs` | 9 | 调试物品特性 | :5 |
| `DebugItemsContainerAttribute.cs` | 5 | 调试物品容器特性 | :5 |
| `DebugMenuItemAttribute.cs` | 11 | 调试菜单项特性 | :5 |
| `FloatListDebugMenuItemAttribute.cs` | 13 | 浮点列表调试菜单特性 | :5 |
| `BuildConfiguration.cs` | 5 | 构建配置枚举 | :2 |
| `Progress.cs` | 6 | 进度基类 | :2 |
| `CancellableProgress.cs` | 15 | 可取消进度 | :2 |
| `ZipArchive.cs` | 394 | 自实现 zip 读解压（.scmod 载体） | :5 |
| `ZipArchiveEntry.cs` | 28 | zip 条目 | :2 |
| `FileAlreadyExistsException.cs` | 11 | 文件已存在异常 | :2 |
| `ActiveExternalContentInfo.cs` | 8 | 当前激活外部内容信息 | :2 |
| `ExternalContentEntry.cs` | 12 | 外部内容条目 | :2 |
| `ExternalContentType.cs` | 20 | 外部内容类型枚举（世界/皮肤/纹理包/材质…） | :2 |
| `CommunityContentEntry.cs` | 38 | 社区内容条目（下载中心列表项） | :4 |
| `CommunityContentMode.cs` | 7 | 社区内容模式枚举 | :2 |
| `UserInfo.cs` | 11 | 用户信息 | :2 |
| `DataSizeFormatter.cs` | 29 | 数据量格式化 | :4 |
| `CharacterSkinsCache.cs` | 25 | 皮肤缓存 | :4 |
| `HelpTopic.cs` | 9 | 帮助主题 | :2 |
| `UpdateOrder.cs` | 15 | 更新顺序枚举 | :2 |
| `IUpdateable.cs` | 7 | 可更新接口 | :2 |
| `INoiseListener.cs` | 6 | 噪声监听接口（生物听觉） | :4 |
