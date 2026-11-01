# 地形修改与MovingBlocks

> 域: SC引擎 · 更新: 2026-11-01 · 状态: 全读(SubsystemTerrain/TerrainChunk/Terrain/TerrainChunkState/TerrainUpdater/TerrainSerializer23/SubsystemMovingBlocks/MovingBlock/SubsystemPistonBlockBehavior/SubsystemCollapsingBlockBehavior/SubsystemExplosions/SubsystemEntityBlockBehavior/SubsystemBlockEntities/SubsystemBlockBehavior)

## 一句话定位

运行时改世界的唯一入账口是 `SubsystemTerrain.ChangeCell`（钩子→写格→脏计数→3×3 降级→行为派发五连）；存档不记"修改日志"而是**只把脏过的整块快照**写进 Region 文件；活塞/塌方把方块从网格搬进 `MovingBlockSet` 浮空集合、落地用 `DestroyCell` 带块回写——爆炸则是"逐格 DestroyCell"的批量原版范式。

## 修改入账链（运行时改一格发生什么）

| # | 发生什么 | 出处 |
|---|---|---|
| 1 | 入口 `ChangeCell(x,y,z,value, updateModificationCounter=true, movingBlock=null)` | `Survivalcraft\Subsystem\SubsystemTerrain.cs:355` |
| 2 | ⚡`TerrainChangeCell` 钩子（`out Skip=true` 整段跳过原版写格） | SubsystemTerrain.cs:357-369 |
| 3 | 合法性只查 y∈[0,256)（`Terrain.IsCellValid`，x/z 越界由 `GetChunkAtCell` 返 null 兜住） | SubsystemTerrain.cs:370-372; `Survivalcraft\Game\Terrain.cs:228` |
| 4 | 新旧值**清光位**后比较，相同直接 return——手写光值无效，光只由重算产生 | SubsystemTerrain.cs:373-378 |
| 5 | `Terrain.SetCellValueFast` 写入 Cells 数组（同步可见） | SubsystemTerrain.cs:379; Terrain.cs:260; `Survivalcraft\Game\TerrainChunk.cs:171` |
| 6 | `chunk.ModificationCounter++`（**全仓唯一自增点**；`updateModificationCounter=false` 可跳过，原版仅活塞回缩用） | SubsystemTerrain.cs:380-384 |
| 7 | `DowngradeChunkNeighborhoodState(coords, radius=1, InvalidLight, false)`——自身+8 邻降级，光照/网格交给状态机重算 | SubsystemTerrain.cs:385; `Survivalcraft\Game\TerrainUpdater.cs:416-432` |
| 8 | 记入 `m_modifiedCells` → 下一帧 `Update→ProcessModifiedCells`：对 7 个偏移(含自身)逐个发 `OnNeighborBlockChanged` | SubsystemTerrain.cs:387, :493-498, :66-84 |
| 9 | `ChangeCellToBehavior`（try/catch 只记日志）：movingBlock 分支见下；否则 contents 变→`OnBlockRemoved`(旧)→`OnBlockAdded`(新)，不变→`OnBlockModified` | SubsystemTerrain.cs:388-393, :396-427 |
| 10 | `DestroyCell(toolLevel,…,movingBlock)` = 掉落表→碎屑粒子→`ChangeCell(:469)`；挖/爆炸/落地回写全汇这里 | SubsystemTerrain.cs:429-470 |

- **裸写旁路**：`Terrain/TerrainChunk.SetCellValueFast` 不计数、不降级、不发行为——只许生成管线与画布地形用；运行时直写 = 修改不落盘 + 光照网格冻结。
- **移动分支**（`movingBlock.MovingBlockSet!=null` 时第 9 步换成）：集合未停→旧值行为 `OnBlockStartMoving`；已停→新值行为 `OnBlockStopMoving`；然后 **return——OnBlockAdded/Removed 完全不触发**（这是箱子搬家内容不丢的根因） | SubsystemTerrain.cs:401-413
- **批量范式=爆炸**：`AddExplosion` 入队(:237-244)→`Update` 把中心 ±4 内的排队爆炸一次全爆(:246-327)→`SimulateExplosion` BFS 压力衰减波(:343-639，衰减 `pressure/(pow(块数,0.66)+5·max(步-7,0))` :376-377)→每毁格 `DestroyCell(0,noDrop=true,noPS=true)`(:671-679)+75/95% 概率链爆 `TryExplodeBlock`(:225-235,:683)+碎块变抛射物(:701-750)→`PostprocessExplosions`：存活格行为 `OnExplosion`(:794-802)+起火(:803-809)+实体/掉落物冲量(:811-838)+音效分档(:839-882) | `Survivalcraft\Subsystem\SubsystemExplosions.cs`

