# Subsystem体系

> 域: SC引擎 · 更新: 2026-11-01 · 状态: 全读(111/111，特大文件0个)——顶层40+BlockBehavior子目录71，共20185行全部读毕；逐文件明细见 [02a-子系统明细.md](明细/02a-子系统明细.md)

## 一句话定位

Subsystem 是"每个世界一份的单例服务"：注册进 Project 模板、按依赖递归 Load、每 tick 被 SubsystemUpdate 驱动、Save 时按实例化顺序落盘；业务能力由 40 个顶层子系统 + 71 个方块行为(SubsystemBlockBehavior)构成。

## 目录地图

| 符号(类/文件) | 仓库路径 | 职责 |
|---|---|---|
| `Subsystem` 基类 | E:\SurvivalcraftAPIProject\EntitySystem\GameEntitySystem\Subsystem.cs | 生命周期契约(Load/Save/Dispose/OnEntityAdded) |
| `Project` | E:\SurvivalcraftAPIProject\EntitySystem\GameEntitySystem\Project.cs | 持有子系统表；实例化/加载/保存/互查 |
| `SubsystemUpdate` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemUpdate.cs | tick 驱动器：IUpdateable 注册表+排序+派发 |
| `SubsystemTime` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemTime.cs | 游戏时钟与速度倍率 |
| `SubsystemTerrain` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemTerrain.cs | 地形门面：ChangeCell/Raycast/DestroyCell/序列化 |
| `SubsystemBodies` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemBodies.cs | ComponentBody 8x8 空间网格索引(全游戏空间查询底座) |
| `SubsystemSpawn` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemSpawn.cs | chunk 实体卸载/重生；SpawningChunk 事件源 |
| `SubsystemCreatureSpawn` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemCreatureSpawn.cs | 刷怪规则中枢(60+ 硬编码生物规则) |
| `SubsystemElectricity` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemElectricity.cs | 电路模拟(0.01s 固定步进) |
| `SubsystemExplosions` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemExplosions.cs | 爆炸(压力 BFS+冲量+掉落转抛射物) |
| `SubsystemMovingBlocks` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemMovingBlocks.cs | 移动方块集底座(活塞/塌方共用) |
| `SubsystemFireBlockBehavior` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\BlockBehavior\SubsystemFireBlockBehavior.cs | 火焰方块(104)蔓延/燃尽 |
| `SubsystemFluidBlockBehavior` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\BlockBehavior\SubsystemFluidBlockBehavior.cs | 流体基类(水/岩浆子类化) |
| `SubsystemBlockBehavior` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\BlockBehavior\SubsystemBlockBehavior.cs | 方块行为抽象基类(20+ 回调契约) |
| `SubsystemBlockBehaviors` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemBlockBehaviors.cs | behavior↔contents 绑定器(Load 时建表) |
| `SubsystemModelsRenderer` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemModelsRenderer.cs | 实体模型渲染+GPU 蒙皮 |
| `SubsystemSky` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemSky.cs | 天空/雾/日月/闪电(计算委托可换) |
| `SubsystemWeather` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemWeather.cs | 降水/闪电/雾状态机+结冰积雪 |
| `SubsystemPickables` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemPickables.cs | 掉落物容器(账本预扩容) |
| `SubsystemProjectiles` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemProjectiles.cs | 抛射物容器(FireProjectile 入口) |
| `SubsystemPathfinding` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemPathfinding.cs | 后台线程 A* 寻路 |
| `SubsystemBlocksScanner` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemBlocksScanner.cs | 方块轮询调度(500 轴/帧预算) |
| `SubsystemItemsScanner` | E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\SubsystemItemsScanner.cs | 全物品扫描(腐烂/GC 事件源) |
| `GameManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\GameManager.cs | LoadProject/SaveProject/DisposeProject |
| `DatabaseManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\DatabaseManager.cs | GameDatabase(模板库)持有者 |
| Project 模板 XML | E:\SurvivalcraftAPIProject\Survivalcraft\Content\Assets\Database.xml | `:4343` `<ProjectTemplate Name="Project">`；子系统根模板 `:4454-4457`(Class/IsOptional/Dependencies) |
| `ModEntity.LoadXdb` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModEntity.cs | `:321-336` mod 的 .xdb 合并进主库 |

