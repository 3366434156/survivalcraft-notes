# Mod 开发配方（任务 → 照抄原版代码）

> 独立库 · 更新: 2026-11-01 · 状态: 最高频 30 条精选；**全量任务索引（235 条·15 大类）见 [Mod开发配方2.md](Mod开发配方2.md)**。
> 本表只含 Survivalcraft 原版实现；mod 侧用法案例不在本库收录范围。

## 这本配方怎么用

写 mod 时遇到"我想做 X"，三步：

1. **在精选表或 [Mod开发配方2.md](Mod开发配方2.md) 对应大类里找到你要做的事**，右边就是引擎里最值得照抄的原版实现（文件+实读行号）；
2. **打开那个文件核对**（源码仓库：https://gitee.com/SC-SPM/SurvivalcraftApi ），看它为什么这样写；
3. **照抄改造成自己的代码**——范例选的都是"最简/最全/唯一"的实现，抄它少踩坑。

配方2 按 15 个任务大类组织（新增类×4 / 修改覆盖 / 拦截钩子 / 绘制渲染 / 音效 / UI 与屏幕 / 输入相机 / 存档数据 / 媒体动画 / 内容资源 / 物理 / 平台工具），类内按域分组；每条附〔NN〕页锚，深入上下文去 `01-引擎\NN-主题.md`。

例：想给方块加"按状态发光"→ 查精选"发光方块"行 → 抄 `CampfireBlock.cs:146-152`（`min(8+data/2,15)`，字段>0 是闸门）。
想理解某段代码的完整上下文（调用链/存档/坑），去对应主题页（导航"引擎主线"）；AI agent 从 [AGENTS.md](AGENTS.md) 进。

## 最高频 30 条精选

