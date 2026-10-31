# A2 深学报告：Survivalcraft\Subsystem\ 全量精读

> 日期: 2026-10-31 · 范围: E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\ 全部 111 个 .cs（顶层 40 + BlockBehavior\ 71），共 20185 行；本次实读 109 个 19833 行（SubsystemUpdate/SubsystemTime 已在前期深读，未重读）。无 >2000 行特大文件，全部全文读；SubsystemCreatureSpawn(1359) 分 2 页读完。
> 基类契约（Subsystem.cs / Project.cs 实例化、Load 递归、Save 顺序）见知识库 02-Subsystem体系.md，本报告不重复。

## 一、顶层 40 个文件逐个笔记

### SubsystemBodies.cs (161)
身体空间索引。8x8 网格：`m_componentBodiesByArea` Point2→DynamicArray\<ComponentBody\>（:12），`m_areaByComponentBody` 反查表（:10）。
- `AddBody/RemoveBody`（:124-141）：OnEntityAdded/Removed 驱动，登记进网格并挂 `PositionChanged` 事件。
- `Update`（:118-122）每 tick 全量 `UpdateBody` 校正跨格；`ComponentBody_PositionChanged`（:158-160）事件路径即时校正（双保险）。
- `FindBodiesAroundPoint`（:18-32）/`FindBodiesInArea`（:34-50）：所有噪声/爆炸/刷怪/哨兵的空间查询底座，O(格数×桶内数)。
- `Raycast`（:52-104）：对区域内 body 的 BoundingBox 求交；mod 钩子 `BodyCountInRaycast`（:73-80）可替换相交计算并 skipVanilla；`inflateAmount` 膨胀盒；`IsRaycastTransparent` 跳过。

### SubsystemCreatureSpawn.cs (1359) — 刷怪规则中枢
静态限额（:54-61）：`m_totalLimit=26`、`m_areaLimit=3`、`m_areaRadius=16`；常驻 `m_totalLimitConstant=6`（挑战 12）、`m_areaLimitConstant=4`、`m_areaRadiusConstant=42`。**均为 static 字段，跨世界保留**。
- `Update`（:69-90）：仅 `EnvironmentBehaviorMode.Living` 生效。新加载 chunk 队列每个试 10 次（`SpawnChunkCreatures(chunk,10,false)` :71-77），已访问 chunk 每个试 2 次（:78-84）；每 60s（冬季 120s，:85-88）`SpawnRandomCreature`。
- `Load`（:92-109）：查 8 个子系统 + `InitializeCreatureTypesFromDatabase`（存档袋子 `CreatureSpawnRules` 内每项 `Class` 反射实例化 CreatureType :1018-1038，异常 Log.Error 跳过）+ `InitializeCreatureTypes`（60+ 硬编码生物规则 :123-987）；订阅 `SubsystemSpawn.SpawningChunk`（:103-108）。
- mod 入口：`ModsManager.HookAction("InitializeCreatureTypes", ...)`（:1009-1015）追加自定义 CreatureType。
- `SpawnChunkCreatures`（:1068-1102）：按 ConstantSpawn 选限额/半径；总数/区域数双限；`GetRandomSpawnLocationType`（:1349-1358）Surface/Cave/Water 各 0.3/0.3/0.4；候选=同位置类型同 spawn 标志的 CreatureType，`GetRandomWeightedItem`（:1334-1347）按 suitability 加权。
- `SpawnRandomCreature`（:1040-1066）：每视角 52 只/68 格硬限，落点在相机 24-48 格环上（`GetRandomSpawnPoint` :1165-1176，Y±30 clamp 2..254），落点 16 格内 ≥3 只放弃。
- `ProcessSpawnPoint`（:1178-1197）：chunk 状态 >InvalidPropagatedLight 时上下各探 30 格；`TestSpawnPoint`（:1199-1261）：Surface 要求 `SkyLightValue-光>3` 且下方可碰撞非水、上方两格空非水；Cave 要求 `SkyLight-光≥5`（洞内暗）；Water 要求目标+上 2 格共 3 格水（顶层可碰撞）。
- `SpawnCreatures`（:1104-1132）：每目标最多 50 次尝试，后续个体随机偏移 X/Z±8、Y-4..+8；`SpawnCreature`（:1134-1150）：`DatabaseManager.CreateEntity(Project, templateName, true)`+设 Position/随机朝向/ConstantSpawn+`Project.AddEntity`，异常 Log.Error 返 null。
- `CalculateSpawnSuitability`（:1263-1269）：同模板存量>8 → 0.25 倍惩罚；`CountCreatures(CreatureType)`（:1271-1279）按实体模板名数 body。
- `CountCreaturesInArea`（:1293-1332）：查 SubsystemBodies 网格 **并把 chunk.SpawnsData 里尚未生成的 despawn 数据也算进区域限额**（:1311-1330）——防"卸载即刷"循环。
- suitability 函数全部硬编码：湿度/温度/`CalculateOceanShoreDistance`/底方块 contents（8=草 2=土 7=沙 3=石 62=雪 18=叶）组合。

### SubsystemSpawn.cs (360) — chunk 级实体存取/卸载
字段（:38-44）：`MaxChunkAge=76800f`（游戏秒）、`VisitedRadius=8`、`SpawnRadius=48`、`DespawnRadius=60`。
- `Update`（:57-74）：4 个定时器——DiscardOldChunks 每 60s（:143-154，LastVisitedTime 空或超 MaxChunkAge 删 SpawnChunk）；UpdateLastVisitedTime 每 5s（:156-172）；SpawnChunks 每 4s（:174-210）；DespawnChunks 每 2s（:212-253）。
- `SpawnChunks`（:174-210）：视角 SpawnRadius 圆内、chunk 状态 >InvalidPropagatedLight：重放 `SpawnsData`→`SpawnEntity`→清空→`SpawningChunk?.Invoke`→IsSpawned=true。**事件即刷怪链入口**。
- `DespawnChunks`（:212-253）：`ComponentSpawn.AutoDespawn` 且离所有视角 >60 格 → 打包 `SpawnEntityData{TemplateName,Position,ConstantSpawn,Data,EntityId}`（mod 可经钩子 `OnSaveSpawnData` 塞 Data）→ 存 `chunk.SpawnsData` → `Despawn()`。
- `SpawnEntity`（:255-282）：`DatabaseManager.FindEntityValuesDictionary`+`Project.CreateEntity(values, data.EntityId)`（**保留原实体 Id**）→ 钩子 `OnReadSpawnData` → 设位置/随机朝向/ConstantSpawn → AddEntity。
- 存档（:102-120/Load :76-100）：`Chunks` 袋子按 `"x,y"` 键存 SpawnChunk；SpawnsData 用紧凑字符串 `"Template,x,y,z,ConstantSpawn,Data,EntityId;"`（`SaveSpawnsData` :338-359 / `LoadSpawnsData` :298-323；旧 ValuesDictionary 格式有 Obsolete 兼容 :284-296/326-336）。坐标保存前四舍五入到 0.1。

### SubsystemTerrain.cs (613) — 地形门面
静态开关：`TerrainRenderingEnabled`/`TerrainUpdaterEnabled`（:7-8）。DrawOrders=[0,100]（:40，不透明+alphaTested 与透明两趟）。`UpdateOrder => UpdateOrder.Terrain`（=100）。
- `ChangeCell`（:355-394）：钩子 `TerrainChangeCell` 可整体跳过（:357-369）→ `IsCellValid` 校验 → 新旧值清光位后相同则短路（:374-378）→ `SetCellValueFast` → `chunk.ModificationCounter++`（可关）→ `TerrainUpdater.DowngradeChunkNeighborhoodState(...,InvalidLight)` → `m_modifiedCells` 记账 → `ChangeCellToBehavior`（异常 Log.Error 不中断 :388-393）。
- `ChangeCellToBehavior`（:396-427）：MovingBlockSet 未停 → `OnBlockStartMoving`（设置移动中）/`OnBlockStopMoving`（Stopped）；否则按 contents 变化分派 `OnBlockRemoved`→`OnBlockAdded` 或 `OnBlockModified`。
- `ProcessModifiedCells`（:66-84）：`Update()` 里在 `TerrainUpdater.Update()` 之后跑（:493-498）；对每个变更格 + 6 邻居偏移调 `OnNeighborBlockChanged`——**邻居通知的地形侧入口**。
- `DestroyCell`（:429-470）：`block.GetDropValues` → 逐 drop 调 `OnItemHarvested`（可改 dropValue/newValue）→ `AddPickable` → 距视角<16 出 debris 粒子 → `ChangeCell`。**掉落物生成点**。
- `Raycast`（:86-212）实例版 + static `Raycast(Terrain,...)`（:226-353，无 SubsystemTerrain 依赖，注释警告家具类方块会异常）；DDA 逐格、`block.Raycast` 求交、按命中点三轴贴面定 face。
- `Load`（:500-585）：创建 Terrain（钩子 `OnTerrainCreated` 可替换）、TerrainRenderer/TerrainUpdater/TerrainSerializer23；BlockGeometryGenerator（钩子 `OnBlockGeometryGeneratorCreated` 可替换 :527-541）；按存档版本 2.1/2.2/2.3/2.4 选 TerrainContentsGenerator21/22/23/24 或 Flat。
- `Save`（:587-605）：钩子 `BeforeTerrainSave` → `TerrainUpdater.UpdateEvent.WaitOne()` 挂起更新线程 → 逐 chunk `TerrainSerializer.SaveChunk` → Set 恢复。
- `Draw`（:472-491）：钩子 `OnTerrainDraw` 每趟都发。