全目录 111 个文件（顶层 40 + BlockBehavior\ 71，20185 行）已全读：四个核心机制见下文保留章节，其余全部子系统的逐文件职责/关键方法行号见 [02a-子系统明细.md](明细/02a-子系统明细.md)。

## 核心机制

### 基类契约(`Subsystem.cs:5-38`)

字段 `m_project`/`m_valuesDictionary`；虚方法 5 个：`OnEntityAdded/OnEntityRemoved`、`Load(ValuesDictionary)`(`:20`)、`Save(ValuesDictionary)`(`:22`)、`Dispose`。`Initialize(Project, ValuesDictionary)`(`:31-37`) 校验袋子类型必须是 `MemberSubsystemTemplate` 并回填两个引用——**没有 LoadOrder 参数**：子系统不像组件按 `LoadOrder` 排，只有 `Dependencies` 字符串。

### 注册：.xdb → Project 模板

mod 在自己 `.xdb` 里写 `<ProjectTemplate Guid="85023bf8-1c90-4dd1-9442-e6c13691d078">`(定位原版 Project 模板) + `<MemberSubsystemTemplate Name="…">`，内含 `Parameter Class="命名空间.类名"`、`Dependencies="名1,名2"`、`IsOptional`。合并链：启动加载第 13 步 `ModEntity.LoadXdb`(`ModEntity.cs:321-336`) → `ModsManager.CombineDataBase`(`ModsManager.cs:1079/1083`)——按(元素名+Guid)递归找节点，**命中就把 mod 的孩子追加到该节点末尾**；`Remove="true"` 删节点，`New-属性` 改属性。加载后 `DatabaseManager.LoadDataBaseFromXml`(`DatabaseManager.cs:31-43`) 序列化成 `GameDatabase`。

### 实例化与加载顺序的决定因素(`Project.cs:42-108`)

**顺序由"合并后 Database.xml 里 ProjectTemplate 的子节点文档顺序"决定**：原版 40+ 个按原文件顺序在前(BlocksManager、UsedMods…)，mod 的追加在尾。ctor 内部时序：

1. 遍历 `projectData.ValuesDictionary.Values` 中类型为 `MemberSubsystemTemplate` 的袋子(`:48-52`)，读 `IsOptional`/`Class`(`:53-55`)，`TypeCache.FindType`+`Activator.CreateInstance`+`Initialize`(`:56-76`)——**只构造，不 Load**；同时登记进 `m_subsystems`(实例化表)与名字典(`:75-76`)。
2. `InitializeEntities`+`AddEntities`(`:81-85`)：实体建好挂起(`PostponeFireEntityAddedEvents=true`，`Project.cs:39`，不触发 OnEntityAdd)。
3. `BeforeSubsystemsAndEntitiesLoad` 静态事件(`:86`)→钩子 `ProjectBeforeSubsystemsAndEntitiesLoad`——**此时所有子系统已实例化但未 Load，是互查/注入的最后窗口**。
4. `LoadSubsystem` 依赖递归(`:87-89`→`:358-386`)：读本子系统袋子的 `Dependencies`(逗号分隔**子系统 Name**，`:370-383`)，先递归加载依赖再 `subsystem.Load(valuesDictionary)`(`:384`)；递归深>100 抛(`:362-366`)；依赖名找不到抛(`:379-381`)。
5. `LoadEntities`(`:90`)：组件 Load，然后统一 `FireEntityAddedEvents`(`:316-325`：组件→全部子系统 OnEntityAdded→`EntityAdded` 事件)。
6. `OnProjectLoad`(`:91`)→钩子 `OnProjectLoaded`。

### 更新体系：谁驱动谁

驱动链(每帧一次)：`GameScreen.Update`(`GameScreen.cs:48`)→`GameManager.UpdateProject`(`GameManager.cs:191`)→`SubsystemUpdate.Update`(`SubsystemUpdate.cs:44-133`)：