| 我要做… | 照抄哪里 |
|---|---|
| 新增方块 | `IceBlock.cs`（4 行最简）；带染色仿 `BasaltBlock.cs:5` 〔04〕 |
| 拦截所有方块变更 | `SubsystemTerrain.ChangeCell:355`（总闸+TerrainChangeCell 钩子）；邻居通知延后 `ProcessModifiedCells:66` 〔04〕 |
| 发光方块 | `Block.DefaultEmittedLightAmount`(:83)/override `GetEmittedLightAmount`(:508)；仿 `CampfireBlock.cs:146-152` 〔14〕 |
| 新增子系统 | Subsystem 基类+xdb MemberSubsystemTemplate（[02页](01-引擎/02-Subsystem体系.md) 全链含 XML 路由） 〔02〕 |
| 往存档写自定义数据 | 重写 Subsystem.Save/Load；Count>0 才落盘，读端必须给默认值 〔02·11〕 |
| 自定义类型进存档 | `Game\FloatCurve.cs:6-13`（struct 内嵌套 HumanReadableConverter，一个文件搞定） 〔11〕 |
| 存档版本迁移 | `VersionConverter21To22.cs:6-30`（按键定位改值；Version 更新放最后） 〔11〕 |
| 注册钩子标准写法 | `SurvivalCraftModLoader.cs:15-26`（__ModInitialize 注册块，勿晚注册） 〔12〕 |
| 合并原版 Database | `ModsManager.cs:1083-1152`（.xdb 统一 new-*/Remove 前缀，不走 Harmony 硬改） 〔12〕 |
| 声明模组设置页面 | `ModSettingsParser.cs:23-53`（Id 禁 /、类型全限定名） 〔12〕 |
| 新增粒子系统 | ParticleSystem 基类 5 步+`BlockDebrisParticleSystem.cs:18-59`；注册 `Block.cs:499-503` 〔07〕 |
| 弹丸拖尾 | `SubsystemArrowBlockBehavior.cs:14`（AddTrail 一行注册） 〔07〕 |
| 3D 一次性音效 | `SubsystemBowBlockBehavior.cs:125`（PlaySound 位置系重载；minDistance=满音量半径） 〔08〕 |
| 循环环境音 | `SubsystemAmbientSounds.cs:26-79`+`ComponentOnFire.cs:68-72`（贡献聚合，勿每声源各开 source） 〔08〕 |
| 背景音乐 | `MusicManager.cs:61-85,131-161`（ogg 流式+交叉淡化；游戏内走 hook:107） 〔08〕 |
| 声音材质（脚步/撞击） | `SubsystemSoundMaterials.cs:17-27`（新方块只给 SoundMaterialName 即复用全套） 〔08〕 |
| 自定义电元件 | ElectricElement 子类 4 步+63 ID 硬编码表 `SubsystemElectricBlockBehavior.cs:8-70` 〔15〕 |
| 最小执行元件 | `GunpowderKegElectricElement.cs:5-12`（11 行：高电平→调行为子系统） 〔15〕 |
| 自定义 AI 行为 | `ComponentWalkAroundBehavior.cs:6`（最简 ComponentBehavior；调度器自动收集） 〔03〕 |
| 伤害/死亡/掉落全链 | [03页](01-引擎/03-实体与组件体系.md)"生命/伤害结算链"（Injure→Process→Die→掉落→Despawn） 〔03〕 |
| 掉落物生成 | `Pickable.cs:129-145`（Initialize 全参数+随机抛物初速；调优挂 MaxTimeExist/IsFireProof） 〔16〕 |
| 注册合成配方 | `Managers\CraftingRecipesManager.cs:18-56`（Initialize 钩子窗口内加 CraftingRecipe） 〔16〕 |
| 初始装备/新手包 | `PlayerData.cs:632-645`（ValuesDictionary overrides 注入，一处改全体） 〔16〕 |
| 两按钮确认框 | `MessageDialog.cs:18-47`（ctor 填 4 文本+handler，OnShowDialog=最小侵入替换点） 〔18〕 |
| 最小设置屏 | `Screen\SettingsAudioScreen.cs:5-34`（40 行含全部模板） 〔17〕 |
| 设置页加自定义按钮 | `Screen\SettingsScreen.cs:32-43,86-115`（OnSettingsScreenCreated 钩子+AddSettingButton 奇偶分列） 〔17〕 |
| 组合控件（按钮+字+图） | `BevelledButtonWidget.cs:75-86`（XML 模板装配+Find 改装） 〔09〕 |
| 自定义相机 | `OrbitCamera.cs:117-167`（参数化+平滑+地形钳制）；注册照 `SurvivalCraftModLoader.cs:41-61` 〔10·12〕 |
| 跨线程回主线程 | `Engine\Engine\Dispatcher.cs:38-64` Dispatch（后台线程算完 Dispatch(()=>…)，唯一正道） 〔21〕 |
| 安全写档 | `Engine\Engine\Storage.cs:204-245` MoveFileSafely（备份-替换-回滚三段式） 〔21〕 |

〔NN〕页锚释义与全部 235 条见 **[Mod开发配方2.md](Mod开发配方2.md)**（15 大类：一 方块/地形/世界 · 二 实体/AI/玩法 · 三 子系统/电学 · 四 粒子/特效 · 五 音效与音乐 · 六 UI 与屏幕 · 七 输入与相机 · 八 绘制与渲染 · 九 修改与覆盖 · 十 拦截与钩子 · 十一 存档与数据 · 十二 媒体与动画 · 十三 内容与资源 · 十四 物理与弹道 · 十五 平台工具与排查）。

## 逐文件速查索引

- [02a-子系统明细](01-引擎/明细/02a-子系统明细.md)（111 文件一行一表）、[03a-组件明细](01-引擎/明细/03a-组件明细.md)（91+EntitySystem 20 文件）
- 04a-22a 共 20 张逐文件明细见各自主页链接（`01-引擎\明细\`）

## 回填规则

- 每完成一个深读批次 → 新范例先进 [Mod开发配方2.md](Mod开发配方2.md) 对应大类对应域；其中最高频的提炼进本页精选表（保持 30 条上下）。
- 行号必须实读；一句话说清"为什么抄它"（最简/最全/唯一）。
- 钩子类任务另有 [Mod钩子总表.md](Mod钩子总表.md)（236 钩子速查）与 [Mod钩子明细.md](Mod钩子明细.md)（全量派发点）。