### SubsystemMovingBlocks.cs (714)
`MovingBlockSet`（:11-108）：Id/Tag/Position/TargetPosition/Speed/Acceleration/Drag/Smoothness/Blocks/Box/CurrentVelocity/Geometry；`IMovingBlockSet` 接口暴露只读视图；`SetBlock(offset,value)`（:96-103）改块并使 Geometry 失效（GeometryGenerationPosition=int.MaxValue）。
- `AddMovingBlockSet`（:152-202）：钩子 `OnMovingBlockSetAdded`（可改集合、testCollision、拒收）→ testCollision 时 `MovingBlocksCollision` 预检 → `GenerateGeometry`（若首帧已过）→ 入表。返回 null=被拒。
- `Update`（:304-380）：每 set 钩子 `OnMovingBlockSetUpdate` 可 skip；chunk 无效跳过；`Speed+=Acceleration*dt`、Drag 幂衰减（:327-330）；Smoothness 两轴 saturate 减速（:333-335）；速度上限 0.95/dt（:338）；到 Target 置位；**Stop 时位置按速度方向 Ceiling/Floor 对齐格点**（:352-371）→ `MovingBlocksCollision`（集合互撞→Stop :524-534）+ `TerrainCollision`（盒内逐格非空→`CollidedWithTerrain` 事件 :536-554）→ 停/达 加入 m_stopped → `Stopped` 事件（:376-379）。
- 几何：`GenerateGeometry`（:556-662）用独立 canvasTerrain（2x2 chunk 懒建，:574-603），把每格包成 ShadowBlock(257) 保阴影强度，逐块 `GenerateTerrainVertices` 到 `movingBlockSet.Geometry`；仅当整数格锚点变化才重生成（:557-567）。
- `Draw`（:382-430）：Buffers 每帧重建；AlphaTested shader；m_removing 的 set 在 RemoveMovingBlockSet 后再画 4 帧（RemainCounter，:391-401）防消失闪烁。
- `AddTerrainBlock`（:692-713）：**set 停止后写回地形的标准路径**——`Stop()`+`DestroyCell(…,movingBlock)`（触发 OnBlockStopMoving 分支）；`m_noDropOnMovingBlockStopped=false` 默认不掉落。
- 存档（:432-509）：MovingBlockSets 袋子；Blocks 是 `"value,ox,oy,oz;…"` 字符串。
- `Raycast`（:238-302）：先 set 盒求交再逐块 block.Raycast。
- 事件：`CollidedWithTerrain`、`Stopped`（:146-148）——Piston/Collapsing 订阅。

### SubsystemElectricity.cs (747)
常量 `CircuitStepDuration=0.01f`（:237）。静态表：`m_connectionPathsTable`（160 项 :10-131）、`m_connectorDirectionsTable`（:133-170）、`m_connectorFacesTable`（:172-203）。
- `Update`（:395-452）：`m_remainingSimulationTime=min(+dt,0.1)`；每 0.01s：`UpdateElectricElements()`→`CircuitStep++`→跑 `m_futureSimulateLists[CircuitStep]`（异常 **无条件 rethrow** :416-423，DEBUG 打印）。
- `UpdateElectricElements`（:611-654）：m_pointsToUpdate（bool=true=增删后）→ 找到旧元素（WireDomain 进 m_wiresToUpdate，其它进 remove）→ `RemoveWireDomains`→Remove→`AddWireDomains`（:656-674，对更新点 27 邻域 6 面全扫 `ScanWireDomain` 泛洪 :693-730）→`AddElectricElement`（:529-594，逐 CellFace 建双向 Connections，把元素与邻居排进下 1/2 步）。
- `QueueElectricElementForSimulation`（:357-373）：step==CircuitStep+1 → m_nextStepSimulateList；更远 → m_futureSimulateLists[step]；字典缓存池 `GetListFromCache/ReturnListToCache`（:732-744）。
- `SimulateElectricElement`（:523-527）：`Simulate()` 返 true → 邻居排下步。
- 持久电压：`m_persistentElementsVoltages`（:207），存档 `"VoltagesByCell"` 字符串（Load :454-477 4 元组解析失败抛 InvalidOperation；Save :479-496 **num>500 截断**）。WritePersistentVoltage 供记忆库等用。
- `OnChunkDiscarding`（:271-280）：chunk 卸载时把其中元素标脏重建。
- 性能表 `UpdateTimeDebug`（:241，Save 时输出 :497-517）。

### SubsystemExplosions.cs (922)
`SparseSpatialArray<T>`（:7-138）：256³ 体素（中心±128），4096 桶×4096 槽，`m_activeBuckets` 非空桶索引（Set 时追加），`NonDefaultEntries()`（:107-129）按桶序+槽序枚举（**顺序与旧 ToDictionary 完全一致**，消费端依赖）。
- `ExplosionData`（:140-159）含 `ValuesDictionaryForMods` 给 mod 传参。
- `AddExplosion`（:237-244）：>0 入队 + `ApplyBodiesShaking`（全 body `UnderExplosionStart` :764-768）。
- `Update`（:246-327）：取队首为锚，4 格内全部出队同步 `SimulateExplosion`（注释掉的 Task.Run/Parallel.For 均弃用）；`PostprocessExplosions`；`ShowExplosionPressure=false` 时释放两个大数组。
- `SimulateExplosion`（:343-639）：爆心 ChangeCell(0)；压力 BFS：`num5=pressure/(explosionPower^0.66+5*max(step-7,0))`，`num5>=爆心韧性` 才展开；三队列 list/list2/list3 轮换（沿轴优先 Axis0/1/2/其它 4 方案 :383-630）。
- `TryAddPoint`（:641-762）：6 邻压力和 / `max(韧性*随机1..2(1/8 概率×3),1)` >1 → `DestroyCell(0,...,noDrop:true,noPS:true)` → 0.75(>5 压力 0.95) 概率 `TryExplodeBlock` 链爆；未爆块按压力算冲量并**把掉落转成抛射物**（`m_projectilesCount` 限流 <40 全出 /<60 一半 /<80 1/4 /≥80 1/8，:707-710；`ExplosionKeepsPickables` 豁免；烟尾概率 0.5 且 <35）。
- `PostprocessExplosions`（:770-883）：逐压力点设爆炸粒子（随机饱和度）；钩子 `CalculateExplosionPower`（:787-793）可改总压力；对 surroundingPressure 点调 `OnExplosion` + 概率点火（`SetCellOnFire` 燃烧弹 1.0/普通 0.3）；全体 body/pickable/projectile `CalculateImpulseAndDamage`+`UnderExplosion`（本波生成的抛射物豁免 :827-838）；按总压力 7 档放音（>2000000 Explosion7 …>0 Explosion1）+ MakeNoise(130..30 格)。
- `CalculateImpulseAndDamage`（:895-921）：3³ 邻域压力矢量和；被固体包围的格子用 obstaclePressure 兜底（防止墙后 0 冲量）。

### SubsystemSky.cs (1017)
DrawOrders=[-100,5,105]（:139）：-100 先算雾/水下参数；5 画天空顶；105 画闪电。
- `Draw`(-100)（:286-387）：`GetSurfaceHeight` 判水下/岩浆深度 → 水下雾色按水温湿度+深度衰减；岩浆固定橙雾；陆上用 `Weather.FogSeed` 生成 FogBottom/Top/Density（:329-335）、四方向天空色均值得 ViewFogColor（:347-354）；`DrawSkyEnabled=false` 或天空禁用时铺全屏雾色 quad（钩子 `ViewFogColor` :376-382）。
- DrawSkydome（:482-534）：每 GameWidget 一个 SkyDome（128 顶点半球，顶点色=CalculateSkyColor）；缓存条件 timeOfDay>0.0005 等变化才重填（:502-517）。
- 星星 250 颗（:123）+ 前 3 颗手放（北极星等 :852-880）；日月 `QueueCelestialBody`（:745-773）900 距离，晨昏光晕 Lerp 半径/色。
- `MakeLightningStrike`（:189-270）：钩子 `OnLightningStrike` 可改位置/是否打/压力/是否点火；冷却 1s；4 格内 body 点火（`ComponentOnFire.SetOnFire` 12-15s）+ StruckByLightning++；树叶旁不打雷坑（:247-257）；0.2 概率 39 压力爆炸（`SubsystemExplosions.AddExplosion` 无声版）；雷声按距离 Near/Far。
- 计算委托全部可换：`InitializeCalculation`（:450-461）默认 *Survivalcraft 实现——`CalculateFog/CalculateLightIntensity/CalculateSeasonAngle/CalculateHazeFactor/CalculateSkyColor/CalculateSkyFog/CalculateDawn(Dusk)GlowIntensity/CalculateWinterDistance`。
- `CalculateSkyColorSurvivalcraft`（:960-991）钩子 `ChangeSkyColor` 最后改色。
- 光照值表：`m_lightValuesMoonless=[0,3,6,9,12,15]`/`m_lightValuesNormal=[3,5,8,10,13,15]`（:145-147），`UpdateLightAndViewParameters`（:775-781）按 SkyLightIntensity 查表得 SkyLightValue（刷怪 Surface 判定用）。
- 月相 `UpdateMoonPhase`（:783-785）`(Day-0.5+5)%8`。

### SubsystemWeather.cs (543)
DrawOrders=[50]（降水轴粒子）。字段状态机：降水 start/end/rampTime、雾 start/end/rampTime、`FogSeed/FogProgress/FogIntensity`、`PrecipitationIntensity`。
- `Update`（:224-228）=UpdatePrecipitation+UpdateLightning+UpdateFog。
- `UpdatePrecipitation`（:289-384）：结束后按季节重排下次雨（Summer 1/1/0.5 … Spring 1.5/2/1 = 时长系数/闪电系数/闪电概率 :294-315）；ramp 10-30s；`AreWeatherEffectsEnabled=false` 强制 0；雨声每 0.33s 实时按 15×15 轴音量积分（:344-374）。
- `UpdateLightning`（:386-415）：雨满（Intensity==1）时每游戏秒随机挑 chunk，`m_lightningIntensity*0.0002` 概率 → 局部 16×16 找最高点 → `SubsystemSky.MakeLightningStrike(false)`。
- `GetPrecipitationShaftInfo`（:102-128）：`IsPlaceFrozen(季温,顶高)`→雪；季温≤8 或湿度≥8→雨；否则无。
- `FreezeThawAndDepositSnow`（:454-542）：挂 `BlocksScanner.ScanningChunkCompleted`（0.66/0.66）与 `TerrainUpdater.ChunkInitialized`（1.0/1.0）两个入口；256 轴洗牌抽样：雪带内水面冻冰（海岸>-35）、雪盖（`CanSupportSnow`）、融雪 thaw 概率逐顶 DestroyCell(61/62)。
- 静态工具：`GetTemperatureAdjustmentAtHeight`（y>64 二次递减 :96-97）、`IsPlaceFrozen`、`ShaftHasSnowOnIce`（哈希 10%）。
- Draw（:172-222）：视角 7-9 半径方形补/撤 `PrecipitationShaftParticleSystem`（按 SettingsManager.VisibilityRange 定 49/64/81 轴）；移动 >1 格才重算；钩子 `SetRainAndSnowColor`。

