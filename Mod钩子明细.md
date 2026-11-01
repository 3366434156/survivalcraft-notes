# Mod钩子明细（全量 236）

> 域: Mod开发参考 · 更新: 2026-11-01 · 状态: 全读(ModLoader.cs 2338 行，236 个 public virtual 成员全部编目；233 处派发点全 grep 实读)

机制与用法见 [Mod钩子总表.md](Mod钩子总表.md)。本页一行一钩子。

**列说明**：`ML:行`=成员在 ModLoader.cs 的行号；派发点为相对 `E:\SurvivalcraftAPIProject\Survivalcraft\` 的文件:行（今日实读）；【死】=无任何派发点，重写无效；【过时】=标 Obsolete 但仍派发；注册名默认=成员名，不一致在备注标出。

## 派发点文件路径对照

| 目录 | 文件 |
|---|---|
| ModsManager\ | ModLoader.cs · ModsManager.cs · ModEntity.cs · ModSettingsManager.cs · SurvivalCraftModLoader.cs |
| Managers\ | GameManager.cs · BlocksManager.cs · CraftingRecipesManager.cs · LightingManager.cs · MusicManager.cs · ScreenCaptureManager.cs · SettingsManager.cs · KeyCompatibleGroupsManager.cs · DialogsManager.cs · Fonts\FontManager.cs |
| Component\ | ComponentBody.cs · ComponentClothing.cs · ComponentDispenser.cs · ComponentGui.cs · ComponentHealth.cs · ComponentInput.cs · ComponentLevel.cs · ComponentFactors.cs · ComponentLocomotion.cs · ComponentMiner.cs · ComponentModel.cs · ComponentCreatureModel.cs · ComponentHumanModel.cs · ComponentFishModel.cs · ComponentFirstPersonModel.cs · ComponentAimingSights.cs · ComponentLoot.cs · ComponentPilot.cs · ComponentPlayer.cs · ComponentRider.cs · ComponentVitalStats.cs · ComponentShapeshifter.cs |
| Component\Behavior\ | ComponentChaseBehavior.cs · ComponentEatPickableBehavior.cs · ComponentFlyAwayBehavior.cs · ComponentHerdBehavior.cs |
| Subsystem\ | SubsystemTerrain.cs · SubsystemExplosions.cs · SubsystemSky.cs · SubsystemWeather.cs · SubsystemCreatureSpawn.cs · SubsystemSpawn.cs · SubsystemProjectiles.cs · SubsystemPickables.cs · SubsystemMovingBlocks.cs · SubsystemUpdate.cs · SubsystemDrawing.cs · SubsystemTime.cs · SubsystemModelsRenderer.cs · SubsystemBodies.cs · BlockBehavior\Subsystem{Plant,TreasureGenerator,FurnitureBlock,EntityBlock}Behavior.cs |
| Game\ | Attackment.cs · Injury.cs · TerrainUpdater.cs · Terrain.cs · TerrainContentsGenerator23.cs · TerrainContentsGenerator24.cs · TerrainRenderer.cs · SkyPrimitiveRender.cs · BlockMesh.cs · Projectile.cs · Pickable.cs · FurnitureDesign.cs · PlayerData.cs · WorldSettings.cs · BasePerspectiveCamera.cs · ClothingSlot.cs |
| 其他 | Widget\{Widget,ViewWidget,InventorySlotWidget,GameWidget,PlayerModelWidget}.cs · Screen\{PlayScreen,LoadingScreen,MainMenuScreen,SettingsScreen,BestiaryScreen,BestiaryDescriptionScreen,RecipaediaDescriptionScreen,RecipaediaRecipesScreen}.cs · Block\ClothingBlock.cs · Dialog\ViewGameLogDialog.cs |

## 一、生命周期与加载（20）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `__ModInitialize` ML:21 | ModLoader 被实例化后立即 | ModEntity.cs:418 直调 | 无 | 全 Loader；**唯一可靠 RegisterHook 时机** |
| `Priority` ML:16 | HandleAssembly 排序时读取 | ModEntity.cs:440 直调 | int 属性 | 越小越先；最小者=主 Loader（Loader 属性） |
| `GetModFiles` ML:31 | 引擎按扩展名取本模组文件 | ModEntity.cs:101 直调 | (ext, action(名,流), out skip) | **仅主 Loader**；skip=true 接管文件提供 |
| `GetModFile` ML:43 | 引擎按文件名取单文件 | ModEntity.cs:143 直调 | (名, action(流), out skip, out fileFound) | **仅主 Loader**；modinfo/icon 固定走原版逻辑 |
| `ModDispose` ML:61 | 模组被卸载（重启/Reboot） | ModEntity.cs:540 直调 | 无 | 全 Loader；异常被吞 |
| `BeforeGameLoading` ML:768 | 玩家点进存档前 | PlayScreen.cs:278 | (PlayScreen, item=WorldInfo)→object | 返回 null 阻止进入存档 |
| `OnLoadingStart` ML:774 | 加载任务表建立（BlocksManager 初始化前） | LoadingScreen.cs:485 | (List\<Action\>) | 可插入自定义加载任务 |
| `OnLoadingFinished` ML:781 | 全部加载任务完成（BlocksManager 初始化后） | LoadingScreen.cs:580 直调 | (List\<Action\>) | 全 Loader **无需注册**；社区管线此后运转 |
| `OnXdbLoad` ML:801 | 本模组 .xdb 合并进 Database 后 | ModEntity.cs:335 直调 | (XElement 全库节点) | 全 Loader（注意：非仅主 Loader） |
| `BlocksInitalized` ML:760 | BlocksManager 初始化完成 | BlocksManager.cs:424 | 无 | 在 .csv 方块数据加载后（BlocksManager.cs:410） |
| `OnProjectLoaded` ML:750 | Project 加载完成 | GameManager.cs:58 | (Project) | 进世界后 |
| `OnProjectDisposed` ML:755 | Project 释放 | GameManager.cs:203 | 无 | 退世界 |
| `ProjectBeforeSubsystemsAndEntitiesLoad` ML:1788 | Project 创建、Subsystem/Entity 载入前 | GameManager.cs:94 | (Project) | 可移除 Subsystem/Entity/Component |
| `EntityComponentsInitialized` ML:1782 | 实体组件表初始化 | GameManager.cs:85 | (Entity, List\<KVP\<int,Component\>\>) | 可移除特定组件 |
| `OnMainMenuScreenCreated` ML:1846 | 主界面初始化后 | MainMenuScreen.cs:46 | (MainMenuScreen, 左下bar, 右下bar) | 主界面加按钮首选（右下 bar） |
| `OnMainMenuScreenUpdate` ML:1857 【死·过时】 | — | 无派发 | — | 官方注释：用 OnMainMenuScreenCreated |
| `WindowModeChanged` ML:1063 | 窗口模式切换 | SettingsManager.cs:217,413 | (WindowMode) | |
| `GetKeyboardMappings` ML:1931 | 模组键位初始化/重置默认值 | ModSettingsManager.cs:119,418 直调 | yield KVP\<映射名, Key\|MouseButton\> | 全 Loader 无需注册 |
| `GetGamepadMappings` ML:1938 | 手柄键位初始化/重置 | ModSettingsManager.cs:120,432 直调 | yield KVP；组合键写法见 ML:1939 注释 | 同上 |
| `GetCameraList` ML:1953 | 相机列表初始化/重置 | ModSettingsManager.cs:121,446 直调 | yield KVP\<相机类名, 序号\> | 全 Loader；配合 ManageCameras |

## 二、存档与设置（8）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `CompareModVersion` ML:56 | 进存档校验模组版本 | PlayScreen.cs:212 直调 | (当前版, 存档上次的版)→bool | **仅主 Loader**；false=拒绝加载该存档 |
| `ProjectXmlLoad` ML:808/809 | Project.xml 读取时 | GameManager.cs:46 | (XElement) / (XElement, WorldInfo, gameWidget) | 两重载都调；用新重载 |
| `ProjectXmlSave` ML:815 | Project.xml 保存时 | GameManager.cs:138 | (XElement) | |
| `OnProjectXmlSaved` ML:821 | 所有 Entity/Subsystem 保存完后 | GameManager.cs:150 | (XElement) | 写自定义全局数据 |
| `SaveSettings` ML:787 | 模组设置写盘 | ModEntity.cs:518←ModsManager.cs:384 直调 | (XElement 空容器) | 全 Loader；把自己的设置存入 |
| `LoadSettings` ML:795 | 模组设置读盘（加载流程尾段） | ModEntity.cs:526←ModsManager.cs:434 直调 | (XElement) | 全 Loader；API 不常驻保存设置，读完入自己的类 |
| `OnModSettingChanged` ML:1976 | 数据驱动设置项值变更 | ModSettingsManager.cs:317 直调 | (idPath[去包名], value) | 按 PackageName 精准分发；需立即生效的逻辑写这里 |
| `InitKeyCompatibleGroups` ML:1960 | 按键兼容组初始化 | KeyCompatibleGroupsManager.cs:24 | 无 | 原版示例 SurvivalCraftModLoader.cs:24 |

## 三、世界与地形（19）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `OnTerrainCreated` ML:676 | SubsystemTerrain.Load 建 Terrain 时（一次） | SubsystemTerrain.cs:513 | (st, ref Terrain) | 可换 Terrain 子类：自定义存取/扩世界高度 |
| `OnTerrainChunkCreated` ML:686 | Terrain.AllocateChunk 时 | Terrain.cs:181 | (terrain, cx, cz, ref TerrainChunk) | 可换区块子类；**可能在地形更新线程** |
| `OnTerrainContentsGenerated` ML:654 | 区块地形内容生成完成 | TerrainUpdater.cs:702 | (TerrainChunk) | **子线程执行** |
| `ToAllocateChunks` ML:668 | TerrainUpdater 分配区块 | TerrainUpdater.cs:506 | (updater, locations)→bool | true=区块数有变动 |
| `ToFreeChunks` ML:660 | 区块即将释放 | TerrainUpdater.cs:465 | (updater, chunk, out keepWorking) | keepWorking=true 保活不释放 |
| `TerrainChangeCell` ML:525 | 任意改方块（SetCell/ChangeCell） | SubsystemTerrain.cs:357 | (st, x,y,z, value, out skip) | skip=true 跳过原 ChangeCell；广播 |
| `BeforeTerrainSave` ML:693 | 保存地形数据之前 | SubsystemTerrain.cs:588 | (st) | 把自定义地形数据排入保存队列 |
| `OnTerrainDraw` ML:702 | 地形绘制完成 | SubsystemTerrain.cs:484 | (st, camera, drawOrder) | drawOrder 0 与 100 各一次 |
| `OnBlockGeometryGeneratorCreated` ML:716 | 创建方块几何生成器 | SubsystemTerrain.cs:527 + SubsystemMovingBlocks.cs:581 | (7 原版参数…, ref generator) | 可换生成器子类；主世界与移动方块画布各触发一次 |
| `OnTerrainBrushesCreated` ML:1542 | 原版地形刷（矿/水/植物）建好后 | TerrainContentsGenerator23.cs:2461 + 24:2414 | 无 | 调原版刷子改矿物生成量 |
| `FindCoarseSpawnPosition` ML:1549 | 建世界找玩家初步落点 | TerrainContentsGenerator23.cs:394 + 24:390 | (tcg, ref spawnPosition) | |
| `TerrainContentsGenerator23Initialize` ML:1713 【过时】 | 地形生成器初始化 | TerrainContentsGenerator23.cs:353 | (tcg, st) | 用 24 版 |
| `TerrainContentsGenerator24Initialize` ML:1716 | 地形生成器初始化 | TerrainContentsGenerator24.cs:352 | (tcg, st) | |
| `GenerateChunkVertices` ML:1043 | 区块顶点生成 | TerrainUpdater.cs:773【单播】+ 792 | (chunk, even) | 773 处恒 return true：只有第一个注册者收到 |
| `GenerateChunkLightSources` ML:1050 | 收集区块光源 | TerrainUpdater.cs:881 | (lightSources, chunk) | 加自定义光源 |
| `FindTerrainCollisionBoxes` ML:732 | 物理体收集地形碰撞箱 | ComponentBody.cs:1003 | (body, box, result, out skip) | 改扫描范围/负坐标支持 |
| `OnLightningStrike` ML:1533 | 闪电劈下 | SubsystemSky.cs:193 | (sky, ref 位置, ref strike, ref 爆炸威力, ref 点燃) | |
| `OnTreasureGenerate` ML:982 | 挖掘触发宝物生成 | SubsystemTreasureGeneratorBlockBehavior.cs:51【截断】 | (st, xyz, 邻块xyz, ref 方块值, ref 数量, out isGenerate) | isGenerate=true 截断后续 mod（能看到上个 mod 的产物） |
| `GrowPlant` ML:1761 | 植物生长判定 | SubsystemPlantBlockBehavior.cs:87 | (spbb, x,y,z, pollPass, out skipVanilla) | 只对自己模组方块接管 |

## 四、方块与物品（6）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `DamageItem` ML:1074 | DamageItem 算出新方块值时 | BlocksManager.cs:1016 | (block, old, damageCount, owner, out skipVanilla)→int 新值 | 工具耐久结算改写 |
| `OnBlockExploded` ML:464 | 方块被炸掉 | SubsystemExplosions.cs:364,690 | (st, x,y,z, value) | 两处派发 |
| `OnBlockDug` ML:1260 | 方块被挖掘完毕 | ComponentMiner.cs:286 | (miner, digValue, cellValue, ref 耐久损耗, ref mute, ref 统计增量) | |
| `OnFurnitureDesigned` ML:1312 | 家具创建时 | SubsystemFurnitureBlockBehavior.cs:247 | (design, 由现有家具创建, ref 掉落数, ref 拆原型, ref 锤耐久) | 禁家具复制改 designedFromExistingFurniture 分支 |
| `SetFurnitureDesignColor` ML:218 | 设置家具颜色 | FurnitureDesign.cs:729 | (design, block, value, ref 贴图槽, ref color) | |
| `OnEntityBehaviorBlockInteracted` ML:2086 | 玩家开始交互带 SubsystemEntityBlockBehavior 的方块 | SubsystemEntityBlockBehavior.cs:55,68 | (raycast, isInitialNull, ref blockEntity) | 可给野生箱子补建实体；官方提示易冲突 |

## 五、挖掘·放置·攻击（15）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `OnMinerDig` ML:138 | 人物挖掘中 | ComponentMiner.cs:234 | (miner, raycast, ref digProgress, out digged) | digged=true 视为已挖掉 |
| `BeforeMinerPlace` ML:152 | 放置前（OnMinerPlace 之前） | ComponentMiner.cs:358 | (miner, raycast, x,y,z, placementData, out notAllowed) | true=禁止放置 |
| `OnMinerPlace` ML:174 【过时】 | 人物放置时 | ComponentMiner.cs:379 | (…, value, out placed) | placed=true 不执行原放置 |
| `OnMinerPlace` ML:196 | 人物放置时 | ComponentMiner.cs:397 | (…, value, placementData, out placed) | 新重载；**两个重载都会被调**，只重写新的 |
| `OnMinerHit` ML:86 | 攻击命中 | ComponentMiner.cs:651 | (miner, body, 命中点/向, ref 攻击力, ref 玩家/生物命中率, out hitted) | |
| `OnMinerHit2` ML:123 | 攻击命中（含耐久与攻击对象） | ComponentMiner.cs:680 | (miner, body, 命中点/向, ref 耐久损耗, ref Attackment) | |
| `SetHitInterval` ML:100 | 设置伤害间隔 | ComponentMiner.cs:590 | (miner, ref hitInterval) | |
| `IsLevelSufficientForTool` ML:110 | 判定能否挖掘/使用/伤害/瞄准 | ComponentMiner.cs:1297 | (miner, toolValue, ref canUse, out skip) | 自定义物品使用条件 |
| `ProcessAttackment` ML:313 | 攻击结算 | Attackment.cs:217 | (Attackment) | 改击退/击晕的现行接口 |
| `AttackPowerParameter` ML:231 【过时】 | 攻击结算 | Attackment.cs:237 | (target, attacker, …, ref impulse, ref stun, ref recalc) | 用 ProcessAttackment |
| `AttackBody` ML:302 【死·过时error】 | — | 无派发 | — | 已弃用 |
| `SetHitValueParticleSystem` ML:635 | 伤害数字粒子参数 | ComponentMiner.cs:697,1142 + Attackment.cs:127 | (粒子, Attackment|null=null=未命中) | 三处派发 |
| `CalculateExplosionPower` ML:501 | 计算爆炸威力 | SubsystemExplosions.cs:787 | (subsys, ref power) | |
| `OnComponentBodyExplodedStart` ML:1747 | 爆炸开始、算动物摇晃时 | ComponentBody.cs:311 | (body, 爆心, 威力, ref shakeStrength) | 只接管自己模组生物 |
| `OnComponentBodyExploded` ML:511 | 实体遭爆炸 | ComponentBody.cs:330 | (body, ref Injury, ref impulse, ref setOnFire, ref fluctuation) | |

## 六、生命·受伤·死亡（9）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `CalculateCreatureInjuryAmount` ML:545 | 计算生物受伤量 | Injury.cs:51 | (Injury) | 直接改 Injury 上的伤害数据 |
| `OnCreatureDying` ML:554 | 受伤且生命<0 时（死前） | ComponentHealth.cs:163 | (health, injury) | 回调后 Health>0 则取消死亡（不死图腾） |
| `OnCreatureDied` ML:563 | 生物死亡 | ComponentHealth.cs:183 | (health, injury, ref 经验球数, ref calculateInKill) | |
| `DeadBeforeDrops` ML:520 | 死亡前瞬间 | ComponentHealth.cs:411 | (health, ref 死亡粒子, ref dropAllItems) | |
| `CalculateFallDamage` ML:1577 | 计算坠落伤害 | ComponentHealth.cs:305 | (health, ref damage) | |
| `ChangeVisualEffectOnInjury` ML:574 | 每帧调受伤视觉效果 | ComponentHealth.cs:372 | (health, lastHealth, ref 红屏, ref 痛叫, ref 血条闪烁, ref 模型变红) | |
| `OnCreatureSpiked` ML:581 | 生物被尖刺扎 | ComponentHealth.cs:42 | (health, spikeBehavior, cellFace, velocity, ref Injury) | |
| `OnCreatureInjure` ML:533 【死·过时error】 | — | 无派发 | — | 用下面三个代替 |
| `DecideLoot` ML:1837 | 计算生物战利品 | ComponentLoot.cs:64 | (loot, List\<BlockDropValue\>) | 增删而非清空，保兼容 |

## 七、生命状态 VitalStats（6）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `OnVitalStatsEat` ML:2138 | 人物尝试进食 | ComponentVitalStats.cs:111 | (vitalStats, ref value, ref skipVanilla, out eatSuccess) | skipVanilla=true 时自行改 Food/饱食 |
| `OnVitalStatsUpdateFood` ML:2162 | UpdateFood 前 | ComponentVitalStats.cs:253 | (vitalStats, ref food, ref dt, ref skipVanilla) | 未 skip 时引擎把 food 写回组件 |
| `OnVitalStatsUpdateStamina` ML:2183 | UpdateStamina 前 | ComponentVitalStats.cs:330 | (vitalStats, ref stamina, ref dt, ref skipVanilla) | 同上 |
| `OnVitalStatsUpdateSleep` ML:2204 | UpdateSleep 前 | ComponentVitalStats.cs:426 | (vitalStats, ref sleep, ref dt, ref skipVanilla) | 同上 |
| `OnVitalStatsUpdateTemperature` ML:2225 | UpdateTemperature 前 | ComponentVitalStats.cs:506 | (vitalStats, ref temperature, ref dt, ref skipVanilla) | 同上 |
| `OnVitalStatsUpdateWetness` ML:2246 | UpdateWetness 前 | ComponentVitalStats.cs:631 | (vitalStats, ref wetness, ref dt, ref skipVanilla) | 同上 |

## 八、玩家与输入（16）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `OnPlayerSpawned` ML:282 | 人物出生 | PlayerData.cs:657 | (spawnMode, player, position)→bool | |
| `OnPlayerDead` ML:289 | 人物死亡（重进死档也触发） | PlayerData.cs:294 | (PlayerData) | 区分刚死/读档见 ML:286 注释 |
| `PlayerDataFirstUpdate` ML:1989 | PlayerData 首次更新 | PlayerData.cs:153 | (PlayerData) | |
| `UpdateDeathCameraWidget` ML:1737 | 死亡界面更新 | PlayerData.cs:312 | (playerData, ref 禁原版点击复活, ref respawn) | |
| `OnPlayerControlSteed` ML:1411 | 骑动物时每帧 | ComponentPlayer.cs:182 | (player, skippedByOtherMods, out skipVanilla) | |
| `OnPlayerControlBoat` ML:1421 | 乘船时每帧 | ComponentPlayer.cs:227 | 同上 | |
| `OnPlayerControlOtherMount` ML:1431 | 乘船/动物以外的坐骑每帧 | ComponentPlayer.cs:245 | 同上 | 模组坐骑控制 |
| `OnPlayerControlWalk` ML:1441 | 无坐骑无船时每帧（行走） | ComponentPlayer.cs:257 | 同上 | |
| `OnPlayerInputInteract` ML:1454 | 玩家输入交互 | ComponentPlayer.cs:307 | (player, ref operated, ref 间隔, ref 使用/交互/放置优先级) | 优先级≤0 禁对应操作 |
| `UpdatePlayerInputAim` ML:1470 | 玩家瞄准时 | ComponentPlayer.cs:340,394 | (player, aiming, ref operated, ref 间隔, skipped, out skipVanilla) | |
| `OnPlayerInputHit` ML:1488 | 玩家“攻击”动作 | ComponentPlayer.cs:415 | (player, ref operated, ref 间隔, ref 近战距离, skipped, out skipVanilla) | 近战距离≤0=不近战 |
| `UpdatePlayerInputDig` ML:1506 | 玩家“挖掘”动作 | ComponentPlayer.cs:452,478 | (player, digging, ref operated, ref 间隔, skipped, out skipVanilla) | 间隔调小=极速挖掘 |
| `OnPlayerInputDrop` ML:1521 | 玩家丢弃手中物品 | ComponentPlayer.cs:490 | (player, skipped, out skipVanilla) | **注册名是 "UpdatePlayerInputDrop"**（≠成员名） |
| `UpdateInput` ML:447 | 更新输入时 | ComponentInput.cs:234 | (ComponentInput, WidgetInput) | |
| `IsCrosshairVisible` ML:1925 | 十字准星可见性 | ComponentAimingSights.cs:68 | (sights, ref isVisible) | 关 PC 强制准星 |
| `InitKeyCompatibleGroups` ML:1960 | 按键兼容组初始化 | KeyCompatibleGroupsManager.cs:24 | 无 | 见二组表 |

## 九、骑乘与载具（4）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `ScoreMount` ML:965 | 评估可骑乘目标 | ComponentRider.cs:195 | (rider, mount, out float? score) | null=不处理；正=允许，负=禁止 |
| `OnStartMounting` ML:2306 | 开始骑乘 | ComponentRider.cs:66 | (rider, mount, ref skipVanilla) | |
| `OnStartDismounting` ML:2314 | 结束骑乘 | ComponentRider.cs:94 | (rider, mount 可为 null, ref skipVanilla) | |
| `IsTerrainSafeToGo` ML:902 | 飞行器判地形是否安全 | ComponentPilot.cs:252 | (pilot, position, direction, out safe, out skipVanilla) | |

## 十、实体与 AI（31）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `OnEntityAdd` ML:469 | 实体被添加 | GameManager.cs:67 | (Entity) | |
| `OnEntityRemove` ML:474 | 实体被移除 | GameManager.cs:76 | (Entity) | |
| `OnSetModel` ML:318 | 模型对象设模型 | ComponentModel.cs:362 | (model, Model, out isSet) | isSet=true 跳过原设值 |
| `UpdateComponentBody` ML:1165 | 动物 Update（物理体） | ComponentBody.cs:419 | (body, dt, skipped, out skipVanilla) | 只对自己模组动物接管 |
| `BodyCountInRaycast` ML:1175 | 动物在 Raycast 下的表现 | SubsystemBodies.cs:73 | (body, ray, out skip)→float? | null=不计入；数值=命中距离 |
| `InitializeCreatureTypes` ML:481 | 自然生成生物列表初始化 | SubsystemCreatureSpawn.cs:1009 | (spawn, List\<CreatureType\>) | 加自然生成生物 |
| `SpawnEntity` ML:490 【死】 | — | 无派发 | — | 生物生成走 Database 模板 |
| `OnDespawned` ML:499 | 生物消失 | ComponentShapeshifter.cs:111 | (entity, spawn) | **目前仅变身时派发**，普通消失不触发 |
| `OnSaveSpawnData` ML:642 | 储存生物数据 | SubsystemSpawn.cs:242 | (spawn, SpawnEntityData) | |
| `OnReadSpawnData` ML:647 | 读取生物数据 | SubsystemSpawn.cs:259 | (entity, SpawnEntityData) | |
| `GetMaxInstancesCount` ML:616 | 设生物最大组件数 | SubsystemModelsRenderer.cs:221 | →int | 多 mod 取最大；默认 7 |
| `OnLocomotionStopped` ML:1584 | 动物晕眩/死亡时移动 | ComponentLocomotion.cs:288【反向】 | (locomotion, ref fallsOnDeathOrStun) | **唯一 HookActionReverse**：反注册序派发 |
| `OnComponentLocomotionLoaded` ML:1594 | ComponentLocomotion 加载 | ComponentLocomotion.cs:347 | (locomotion, ref 走/飞/泳速度乘数, ref 禁创飞) | |
| `OnChaseBehaviorStartChasing` ML:1816 | 开始追击 | ComponentChaseBehavior.cs:126 | (chaseBehavior) | |
| `OnChaseBehaviorStopChasing` ML:1817 | 停止追击 | ComponentChaseBehavior.cs:144 | (chaseBehavior) | |
| `OnChaseBehaviorAttacked` ML:1559 | 近战命中目标 | ComponentChaseBehavior.cs:172 | (chase, 追逐时间前, ref 后, ref hitBody, ref 音效) | |
| `OnChaseBehaviorAttackFailed` ML:1570 | 近战未命中 | ComponentChaseBehavior.cs:187 | (chase, ref chaseTime) | |
| `ChaseBehaviorScoreTarget` ML:1826 | 选追击对象评分 | ComponentChaseBehavior.cs:469 | (chase, 目标, ref score) | 分高者被选 |
| `UpdateChaseBehaviorLookingForTarget` ML:1828 | 寻找目标阶段 | ComponentChaseBehavior.cs:299 | (chase) | |
| `UpdateChaseBehaviorChasing` ML:1829 | 追击中每帧 | ComponentChaseBehavior.cs:411 | (chase) | |
| `IsPredator` ML:919 | 判目标是否捕食者（飞走） | ComponentFlyAwayBehavior.cs:228 | (behavior, target, out isPredator, out skipVanilla) | |
| `CallNearbyCreaturesHelp` ML:934 | 摇人行为 | ComponentHerdBehavior.cs:37 | (herd, target, maxRange, maxChaseTime, isPersistent, out skipVanilla) | 只对自己模组生物 |
| `FindHerdCenter` ML:951 | 找大部队中心点 | ComponentHerdBehavior.cs:68 | (creature, out Vector3? center, out skipVanilla) | null=不受群体约束 |
| `OnEatPickable` ML:275 | 动物吃掉落物 | ComponentEatPickableBehavior.cs:203【截断】 | (behavior, pickable, out dealed) | dealed=true 截断后续 mod |
| `OnCreatureFootstep` ML:2277 | 生物脚步声动画事件 | ComponentCreatureModel.cs:231 | (creature, parameter) | 模型动画事件 |
| `OnCreatureAttackHit` ML:2284 | 生物攻击命中事件 | ComponentCreatureModel.cs:251 | (creature, parameter) | 模型动画事件 |
| `OnCreatureAttackStart` ML:2291 | 生物攻击开始事件 | ComponentCreatureModel.cs:264 | (creature, parameter) | 模型动画事件 |
| `OnCreatureAttackEnd` ML:2298 | 生物攻击结束事件 | ComponentCreatureModel.cs:279 | (creature, parameter) | 模型动画事件 |
| `OnLevelUpdate` ML:399 【过时·活】 | 等级组件更新（仅玩家） | ComponentLevel.cs:335 | (ComponentLevel) | 官方建议改用模组组件 |
| `OnFactorsUpdate` ML:407 【过时·活】 | 力量/抗性/速度/饥饿因素更新 | ComponentFactors.cs:213 | (factors, dt) | 同上 |
| `OnFactorsGenerate` ML:1872 【死·过时】 | — | 无派发 | — | 因子列表可直接在模组组件改 |

## 十一、射弹·掉落物·移动方块·发射器（17）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `OnProjectileAdded` ML:1221 | 添加射弹 | SubsystemProjectiles.cs:73,297 | (subsys, ref Projectile, ValuesDictionary 可 null) | 读档首加=有 VD，游玩中=null |
| `OnProjectileRaycastBody` ML:2006 | 射弹找下一个命中 Body | Projectile.cs:223 | (body, projectile, distance, out ignore) | ignore=true 无视该 Body |
| `OnProjectileHitTerrain` ML:1090 | 射弹击中方块 | Projectile.cs:374 | (p, raycast, ref 触发方块行为/破坏/音量/卡住/速度/角速度) | |
| `OnProjectileHitBody` ML:1108 | 射弹击中实体 | Projectile.cs:313 | (p, raycast, ref Attackment, ref 速度/角速度, ref ignoreBody) | ignoreBody=true 穿过 |
| `OnProjectileDraw` ML:1125 | 绘制射弹 | Projectile.cs:681 | (p, subsys, camera, drawOrder, ref shouldDrawBlock/大小/颜色) | |
| `OnProjectileFlyOutOfLoadedChunks` ML:1137 | 射弹飞出加载区块 | Projectile.cs:278 | (p) | |
| `OnProjectileTurnIntoPickable` ML:1775 | 射弹转化为掉落物 | Projectile.cs:463 | (p, ref pickable) | |
| `SaveProjectile` ML:1239 | 保存世界存射弹 | Projectile.cs:148 | (subsys, p, ref ValuesDictionary) | |
| `OnPickableAdded` ML:1231 | 添加掉落物 | SubsystemPickables.cs:90,233 | (subsys, ref Pickable, ValuesDictionary 可 null) | |
| `OnPickableDraw` ML:1149 | 绘制掉落物 | Pickable.cs:526 | (pickable, subsys, camera, drawOrder, ref 3 项) | |
| `SavePickable` ML:1249 | 保存世界存掉落物 | SubsystemPickables.cs:263 | (subsys, pickable, ref VD) | |
| `OnMovingBlockSetAdded` ML:1187 | 添加移动方块 | SubsystemMovingBlocks.cs:180 | (ref movingBlockSet, subsys, ref testCollision, out doNotAdd) | |
| `OnMovingBlockSetRemoved` ML:1199 | 移除移动方块 | SubsystemMovingBlocks.cs:208 | (set, subsys) | |
| `OnMovingBlockSetUpdate` ML:1208 | 移动方块更新 | SubsystemMovingBlocks.cs:308 | (set, subsys, skipped, out skipVanilla) | |
| `OnDispenserDispensePickable` ML:1606 | 发射器投掷物品 | ComponentDispenser.cs:77 | (dispenser, ref pickable, ref removeSlotCount) | |
| `OnDispenserShoot` ML:1615 | 发射器弹射物品 | ComponentDispenser.cs:104 | (dispenser, ref projectile, ref canDispensePickable, ref removeSlotCount) | |
| `DispenserChooseItemToDispense` ML:1627 | 发射器选消耗物品 | ComponentDispenser.cs:37【截断】 | (dispenser, ref slot, ref value, out chosen) | chosen=true 截断后续 mod |

## 十二、渲染·相机·天空（26）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `ViewFogColor` ML:69 | 视图雾颜色 | SubsystemSky.cs:376 | (水深, 岩浆深, ref Color) | |
| `CalculateLighting` ML:76 | 方块亮度（黑暗区亮度） | LightingManager.cs:93 | (ref brightness) | |
| `CalculateSmoothLight` ML:1058 | 动物模型平滑光照 | LightingManager.cs:78 | (st, 位置, ref 强度) | |
| `ChangeSkyColor` ML:590 | 天空颜色 | SubsystemSky.cs:983 | (oldColor, direction, timeOfDay, temperature)→Color | |
| `SetRainAndSnowColor` ML:213 | 雨/雪颜色 | SubsystemWeather.cs:181 | (ref rainColor, ref snowColor)→bool | 有修改才返回 true |
| `SkyDrawExtra` ML:610 | 天空额外绘制 | SubsystemSky.cs:398 | (sky, camera) | 星球/日月在 SkyPrimitiveRender |
| `SetShaderParameter` ML:597 | 设地形/天空着色器参数 | TerrainRenderer.cs:143,194,231 + SkyPrimitiveRender.cs:66,79 + SubsystemModelsRenderer.cs:341【全部单播】 | (shader, camera) | 恒 return true：**只有第一个注册者生效** |
| `ModelShaderParameter` ML:602 | 模型着色器参数 | SubsystemModelsRenderer.cs:334【单播】 | (shader, camera, modelsData, alphaThreshold?) | 同上 |
| `PrepareModels` ML:1719 | 模型渲染准备 | SubsystemModelsRenderer.cs:97 | (renderer, camera, skipped, out skip) | |
| `RenderModels` ML:1723 | 模型渲染 | SubsystemModelsRenderer.cs:140 | (renderer, camera, drawOrder, skipped, out skip) | |
| `OnModelDataDrawing` ML:2054 | 单个模型数据被渲染 | SubsystemModelsRenderer.cs:350 | (modelData, modelShader, camera, renderer, out skip) | |
| `OnModelRendererDrawExtra` ML:625 | 绘制额外模型（头顶名牌） | SubsystemModelsRenderer.cs:427 | (renderer, modelData, camera, alphaThreshold?) | 原版名牌实现在 SurvivalCraftModLoader |
| `OnAnimateModel` ML:331 | 模型动画 | ComponentModel.cs:187 | (model, out skip) | |
| `OnModelDrawExtra` ML:342 | 模型额外绘制（手持物） | ComponentModel.cs:324 | (model, camera, out skip) | |
| `OnModelCalculateBones` ML:352 | 计算骨骼绝对变换 | ComponentModel.cs:133 | (model, camera, out skip) | |
| `OnModelCalculateIsVisible` ML:362 | 计算模型可见性 | ComponentModel.cs:155 | (model, camera, out skip) | |
| `RecalculateModelEyePosition` ML:371 | 模型眼睛位置 | ComponentCreatureModel.cs:414 + ComponentFishModel.cs:190 + ComponentHumanModel.cs:623 | (model, ref eyePosition) | 三处派发 |
| `RecalculateModelEyeRotation` ML:378 | 模型眼睛旋转 | ComponentCreatureModel.cs:431 + ComponentHumanModel.cs:644 | (model, ref eyeRotation) | 两处派发 |
| `OnModelAnimate` ML:323 【过时·活】 | 生物模型动画 | ComponentCreatureModel.cs:134 | (ComponentCreatureModel, out skip) | 用 OnAnimateModel |
| `OnFirstPersonModelDrawing` ML:2070 | 第一人称手部/手持图标渲染 | ComponentFirstPersonModel.cs:139 | (model, camera, itemValue, ref matrix, out skip) | |
| `OnAppendModelMeshPart` ML:2102 | BlockMesh.AppendModelMeshPart 前 | BlockMesh.cs:265 | (blockMesh, meshPart, matrix, 4 bool, color, out skip) | **注册名是 "OnFirstPersonModelDrawing"**（≠成员名） |
| `OnAppendModelMesh` ML:2120 | BlockMesh.AppendModelMesh 前 | BlockMesh.cs:412 | (blockMesh, blockMesh1, out skip) | **注册名是 "OnFirstPersonModelDrawing"** |
| `OnCameraChange` ML:873 | 切换相机模式 | ComponentGui.cs:644 | (player, gui) | 原版切相机实现在 SurvivalCraftModLoader.cs:76 |
| `ManageCameras` ML:879 | GameWidget 创建时加相机 | GameWidget.cs:77 | (GameWidget) | 加自定义相机；配 GetCameraList |
| `RecalculateCameraProjection` ML:1996 | 摄像机投影矩阵 | BasePerspectiveCamera.cs:233 | (camera, ref Matrix) | |
| `OnCapture` ML:884 | 截屏时 | ScreenCaptureManager.cs:151 | 无 | |

## 十三、音频（2）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `MenuPlayMusic` ML:889 | 主页背景音乐 | MusicManager.cs:64 | (out string 路径) | |
| `PlayInGameMusic` ML:1710 | 游戏中放音乐 | MusicManager.cs:108 | 无 | 自行调音乐 API |

## 十四、UI·Screen·图鉴（27）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `OnWidgetConstruct` ML:999 | 界面 Widget 被创建 | Widget.cs:495 | (ref Widget) | 可整体替换 Widget（ref 在实例化后、挂树+LoadContents 前）。**仅 XML 新建路径触发**（每节点一次）：① 一切 XML 模板的非根节点——`LoadChildren` 递归走 `LoadWidget`（Widget.cs:603），Screens/Dialogs/Widgets 及子面板全覆盖（屏本体走 `LoadContents`，其全部子节点走这里）；② 直接调 `LoadWidget` 建根容器的屏：PlayScreen.cs:30、RecipaediaScreen.cs:62、BestiaryScreen.cs:24、HelpScreen.cs:39、ExternalContentScreen.cs:37、WorldOptionsScreen.cs:356/447、PlayerScreen.cs:163、ManageContentScreen.cs:60-137、ManageUserScreen.cs:108/147、KeyboardMappingScreen.cs:11、GamepadMappingScreen.cs:12、VrControllerMappingScreen.cs:53、CameraManageScreen.cs:8、OriginalCommunityContentScreen.cs:73/86；③ 运行期构建：InventorySlotWidget.cs:311（拖放模板）、MotdWidget.cs:138（公告行）。**不触发**：纯代码 `new` 的控件（如 EditColorDialog 全代码框、AddSettingButton 按钮）、屏/框根本体、已存在 Name 的合并重载（Widget.cs:597-600 只走 LoadContents→改挂 `OnWidgetContentsLoaded`） |
| `OnWidgetContentsLoaded` ML:1005 | 界面内容加载完成 | Widget.cs:510 | (Widget) | 改已有界面元素 |
| `BeforeWidgetUpdate` ML:1808 | Widget.Update 前 | Widget.cs:849 | (Widget) | 可拦截原版按钮功能 |
| `AfterWidgetUpdate` ML:1814 | Widget.Update 后 | Widget.cs:857 | (Widget) | |
| `BeforeWidgetDrawItemRender` ML:1015 | DrawItem 绘制前 | Widget.cs:140 | (drawItem, out skipVanillaDraw, out afterDraw, ref scissor, dc) | 原版输入法候选窗示例在 SurvivalCraftModLoader（注释态） |
| `OnDrawItemAssigned` ML:1028 | DrawItem 排序后 | Widget.cs:113 | (DrawContext) | 调绘制层级 |
| `DrawToScreen` ML:452 | ViewWidget 绘制屏幕 | ViewWidget.cs:140,180 | (viewWidget, DrawContext) | 两处派发 |
| `OnSwitchScreen` ML:2257 | 切换屏幕前 | ScreensManager.cs:52 | (ref Screen, parameters) | screen=null 取消切换 |
| `OnScreenEntered` ML:1795 | 进入 Screen | ScreensManager.cs:309 | (Screen, parameters) | |
| `OnScreenLeaved` ML:1801 | 离开 Screen | ScreensManager.cs:295 | (Screen) | |
| `OnShowDialog` ML:2264 | 显示对话框 | DialogsManager.cs:47 | (ref parentWidget, ref dialog) | dialog=null 不显示 |
| `OnHideDialog` ML:2270 | 隐藏对话框 | DialogsManager.cs:80 | (ref dialog) | |
| `OnModalPanelWidgetSet` ML:1036 | ModalPanel 被设置 | ComponentGui.cs:168 | (gui, oldWidget, newWidget) | |
| `GuiUpdate` ML:413 | Gui 组件帧更新 | ComponentGui.cs:236 | (gui) | |
| `GuiDraw` ML:421 | Gui 组件绘制 | ComponentGui.cs:746 | (gui, camera, drawOrder) | |
| `DisplaySmallMessage` ML:433 | 屏幕中下方小消息显示前 | ComponentGui.cs:189 | (gui, ref 文本, ref 颜色, ref 闪烁, ref 提示音, out skip) | |
| `ClothingWidgetOpen` ML:459 | 衣物界面打开 | ComponentGui.cs:559 | (gui, clothingWidget) | |
| `ModifyLogColor` ML:1983 | 日志消息颜色 | ViewGameLogDialog.cs:149 | (text, ref Color) | |
| `OnSettingsScreenCreated` ML:1968 | 设置界面创建 | SettingsScreen.cs:32 | (screen, out Dictionary\<ButtonWidget,Action\>) | 加设置按钮；免语言切换丢失 |
| `LoadWorldInfoWidget` ML:1637 | 世界选择列表存档条目 | PlayScreen.cs:50 | (WorldInfo, XElement, ref ContainerWidget) | 改存档外观 |
| `ResetOptionsForNonCreativeMode` ML:1689 | 世界设置非创造模式修正 | WorldSettings.cs:88 | (settings, 4 个原值) | |
| `EditBlockDescriptionScreen` ML:1644 【过时】 | 方块介绍页字段 | RecipaediaDescriptionScreen.cs:153 | (Dictionary) | 两重载都调；用新重载 |
| `EditBlockDescriptionScreen` ML:1651 | 方块介绍页字段 | 同上 | (Dictionary, blockValue) | 增减属性字段 |
| `EditRecipeScreenWidget` ML:1657 | 合成表页每帧 | RecipaediaRecipesScreen.cs:56 | (screen) | |
| `UpdateCreaturePropertiesInBestiaryDescriptionScreen` ML:1665 | 生物图鉴详情页每帧 | BestiaryDescriptionScreen.cs:151 | (screen, info, VD) | |
| `LoadCreatureInfoInBestiaryScreen` ML:1676 | 生物图鉴目录条目 | BestiaryScreen.cs:35 | (screen, widget, info, VD) | |
| `OnPlayerModelWidgetMeasureOverride` ML:1918 | 人物界面模型布局 | PlayerModelWidget.cs:156 | (playerModelWidget) | 经 m_modelWidget 增删元素 |

## 十五、物品栏·衣物·护甲（16）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `OnInventorySlotWidgetDefined` ML:1323 | 创建 InventorySlotWidget | InventorySlotWidget.cs:180 | (slotWidget, out List\<Widget\>) | 返回要加的子 Widget |
| `InventorySlotWidgetMeasureOverride` ML:1332 | 格子布局测量 | InventorySlotWidget.cs:409 | (slotWidget, parentAvailableSize) | 画耐久/食物条 |
| `HandleMoveInventoryItem` ML:1344 | 移动物品（格→格） | InventorySlotWidget.cs:537 | (widget, 源/目标 inv+index, ref count, out moved) | |
| `OnInventorySlotWidgetCalculateSplitCount` ML:1362 | 计算分割数量 | InventorySlotWidget.cs:514 | (widget, total, dragMode, ref splitCount) | 自定义 1 个/一半逻辑 |
| `HandleInventoryDragProcess` ML:1378 | 拖放先执行“修改” | InventorySlotWidget.cs:585 | (widget, 源/目标, ref processCapacity) | 容量≤0=跳过原版（火药上膛类） |
| `HandleInventoryDragMove` ML:1395 | 拖放后执行“移动” | InventorySlotWidget.cs:650 | (widget, 源/目标, skipped, out skip) | |
| `ClothingSlotProcessCapacity` ML:262 | 拖物品到人物身上判容量 | ComponentClothing.cs:430 | (clothing, slotIndex, blockValue, ref notToProcessVanilla, out capacity) | capacity 多 mod 取最大；1=可处理 |
| `ClothingProcessSlotItems` ML:249 【过时】 | 人物吃/穿物品 | ComponentClothing.cs:457 | (player, block, slot, value, count)→bool | 三个重载都会被调 |
| `ClothingProcessSlotItems` ML:2021 | 同上（现行） | 同上 | (clothing, slot, ref inputValue/Count, ref processedValue/Count, skipped, out skipVanilla) | 奶桶留空桶在此 |
| `ClothingProcessSlotItems` ML:2035 【过时·有误】 | 同上 | 同上 | (player, …同上签名) | 官方标注有误，别用 |
| `SetClothes` ML:270 | 设置衣物集合 | ComponentClothing.cs:152 | (clothing, slot, IEnumerable\<int\>) | |
| `DecideArmorProtectionSequence` ML:1881 | 护甲防御：改参与衣物列表 | ComponentClothing.cs:199 | (clothing, attackment, randomNumber, List\<int\>) | |
| `ApplyProtectionBeforeClothes` ML:1893 | 护甲结算前自定义 | ComponentClothing.cs:190 | (clothing, attackment, ref attackPower) | 力场护盾类 |
| `ApplyArmorProtection` ML:389 【过时】 | 单件护甲免伤 | ComponentClothing.cs:172 | (clothing, attackPower, appliedByOtherMods, out applied)→float | 新方案：给护甲建新 ClothingData |
| `ApplyProtectionAfterClothes` ML:1904 | 护甲结算后自定义 | ComponentClothing.cs:246 | (clothing, attackment, listAfter, ref attackPower) | |
| `InitializeClothingSlots` ML:1912 | ClothingSlot 初始化 | ClothingSlot.cs:39 | 无 | 加脖子/手臂等穿戴部位 |

## 十六、配方（6）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `CraftingRecipesManagerInitialize` ML:1700 | 配方表加载时 | CraftingRecipesManager.cs:30 | (recipes, ref sort) | 删原版配方 |
| `CraftingRecipesManagerInitialized` ML:1705 | 配方表加载+排序完成 | CraftingRecipesManager.cs:50 | 无 | |
| `OnCraftingRecipeDecode` ML:829 | 配方 XML 解码 | CraftingRecipesManager.cs:68【截断】 | (recipes, element, out decoded) | decoded=true 截断后续 mod |
| `MatchRecipe` ML:839 | 配方匹配 | CraftingRecipesManager.cs:223【截断】 | (需要, 实际, out matched)→bool | matched=true 截断 |
| `DecodeResult` ML:850 | 解码结果物品 | CraftingRecipesManager.cs:181【截断】 | (result, out decoded)→int | |
| `DecodeIngredient` ML:862 | 解码配方材料 | CraftingRecipesManager.cs:203【截断】 | (ingredient, out craftingId, out int? data, out decoded) | 自定义配方材料格式 |

## 十七、字体（3）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `OnBuildingBodyFontChainEntries` ML:2324 | 正文字体链构建 | FontManager.cs:668→700 | (List\<ChainEntry\>) | 只做添加；可能在线程池，勿碰 UI |
| `OnBuildingMonoFontChainEntries` ML:2330 | 等宽字体链构建 | FontManager.cs:683→700 | (List\<ChainEntry\>) | 同上 |
| `OnFontChainsRebuilt` ML:2337 | 字体双链重建完成 | FontManager.cs:393 | 无 | 主线程；刷新自家字体引用 |

## 十八、系统调度（5）

| 钩子名 | 触发时机 | 派发点 | 参数/返回 | 备注 |
|---|---|---|---|---|
| `SubsystemUpdate` ML:743/744 | 子系统帧更新 | SubsystemUpdate.cs:122 | (dt) / (SubsystemUpdate, dt) | 两重载同一次都调 |
| `OnIUpdateableAddOrRemove` ML:1285 | IUpdateable 添/删 | SubsystemUpdate.cs:51 | (subsysUpdate, updateable, toAdd1OrRemove0, skipped, out skip) | skip=接管其 Update |
| `OnIDrawableAdded` ML:1300 | IDrawable 添加 | SubsystemDrawing.cs:115 | (drawing, drawable, skipped, out skip) | skip=接管其 Draw |
| `ChangeGameTimeDelta` ML:1274 | 时间流速 | SubsystemTime.cs:91 | (subsysTime, ref dt) | 偏底层 |

---

**电力**：无专用钩子——电路逻辑随 SubsystemUpdate 帧更新走，改方块走 TerrainChangeCell。
**核对**：18 组覆盖全部 236 个成员（230 唯一名；SubsystemUpdate ML:743/744 与 ProjectXmlLoad ML:808/809 两行各合并两个重载，其余重载分行），与 ModLoader.cs 一一对应，无一遗漏。