### mod 视角：世界编辑器/结构放置的接口清单

- **正道**：循环 `ChangeCell`（同区块重复降级幂等，无 N² 放大）；只有格子值需同步读时才可夹 `SetCellValueFast` 读-改，最后仍走 ChangeCell 收账。
- **等待契约**：格子值同步可见；光照/网格要等状态机把区块重新推到 `Valid`（相机前 6 格会在 `PrepareForDrawing` 同步等完，TerrainUpdater.cs:392-414）；邻居行为通知**延后一帧**（ProcessModifiedCells）——OnBlockAdded 里读邻居是"未通知态"。
- **时机红线**：目标区块 `State≤InvalidContents4`（还在生成趟）别写——生成趟会覆盖早写的格。活塞的原版判据是 3×3 邻域区块全部已生成才动手（SubsystemPistonBlockBehavior.cs:229-237），照抄。
- **省盘技巧**：纯视觉改动传 `updateModificationCounter:false` 可不脏化区块（但改动也不会存盘）。

## 持久化契约

- **整块快照，非修改日志**：`SaveChunk` 门槛 `State>InvalidContents4 && ModificationCounter>0`，落盘后清零——**没被改过的区块永不写盘**，重进世界由种子重生成 | `Survivalcraft\Game\TerrainSerializer23.cs:593-599`
- **文件组织**：每世界目录 `Regions/Region X,Y.dat`，一个文件装 16×16 个区块（坐标 `>>4` 定位 :343-344/:359-360）；头=FourCC `RGN1`+256 个 8 字节目录项(:507-514)；每条目前置 4 字节 `CHK1`(:516-520)；就地写不下→tmp 整文件重建换名(:381-442)；单 Region 上限 256MB(:540-545)；句柄 LRU 100(:473-475) | TerrainSerializer23.cs
- **压缩**：256 字节温湿度（每列 `温度<<4|湿度` 挤一字节 :654-659）→ 按 y→x→z 对**光位清零**的整格 value 做 RLE，游程长度藏进 light 位（≤15：4 字节；≤271：5 字节 :751-764）→ Deflate Fastest(:688)；解压未精确填满 16×256×16 抛 "Corrupt chunk data"(:719-723) | TerrainSerializer23.cs:652-724
- **光不落盘**：读档走 `NotLoaded→InvalidLight`（跳过四趟生成，玩家修改因此幸存）并标 `IsLoaded=true` | `Survivalcraft\Game\TerrainUpdater.cs:653-667`
- **十态参与情况**（TerrainChunkState.cs:2-13）：只有 ≥InvalidLight(5) 的区块有落盘资格；停在 NotLoaded~InvalidContents4 的区块被卸载 = 直接放弃重生成。ChangeCell 的降级目标就是 InvalidLight——正常路径下"改过的区块"状态恒 ≥5，门槛必过。
- **退出保存**：`SubsystemTerrain.Save` 遍历全部 AllocatedChunks 逐个过同一门槛(:597-600)；期间 `TerrainUpdater.UpdateEvent.WaitOne/Set` 暂停后台线程防并发释放 | `Survivalcraft\Subsystem\SubsystemTerrain.cs:587-605`
- **读档 IO 异常**→杀工程回 Play 屏弹日志对话框 | TerrainSerializer23.cs:611-625
- **非区块地形改动的持久化**：进行中的 `MovingBlockSet` 整体随 SubsystemMovingBlocks 存档（`Blocks` 序列化成 `value,ox,oy,oz;…` 串 :495-506；含 Position/TargetPosition/Speed 等 :481-494）；读档 `testCollision=false` 原地重挂(:459-470)。BlockEntity 内容物与地形无关，由实体存档承载（见 [25页](25-方块实体与容器.md)）。
- 老格式 TS14/129/22 只被版本转换器读写；`SingleFileStorage`(Chunks32fs.dat) 在本仓库构造函数里已不启用（构造固定 `new RegionFileStorage()` :586-589），属备用/闲置后端。