1. `for (i < UpdatesPerFrame)`(`:45`，正常=1，睡觉=20，每轮重读属性)。
2. `m_subsystemTime.NextFrame()`(`:46`)：算 dt→派 `ChangeGameTimeDelta` 钩子→累加 `GameTime`→处理睡眠/菜单倍率(`SubsystemTime.cs:88-141`)。
3. 消费 `m_toAddOrRemove`(`:48-71`)：钩子 `OnIUpdateableAddOrRemove` 可 `skipVanilla` 拦截。
4. 检测 `FloatUpdateOrder` 变化则重建排序表(`:72-85`)。排序规则(`:13-23`)：先比 `FloatUpdateOrder`，**相等比 `GetHashCode()`——同序者相对顺序不稳定**；`UpdateOrder` 枚举(`E:\SurvivalcraftAPIProject\Survivalcraft\Game\UpdateOrder.cs:3-14`)：Reset=-100, SubsystemPlayers=-20, Input=-10, Default=0, …, Terrain=100, Views=200。细插序用浮点(如 +0.01f)。
5. 逐个 `lock (sortedUpdateable) { Update(dt) }`(`:90-95`)——**dt 是游戏时间增量不是帧时间**；异常被 `catch (Exception) {}` **彻底静默**(`:97-99`)。
6. 派 `SubsystemUpdate` 钩子(`:122-131`)，旧新两个重载都调，mod 只重写带 `(SubsystemUpdate, float dt)` 的那个。

子系统进表两条路：自身实现 `IUpdateable` 的在 `SubsystemUpdate.Load` 收(`:147-153`)；实体的 `IUpdateable` 组件经 `OnEntityAdded/OnEntityRemoved` 自动进出(`:179-189`)。性能表工具 `UpdateTimeDebug`(`:38`，Save 时输出，`:155-177`)。

### Save/Load 时序

**Save**(触发点 4 个：失焦 `GameScreen.cs:13`、Leave `:28`、300 秒自动 `:37-41`、菜单手动)：`GameManager.SaveProject`(`GameManager.cs:118-131`)：`m_project.Save()` 在**游戏线程**完成(`:120`)→`Project.Save`(`Project.cs:284-297`) 按 `m_subsystems` 顺序(=实例化顺序)逐个 `subsystem.Save(vd)`，**`vd.Count>0` 才写入 ProjectData**(`:290-292`)→后台 `Task.Run(InternalSaveProject)`(`GameManager.cs:125`)：备份 `Project.bak`(`:136`)→钩子 `ProjectXmlSave`(空 `<Project>`)→`projectData.Save(xElement)`→钩子 `OnProjectXmlSaved`(改 XML 最后机会)→写盘(`:155-159`)。

**Load**：`GameManager.LoadProject`(`:32-116`)：读 `<存档>/Project.xml`→钩子 `ProjectXmlLoad`(先旧后新签名，`:46-55`)→挂 5 个事件转发(`:56-102`，其中 `EntityComponentsInitialized`/`BeforeSubsystemsAndEntitiesLoad` 静态事件只 += 永不 -=，**每次进世界重复派发**)→`new ProjectData(模板+存档覆盖)`+`new Project`(`:102-103`)→`FindSubsystem<SubsystemUpdate>` 缓存(`:104`)。存档里没有的子系统模板(新装的 mod)按模板默认值走 ctor 流程。

**Dispose**(`Project.cs:299-314`)：先实体后子系统逐个 `DisposeInternal`。

### 子系统互查

`Project.FindSubsystem<T>(throwOnError)`(`Project.cs:143-147`)：对 `m_subsystems` **线性扫描**，按 `IsAssignableFrom` 匹配；按名字查 `:126-141`(存档袋名=模板 Name)；多个同类型用 `FindSubsystems<T>()`(`:157-163`)。在 `Load` 里查别的子系统时，若对方没载完拿到的是"已构造未 Load"对象——有顺序要求用 `Dependencies` 声明(原版范式：`SubsystemUpdate.Load:148` 要 SubsystemTime、`SubsystemTime.Load:156-158` 要 SubsystemPlayers/SubsystemUpdate)。**别把查到的子系统缓存进 static 字段**：换世界后是旧对象，要存就用 `OnProjectDisposed` 清。

### 刷怪链：SubsystemSpawn → SubsystemCreatureSpawn

