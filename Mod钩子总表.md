# Mod钩子总表

> 域: Mod开发参考 · 更新: 2026-11-01 · 状态: 全读(ModLoader.cs 2338 行；钩子 236/236 全编目；全仓 233 处派发点实读)

## 一句话定位

ModLoader 全部 236 个钩子的"钩子名→语义→派发点"速查页；全量明细在 [Mod钩子明细.md](Mod钩子明细.md)。

## 怎么用这张表

1. 按任务关键词在本页"高频钩子精选"或明细页对应分组找到钩子名与注册名。
2. 重写该虚方法（签名照抄 `E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModLoader.cs` 对应行）。
3. 在 `__ModInitialize` 里 `ModsManager.RegisterHook("注册名", this)`——**不注册的覆写永不触发**。例外清单里的钩子直接重写、无需注册。

## 派发机制（今日实读）

- 继承 `Game.ModLoader`（`E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModLoader.cs`）；生效=重写虚方法+注册。
- `RegisterHook("名", this)`：`E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModsManager.cs:182`；带优先级重载 :197（priority<<16|注册序，同优先级按注册先后）。
- 派发 `HookAction("名", loader=>…)`：ModsManager.cs:133，按注册序逐 loader 调用；lambda `return true` 截断后续 loader；异常被 TryInvoke(:158) 捕获记日志（每 hook+loader 只记一次）。
- **截断型仅 7 个**（out bool=true 则后续 mod 收不到）：OnCraftingRecipeDecode、MatchRecipe、DecodeResult、DecodeIngredient、DispenserChooseItemToDispense、OnEatPickable、OnTreasureGenerate。其余全部广播——`out skip/skipVanilla=true` 只跳过原版逻辑，**不拦截其他 mod**。
- **单播型 3 个**（派发处恒 return true，只有第一个注册者收到）：SetShaderParameter、ModelShaderParameter、GenerateChunkVertices（TerrainUpdater.cs:773 首处）。
- **仅主 Loader**（Priority 最小者，ModEntity.cs:440 排序）：GetModFiles、GetModFile、CompareModVersion。
- 全部 233 处派发点逐条见 [Mod钩子明细.md](Mod钩子明细.md)。

## 最小 mod 骨架（机制全部来自源码实读）

**modinfo.json 全键模板**（键与语义照 `ModsManager.DeserializeJson`，ModsManager.cs:219-353）：

```json
{
  "Name": "示例模组",
  "Version": "1.0.0",
  "ApiVersion": "1.9.5.1",
  "Description": "一句话描述",
  "ScVersion": "2.4",
  "Link": "https://example.com/mod",
  "Author": "作者",
  "PackageName": "com.example.mymod",
  "Dependencies": ["com.example.base:>=1.0.0", { "Name": "富依赖名", "PackageName": "com.example.rich", "Version": "^2.0.0", "Link": "https://example.com" }],
  "LoadOrder": 0,
  "NonPersistentMod": false,
  "GameplayImpactLevel": "Assist",
  "Settings": []
}
```

- ApiVersion 当前 `1.9.5.1`（ModsManager.cs:19）；"1.80"/"1.81" 自动归一为 1.8/1.8.1。
- PackageName 禁空/分号/换行/survivalcraft/fastdebug（ModEntity.cs:238-241）；重复包名=双双禁用。
- Dependencies 版本范围支持 `=,>,>=,<,<=,^,~` 与裸字符串（ModsManager.TryParseVersionRange:1214）；Settings 多时可移到独立 `modsettings.json`（优先级更高，ModEntity.cs:216）。
- GameplayImpactLevel：`Cosmetic/Assist/Turbo/Break/Godmode`（Game\GameplayImpactLevel.cs:5-36）。
- LoadOrder 小者先加载；再按 Dependencies+LoadAfter 做拓扑排序（ModsManager.cs:543）。

**ModLoader 类骨架**：