## MovingBlocks 全链（活塞/塌方整体搬家）

**结构**：`MovingBlock{Offset,Value,MovingBlockSet}`（`Survivalcraft\Block\MovingBlock.cs:91-95`）；`MovingBlockSet{Position/TargetPosition/Speed/Acceleration/Drag/Smoothness, Blocks, Box, Geometry}`（`Survivalcraft\Subsystem\SubsystemMovingBlocks.cs:11-108`，接口 `Survivalcraft\Block\IMovingBlockSet.cs`）。集合**不是实体**：渲染自绘（Draw :382-430，几何用"画布 Terrain+ShadowBlock(257) 背板"烘出来 :556-662），物理是位置插值而非 ComponentBody。

全链（以活塞推为例，一步不漏）：

1. 触发：电元素 → `AdjustPiston(position,length)` 入 `m_actions` | `Survivalcraft\Subsystem\BlockBehavior\SubsystemPistonBlockBehavior.cs:44-50`
2. `Update` 每 0.125s 一拍 `ProcessQueuedActions`(:52-57,:204-251)：格不是活塞就停(:210-214)；**3×3 邻域区块必须全生成**(:229-237)；每帧另跑 `UpdateMovableBlocks` 维护集合内活塞头(:253-288，增删用 `IMovingBlockSet.SetBlock` :96-103)
3. `MovePiston`(:311-469)：收集头链(238)+可推块（≤8，上限常量 :34-38；`IsBlockMovable` :549-554）→ `AddMovingBlockSet(start,target,…,"Piston",tag=活塞坐标,testCollision=true)`(:368-379；钩子 `OnMovingBlockSetAdded` :180-187) → **逐块 `ChangeCell(…,0,true,movingBlock)` 让方块离开网格**(:385-392) → 活塞格标 `IsExtended`(:399-404)
4. 上一步的 ChangeCell 带 movingBlock→`OnBlockStartMoving`（旧值行为）：BlockEntity 从坐标字典切进 `m_movingBlockEntities`——**实体不销毁，内容物全程保留**（对照 `OnBlockRemoved` 会 `DropAllItems`+删实体） | `Survivalcraft\Subsystem\BlockBehavior\SubsystemEntityBlockBehavior.cs:80-87`（对照 :37-46）；`Survivalcraft\Subsystem\SubsystemBlockEntities.cs:6-8`
5. 每帧 `SubsystemMovingBlocks.Update`(:304-380)：所在区块未生成/半生成直接**冻结跳过**(:319-326)；加速度+阻力+双端平滑(:327-335)；速度钳 `0.95/dt`(:338-339)；到点→Position=Target(:340-344)；`MovingBlocksCollision`(集合互撞 :524-534)+`TerrainCollision`(撞地形，逐格发 `CollidedWithTerrain` 事件 :536-554)(:350-351)；Stop 时按运动方向 Ceiling/Floor **对齐格线**(:352-371)
6. 落地：到点或撞死→`m_stopped`→`Stopped` 事件(:372-379)→活塞侧 `MovingBlocksStopped` 回队(:535-547)→`StopPiston`(:471-503)：`RemoveMovingBlockSet`（RemainCounter=4，多画 4 帧幽灵防闪断 :204-217,:391-401）→ 逐块 **`AddTerrainBlock`**(:487)
7. **`AddTerrainBlock`(:692-713) = 官方落地写回**：集合 `Stop()`(:697) → `DestroyCell(0,x,y,z,原值,noDrop=m_noDropOnMovingBlockStopped,movingBlock)`(:698-707) → ChangeCell 带已停集合→`OnBlockStopMoving`（新值行为）：字典切回坐标键+`Coordinates` 改写 | SubsystemEntityBlockBehavior.cs:89-97
8. 卸载保险：`OnChunkDiscarding` 把 16 格扩边内的活塞集合全停掉（防集合悬在将消失的区块上） | SubsystemPistonBlockBehavior.cs:182-191
9. **塌方同构**：`OnNeighborBlockChanged`(Living 模式)→`TryCollapseColumn`(:67-104)：向上扫整列 `GetIsCollapsable`(:76-83)→`AddMovingBlockSet(target.y=-count-1` 自由落体, accel=10/drag=0.7 :85-96)→逐块 `ChangeCell(…,0,true,item)`(:98-101)；砸到支撑块停、砸到可毁块 DestroyCell 穿透(:29-47)；落地全量回写+移除(:49-65) | `Survivalcraft\Subsystem\BlockBehavior\SubsystemCollapsingBlockBehavior.cs`