卸载/重生(`SubsystemSpawn.cs`)：`Update:57-74` 四定时器——UpdateLastVisitedTime 每 5s、SpawnChunks 每 4s、DespawnChunks 每 2s、DiscardOldChunks 每 60s(MaxChunkAge=76800 游戏秒)。`SpawnChunks:174-210`：视角 SpawnRadius=48 圆内、chunk 状态>InvalidPropagatedLight → 重放 `chunk.SpawnsData`(`SpawnEntity:255-282`，`Project.CreateEntity(values, data.EntityId)` **保留原实体 Id**，钩子 `OnReadSpawnData`)→清空→`SpawningChunk?.Invoke`→IsSpawned=true。`DespawnChunks:212-253`：`ComponentSpawn.AutoDespawn` 且离所有视角>DespawnRadius=60 → 打包 SpawnEntityData(TemplateName/Position/ConstantSpawn/Data/EntityId；mod 钩子 `OnSaveSpawnData` 塞 Data)→存回 chunk→`Despawn()`。存档用紧凑字符串 `"Template,x,y,z,ConstantSpawn,Data,EntityId;"`(`SaveSpawnsData:338-359`)。

规则刷怪(`SubsystemCreatureSpawn.cs`)：Load(`:92-109`) 订阅 SpawningChunk 入队；`Update:69-90` 仅 `EnvironmentBehaviorMode.Living`——新 chunk 每个试 10 次、已访问 chunk 试 2 次，每 60s(冬 120s) SpawnRandomCreature。`SpawnChunkCreatures:1068-1102`：总限额 m_totalLimit=26(常驻 6/挑战 12)、区域限额 3(常驻 4/半径 42)——**这些是 static 字段(:54-61)**；位置类型 Surface/Cave/Water 按 0.3/0.3/0.4 随机(`:1349-1358`)；候选 CreatureType 按 SpawnSuitabilityFunction 加权随机(`GetRandomWeightedItem:1334`)。落点验证 `TestSpawnPoint:1199-1261`：Surface 要求 `SkyLightValue-光照>3`+下碰撞上两格空非水；Cave 要求 `SkyLight-光照≥5`(暗)；Water 要求 3 格水。生成 `SpawnCreatures:1104-1132` 每目标 50 次尝试±8 偏移→`DatabaseManager.CreateEntity`+`Project.AddEntity`。区域计数 `CountCreaturesInArea:1293-1332` 走 SubsystemBodies 网格**且把未生成的 SpawnsData 也算数**(防卸载即刷)。60+ 生物规则的湿度/温度/海岸距离/底方块判定全硬编码在 `InitializeCreatureTypes:123-987`；mod 加类型走钩子 `InitializeCreatureTypes`(`:1009`)或存档 CreatureSpawnRules 的 Class 反射(`:1018-1038`)。

### 地形写入链：ChangeCell → 行为分派 → 邻居通知

一切方块交互总闸 `SubsystemTerrain.ChangeCell:355-394`：钩子 `TerrainChangeCell` 可整体跳过→新旧值清光位后相同短路→`SetCellValueFast`+`chunk.ModificationCounter++`→`TerrainUpdater.DowngradeChunkNeighborhoodState(InvalidLight)`→`m_modifiedCells` 记账→`ChangeCellToBehavior:396-427` 分派：contents 变→`OnBlockRemoved`→`OnBlockAdded`，同 contents→`OnBlockModified`；MovingBlockSet 未停→`OnBlockStartMoving`/`OnBlockStopMoving`。**邻居通知延后**：`ProcessModifiedCells:66-84` 在 `Update:493-498`(UpdateOrder.Terrain=100)里于 TerrainUpdater.Update 之后跑，对每变更格+6 邻居调 `OnNeighborBlockChanged`——behavior 在 OnBlockAdded 里看邻居时邻居尚未收到通知。

`DestroyCell:429-470`：`block.GetDropValues`→逐 drop 调 `OnItemHarvested`(可改掉落)→`AddPickable`→距视角<16 出 debris→ChangeCell；爆炸/塌方等毁灭调用一律 noDrop:true。

消费者范式：`SubsystemBlockBehaviors.Load:16-48` 把"Block.Behaviors 字符串"与"behavior.HandledBlocks"两路绑定成 `m_blockBehaviorsByContents`，并反射检测 OnUse override 置 `DefaultIsUseable`(`:39-46`)。火焰(104 方块 bitmask 面，`SubsystemFireBlockBehavior.Update:106-243` 分帧 50 点/帧+5s 落地批)、流体(`SubsystemFluidBlockBehavior.SpreadFluid:149-265` 两轮 level 扩散+最近落点 BFS)、植物轮询(`SubsystemBlocksScanner.Update:36-97` 500 轴/帧预算+pollPass)、延迟写入(`SubsystemCellChangeQueue:26-53` 乐观锁+20s 冲刷)都挂在这条链上。