### SubsystemModelsRenderer.cs (670) — 实体模型渲染
DrawOrders=[-10000,1,99,201]（:87）：-10000 准备帧（可见性+排序+骨骼），1 不透明/alphaTest，99 水前透明，201 水后透明。
- GPU skinning：`MaxJointsCount`/`MaxInstancesCount` 运行时按 `GL_MAX_VERTEX_UNIFORM_VECTORS` 算（Load :214-219，非蒙皮 instance 上限 64、joint 上限 128）；4 个 ModelShader（普通/蒙皮 × opaque/alphaTested，:229-256）。蒙皮 shader instances=1（不批量，腾 uniform 给关节）。
- Draw 准备段（:95-137）：钩子 `PrepareModels` 可跳；可见模型按 `PrepareOrder` 排序进 m_modelsToPrepare；`UseCustomRendering&&CustomRenderer` 时整队交给 ICustomModelRenderer（mod 自渲染管线）。
- `DrawInstancedModels`（:314-435）：钩子 `ModelShaderParameter`/`SetShaderParameter`（return true=不覆盖）/`OnModelDataDrawing`（可 skip 单模型）；材质分组 `InstancedModelsManager.GetInstancedModelDataByMaterial`；DiffuseColor/TextureOverride 优先。
- `DrawSkinnedModel`（:440-537）：`CalculateJointMatrices`（:560-596）——jointMatrix = inverseBind * jointWorldGlTF * rootBoneTransform，注释引用 Plan/GPUSkinningPitfalls.md；`Transforms.World[0]=camera.ViewMatrix`（视图空间约定）。
- `PrepareModel`（:274-287）：Animate 每帧 1 次；光照 `CalculateModelLight`（:598-609）0.1s 缓存，取身体顶 +0.95 高度平滑光。
- 阴影：`DrawModelsExtras`（:539-550）调 `SubsystemShadows.QueueShadow`（直径=2.25×盒宽）。
- `ShadowDraw`（:612-669）独立版阴影算法（SubsystemShadows 的近亲，距离上限 1024 vs 2304）。

### SubsystemAnimatedTextures.cs (598)
`AnimatedBlocksTexture`（:38-45）：RenderTarget2D 副本，Disable 时退回静态图。`Update`（:49-108）受 `AnimatedTextureRefreshLimit` 限频；每帧重画整个方块图集+动画水/岩浆槽；`TerrainMipmapsEnabled` 时隔帧 GenerateMipMaps（:102-105）。
- `AnimateWaterBlocksTexture`（:125-341）/`AnimateMagmaBlocksTexture`（:343-559）：对水(18)/岩浆(92) 的 3×3 槽邻域做双层交叉淡入（2s 周期随机偏移 uv）+ 对角滚动。
- `AnimateFireBlocksTexture`（:561-579）：`ScreenSpaceFireRenderer` 200 粒子往火槽(104) 3 行高度喷，scissor 限定槽区。

### SubsystemPickables.cs (277) — 掉落物
`m_pickables`+`m_pickablesToRemove`+锁 `m_lock`（:80）；`m_blockDemandLedger`（:39）方块批次容量账本（增删自报 `BlocksManager.GetBlockDrawDemand`，Load 恢复也入账 :243，注释解释漂移防护）。
- `AddPickable`（:82-103）：钩子 `OnPickableAdded`；CreationTime 默认现在；`AddPickable<T>` 泛型创建（CreatePickable :114-133）。
- `Update`（:178-203）：`m_soundPlaysInFrame=0` 重置 → 逐个 Pickable.Update（异常 Log.Error+ToRemove）→ 移除批出账；`PlayRandomSound` 包装（:58-64）**每帧限 10 次**（MaxSoundPlayInOneFrame :51）防掉落物入水音效风暴。
- `Draw`（:148-176）：按账本预扩容 → 逐个画（LogDrawError 一次）→ Flush。
- 存档（:217-274）：`"Projectiles"` 同款结构——每项 ValuesDictionary 含 `Class`（Pickable 子类全名）反射恢复；`Save` 每项钩子 `SavePickable`。
- `DefaultCalcVisibilityRange`（:276）= min(VisibilityRange,30)。

### SubsystemProjectiles.cs (366) — 抛射物
结构与 Pickables 镜像：m_projectiles/ToRemove/锁/`m_blockDemandLedger`（:42-43）；DrawOrders=[10]。
- `AddProjectile(Projectile)`（:67-90）：记 CreationTime、IsInFluid、钩子 `OnProjectileAdded`（Load 恢复时带 valuesDictionary 第二参 :297-303）、入账、Owner.PlayerStats.RangedAttacks++、`ProjectileAdded` 事件。
- `CreateProjectile<T>`（:98-116）泛型初始化（委托闭包注入 Terrain/DrawEnv/Fog/Renderer）；`AddProjectile<T>`（:118-129）；`FireProjectile<T>`（:164-172）=CanFireProjectile（:134-162，从 owner 身后回退发射点+ProjectileTipOffset 射线探空）→`FireProjectileFast`（:174-183，逐 blockBehavior `OnFiredAsProjectile`）。
- `AddTrail/RemoveTrail`（:185-198）烟尾粒子挂/摘。
- `Update`（:230-261）：移除批先查 ToRemove；逐个 Update（异常 Log.Error+ToRemove）；移除时账本出账+`ProjectileRemoved`。
- `Draw`（:200-228）：按账本预扩容；`AnimatedBlocksTexture` 作为批次纹理；逐个 Draw（LogDrawError 一次）。
- 存档（:278-330）：同 Pickables，`Class` 反射恢复（TypeCache.FindType(className,false,true)）。
- Obsolete 提示（:341-357）：更新逻辑已迁 `Projectile.Update()`；`IsMagma/MakeProjectileNoise` 弃用。
- `CalculateVelocityAlignMatrix`（:359-365）：速度方向 Up 构造朝向矩阵。

### SubsystemAudio.cs (202)
队列制：`PlaySound`（:86-96）只进 `m_queuedSounds`（Time=GameTime+delay），`Update`（:143-169）到期才 `AudioManager.PlaySound`；游戏时间倍率≠1 或 FixedTimeStep 时**全部静音**（:156-158）。
- `CalculateVolume`（:135-137）反比衰减 rolloff 2；`CalculateDelay`（:139-141）=min(dist/120,3)s 声速延迟；`CalculateListenerDistance(Squared)`（:57-68）取多视角最近。
- `PlayRandomSound`（:108-127）按目录随机挑；目录空 Log.Warning。
- `CreateSound`（:129-133）常驻循环音（火/水/岩浆/雨/引信用）。
- 拥塞控制 `UpdateCongestion`（:182-201）：同名音 0.33s 内累计，Value>6 拒播（同屏大量同类声不叠爆）。
- `Mute/Unmute`（:70-84）暂停/恢复全部。

### SubsystemPlayers.cs (139)
`m_playersData`(PlayerData 列表) + `m_componentPlayers`(缓存视图 :131-138)；`MaxPlayers=4`（:16 static）。
- `AddPlayerData`（:54-64）超 4 抛异常；`RemovePlayerData`（:66-76）连带 RemoveEntity。
- `Update`（:78-85）：**无人时强制切 PlayerScreen.Initial**（:79-81）；逐 PlayerData.Update。
- `UpdateOrder => UpdateOrder.SubsystemPlayers`（=-20，很早）。
- 存档（:93-115）：NextPlayerIndex/GlobalSpawnPosition/Players 袋子。
- `FindNearestPlayer`（:41-52）/`IsPlayer`（:32-39）。

### SubsystemGameInfo.cs (117)
世界元数据：WorldSettings/DirectoryName/TotalElapsedGameTime/WorldSeed（:11-19）。
- `Update`（:93-116）：累加游戏时间；季节推进（AreSeasonsChanging 时每 10s 推 TimeOfYear :97-101）；GameTime 过 600s 那一帧上报游玩时长（CommunityContentManager.SendPlayTime :102-115）。
- `GetActiveExternalContent`（:23-75）：世界/贴图/皮肤/家具包四类外部内容枚举。
- 存档（:77-91）：WorldSettings.Save+WorldSeed+TotalElapsedGameTime。

### SubsystemTimeOfDay.cs (95)
`DayDuration=1200s`（:13，一天 20 分钟）；DawnStart/DayStart/DuskStart/NightStart 由 `UpdateStarts`（:84-94）按季节算白昼长（夏长冬短，num3∈0.2-0.4）。
- `TimeOfDay`（:39-60）：Changing 模式由 TotalElapsedGameTime 推；固定模式返 Midday/Midnight/Middawn/Middusk；TimeOfDayEnabled=false 返 Midday。
- `TimeOfDayOffset` 存档唯一字段（:80-82）——改时间=改偏移。
- `CalculateDay/CalculateTimeOfDay`（:66-71）。

### SubsystemSeasons.cs (83)
静态季界：Summer 0/Autumn 0.25/Winter 0.5/Spring 0.75（:13-19）；`TimeOfYearToSeason`（:65-82）线性归一。
- `Update`（:59-63）每 tick 从 WorldSettings.TimeOfYear 刷新 Season/TimeOfSeason。
- `GetTimeOfYearName/Color`（:37-53）UI 用。
- 无存档字段——季节由 GameInfo.WorldSettings.TimeOfYear 承载。