```csharp
using System.Collections.Generic;
using Engine;
using Game;

namespace MyMod {
    public class MyModLoader : ModLoader {
        public override void __ModInitialize() {   // 唯一可靠注册点（ModEntity.cs:418 实例化后直调）
            ModsManager.RegisterHook("OnProjectLoaded", this);        // 注册名=成员名（3 个别名坑见下）
            ModsManager.RegisterHook("TerrainChangeCell", this, 10);  // 优先级越小越先（ModsManager.cs:197）
        }
        public override void OnProjectLoaded(Project project) { }  // 签名照抄 ModLoader.cs:750
        public override void TerrainChangeCell(SubsystemTerrain st, int x, int y, int z, int value, out bool skip) {
            skip = false;                                          // true 只跳过原版，不拦其他 mod
        }
    }
}
```

**打包要点**（ModEntity.cs / ModsManager.cs 实读）：

- `.scmod` = zip。根下放 `modinfo.json`（必需，坏则禁用）、`icon.webp`/`icon.png`、`modsettings.json`（可选）、`.dll`（根目录；Assets/ 里的 dll 不加载；禁名 Survivalcraft.dll/Engine.dll/EntitySystem.dll，ModEntity.cs:31）。
- `Assets/` 资源进 ContentManager；`Assets/Lang/en-US.json`+语言 json=语言包；根下 `.csv`=方块数据、`.xdb`=Database 合并（`Remove` 属性删条目、`new-*` 改属性、新增 EntityTemplate 自动加 ModSource）、`.clo`=衣物、`.cr`=配方（`Result` 条目配 `new-*`/`r-`/`Remove`）、`.js`=JsInterface 执行。
- `Block`/`CreatureType`/`IContentReader` 子类在 HandleAssembly 自动发现注册（ModEntity.cs:406-439）。
- 包首两种混淆头（ModsManager.HeadingCode，ModsManager.cs:1291）会被 GetDecipherStream 自动解密——引擎侧只读事实。

## 目录（18 组 · 236 钩子，全表在 [Mod钩子明细.md](Mod钩子明细.md)）

| 组 | 钩子数 | 组 | 钩子数 |
|---|---|---|---|
| 一 生命周期与加载 | 20 | 十 实体与 AI | 31 |
| 二 存档与设置 | 8 | 十一 射弹·掉落物·移动方块·发射器 | 17 |
| 三 世界与地形 | 19 | 十二 渲染·相机·天空 | 26 |
| 四 方块与物品 | 6 | 十三 音频 | 2 |
| 五 挖掘·放置·攻击 | 15 | 十四 UI·Screen·图鉴 | 27 |
| 六 生命·受伤·死亡 | 9 | 十五 物品栏·衣物·护甲 | 16 |
| 七 生命状态 VitalStats | 6 | 十六 配方 | 6 |
| 八 玩家与输入 | 16 | 十七 字体 | 3 |
| 九 骑乘与载具 | 4 | 十八 系统调度 | 5 |

（合计 236。电力/社区无专用钩子，见"例外与死钩子清单"。）

## 高频钩子精选（按任务找钩子）