**交互面**：`SubsystemMovingBlocks.Raycast`(:238-302) 供选中移动块；`ComponentMiner.Interact(MovingBlocksRaycastResult)`(:548-583)→行为 `OnInteract(MovingBlocksRaycastResult,…)`（箱子经 `GetBlockEntity(movingBlock)` 摸到搬移中的实体，SubsystemEntityBlockBehavior.cs:65-76）。**移动中的方块不可挖**：`Raycast<T>` 按返回类型过滤（ComponentMiner.cs:1073-1081），Dig 只收 TerrainRaycastResult，最近命中是移动块时拿到 null。

## 区块生命周期（修改视角）

- **装载圈**：`IsChunkInRange`=到任一 UpdateLocation 中心距离²≤ContentDistance²（TerrainUpdater.cs:447-457）；位置由相机每帧上报（visibility=天空能见度、content=64，:392-393）。
- **卸载**：圈外→⚡`ToFreeChunks` 钩子(:465-475)→全行为 `OnChunkDiscarding`(:477-479)→`SaveChunk`（门槛过滤，脏了才写）(:480)→`FreeChunk`(:481)。**卸载即保存**，无全局"退出才存"依赖。
- **重生成判据**：下次进圈 `AllocateChunk`(:494)→NotLoaded→读档成功=保留修改直进 InvalidLight(:653-667)；无档=全量生成。TCG 与玩家修改的边界 = **Region 文件里有没有这个区块**。
- **降级重算粒度**：光照=3×3 邻域整域重算（降级即失效）；网格按 16×16×16 slice 的**内容哈希**跳过未变层（`CalculateChunkSliceContentsHashes` :1228-1297；`GenerateChunkVertices` 命中即 skip :1157-1165）——改一格只重画所在 slice 与波及列。
- **全局降级源**：天光值变化→InvalidLight(:318-322)；季节温湿变化→InvalidVertices1(:323-330)；亮度设置→InvalidVertices1+强制几何重建(:1334-1338)。
- **"改过没有"的读法**：`chunk.ModificationCounter>0`（本会话改过）、`chunk.IsLoaded`（来自存档而非生成）——原版家具雕刻用两者判"区块是否处女地"（`Survivalcraft\Subsystem\BlockBehavior\SubsystemFurnitureBlockBehavior.cs:148-155`）。

## 坑与对策

- **SetCellValueFast 直写三宗罪**：不落盘（计数不增）、光照网格冻结、无行为派发。运行时一律 ChangeCell。
- **生成中的区块被写**：生成趟会覆盖；照抄活塞"3×3 邻域全生成才动手"。
- **ChangeCell 里 OnBlockAdded 读邻居是旧的**：通知延后一帧到 ProcessModifiedCells（入账链 8）。
- **移动块落地写错分支**：`StopPiston` 先 `RemoveMovingBlockSet`（只移出列表，MovingBlock→集合的引用还在）再逐块 `AddTerrainBlock`，依赖"引用完好+集合随后 Stop()"走 OnBlockStopMoving；若 mod 提前断开引用或集合被销毁，ChangeCell 退回普通分支触发 OnBlockAdded/Removed——箱子会被拆成掉落物 [推测：后果由 OnBlockRemoved:41-44 决定，断链条件未实测]
- **爆炸是逐格账**：N 个毁格=N 次 ChangeCell+3×3 降级（幂等但非零开销）；巨量修改（如 >1 万格）考虑分帧。
- **RLE 上限 271**：同一值连续 272+ 格会自动切段，无需处理；但解码器强校验 16×256×16 恰好填满，手改存档极易触发 "Corrupt chunk data"。