### SubsystemPathfinding.cs (352) — 后台线程寻路
`Request`（:7-21）含 BoxSize（碰撞体尺寸）/IgnoreDoors/MaxPositionsToCheck/PathfindingResult。
- `QueuePathSearch`（:191-223）：队列上限 10，**满了直接置 IsCompleted+空路径返回**；lock+Monitor.Pulse。
- `Load`（:225-232）建 AStar+Storage+World，`Task.Run(ThreadFunction)` 常驻；`ThreadFunction`（:241-258）Monitor.Wait 等队列，**每请求后 Task.Delay(250)**；Dispose enqueue null 退出（:234-240）。
- `World`（:40-183）：8 邻域 `AddNeighbor`（:70-126）——目标格可碰撞时用 `GetBlockWalkingHeight`（门/栅栏门 0，其余取自定义盒最高 :128-140）、NoAutoJump/NoSmoothRise 且高差>0.5 拒；空中格向下探 4 格找落点；斜走 3 步插值盒检测 `IsBlocked`（:142-182，逐格自定义盒求交）；Heuristic 对角 1.41（:59-66）；Cost 偏向终点方向（:45）。
- `ProcessRequest`（:261-273）→`SmoothPath`（:275-281）拉直线消除中间点（`IsPassable` 3 条障碍线+3 条支撑线射线 :283-327）。

### SubsystemBlocksScanner.cs (121) — 方块轮询调度
`MaxShaftsPerFrame=500`（:30）、`ScanPeriod=60s`（:7）、`UpdateOrder => UpdateOrder.BlocksScanner`（:32）。
- `Update`（:36-97）：预算制——`m_pollShaftsCount += 已分配chunk数×256×dt/60`，clamp 上限 500；`terrain.LoopChunks` 循环全 chunk；每轴从 0 到 TopHeight 逐格调 `SubsystemPollableBlockBehavior.OnPoll(value,x,y,z,pollPass)`（异常 Log.Error 带坐标 :67-74）；chunk 完成发 `ScanningChunkCompleted` 事件（天气结冰挂这里）；`hasLooped` 时 pollPass++。
- 存档（:116-120）：PollChunkCoordinates/PollPoint/PollPass——**轮询进度跨存档保留**。
- `Load`（:99-114）：从 SubsystemBlockBehaviors 过滤出每 contents 的 Pollable 列表。

### SubsystemBlockBehaviors.cs (49) — behavior 绑定器
`Load`（:16-48）：两路绑定——①`BlocksManager.Blocks[i].Behaviors` 字符串（逗号分隔子系统 Name）→ `Project.FindSubsystem<SubsystemBlockBehavior>(name)`；②各 behavior 的 `HandledBlocks` 补进表。得到 `m_blockBehaviorsByContents[contents][]`。
- 聚合检测（:39-46）：反射判断 behavior 是否 override OnUse → `BlocksManager.Blocks[k].DefaultIsUseable=true`；注释说明假定所有 behavior 在本 Load 前注册。
- `GetBlockBehaviors(contents)`（:14）是全 behavior 消费端入口。

### SubsystemBlockBehavior.cs (77) — behavior 基类契约
抽象基类（:6-77）：`HandledBlocks => []`（:7）、`SubsystemTerrain` 属性（Load :72-74 注入）。虚方法全集：
生命周期：OnChunkInitialized/OnChunkDiscarding/OnBlockGenerated/OnBlockAdded/OnBlockRemoved/OnBlockModified/OnBlockStartMoving(默认转 OnBlockRemoved :23-25)/OnBlockStopMoving(默认转 OnBlockAdded :27-29)/OnNeighborBlockChanged；
交互：OnUse/OnInteract(Terrain 版+Moving 版)/OnAim/OnEditBlock/OnEditInventoryItem；
物品：OnItemPlaced/OnItemHarvested/GetProcessInventoryItemCapacity/ProcessInventoryItem(默认抛异常 :62-70)；
物理/投射：OnCollide/OnExplosion/OnFiredAsProjectile/OnHitAsProjectile/OnHitByProjectile(CellFace 版+MovingBlock 版)；
拾取：OnPickableGathered（:76）。

### SubsystemEntityBlockBehavior.cs (114) — 方块实体基类
`m_databaseObject`（子类 Load 里 FindDatabaseObject 填，如 Chest/CraftingTable/Dispenser/Furnace）。
- `OnBlockAdded`（:25-35）：已有 blockEntity 则 Log.Error 拒加；`ValuesDictionary.PopulateFromDatabaseObject`+`BlockEntity.Coordinates` → CreateEntity+AddEntity。
- `OnBlockRemoved`（:37-46）：IInventory.DropAllItems+RemoveEntity。
- `OnInteract`（:48-76）：取 blockEntity → 钩子 `OnEntityBehaviorBlockInteracted`（mod 可替换实体）→ `InteractBlockEntity`（子类开 UI）。
- `OnBlockStartMoving/StopMoving`（:80-97）：搬 `m_subsystemBlockEntities.m_blockEntities↔m_movingBlockEntities`，更新 blockEntity.MovingBlock/Coordinates。
- `OnHitByProjectile`（:99-113）：`blockEntity.GatherPickable(worldItem)` 投射物收纳（漏斗/发射器原理）。

### SubsystemEditableItemBehavior.cs (159) — 可编辑数据基类（泛型）
`SubsystemEditableItemBehavior<T> : SubsystemBlockBehavior where T : IEditableItemData, new()`（:6）。三字典：`m_itemsData`(id→T)、`m_blocksData`(Point3→T)、`m_movingBlocksData`(MovingBlock→T)（:11-14）。
- `StoreItemDataAtUniqueId`（:51-55）+`FindFreeItemId`（:133-140，1..999 线性找空）。
- `OnItemPlaced`（:57-63）物品→方块复制；`OnItemHarvested`（:65-72）方块→物品回填 data；OnBlockRemoved 清 blocks；Start/StopMoving 搬字典（:78-90）。
- 存档 Blocks（键 Point3 或 MovingBlock 字符串自动判 :95-106）+Items；`GarbageCollectItems`（:142-158）挂 ItemsScanner.ItemsScanned 清孤儿 id。
- 子类：TruthTable(188)/MemoryBank(186)。

### SubsystemBlocksManager.cs (62) — 动态方块 ID 持久化
**override Initialize 而非 Load**（:23-30）——先于一切 Load 跑；`InitializeBlocks(this)`(BlocksManager 静态) + `PostProcessBlocksLoad` + `CraftingRecipesManager.Initialize()`。
- `CallAllocate`（:32-55）：从袋子读 `"1023"→"类名"` 映射建 `DynamicBlockNameToIndex`（SurvivalCraftBlockCount+1..1023）。
- `Save`（:57-61）：反向写 `"index"→"类名"`。**动态 ID 稳定性靠这条链**。

### SubsystemUsedMods.cs (31)
`Save` only（:6-30）：ModList 里非 SurvivalCraftModEntity/FastDebugModEntity、非 NonPersistentMod 的 modInfo（Name/Version/ApiVersion/ScVersion/Author/Link/PackageName）写进 `"Mods"` 袋子+ModsCount。读端在别处比对 mod 是否仍在。

### SubsystemPlayerStats.cs (49)
`m_playerStats`(playerIndex→PlayerStats)；`GetPlayerStats`（:9-15）懒建。Load（:17-38）：恢复；**非 SafeMode 时取所有启用 mod 的最高 GameplayImpactLevel 并抬升玩家 HighestGameplayImpactLevel**（:24-37）。Save（:40-48）逐玩家。

### SubsystemCellChangeQueue.cs (54)
`QueueCellChange(x,y,z,value,applyImmediately)`（:26-36）：立即 or 入 `m_toChange`（记 RequiredValue=当时值）；**≥10000 条强制冲刷**（:33-35）；Update 每 20s `ApplyCellChanges`（:38-53）：当前值(清光位)==RequiredValue 才 ChangeCell——乐观锁防覆盖。消费者：植物生长/仙人掌/落叶。

### SubsystemPalette.cs (103)
16 色调色板（WorldPalette）：Load 从 WorldSettings.Palette 取 Colors/Names（:85-90）；`CreateFabricColors`（:92-102）饱和度×0.85 衣料色。静态 `GetColor/GetFabricColor/GetName`（:27-83）三级回退（generator/environmentData/terrain→默认）。方块染色/家具用。

### SubsystemSoundMaterials.cs (104)
撞击/脚步声材质映射（存档 `ImpactSounds`/`FootstepSounds` 两袋子 :98-103）。`PlayImpactSound`（:17-27）查 `block.GetSoundMaterialName`。`GetFootstepSoundMaterialName`（:68-96）：水深>0.2→"Water"；梯子 59→WoodenLadder 否则 MetalLadder；脚下格→StandingOnValue 兜底。`PlayFootstepSound`（:29-66）先查生物自定义（ComponentCreatureSounds 袋子 CustomFootstepSounds）再全局；湿脚加 Squishy（Wetness^4 音量 :47-61）。

### SubsystemItemsScanner.cs (108) — 全物品扫描
`ScanItems`（:17-60）：所有 Project.Subsystems 中 IInventory → Project.Entities 组件 IInventory → Pickables → Projectiles → MovingBlockSets 逐块，产出 ScannedItemData{Container,IndexInContainer,Value,Count}。`TryModifyItem`（:62-84）按容器类型改写（IInventory 换值/WorldItem.Value/IMovingBlockSet.SetBlock）。`Update`（:86-91）每 60s 帧时间触发 `ItemsScanned` 事件。消费者：Rot 腐烂/EditableItem GC/FurnitureDesign GC。

### SubsystemBlocksTexture.cs (35)
`BlocksTexture` 从 `BlocksTexturesManager.LoadTexture(WorldSettings.BlocksTextureName)`（:19-22）；DeviceReset 重载；Dispose 非 Content 才释放（:24-30）。

### SubsystemNoise.cs (37)
`MakeNoise(position,loudness,range)`（:11-13）/`MakeNoise(body,...)`（:15-17）→`MakeNoisepublic`（:23-36）：Bodies 找半径内 body→逐 `INoiseListener.HearNoise`。声音感知链底座。