| 我要… | 钩子(注册名=成员名) | 签名见 | 关键语义 |
|---|---|---|---|
| 加新方块/物品数据 | BlocksInitalized | ML:760 | BlocksManager 初始化完，注册方块行为 |
| 加/删合成表 | CraftingRecipesManagerInitialize · OnCraftingRecipeDecode | ML:1700 · ML:829 | 后者 decoded=true 截断 |
| 改任何方块写入 | TerrainChangeCell | ML:525 | skip=true 跳过原版 SetCell |
| 世界地形生成 | OnTerrainContentsGenerated · OnTerrainBrushesCreated | ML:654 · ML:1542 | 前者子线程 |
| 自定义世界高度 | OnTerrainCreated · OnTerrainChunkCreated · OnBlockGeometryGeneratorCreated | ML:676 · 686 · 716 | 三件套换子类 |
| 人物挖掘/放置 | OnMinerDig · BeforeMinerPlace · OnMinerPlace(ML:196 新重载) | ML:138 · 152 · 196 | |
| 攻击伤害结算 | ProcessAttackment · OnMinerHit2 · CalculateCreatureInjuryAmount | ML:313 · 123 · 545 | |
| 生物死亡掉落 | OnCreatureDying · OnCreatureDied · DecideLoot · DeadBeforeDrops | ML:554 · 563 · 1837 · 520 | |
| 饥饿/体温/口渴类 | OnVitalStatsUpdate* 6 件套 | ML:2162-2246 | |
| 玩家出生/死亡 | OnPlayerSpawned · OnPlayerDead · PlayerDataFirstUpdate | ML:282 · 289 · 1989 | |
| 改玩家移动/操控 | OnPlayerControlWalk · UpdatePlayerInputDig 等 | ML:1441 · 1506 | |
| 射弹（箭/枪） | OnProjectileAdded/HitBody/HitTerrain · OnProjectileRaycastBody | ML:1221 · 1108 · 1090 · 2006 | |
| 掉落物 | OnPickableAdded · OnPickableDraw · SavePickable | ML:1231 · 1149 · 1249 | |
| 生物 AI | UpdateComponentBody · ChaseBehavior 系列 · IsPredator | ML:1165 · 1816-1829 · 919 | |
| 自然生成生物 | InitializeCreatureTypes | ML:481 | |
| 加生物组件 | EntityComponentsInitialized · ProjectBeforeSubsystemsAndEntitiesLoad | ML:1782 · 1788 | 可删组件/Subsystem |
| 存自定义世界数据 | ProjectXmlSave · OnProjectXmlSaved · ProjectXmlLoad | ML:815 · 821 · 809 | |
| 存档兼容性校验 | CompareModVersion | ML:56 | 仅主 Loader |
| 模组设置 | SaveSettings/LoadSettings · OnModSettingChanged · OnSettingsScreenCreated | ML:787 · 795 · 1976 · 1968 | |
| 加键位 | GetKeyboardMappings · GetGamepadMappings · InitKeyCompatibleGroups | ML:1931 · 1938 · 1960 | 直调无需注册 |
| 手柄组合键注册 | GetGamepadMappings | ML:1938-1947 | 值传 ValuesDictionary（官方注释示例 ML:1939-1945）：`SetValue("ModifierKey", GamePadButton.LeftShoulder)`（修饰键仅 LS/RS/GamePadTrigger.Left/Right 四者）+`SetValue("ActionKey", GamePadButton.X)`（可为四个修饰键外任意键）→ `yield return new("映射名", 字典)` |
| 加相机 | ManageCameras · GetCameraList · OnCameraChange | ML:879 · 1953 · 873 | |
| 改界面 | OnWidgetContentsLoaded · BeforeWidgetUpdate/AfterWidgetUpdate · OnScreenEntered | ML:1005 · 1808/1814 · 1795 | |
| 主界面/设置加按钮 | OnMainMenuScreenCreated · OnSettingsScreenCreated | ML:1846 · 1968 | |
| 渲染特效 | SkyDrawExtra · OnModelDrawExtra · GuiDraw · DrawToScreen | ML:610 · 342 · 421 · 452 | |
| 改雾/天空/雨雪 | ViewFogColor · ChangeSkyColor · SetRainAndSnowColor | ML:69 · 590 · 213 | |
| 自定义字体 | OnBuildingBodyFontChainEntries · OnFontChainsRebuilt | ML:2324 · 2337 | |
| 每帧更新 | SubsystemUpdate(ML:744 新重载) · OnIUpdateableAddOrRemove | ML:744 · 1285 | |
| 护甲/防具 | DecideArmorProtectionSequence · ApplyProtectionBefore/AfterClothes | ML:1881 · 1893/1904 | |
| 骑乘 | ScoreMount · OnStartMounting/Dismounting · OnPlayerControlSteed | ML:965 · 2306/2314 · 1411 | |
| 发射器 | OnDispenserShoot · DispenserChooseItemToDispense | ML:1615 · 1627 | |

## 例外与死钩子清单

**直调例外（不走钩子表，重写即生效、无需 RegisterHook）**——全部全 Loader，除注明：

| 钩子 | 直调点 |
|---|---|
| `__ModInitialize` / `Priority` | ModEntity.cs:418 / :440（HandleAssembly） |
| `GetModFiles` / `GetModFile` | ModEntity.cs:101 / :143（**仅主 Loader**） |
| `CompareModVersion` | PlayScreen.cs:212（**仅主 Loader**） |
| `ModDispose` | ModEntity.cs:540（Dispose） |
| `OnLoadingFinished` | LoadingScreen.cs:580 |
| `OnXdbLoad` | ModEntity.cs:335（LoadXdb 内，每模组合并后） |
| `SaveSettings` / `LoadSettings` | ModEntity.cs:518 / :526（←ModsManager.cs:384/:434） |
| `GetKeyboardMappings` / `GetGamepadMappings` / `GetCameraList` | ModSettingsManager.cs:119-121,418,432,446 |
| `OnModSettingChanged` | ModSettingsManager.cs:317（按 PackageName 精准分发） |