### 移动方块链：MovingBlocks 底座 + 活塞/塌方消费者

`SubsystemMovingBlocks.AddMovingBlockSet:152-202`(钩子 `OnMovingBlockSetAdded` 可改/拒) → `Update:304-380`：速度=Speed+Acceleration·dt、Drag 幂衰减、Smoothness 收尾；每步 `MovingBlocksCollision`(集合互撞→Stop)+`TerrainCollision`(盒内非空→`CollidedWithTerrain` 事件)；Stop 时位置按速度方向对齐格点(`:352-371`)→`Stopped` 事件。渲染用独立 canvasTerrain 几何(`GenerateGeometry:556-662`，整数锚点变化才重建)。

写回标准路径 `AddTerrainBlock:692-713`=`Stop()`+`DestroyCell(…,movingBlock)`——走 OnBlockStopMoving 分支，方块实体/告示文本/可编辑数据随搬(`SubsystemEntityBlockBehavior:80-97`、`SubsystemSignBlockBehavior:172-192`、`SubsystemEditableItemBehavior:78-90`)。消费者：活塞 `SubsystemPistonBlockBehavior`(UpdateOrder=MovingBlocks+1，MovePiston:311-469 ≤8 块/伸缩 8，StopPiston:471)与塌方 `SubsystemCollapsingBlockBehavior`(TryCollapseColumn:67)。

### 电路模拟链：0.01s 固定步进，与 tick 解耦

`SubsystemElectricity.Update:395-452`：`m_remainingSimulationTime=min(+dt,0.1)`，每 0.01s(`CircuitStepDuration:237`)跑一轮：`UpdateElectricElements:611-654` 重建元素/线域(线域=导线泛洪 `ScanWireDomain:693-730`)→`AddElectricElement:529-594` 建双向 Connections→`QueueElectricElementForSimulation:357-373` 按目标步进排表(m_futureSimulateLists+字典缓存池)。`SimulateElectricElement:523-527`：`Simulate()` 返 true 才向邻居传播下一步。**100 步/秒固定频率，与 SubsystemUpdate 的 dt 无关**；元素 Simulate 抛异常无条件 rethrow(`:416-423`)→整帧电路死且被 SubsystemUpdate 静默。持久电压存档≤500 条(`:483`)。方块变化入口在 `SubsystemElectricBlockBehavior`——其 HandledBlocks 是 63 个硬编码 ID(`:8-70`)，新电力方块必须手工补。

### 绘制与资源调度全景

DrawOrders 实测序：-10000 ModelsRenderer 准备 | -100 Sky 雾参数 | 0 Terrain 不透明 | 1 Models | 5 Sky 顶 | 10 Projectiles/Pickables | 50 Weather/Signs | 99 Models 水前透明 | 100 Terrain 透明 | 105 Sky 闪电 | 110 Glow | 200 Shadows | 201 Models 水后透明 | 300 Particles。调度器 `SubsystemDrawing.Draw:39-80` 按 DrawOrders 排序逐个 Draw、异常静默；实体组件 IDrawable 经 OnEntityAdded 自动进出。爆炸链 `SubsystemExplosions.Update:246-327`(同帧压力 BFS→掉落转抛射物限流:707→全体 body/pickable/projectile 冲量:770-883)。音频链 `SubsystemAudio`(队列+拥塞闸:182+声速延迟；游戏加速时全静音:156)。

## 坑与对策