### SubsystemNames.cs (42)
`ComponentName` 注册表 `m_componentsByName`（:5）；`FindEntityByName/FindComponentByName`（:7-21）按名查实体；OnEntityAdded/Removed 维护。重名后加者顶掉（Dictionary Add）。

### SubsystemBlockEntities.cs (46)
`m_blockEntities`(Point3→ComponentBlockEntity)+`m_movingBlockEntities`(MovingBlock→)（:6-8）；`GetBlockEntity` 三重载（:10-23）；OnEntityAdded/Removed 维护（:25-45，Y<0 不入表 :31-33）。**方块实体（箱子/熔炉/告示牌…）的空间定位**。

### SubsystemAmbientSounds.cs (81)
火/水/岩浆三条循环音；`Update`（:26-67）音量向 `SettingsManager.SoundsVolume×FireSoundVolume` Lerp(3×帧时长)，>0.5×MinAudibleVolume 才 Play 否则 Pause；岩浆 0.2×dt 概率 Sizzles；**每帧末尾三个 Volume 清零**（:64-66）——由各行为 Update 里 `MathUtils.Max(上值,自己的)` 竞争写入。

### SubsystemGlow.cs (122) — 发光点精灵
`m_glowPoints`(GlowPoint→bool)；`AddGlowPoint/RemoveGlowPoint`（:20-28）。`Draw`（:30-81）：按点数×4/6 **精确预扩容** 4 批次（:35-42，RoundGlow/SquareGlow/HorizontalRectGlow/VerticalRectGlow）；背面剔除+雾色 Lerp+FarDistance 缩放。DrawOrders=[110]。

### SubsystemShadows.cs (128)
`QueueShadow`（:20-78）：≤48 格；对影子圆覆盖的每格从影位向下探 2 格找 `GetObjectShadowStrength>0` 的块，用其自定义碰撞盒画 4 边形贴顶（alpha=0.45×强度×距离衰减×雾×高度衰减）；contents==18(水) break。`Draw`（:80-82）只 Flush。DrawOrders=[200]。

### SubsystemDrawing.cs (134) — IDrawable 调度
`m_drawables`(IDrawable→bool)+`m_sortedDrawables`(SortedMultiCollection<int,IDrawable>)（:9-11）。
- `Draw(camera)`（:39-80）：锁表按 `DrawOrders` 展开→排序→逐个 `Draw(camera, drawOrder)`——**异常静默 catch**（:57-59）；`UpdateTimeDebug` 计时表（:88-110）。
- `AddDrawable/RemoveDrawable`（:25-37）重复加 Log.Error；OnEntityAdded/Removed（:112-133）实体组件 IDrawable 自动进出（钩子 `OnIDrawableAdded` 可 skip）。
- `Load`（:82-86）收集所有实现 IDrawable 的子系统。

### SubsystemParticles.cs (156)
`m_particleSystems`(ParticleSystemBase→bool)+`m_batchDemand` 账本（:10-13，增删自报 GetBatchDemands）。
- `AddParticleSystem/RemoveParticleSystem`（:35-59）挂/摘+记账（`BookBatchDemand` :62-81，静态 s_demandEntries 避分配）。
- `Update`（:90-108）：`Simulate(GameTimeDelta)` 返 true 或异常 → 结束移除批。
- `Draw`（:110-155）：按账本 TexturedBatch().EnsureCapacity 精确预扩容 → 逐系统 Draw（异常 Log.Error）→ 统一 AlphaTested shader 雾参数 → 逐批 FlushWithDeviceState。DrawOrders=[300]（最上）。
- 开关 `ParticleSystemsDraw/Simulate`（:21-22）。

### SubsystemGameWidgets.cs — 不在本目录（Views），被 8+ 子系统引用（视角列表/最近距离计算）。

## 二、BlockBehavior 子目录 71 个文件逐个笔记

### 基础设施类
- **SubsystemPollableBlockBehavior.cs (4)**：抽象 `OnPoll(value,x,y,z,pollPass)`（:3）——被 BlocksScanner 周期轮询。
- **SubsystemWaterBlockBehavior.cs (60)**：水流体（HandledBlocks=[18]，构造传 FluidBlocks[18]+generateSources:true :13）。`Update`（:15-31）每 0.25s `SpreadFluid()`；水声距离积分。`OnFluidInteract`（:33-49）遇岩浆→DestroyCell+Set 石头(3)+Sizzles。`OnItemHarvested`（:51-59）y>80 且冻结给冰(62)。
- **SubsystemMagmaBlockBehavior.cs (100)**：岩浆（[92]，无水源生成）。每 2s SpreadFluid；`ApplyMagmaNeighborhoodEffect`（:78-99）加火+雪(61/62)烧毁+草(8)变土(2)；遇水→黑曜石(67)（:54-70）。
- **SubsystemFluidBlockBehavior.cs (388)**：流体基类。`SpreadFluid`（:149-265）两轮：m_toUpdate→level 扩散（侧 4 格最低 level+1）、水源生成（generateSources && level!=0 && 侧同液 level==0 计数≥2 :190-194）、下落探测（`LevelAtNearestFall` BFS :354-387）→ `FlowTo`；m_toSet 落盘（异液 DestroyCell 交互 :243-257）→ **每轮 `ProcessModifiedCells()`**（:263）。`GetSurfaceHeight`（:66-94）/`CalculateFlowSpeed`（:96-140，SimplexNoise 随机流缓存 1000 条自清 :123-132）。`OnFluidInteract` 默认版（:267-282）替换非 FluidBlocker。
- **SubsystemFireBlockBehavior.cs (405)**：火=方块 104，data 是 4 位面 bitmask（bit0=+z,1=+x,2=-z,3=-x；y 向单独）。`SetCellOnFire`（:80-104）在 5 面（4 水平+下）找空气/已有火/雪格点燃。`Update`（:106-243）分帧：每帧最多扫 50 火点（:118-121），各面倒计时（Time0-3/Time5，初始化=相邻可燃物 FireDuration×0.75-1.25 :376-399）到 0 → `QueueBurnAway`；按 `m_expansionProbabilities`（Load 预计算 5×3×5 邻域 0.02/(横向距+纵向罚) :344-360）×FireExpandability×0.85 蔓延；每 5s 统一执行 toBurnAway（ChangeCell 0+再点燃邻居+烟/声限流 15/4 :204-241）。`IsCellOnFire`（:60-78）供引信/爆炸用。**火不存档**——FireData 全内存，重载后按方块 104 重新 OnBlockGenerated 点燃。
- **SubsystemPistonBlockBehavior.cs (557)**：`UpdateOrder => MovingBlocks.UpdateOrder+1`（:40）。`AdjustPiston`（:44-50）进 m_actions；`Update`（:52-57）每 0.125s `ProcessQueuedActions`（:204-251：Stop 优先且同帧禁 Move；周围 3×3 chunk 有效才动）+`UpdateMovableBlocks`（:253-288：轴/头随位置动态增删）。`MovePiston`（:311-469）：沿 face 收集活塞头(238)链 ≤8 → 推（长度增：加头+收集 ≤8 可推块 `IsBlockMovable` :549-554）/拉（StrictPulling 需满 pullCount+1 :411-431）→ AddMovingBlockSet("Piston",tag=position,testCollision:true) → 源格 ChangeCell(0,movingBlock)；速度表 GetSpeedAndSmoothness（:290-309，5/4.5/4/3.5）。`StopPiston`（:471-503）写回（`AddTerrainBlock`）。`OnBlockRemoved`（:106-180）拆头/座联动（m_allowPistonHeadRemove 临时放行 :381-398）。常量：MaxMovedBlocks=8/MaxExtension=8/MaxSpeed=3（:34-38）。
- **SubsystemCollapsingBlockBehavior.cs (117)**：塌方。`OnNeighborBlockChanged`（:14-18）Living 模式 `TryCollapseColumn`（:67-104）：下方非支撑块 → 从该格向上收集连续 `GetIsCollapsable` 块 → AddMovingBlockSet("CollapsingBlock", 加速度 10/drag 0.7) → 源格清 0。`MovingBlocksCollidedWithTerrain`（:29-47）：撞支撑块停/撞可毁块 DestroyCell。`MovingBlocksStopped`（:49-65）：逐块 AddTerrainBlock+音效+RemoveMovingBlockSet。

### 容器/交互实体类（SubsystemEntityBlockBehavior 子类）
- **SubsystemChestBlockBehavior.cs (22)**：[45]，"Chest" 模板，Interact 开 ChestWidget（:12-21）。
- **SubsystemCraftingTableBlockBehavior.cs (25)**：[27]，"CraftingTable"，开 CraftingTableWidget。
- **SubsystemDispenserBlockBehavior.cs (40)**：[216]，"Dispenser"；冒险模式禁用 UI（:13）；`OnHitByProjectile` 受 `AcceptsDrops` 控制（:25-39）。
- **SubsystemFurnaceBlockBehavior.cs (88)**：[64,65]；火焰粒子逻辑全注释掉（AddFire/RemoveFire 空壳 :70-87）；OnBlockAdded 只在非 64/65 间转换才创建实体（:12-20）。

### 可编辑数据类（SubsystemEditableItemBehavior 子类）
- **SubsystemMemoryBankBlockBehavior.cs (88)**：[186]；按 `SettingsManager.UsePrimaryMemoryBank` 选 EditMemoryBankDialog / EditMemoryBankDialogAPI（:19-46）；编辑后把 ElectricElement 排下步模拟（:60-64）。
- **SubsystemTruthTableCircuitBlockBehavior.cs (52)**：[188]；同款结构（:9-51）。