**死钩子（重写无效，无任何派发点）**：`AttackBody` ML:302、`SpawnEntity` ML:490、`OnCreatureInjure` ML:533、`OnMainMenuScreenUpdate` ML:1857、`OnFactorsGenerate` ML:1872。另有两处死代码：ModEntity.OnBlocksInitalized（ModEntity.cs:533，无调用者；BlocksInitalized 钩子本身走表）与死注册 `OnCameraListInit`（SurvivalCraftModLoader.cs:17 注册但无派发、也非 ModLoader 成员）。电力、社区内容均无专用钩子（社区管线在 OnLoadingFinished 后运转，CommunityFramePump.cs:13）。

## 坑与对策

- **注册名≠成员名（3 处别名坑）**：`OnPlayerInputDrop` 注册名 "UpdatePlayerInputDrop"（ComponentPlayer.cs:490）；`OnAppendModelMeshPart`/`OnAppendModelMesh` 注册名 "OnFirstPersonModelDrawing"（BlockMesh.cs:265/412）。→ 按"注册名"RegisterHook，成员名照常重写。
- **skip≠截断**：绝大多数钩子 out skip/skipVanilla=true 只跳过原版，所有 mod 照样被调用。→ 要"独占处理"用 7 个截断型钩子或在回调里判断归属性。
- **单播钩子被原版/先加载 mod 抢占**：SetShaderParameter、ModelShaderParameter、GenerateChunkVertices 只有第一个注册者收到。→ 需要时用 HarmonyX 注入替代（另见 [Mod开发配方.md](Mod开发配方.md)）。
- **OnDespawned 只在变身时派发**（ComponentShapeshifter.cs:111），普通生物消失不触发。→ 监听 OnEntityRemove。
- **重进死档重复死亡判定**：OnPlayerDead 在进世界且死亡态时也触发。→ 按 ML:286 注释用 PreviousState=="Playing" 区分。
- **子线程钩子**：OnTerrainContentsGenerated、OnTerrainChunkCreated 可能在线程更新线程。→ 勿碰 UI/GL。
- **钩子异常不炸游戏**：TryInvoke 吞异常记日志（每 hook+loader 一次）。→ 调试期看 Bugs 日志，勿依赖异常中断。

## 原版范例

| 我要做… | 照抄哪里 |
|---|---|
| 注册钩子的标准姿势 | `E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\SurvivalCraftModLoader.cs:15-28`（原版内置 ModLoader 的 __ModInitialize） |
| 加相机全套 | 同上 :76-103（ManageCameras+OnCameraChange+GetCameraList 完整实现） |
| 头顶名牌渲染 | 同上 :110-249（OnModelRendererDrawExtra 完整实现） |
| 键位兼容组 | 同上 :30-43（InitKeyCompatibleGroups 五组示例） |
| 钩子截断语义实现 | `E:\SurvivalcraftAPIProject\Survivalcraft\Managers\CraftingRecipesManager.cs:60-75`（OnCraftingRecipeDecode 派发+截断） |

## 快查路由

| 我想… | 去/看 |
|---|---|
| 查某个钩子的派发点/参数/备注 | [Mod钩子明细.md](Mod钩子明细.md) 对应分组行 |
| 查某功能的写法配方 | [Mod开发配方.md](Mod开发配方.md) |
| 看 ModLoader 某成员原文 | `E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModLoader.cs`（明细页"ML:行"即行号） |
| 看钩子派发机制源码 | `E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModsManager.cs:133-214` |
| 看模组加载全流程 | `E:\SurvivalcraftAPIProject\Survivalcraft\Screen\LoadingScreen.cs:217-580`（依赖→资源→dll→注册→加载任务） |
| 看直调例外如何被调 | `E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModEntity.cs`（GetFiles/GetFile/HandleAssembly/Dispose） |
| 模组设置/键位/相机系统 | `E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModSettingsManager.cs:86-330` |
| 数据驱动设置项 | OnModSettingChanged（ML:1976）+ ModSettingsManager.Get\<T\>/TryGet\<T\> |