- **mod 子系统 Load 时机太早/太晚**：顺序=文档顺序+Dependencies；需要"别人 Load 完才初始化"就把依赖名写进 `Dependencies`(找不到直接抛，好过静默)。想拦"全体 Load 前"用 `ProjectBeforeSubsystemsAndEntitiesLoad` 钩子。
- **Save 一个值没写→读档时袋子整个消失**：`Count>0` 才落盘(`Project.cs:290-292`)，读取端必须给默认值，不能假设袋子存在。
- **子系统 Update 里抛异常无任何日志**(`SubsystemUpdate.cs:97-99`)：自己 try/catch+`Log.Warning`；怀疑"逻辑没跑"先查这条。
- **同名袋子/重复 Guid**：`MemberSubsystemTemplate` 的 Name 即存档键，两个同名会互相顶；新节点 Guid 必须新随机值(重复 Guid=整个数据库加载失败)。
- **静态事件重复派发**：第二次进世界 `EntityComponentsInitialized`/`ProjectBeforeSubsystemsAndEntitiesLoad` 会再触发一遍，钩子里按 project/entity 去重或挪去 `OnProjectLoaded`。
- **Dictionary 序即载入序**：`dictionary.Values` 遍历(`Project.cs:87`)保持插入序，但**别依赖它**——顺序的真正来源是 XML 文档序，改 merge 顺序/换平台都不保证；跨子系统顺序需求一律写 `Dependencies`。
- **ElectricElement.Simulate 异常=全电路炸**：`SubsystemElectricity.cs:416-423` catch 后无条件 rethrow，冒泡到 SubsystemUpdate 静默 catch——当帧全部电路停摆无日志。自定义元素 Simulate 内部全 try/catch。
- **新电力方块漏登记 HandledBlocks**：`SubsystemElectricBlockBehavior.cs:8-70` 硬编码 63 个 ID，漏了则 OnBlockAdded 等不触发、电路不建元素。
- **刷怪限额是 static**：`SubsystemCreatureSpawn.cs:54-61` m_totalLimit 等静态字段，改了全局生效且换世界不清零。
- **寻路队列满=假完成**：`SubsystemPathfinding.cs:198-222` 队列>10 时直接置 IsCompleted+空路径(生物"不动"先查这里)；后台每单还 Task.Delay(250)。
- **火焰燃烧进度不存档**：FireData 纯内存(`SubsystemFireBlockBehavior` 无 Save)——读档后全部火重新计时。
- **爆炸掉落限流**：`SubsystemExplosions.cs:707-710` 抛射物数≥40 后掉落概率骤降——大爆炸"东西没了"是限流非 bug；`ExplosionKeepsPickables=true` 豁免。
- **水体扩散放大邻居通知**：`SpreadFluid` 每轮手动 `ProcessModifiedCells`(`SubsystemFluidBlockBehavior.cs:263`)，大面积水每 0.25s 两轮全量回调。

## 原版范例

路径为仓库相对路径（源码树根起）。

| 我要做… | 照抄哪里 | 为什么抄它 |
|---|---|---|
| 最小完整子系统骨架（Load+每帧 Update） | `Survivalcraft\Subsystem\SubsystemSeasons.cs`（83 行全文件）：`:8` 继承 Subsystem+IUpdateable、`:33` UpdateOrder 属性、`:55-57` Load 里 `FindSubsystem<SubsystemGameInfo>(true)` 抓依赖、`:59-63` Update | 全库最短的"可更新子系统"完整文件，字段/属性/生命周期各占其位，零噪音 |
| Save/Load 契约（数值进存档） | `Survivalcraft\Subsystem\SubsystemGameInfo.cs:77-91`：Load `GetValue<T>("键")`(:82-84) 与 Save `SetValue("键", …)`(:87-91) 一键一对 | 原版主信息子系统就是这份"读写成对"清单；对照本页"Count>0 才落盘"坑看最直观 |
| 把一组对象打包存档（嵌套袋列表） | `Survivalcraft\Subsystem\SubsystemUsedMods.cs:6-30`（全文件 31 行）：循环 new 子 ValuesDictionary→`valuesDictionary.SetValue("Mods", modsDict)`+计数键 | 存"列表/数组"没有专用类型，原版就是"计数+编号子袋"，抄它不用自己发明协议 |
| Dependencies 声明与消费（配对看两处） | 声明：`Survivalcraft\Content\Assets\Database.xml:3649`（Players：`Dependencies="GameInfo, Terrain"`，逗号分隔多依赖）+`:3611`（BombBlockBehavior：`"Projectiles, BlockBehaviors"`）；消费：`Survivalcraft\Subsystem\SubsystemUpdate.cs:147-153`（Load 第一行抓 SubsystemTime 再收全体 IUpdateable） | 声明端保证自己 Load 时依赖已 Load，消费端示范"Load 里抓服务"的标准第一行 |
| 子系统响应实体增删（维护索引） | `Survivalcraft\Subsystem\SubsystemNames.cs:31-41`：OnEntityAdded/Removed 增删 name→ComponentName 字典；查询端 `FindEntityByName`(:18-21) | 基类仅有的两个实体回调的真实用法；进世界批量建实体时也是统一走它 |
| 做一个"别人调、别人听"的世界服务 | `Survivalcraft\Subsystem\SubsystemNoise.cs:11-36`：MakeNoise 双重载(:11-17)→FindBodiesAroundPoint 扫半径(:26)→对每 body 的 `FindComponents<INoiseListener>()` 广播(:31-32) | 接口解耦的服务广播范式：调用方不认识监听方，加新监听者零改动 |
| 游戏时钟节流/延时（tick 内） | `Survivalcraft\Subsystem\SubsystemTime.cs:147-155`（`PeriodicGameTimeEvent`）+`:143-145`（`QueueGameTimeDelayedExecution`）+用法 `Survivalcraft\Component\ComponentHealth.cs:320`（每 2 游戏秒判一次溺水） | 与 01 页墙钟 `Time.PeriodicEvent` 区分：这套跟随游戏速度倍率，睡觉加速会同步加速 |