### 电力类
- **SubsystemElectricBlockBehavior.cs (164)**：`HandledBlocks` **63 个硬编码 ID**（:8-70，133/140/137/143/156/134/135/145/224/146/157/180/181/183/138/139/141/142/184/187/186/188/144/151/179/152/254/253/182/185/56/57/58/83/84/166/194/86/63/97/98/210/211/105/106/107/234/235/236/147/153/154/223/155/243/120/121/199/216/227/237）。全部生命周期转发 `SubsystemElectricity.OnElectricElementBlockAdded/Removed/Modified/Generated`（:72-98）；OnNeighborBlockChanged 转 6 面 ElectricElement.OnNeighborBlockChanged（:100-105）；OnInteract/OnCollide/OnHitByProjectile 找到第一个面元素转发。
- **SubsystemBatteryBlockBehavior.cs (56)**：[138]；EditVoltageLevelDialog 改电压；改完把**连接**排下步（QueueElectricElementConnectionsForSimulation :45-48）。
- **SubsystemButtonBlockBehavior.cs (48)**：[142]；同款改电压 UI（不触发电路重算——按钮自己会发脉冲）。
- **SubsystemSwitchBlockBehavior.cs (48)**：[141]；同款。
- **SubsystemAdjustableDelayGateBlockBehavior.cs (51)**：[224]；改 Delay 后把该格元素排下步（:40-44）。
- **SubsystemFenceGateBlockBehavior.cs (58)**：`OpenCloseGate`（:12-25）SetOpen+ChangeCell+门音；`IsGateElectricallyConnected`（:27-39）铰链面元素有连接时手点无效（:41-52，contents==166 铁门直接走电）。
- **SubsystemTrapdoorBlockBehavior.cs (96)**：[83,84]；同款开门逻辑+电连接检查（:12-52）；OnNeighborBlockChanged 支撑检测含 upside-down 双点（:54-90）。
- **SubsystemDoorBlockBehavior.cs (127)**：[56,57,58]；`OpenCloseDoor`（:12-25）；`IsDoorElectricallyConnected`（:27-42）查上下两格铰链面；`OnBlockAdded`（:57-64）自动补上/下半扇；`OnBlockRemoved`（:66-73）拆另一半；OnNeighborBlockChanged 同步 data+支撑缺失毁门（:75-121）。

### 武器/发射类
- **SubsystemBowBlockBehavior.cs (198)**：OnEditInventoryItem 开 BowWidget；`OnAim`（:37-155）：SimplexNoise 手抖（蹲 0.02/站 0.04 + 拉弓累积 :53-61）；InProgress 每抽 0.1s draw+1（:78-83）；Completed 按 draw 算初速 `Lerp(0,28,(draw/15)^0.75)`×力量系数（:98-101）FireProjectile+木/石箭散布（:103-108）；耐久 draw≥15 扣 2/≥4 扣 1（:139-146）。`GetProcessInventoryItemCapacity/ProcessInventoryItem`（:157-188）装箭。
- **SubsystemCrossbowBlockBehavior.cs (192)**：同款；draw 必须==15 才能装填/发射（:80-87）；初速 38；支持 IronBolt/DiamondBolt/ExplosiveBolt（:17-19）。
- **SubsystemMusketBlockBehavior.cs (302)**：装填状态机 Empty→Gunpowder→Wad→Loaded（GetProcessInventoryItemCapacity :233-249 / ProcessInventoryItem :251-289）；瞄准 0.5s 后扳机竖起（:68-72）；Completed：Buckshot 8 弹散布 0.25/80 速、独头弹 60、其它 120（:119-149）；**水中(ImmersionFactor>0.4)哑火**（:154-163）；后坐力 ApplyImpulse(-4×方向)（:199）；枪声+烟+噪声 40 格。
- **SubsystemThrowableBlockBehavior.cs (82)**：`OnAim`（:14-75）：InProgress 摆投掷姿势（矛特殊旋转）；Completed 从右手 0.4 偏移 FireProjectile（速度=block.GetProjectileSpeed×力量系数 :46-49）+移除 1 个+掷音。
- **SubsystemArrowBlockBehavior.cs (50)**：`OnFiredAsProjectile`（:12-18）火箭加烟尾+IsIncendiary；`OnHitAsProjectile`（:20-44）按箭型概率留箭（速度>10 时：钻石 0/铁螺栓 0.05/木 0.2/火 0.5）。
- **SubsystemBulletBlockBehavior.cs (56)**：`OnHitAsProjectile`（:16-48）：速度>30 时 `TryExplodeBlock` 命中面（**穿甲爆**）；密度≥1.5 且>30 概率跳弹（Ricochets 音）返 false 不消耗。
- **SubsystemImpactExplosivesBlockBehavior.cs (21)**：`OnHitAsProjectile` → `TryExplodeBlock`（:9-15）撞击爆炸。
- **SubsystemBombBlockBehavior.cs (67)**：`OnFiredAsProjectile` 式跟踪：Load 扫全部投射物+订阅 ProjectileAdded/Removed（:29-33）——`ScanProjectile`（:36-50）把炸弹弹标记 DoNothing(不消失)+烟尾；`Update`（:52-66）每 0.1s 检查 creationTime>5s → 爆+移除（**5 秒引信**）。
- **SubsystemFireworksBlockBehavior.cs (138)**：`OnFiredAsProjectile`（:48-63）0.8/1.3s 延时 `QueueGameTimeDelayedExecution` → `ExplodeFireworks`（:32-46，先向上 3 射线防天障）；`Update`（:79-137）元旦彩蛋：1 月 1 日 0 点后 180s 自动放烟花（SettingsManager.NewYearCelebrationLastYear 记年 :84-98）；`OnHitAsProjectile` 恒 true 消耗。

