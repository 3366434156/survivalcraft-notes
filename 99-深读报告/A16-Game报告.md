# A16 Game 域（玩法物品背包）· 原始深读报告

> 日期: 2026-10-31 · 读法: `E:\SurvivalcraftAPIProject\Survivalcraft\Game\` 递归 298 个 .cs（根目录 226 + Community\ 72）全量 ls 分类成 22 家族；深读全文 37 个（PlayerData/IInventory/PlayerInput/CraftingRecipe/WorldSettings/PlayerStats/Pickable/FoodType/ClothingData/ClothingSlot/ClothingData/InventoryDragData/WorldItem/Attackment/MeleeAttackment/ProjectileAttackment/Injury/ScannedItemData/WorldPalette/FurnitureInventoryPanel/CreativeInventoryPanel/PlayerInfo/PlayerClass/GameMode/Season/TimeOfDayMode/StartingPositionMode/EnvironmentBehaviorMode/WorldInfo/SignData/FurnitureSet/FurnitureGeometry/SpawnChunk/SpawnEntityData/SpawnLocationType/BestiaryCreatureInfo/ExternalContentType/CommunityContentEntry），头部/关键段补读 3 个（EntityReference/Projectile/FurnitureDesign），其余签名级一行表；跨目录补读 Managers\CraftingRecipesManager.cs 匹配段(130-240)、Subsystem\SubsystemPlayers.cs 存取行、Subsystem\SubsystemGameInfo.cs WorldSettings 流转行。本报告为 16/16a/16b 三页素材底稿。

## 一、分类统计（家族×数量，226 根目录）

| 家族 | 数量 | 归属页 |
|---|---|---|
| 玩家会话与输入 | 11 | 16 页深读 |
| 伤害结算 | 6 | 16 页深读 |
| 库存与物品 | 7 | 16 页深读 |
| 世界掉落物 | 2 | 16 页深读 |
| 弹射物弹道 | 2 | →13 |
| 合成/食物/服装 | 1+1+2 | 16 页深读 |
| 家具 | 4 | 16 页深读(设计) |
| 世界设置/信息/模式 | 15 | 16 页深读 |
| 寻路 | 6 | →03 另见 |
| 实体引用 | 2 | →03 另见 |
| 相机 | 13 | →10 |
| 粒子 | 29 | →07 |
| 地形/区块/生成器/序列化 | 25 | →05/05a/11 |
| 存档版本转换 | 12 | →11 |
| 渲染/网格/着色器 | 24 | →06 |
| 电学机构数据 | 7 | →15 |
| 数学/几何/通用工具 | 15 | 通用 |
| 输入设备/UI 支撑 | 8 | →10/09 |
| 方块支撑+物理射线 | 8 | →04/13 |
| 基础设施/调试/内容 | 26 | →01/12 |
| 合计 | 226 | |

Community\ 72 文件三层：Domain 26（Common 2 / Community 7 / LocalResources 10 / Transfers 7）、Infrastructure 35（根 2 / Http 14 / Integration 7 / Modpacks 2 / Persistence 10）、Models 11（Api 7 / Persistence 4）→ 16b 页。

## 二、核心机制发现（带行号）

1. **PlayerData 是状态机不是实体**：玩家持久数据（名字/职业/等级/皮肤/出生点）挂在 SubsystemPlayers 的子 ValuesDictionary（`Subsystem\SubsystemPlayers.cs:93-114`）；运行期 5 态 StateMachine（FirstUpdate→PrepareSpawn→WaitForTerrain→Playing⇄PlayerDead）全在 `Game\PlayerData.cs:142-343`。等地形每阶段上限 15 秒超时硬生（:240-241，`TerrainMaxWaitTime`:37）。死亡降级：等级减半下取整（:301-303）；Cruel 死亡只弹菜单、Adventure 禁重生直接切 AdventureRestart 屏（:325-331）。
2. **出生点评分**：初次 61×61 打分（海拔 64-85、温度≥8、背山面海射线、头顶遮挡）`PlayerData.cs:458-500`；重生 17³ 立方（脚下实心+两格空+离人远）:502-533。出生在水上自动造 Boat 并骑乘（:559-567）；初始物品仅 Slot1=方块162×1 且非创造才给（:630,642）；默认衣物按"性别×皮肤序号"硬编码四件（:573-629），衣物值=方块 203 的 data 编码（MakeClothingValue :700-702）。
3. **伤害流水线**：`Attackment.ProcessAttackment`（`Game\Attackment.cs:213-263`）= 友伤检查→ProcessAttackment 钩子→生物/非生物双分支→冲量+眩晕。折减链 CalculateInjuryAmount（:82-111）：攻击力→衣物→ComponentFactors.ResilienceFactor→Health/Damage.AttackResilience（可叠两层韧性）。护甲单件吸收 = min(剩余攻击力×saturate(ArmorProtection/attackment.ArmorProtectionDivision), 剩余Sturdiness)（`Game\ClothingData.cs:122-141`），非创造才扣耐久；ArmorProtectionDivision 是 mod 护甲专用除数（Attackment.cs:66-71）。近战冲量按质量比 5.5×saturate(√(攻/受))（MeleeAttackment.cs:13-19）。
4. **掉落物不是实体**：WorldItem（`Game\WorldItem.cs:5-35`）+ Pickable/Projectile 由 SubsystemPickables/SubsystemProjectiles 普通列表管理。寿命与场上数量挂钩（`Game\Pickable.cs:174-196`）：Terrain/无营养植物 >80 个=60s、否则 120s；其他 >80=120s、否则 480s；蛋 240s。火/岩浆上→TryExplodeBlock 连锁爆（:330-405）；UnderExplosion 伤害/韧性>0.1 连锁爆，否则大冲量转弹射物+33% 烟尾（:441-476）。Save 写 Class 全名实现多态（:549）。
5. **库存统一契约**：IInventory 10 成员（`Game\IInventory.cs:5-30`），容量按"槽+物品"二元组回答；创造背包=单只大 IInventory（槽 0-9 手部、10+ 目录），面板按 Block.GetCategory 过滤下标分页（`Game\CreativeInventoryPanel.cs:54-90`）；家具面板只显示 contents=227 且属于当前 FurnitureSet 的槽（`Game\FurnitureInventoryPanel.cs:196-225`），集合上限 32（:100）、设计上限 8192（`Game\FurnitureDesign.cs:25`）。
6. **合成匹配链**（跨目录）：`Managers\CraftingRecipesManager.cs:141 FindMatchingRecipe` = 全空判 null → 先问 256 方块 GetAdHocCraftingRecipe（动态配方）→ 再线性扫静态表 → 热量/等级不足时返回**只带 Message 的假配方**。MatchRecipe(:220) = mod 钩子 → 9 格残阵镜像+平移穷举（j,k∈[-4,2]）。注册窗口在 Initialize(:18) 的双钩子之间。
7. **世界设置流转**：WorldSettings 由 SubsystemGameInfo 持有（`Subsystem\SubsystemGameInfo.cs:11,80-88`），季节推进直接改 TimeOfYear（:97-100）——设置对象是活数据。Save 双模式：live 参数恒存、种子/地形参数仅建档写（`Game\WorldSettings.cs:134-163`）；ResetOptionsForNonCreativeMode 强制 Living/Changing/天气开/地形回默认（:64-101）。GameMode 枚举顺序即难度协议（`Game\GameMode.cs:2-9`），代码里多处 `GameMode <= Survival`、`== 0` 判创造。
8. **PlayerStats 反射持久化**：字段打 [Stat] 即自动 Load/Save+UI 列举（`Game\PlayerStats.cs:135-143,157-185`）；死亡记录 DeathRecord 序列化为 `日,x,y,z,原因` 分号串（:38-50,174-180）。三处 ValuesDictionaryForMods 扩展袋（PlayerStats/PlayerInput/DeathRecord/WorldItem/ClothingData/ScannedItemData——共 6 处）是 API 层留给 mod 的通用数据总线。
9. **Achievements 不存在**：全源码 grep "achievement" 零命中；成长体系=PlayerData.Level + PlayerStats 计数 + GameplayImpactLevel 枚举。任务书里提到的成就系统在本引擎代码中无实现。
10. **Community 子域是完整 DDD 分层**（本 fork 特有，非官方原版代码）：Domain 纯规则/状态机 → Infrastructure Http/持久化/导入 → Models 协议模型。亮点：下载队列状态机+崩溃恢复改判（Imported→Completed）、凭据 v4 加密（魔数 SCBPAUTH4 每服一文件）、上传走又拍云直传（仅 https+*.upyun.com 域校验）。

## 三、新坑列表

1. **Attackment 拼写错误是故意的**：注释明说不许改名否则大量 mod 失效（Attackment.cs:7-11）。
2. **ClothingSlot.Initialize 重入崩溃**：切语言会重调，Clear 重建实例会让旧实体字典 KeyNotFound（ClothingSlot.cs:22-30），只能补缺。
3. **PlayerClass setter 时机**：PlayerData 加入 PlayersData 后再改职业抛 InvalidOperationException（PlayerData.cs:89-97）。
4. **假配方陷阱**：FindMatchingRecipe 失败返回 Message-only 配方而非 null，调用方要查 ResultValue（CraftingRecipesManager.cs:158-168）。
5. **掉落物寿命随数量缩短**：>80 个在场时 Terrain/植物类 60s 消失，刷物场需覆盖 MaxTimeExist（Pickable.cs:180-190）。
6. **WorldSettings.Save 双参**：liveModifiableParametersOnly=true 不写种子/地形参数，改种子只能建档路径（WorldSettings.cs:134-161）。
7. **掉落物找不到**：Pickable 不是 Entity，FindEntity 无效，走 SubsystemPickables。
8. **伤害韧性两层叠加**：ComponentFactors.ResilienceFactor 与 ComponentHealth.AttackResilience 相乘生效，调数值时别只改一层（Attackment.cs:96-105）。
9. **默认衣物硬编码**：新内置皮肤要在 PlayerData.SpawnPlayer 的 if 链里补默认衣，漏了会光着出生（PlayerData.cs:573-629）。
10. **Multi-PlayerData 重复赋值防护**：OnEntityAdded 里 ComponentPlayer 二次赋值抛异常（多维世界 mod 曾踩，:400-416 注释）。

## 四、原版范例候选（16 页收录 9 条）

1. 初始物品/默认衣注入 → PlayerData.cs:632-645（ValuesDictionary overrides）。
2. 出生点算法定制 → PlayerData.cs:458-533（Score* 虚方法）。
3. 护甲/伤害数值 → ClothingData.cs:122-167 + Attackment.cs:66-71。
4. 世界掉落物生成 → Pickable.cs:129-145。
5. 配方注册 → Managers\CraftingRecipesManager.cs:18-56。
6. 世界设置可存项 → WorldSettings.cs:103-163。
7. 玩家统计计数器 → PlayerStats.cs:61-133（[Stat] 一行一个）。
8. 自定义衣物部位 → ClothingSlot.cs:14-45。
9. 整合包/下载基础设施分层 → Community\Persistence\ModpackRegistry.cs + Community\Http\CommunityHttpDownloader.cs。

## 五、回写记录

- 新建 10-SC引擎\16-玩法物品与背包.md（141 行）：一句话定位+家族概览+6 核心机制+7 坑+9 范例+14 路由+分工边界。
- 新建 10-SC引擎\16a-Game明细.md（341 行）：根目录 226 文件 22 家族一行一表，程序化校验零遗漏。
- 新建 10-SC引擎\16b-Game明细2.md：Community 72 文件 11 小节一行一表。
- 未改动 README.md、45-SC原版范例菜谱.md、00-页面模板与规则.md 及任何既有页面；SC 源码项目只读。