## 快查路由

| 我想… | 去/看 |
|---|---|
| 注册一个自己的子系统 | 本页"注册"+百科 07-entity/03-xdb-registration(含最小 XML 片段) |
| 查"为什么我的 Load 没被调/顺序不对" | `Project.cs:358-386` `LoadSubsystem` 依赖递归+检查 Dependencies 拼写(逗号+Name) |
| 每帧跑逻辑(不注入 Update) | 实现 `IUpdateable`(`Survivalcraft\Game\IUpdateable.cs`)+`SubsystemUpdate.Load` 自动收；或钩子 `SubsystemUpdate` |
| 改 dt/游戏速度/睡觉加速 | `SubsystemTime.cs:62-67` `CalculateGameTimeDalta`(Harmony 时照抄 Dalta 拼写)+钩子 `ChangeGameTimeDelta` |
| 往存档写自定义数据 | 重写 `Subsystem.Save/Load`，键自定；注意 Count>0 才落盘；百科 07-entity/05-persistence |
| 查某子系统的职责/关键方法行号 | [02a-子系统明细.md](明细/02a-子系统明细.md) 一行一文件 |
| 加/改刷怪规则 | 本页"刷怪链"；钩子 `InitializeCreatureTypes`(`SubsystemCreatureSpawn.cs:1009`)；限额 static `:54-61` |
| 拦截/改写方块变更 | 钩子 `TerrainChangeCell`(`SubsystemTerrain.cs:357`)；行为分派 `ChangeCellToBehavior:396` |
| 写自定义方块行为 | 继承 `SubsystemBlockBehavior`(`BlockBehavior\SubsystemBlockBehavior.cs:6-77` 契约)或 `SubsystemPollableBlockBehavior`(轮询)；绑定见 `SubsystemBlockBehaviors.Load:16` |
| 做活塞/移动结构 | `SubsystemMovingBlocks.AddMovingBlockSet:152`+订阅 `Stopped/CollidedWithTerrain`(`:146-148`)；参考 `SubsystemPistonBlockBehavior` |
| 电路/自定义 ElectricElement | 本页"电路模拟链"；`SubsystemElectricity.cs:357-373` 排队；Simulate 必须 try/catch |
| 爆炸/伤害 AOI | `SubsystemExplosions.AddExplosion:237`/`TryExplodeBlock:225`；钩子 `OnBlockExploded`/`CalculateExplosionPower` |
| 实体卸载后自定义数据丢失 | 钩子 `OnSaveSpawnData`/`OnReadSpawnData`(`SubsystemSpawn.cs:242/259`) 读写 SpawnEntityData.Data |
| 查渲染顺序(DrawOrders) | 本页"绘制与资源调度全景" |
| 查某钩子在哪 | Grep `ModHooks` 限定 `ModsManager\` 目录；机制与注册窗口见 [12-ModAPI与加载链](12-ModAPI与加载链.md) |

另见：[01-程序入口与主循环](01-程序入口与主循环.md)(tick 在帧序中的位置、SyncDispatcher 与 Dispatcher 的区别)、[04-方块系统](04-方块系统.md)(Block 类与 behavior 的分工)。