### 工具/种植/农业类
- **SubsystemHammerBlockBehavior.cs (23)**：`OnUse`（:10-17）→ `SubsystemFurnitureBlockBehavior.ScanDesign`——锤子=家具扫描器。
- **SubsystemRakeBlockBehavior.cs (101)**：[169,219,171,172]；`OnUse`（:14-93）顶面：草(2)→耕地(168)/耕地(8 土块→2 草? 实际 case 8 土变草位 2——**case 8 是把土(8?) 恢复**，实际语义：case 2 dirt→168 耕地、case 8 → 2（耙掉耕地恢复泥土））；DamageActiveTool。
- **SubsystemFertilizerBlockBehavior.cs (58)**：[102]；`OnUse`（:14-50）顶面 3×3 内耕地(168) 施氮 SetNitrogen(3)+碎屑粒子。
- **SubsystemBucketBlockBehavior.cs (218)**：`HandledBlocks` 9 个（4 桶+245/251/252+128/129 颜料桶 :21-31）；`OnUse`（:33-205）：空桶装水(满 level 0)/岩浆/挤奶(ComponentUdder)；水/岩浆桶倒出（Place+换空桶）；128 白颜料/129 彩色桶对 IPaintableBlock.Paint（:172-202）。
- **SubsystemSaplingBlockBehavior.cs (226)**：[119]；`OnBlockAdded`（:48-57）记 `SaplingData{Point,TreeType,MatureTime=+480-600s(创造 8-12s)}`；`Update`（:82-96）每 tick 最多 10 棵 `MatureSapling`（:120-189）：四角 chunk 全 Valid 才长；光≥9；水分/温湿度算概率 `PlantsManager.CalculateTreeProbability×2`；失败/超时变枯木(28)；`GrowTree`（:191-215）随机刷 20 次 TerrainBrush，需空间空(叶豁免)。存档 "Saplings" 字符串三元组（:98-118）。
- **SubsystemPlantBlockBehavior.cs (307)**：[19,20,24,25,28,99,131,244,132,174,204]；**OnNeighborBlockChanged sealed**（:42，注释禁止覆盖——mod 加植物应另写 ModPlantBlockBehavior）。`OnPoll`（:74-79）Living 模式 Grow+Lifecycle；`Grow`（:81-112）钩子 `GrowPlant` 可 skip——19 高草/FlowerBlock 长高（光≥9 :122-140）、174 黑麦/204 棉花/131 南瓜：光≥9+耕地氮/水/季温算间隔 pollPass%num==0 或概率跳过（:142-304），成熟扣氮。Lifecycle 空虚方法（:306）。
- **SubsystemSoilBlockBehavior.cs (133)**：[168]；`OnCollide`（:18-27）质量>20 重摔退化（m_toDegrade）；`OnPoll`（:29-39）`DetermineHydration`（:88-114，4+2 方向 3 步 BFS 找水/湿土）→ m_toHydrate；`Update`（:54-77）每 2.5s 退化→2、每 10s 改 SetHydration；`OnNeighborBlockChanged`（:41-47）上压退化。
- **SubsystemGrassBlockBehavior.cs (119)**：[8]；`OnPoll`（:18-56）：data==0（无雪）且 Living；上方光==0 记退化、光≥13 时向 3×3×4 邻域扩散草(2→8)+随机长植物 `PlantsManager.GenerateRandomPlantValue`（:45-52）；`Update`（:87-106）每 60s 批量 ChangeCell；`OnNeighborBlockChanged`（:58-73）雪盖 data=1/清理；`KillsGrassIfOnTopOfIt`（:108-118）；`OnExplosion`（:75-79）草→土。
- **SubsystemCactusBlockBehavior.cs (72)**：CactusBlock；`OnNeighborBlockChanged`（:18-32）下非沙/仙人掌毁；`OnPoll`（:34-48）Living：上方空+光≥12+下方两格非仙人掌 → 25% `QueueCellChange` 长高一节；`OnCollide`（:50-62）扎伤 `OnSpiked`。
- **SubsystemSaplingBlockBehavior** 见上。
- **SubsystemIvyBlockBehavior.cs (64)**：`OnPoll`（:52-58）50% 且下方空记 m_toUpdate；`Update`（:16-25）每 60s 铺藤（GrowthStopCell 检查 :54）；`OnNeighborBlockChanged`（:27-50）上方非同藤且贴附面塌则毁。
- **SubsystemWoodBlockBehavior.cs (140)**：树叶凋零。`OnBlockRemoved`（:21-49）砍木→3 格半径收集叶入 `m_leavesToCheck`（上限 5000）；`Update`（:70-82）每 20s 消化 10%~200 棵 `DecayLeavesIfNeeded`（:101-139，3 格内无木→ChangeCell 0）；OnChunkDiscarding 提前清（:51-68）；存档 "LeavesToCheck"。
- **SubsystemDeciduousLeavesBlockBehavior.cs (131)**：阔叶四季变色。`OnPoll/OnBlockGenerated`→`UpdateTimeOfYear`（:106-121，按位置哈希微移季节相位 SetTimeOfYear，入冬 `CreateFallenLeaves` :36-54 落叶 261）+`QueueLeafParticles`（:123-130，≤30000 条 1s 延迟队列）；`Update`（:77-104）每 1s 到点且 <32 格出落叶粒子。

### 电路显示类
- **SubsystemMetersBlockBehavior.cs (326)**：[120,121] 温度计；`m_thermometersByPoint`（:12）；`Update`（:88-102）轮转模拟（周期=max(4/数量,0.5)s）；`CalculateTemperature`（:120-282）**63³ 体素 BFS**：热源(GetHeat)/隔热块(IsHeatBlocker)/露天三种加权平均+7³ 视线可达热源二次计权（:216-252）→ environmentTemperature/targetTemperature/flux；`SimulateThermometer`（:289-315）写读数+降 chunk 顶点态重绘。
- **SubsystemFireworksBlockBehavior** 见上。

### 感知/陷阱类
- **SubsystemSpikesBlockBehavior.cs (84)**：SpikedPlankBlock；`RetractExtendSpikes`（:28-44）SetSpikesState+最近音；`OnCollide`（:46-70）展开面扎伤 1/韧性，1s 冷却表（:15，OnEntityRemoved 清 :78-83）。
- **SubsystemGrassTrapBlockBehavior.cs (62)**：[87] 草皮陷阱；`OnCollide`（:17-27）质量>20 顶面累积 Damage；`Update`（:29-61）Damage>1 → 十字 5 格 DestroyCell。
- **SubsystemBottomSuckerBlockBehavior.cs (57)**：底吸生物块；`OnNeighborBlockChanged`（:15-32）贴附面失支撑毁；`OnCollide`（:34-48）海胆(contents==m_seaUrchinBlockValue) 扎伤 0.1/韧性×|v|。

### 结构/形态类
- **SubsystemStairsBlockBehavior.cs (195)**：ctor 动态 HandledBlocks=全部 StairsBlock（:9-13）；`UpdateIsCorner`（:28-194）——与相邻楼梯组合算 CornerType.OneQuarter/ThreeQuarters（16+16 组合表 :47-188）。
- **SubsystemFenceBlockBehavior.cs (39)**：`UpdateVariant`（:14-38）四邻 `ShouldConnectTo` bitmask SetVariant+ChangeCell。
- **SubsystemLadderBlockBehavior.cs (25)**：[59,213]；贴附面 `IsFaceNonAttachable` 毁。
- **SubsystemTorchBlockBehavior.cs (123)**：[31,17,132]；火把粒子管理：Add/Remove/OnBlockModified 换粒子（:52-67）；支撑检测（:12-50）；OnChunkDiscarding 清粒子（:69-82）。AddTorch 按 data 定偏移（:89-115）。
- **SubsystemCampfireBlockBehavior.cs (194)**：营火 data=火势 1-15；`AddCampfireParticleSystem`（:126-135）data>0 挂火粒子（尺寸 Lerp 0.2-0.5）；`Update`（:30-54）每 5s：降水淋/每 6 轮自然 `ResizeCampfire(-1)`；0.5s 刷火声；`AddFuel`（:145-171）先 TryExplodeBlock（炸药引燃）/雪冰灭火/燃料 `GetFuelHeatLevel`→Resize；`OnInteract` 添加燃料（:111-116）；`OnHitByProjectile` 投掷物当燃料（:104-109）。
- **SubsystemCarpetBlockBehavior.cs (48)**：`OnNeighborBlockChanged` 支撑；`OnPoll`（:31-47）25% 概率查降水轴——**雨淋毁地毯**。
- **SubsystemSnowBlockBehavior.cs (32)**：[61]；支撑检测 `CanSupportSnow`（:19-26，NonAttachable 仅叶可承雪）；静态 `CanBeReplacedBySnow`（落叶可被雪替换）——被 Weather 调用。
- **SubsystemFallenLeavesBlockBehavior.cs (73)**：落叶层；`CanSupportFallenLeaves`（非透明块 :43-46）/`StopsFallenLeaves`/`CanBeReplacedByFallenLeaves` 静态三件套（被 DeciduousLeaves 用）；`OnPoll`/`OnBlockGenerated`→`UpdateFallenLeaves`（:59-72）春夏 DestroyCell。
- **SubsystemGravestoneBlockBehavior.cs (19)**：[189] 墓碑支撑。
- **SubsystemMagnetBlockBehavior.cs (79)**：[167]；`m_magnets` ≤8 个磁石位置（OnBlockAdded/Removed 维护 :57-63）；`FindNearestCompassTarget`（:17-42）指南针目标（无磁石退玩家出生点）；存档 "Magnets" 字符串。
- **SubsystemWhistleBlockBehavior.cs (59)**：[160]；`OnUse`（:16-51）哨声+MakeNoise(30 格)+64 格内 ComponentSummonBehavior 召唤（最近的一批 4 格外设 SummonTarget）。
- **SubsystemSaddleBlockBehavior.cs (42)**：[158]；`OnUse`（:13-36）对活体 raycast → 建对应 `{模板名}_Saddled` 实体换装+移除原实体+消耗鞍。
- **SubsystemBoatBlockBehavior.cs (59)**：[178]；`OnUse`（:19-51）8 格内船 <6（创造豁免）→ 建 "Boat" 实体。
- **SubsystemEggBlockBehavior.cs (54)**：`OnHitAsProjectile`（:19-47）生蛋按蛋型建实体（生成失败给投掷者提示 :36-44）；熟蛋/挑战概率 0.15。
- **SubsystemExperienceBlockBehavior.cs (16)**：`OnPickableGathered`（:5-15）经验球被拾取时 `ComponentLevel.AddExperience`+移除（HandledBlocks=[]，全局 behavior）。
- **SubsystemCollapsingBlockBehavior** 见上。
- **SubsystemWaterPlantBlockBehavior.cs (24)**：水草支撑检测（下需 2/7/72/同种 :5-23）。
- **SubsystemInWaterBlockBehavior.cs (11)**：水生基类；`OnItemHarvested`（:5-11）收获水方块自身→留水+掉水方块物品。
- **SubsystemMatchBlockBehavior.cs (55)**：[108]；`OnUse`（:18-46）先试 `IgniteFuse`（引信）再 `SetCellOnFire`；对准燃烧生物点火（挑战 33% :36-39）；消耗火柴。
- **SubsystemExplosivesBlockBehavior.cs (168)**：引信系统。`IgniteFuse`（:36-47）GunpowderKeg 6-7s/Detonator 0.8-1.2s → `AddExplosive`；`Update`（:49-83）倒计时→`TryExplodeBlock`+引信粒子+引信循环音（音量随最近距离）；`OnNeighborBlockChanged`（:85-89）**自己着火自动点燃**；`OnExplosion`（:111-119）50% 连锁；存档 "Explosives"（:130-148）。
- **SubsystemMagmaBlockBehavior** 见上。
- **SubsystemSignBlockBehavior.cs (587)**：告示牌。`TextData`（:9-31）Point/MovingBlock/Lines[4]/Colors[4]/Url/TextureLocation；`SetSignData/GetSignData`（:90-112）；`OnInteract`（:156-170）冒险模式有 Url 开浏览器/否则 EditSignDialog；`UpdateRenderTarget`（:415-509）**32 张纹理图集 RT**（m_maxTexts=32 :41，按 Display.MaxTextureSize 自适应 :292-295）：视位变化>2 格才重排（:417-434）、≤400 距离平方内按距离排序取前 32、槽位 LRU（ToBeRenderedFrame）;`RenderText`（:315-367）位图字体路径/`RenderTextVector`（:374-413）矢量字体链分流（FontManager.DefaultChain）；`DrawSigns`（:511-586）把 RT 区域 UV 贴到告示面网格（光强 LightIntensityByLightValue :544）；文本随 MovingBlock 搬运（:172-192）。存档 "Texts"（:214-227/263-280）。
- **SubsystemFurnitureBlockBehavior.cs (642)**：家具系统核心。`m_furnitureDesigns[64]`（FurnitureDesign.maxDesign）+`m_furnitureSets`（:23-25）。`ScanDesign`（:111-306）：锤子触发——已作家具克隆 / 或 6 邻域泛洪收集可作方块（`IsValueAllowed`=CanBlockBeBuiltIntoFurniture :588-592、`IsValueDisallowed`=顶层非满流体 :594-603）；尺寸 ≤MaxResolution 检查（:174-179）；chunk 未加载拒绝（:150-155）；`BuildFurnitureDialog` 确认 → `TryAddDesign`（:60-81，满了 `GarbageCollectDesigns` :552-586 三次使用计数 GC+链保留）→ 掉落 227 方块物品（n 个 = clamp(resolution,4,8) :243）；钩子 `OnFurnitureDesigned`（:247-259）。`SwitchToNextState`（:308-350）多态家具交互（LinkedDesign 链+ConnectedMultistate 泛洪 ≤4096）。存档 FurnitureDesigns/FurnitureSets（:471-526）。火把点位粒子（:605-632）。
- **SubsystemTreasureGeneratorBlockBehavior.cs (238)**：[190] 宝箱生成器；`OnNeighborBlockChanged`（:28-91）邻变空/水 → 25% 概率按 61 项静态 TreasureData 权重表（ctor :98-237）随机掉宝+3-6 恶魂之泪(248)；钩子 `OnTreasureGenerate` 可覆盖结果。
- **SubsystemWaterBlockBehavior/SubsystemMagmaBlockBehavior/SubsystemFluidBlockBehavior/SubsystemFireBlockBehavior** 见上。

## 三、横切机制链（详）

### 1. 方块写入链（一切方块交互的总闸）
`SubsystemTerrain.ChangeCell`（:355）→ 钩子 TerrainChangeCell（可全跳）→ 值短路 → 写数组+chunk 状态降级 → m_modifiedCells → ChangeCellToBehavior 分派 behavior 回调（电/流体/火/门/植物…全部从这里出发）。邻居通知延后到 `ProcessModifiedCells`（UpdateOrder.Terrain=100 帧内跑 :66-84）。**注意顺序**：OnBlockAdded/Removed 先于邻居通知（同一帧更晚）——behavior 在自己的 OnBlockAdded 里看邻居时读到的可能是未通知状态。

### 2. 刷怪双链
**持久链**（存档已写死的实体）：SpawnChunks 重放 SpawnsData → SpawnEntity（保留 EntityId）。
**规则链**（动态刷）：SpawningChunk 事件 → CreatureSpawn 队列 → Update 消费 → 限额→位置类型→加权选种→TestSpawnPoint→SpawnCreatures(50 次尝试)→DatabaseManager.CreateEntity。两链都受 CountCreaturesInArea（body 网格+未生成 SpawnsData）约束。生物 Despawn 回写 SpawnsData 的 Data 字段必须经 OnSaveSpawnData/OnReadSpawnData 钩子。

### 3. 电力链
方块变化 → SubsystemElectricBlockBehavior 转发 → m_pointsToUpdate → 下一电路步 UpdateElectricElements 重建元素/线域 → AddElectricElement 建连接 → QueueElectricElementForSimulation 排步 → 每 0.01s Simulate（返回 true 传播邻居）。**节奏与游戏 tick 解耦**（100 步/秒，与 SubsystemUpdate dt 无关——固定仿真频率）。

### 4. 爆炸链
AddExplosion 入队 → Update 同帧模拟（BFS 压力）→ DestroyCell(noDrop) → 掉落转抛射物 → Postprocess：behavior.OnExplosion/点火/全体 body+pickable+projectile 冲量 → 音效/噪声分档。mod 挂点：OnBlockExploded（每被毁格）、CalculateExplosionPower（总压力）。

### 5. 火焰链
SetCellOnFire 放 104 方块（bitmask 面朝可燃物）→ FireBlockBehavior 内存 FireData 计时 → 分帧扫描（50/帧）→ QueueBurnAway/扩散 → 每 5s 落地 ChangeCell。**只有方块是持久的，燃烧计时不是**。

### 6. 移动方块链（活塞/塌方/电梯共用）
AddMovingBlockSet → Update 移动+碰撞（事件）→ Stop → 消费者在 Stopped 事件里 AddTerrainBlock 写回 → ChangeCellToBehavior 走 OnBlockStopMoving（BlockEntity/告示文本/可编辑数据跟随搬迁）。**渲染**：独立 canvasTerrain 生成几何，仅锚点变化才重建。

### 7. 绘制顺序全景（DrawOrders 实测值）
-10000 ModelsRenderer 准备 | -100 Sky 雾参数 | 0 Terrain 不透明+alphaTest | 1 Models 不透明 | 5 Sky 顶 | 10 Projectiles/Pickables | 50 Weather/Signs | 99 Models 水前透明 | 100 Terrain 透明 | 105 Sky 闪电 | 110 Glow | 200 Shadows | 201 Models 水后透明 | 300 Particles。

### 8. 声音链
PlaySound(位置版) → CalculateVolume(距离衰减)+CalculateDelay(声速) → 队列 → Update 到期 → UpdateCongestion 拥塞闸 → AudioManager。环境音（火/水/岩浆/雨）由各 behavior 每帧竞争写入 SubsystemAmbientSounds 的 Volume 字段（清零-最大值模式）。

## 四、ModsManager.HookAction 钩子清单（本域内发现的）

| 钩子名 | 位置 | 作用 |
|---|---|---|
| TerrainChangeCell | SubsystemTerrain.cs:357 | 跳过/改写方块变更 |
| OnTerrainCreated | SubsystemTerrain.cs:513 | 替换 Terrain 对象 |
| OnBlockGeometryGeneratorCreated | SubsystemTerrain.cs:527 | 替换几何生成器 |
| BeforeTerrainSave | SubsystemTerrain.cs:588 | 存盘前 |
| OnTerrainDraw | SubsystemTerrain.cs:484 | 地形绘制 |
| OnProjectileAdded | SubsystemProjectiles.cs:73/297 | 新建/读档抛射物 |
| OnPickableAdded / SavePickable | SubsystemPickables.cs:90/263 | 掉落物 |
| OnSaveSpawnData / OnReadSpawnData | SubsystemSpawn.cs:242/259 | 卸载/重生实体数据 |
| InitializeCreatureTypes | SubsystemCreatureSpawn.cs:1009 | 加刷怪类型 |
| OnBlockExploded | SubsystemExplosions.cs:364/690 | 每被炸毁格 |
| CalculateExplosionPower | SubsystemExplosions.cs:787 | 改爆炸总压力 |
| OnLightningStrike | SubsystemSky.cs:193 | 闪电参数 |
| ChangeSkyColor | SubsystemSky.cs:983 | 天空色 |
| ViewFogColor | SubsystemSky.cs:376 | 全屏雾色 |
| SkyDrawExtra | SubsystemSky.cs:398 | 天空额外绘制 |
| SetRainAndSnowColor | SubsystemWeather.cs:181 | 雨雪颜色 |
| OnMovingBlockSetAdded/Removed/Update | SubsystemMovingBlocks.cs:180/208/308 | 移动方块集 |
| PrepareModels / RenderModels | SubsystemModelsRenderer.cs:97/140 | 模型渲染整段 |
| ModelShaderParameter / SetShaderParameter / OnModelDataDrawing / OnModelRendererDrawExtra | SubsystemModelsRenderer.cs:334/341/350/427 | 着色器与单模型 |
| GetMaxInstancesCount | SubsystemModelsRenderer.cs:221 | 实例上限 |
| OnIDrawableAdded | SubsystemDrawing.cs:115 | 实体绘制组件 |
| OnEntityBehaviorBlockInteracted | SubsystemEntityBlockBehavior.cs:55/68 | 替换方块实体交互 |
| GrowPlant | SubsystemPlantBlockBehavior.cs:87 | 植物生长 |
| OnFurnitureDesigned | SubsystemFurnitureBlockBehavior.cs:247 | 家具设计完成 |
| OnTreasureGenerate | SubsystemTreasureGeneratorBlockBehavior.cs:51 | 宝物生成 |
| BodyCountInRaycast | SubsystemBodies.cs:73 | 身体射线相交 |
| OnIUpdateableAddOrRemove / SubsystemUpdate / ChangeGameTimeDelta 等 | （前页已录） | tick 驱动 |

## 五、坑与对策（本域新发现）

1. **ElectricElement.Simulate 抛异常=全电路炸**：SubsystemElectricity.cs:416-423 catch 后无条件 `throw;`（DEBUG 打印），异常冒泡到 SubsystemUpdate.Update 的静默 catch——当帧所有电路停摆且无日志。对策：自定义 ElectricElement.Simulate 内部 try/catch 全包。
2. **持久电压存档上限 500 条**：SubsystemElectricity.cs:483-485 `if (num > 500) break;`——超出的静默丢弃。大量记忆库/持久电压场景会"读档丢状态"。对策：自查数量，重要状态自己 Save。
3. **新电力方块必须手工补 HandledBlocks**：SubsystemElectricBlockBehavior.cs:8-70 是 63 个硬编码 ID；漏了则 OnBlockAdded 等完全不触发、电路不建元素。
4. **刷怪限额是 static**：SubsystemCreatureSpawn.cs:54-61 `m_totalLimit` 等静态——一个 mod 改了全局生效且退出世界不清。
5. **寻路请求满了直接"假装完成"**：SubsystemPathfinding.cs:198-222 队列>10 时 result.IsCompleted=true+空路径——生物"原地不动"先查这里；且后台每单 Task.Delay(250) 吞吐有限。
6. **火不存燃烧进度**：FireData 纯内存（SubsystemFireBlockBehavior 无 Save 重写）——读档后所有火重计时；想持久化要 mod 自己记。
7. **告示牌文字 RT 只有 32 槽**：SubsystemSignBlockBehavior.cs:41 m_maxTexts=32（低配自适应更小）；33 块牌子同屏必有几张文字消失（距离排序淘汰 :453-456）。
8. **家具设计上限 64 且 GC 激进**：m_furnitureDesigns[64]；GarbageCollectDesigns 按使用计数清（保留 LinkedDesign 链与 FurnitureSet 成员）——批量生成家具留一份在物品栏防 GC。
9. **活塞 UpdateOrder 依赖 MovingBlocks**：`m_subsystemMovingBlocks.UpdateOrder + 1`（SubsystemPistonBlockBehavior.cs:40）——FloatUpdateOrder 微调移动方块时活塞会跟着漂。
10. **水扩散放大邻居通知**：SpreadFluid 每轮结尾手动 `ProcessModifiedCells()`（SubsystemFluidBlockBehavior.cs:263），大面积水体每 0.25s 额外两轮全量邻居回调——大坝工程掉帧主因之一。
11. **DespawnRadius>SpawnRadius 的迟滞**：实体 48 格内生成、60 格外卸载（SubsystemSpawn.cs:42-44）——别在 48-60 环带做"必在实体"逻辑。
12. **Projectile/Pickable 账本要求对称**：Add/Load 都要 Book(+1)、Remove Book(-1)（SubsystemProjectiles.cs:304-305 注释）——mod 直接改 m_projectiles 会破坏预扩容账本。
13. **音频在游戏加速时全静音**：SubsystemAudio.cs:156-158 `GameTimeFactor==1 && !FixedTimeStep` 才播——睡觉加速/慢动作没声音是设计。
14. **旋转楼梯组合表是硬编码 32 分支**：SubsystemStairsBlockBehavior.cs:47-188——mod 自定义楼梯想进组合必须复用 StairsBlock 的 rotation/data 布局。
15. **爆炸掉落转抛射物限流**：m_projectilesCount≥40 后掉落概率骤降（SubsystemExplosions.cs:707-710）——大爆炸"东西消失"是限流非 bug；`ExplosionKeepsPickables=true` 的方块豁免。