## 原版范例

| 我要做… | 照抄哪里 |
|---|---|
| 批量清一片区域 | `SubsystemExplosions.SimulateExplosion`:343——BFS 圈格+逐格 `DestroyCell(0,noDrop,noPS)`，收尾统一派发 OnExplosion/冲量 |
| 结构放置器（批量写入） | 循环 `SubsystemTerrain.ChangeCell`；参考活塞扩展逐块入账(:385-392)；写入前查 3×3 邻域已生成(:229-237) |
| 结构整体平移/搬运 | `SubsystemCollapsingBlockBehavior.TryCollapseColumn`:67-104 三段式：AddMovingBlockSet→ChangeCell(0,movingBlock)→Stopped 事件里 AddTerrainBlock 回写 |
| 搬运时保住方块实体（箱子带内容移动） | `SubsystemEntityBlockBehavior.cs:80-97` 双向切字典；`MovingBlock.SetValuesDicionary`:81-86 让位置随实体存档 |
| 让悬浮方块可被玩家交互 | `SubsystemMovingBlocks.Raycast`:238 + 行为重载 `OnInteract(MovingBlocksRaycastResult,…)`（SubsystemEntityBlockBehavior.cs:65-76） |
| 自定义可塌方块 | `Block.GetIsCollapsable/IsCollapseSupportBlock/IsCollapseDestructibleBlock`（SubsystemCollapsingBlockBehavior.cs:79,:106-116） |
| 挡活塞/被活塞推 | `Block.IsMovableByPiston/IsBlockingPiston`（SubsystemPistonBlockBehavior.cs:549-556）；8 块上限 :34 |
| 判断区块是否处女地 | `chunk.ModificationCounter`+`chunk.IsLoaded`（SubsystemFurnitureBlockBehavior.cs:148-155） |

## 快查路由

| 我想… | 去/看 |
|---|---|
| 改一格后光照/邻居没反应 | 入账链 6~9（降级+延后一帧通知）；等状态机重推 Valid |
| 改动存档后消失 | 用了 SetCellValueFast 直写；或区块未到 InvalidLight 就被卸载 |
| 查一格改动到底触发了哪些行为 | SubsystemTerrain.cs:396-427 分派表（Added/Removed/Modified/StartMoving/StopMoving） |
| 搬一整个结构 | MovingBlocks 全链 1-7；集合存档格式见持久化节 |
| 移动中的箱子打不开/内容丢了 | OnBlockStartMoving/StopMoving 未成对——movingBlock 参数必须传满整链 |
| 活塞推不动某方块 | `IsMovableByPiston` 默认 false；8 块/伸出 8 格上限（SubsystemPistonBlockBehavior.cs:34-38） |
| 调爆炸威力/抗爆 | `Block.GetExplosionPressure/GetExplosionResilience`（SubsystemExplosions.cs:228,:667）；⚡`OnBlockExploded`/`CalculateExplosionPower` 钩子(:364-371,:787-793) |
| 区块何时卸载/修改何时落盘 | 生命周期节+`SaveChunk` 门槛（TerrainSerializer23.cs:593-599） |
| 存档里 Regions 文件内部结构 | 持久化节（RGN1/CHK1/目录项/256MB 上限） |
| 找 pages 的生成侧（四趟/十态/序列化器全貌） | [05页](05-世界与地形生成.md)；挖放玩家链 [24页](24-机制全链.md) 链 1/2；BlockEntity 侧 [25页](25-方块实体与容器.md) |
