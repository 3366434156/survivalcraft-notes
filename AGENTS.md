# AGENTS.md — Agent 专用项目速览

> 给 AI agent 的一页纸：30 秒懂这个库 → 3 分钟懂引擎 → 直接照抄范例开发 Survivalcraft mod。人也可以读，但为 agent 的检索习惯优化（密集、带 file:line、零客套话）。

## 0. 这个库是什么

- **Survivalcraft 引擎源码（1644 个 .cs）的行号级学习笔记**，全部逐文件实读校准；23 个主题页 + 20 张逐文件明细。
- **引擎源码仓库（公开）**：https://gitee.com/SC-SPM/SurvivalcraftApi —— 大陆可直连克隆。本库所有 `E:\SurvivalcraftAPIProject\...:行号` 引用 = 该仓库克隆到本机后的路径（行号 2026-10-31 快照）；改源码后行号以实际为准。
- **在线阅读**：https://3366434156.github.io/survivalcraft-notes/ （github.io 大陆可能超时，仓库内 `docs/` 即整站）。
- **改笔记流程**：改 md → `python tools/build_wiki.py` 重生成 docs/ → commit/push。
- **覆盖对账**：`python tools/coverage_audit.py`（源码文件名反查笔记提名，零提名=遗漏，当前 0）。

## 1. 引擎 30 秒心智模型（8 条）

1. **双层结构**：`Engine\`（平台层：Window/Graphics/Audio/Input/Media/Animation/VR/Serialization/Browser）+ `Survivalcraft\`（游戏层：Game/Managers/Subsystem/Component/Block/Screen/Dialog/ElectricElement/Widget/ModsManager）。
2. **帧链**：`Program` → `Window` 渲染循环 → `ScreensManager`（41 屏注册表）→ `GameScreen` 驱动 tick；一帧全序见 [01页](01-引擎/01-程序入口与主循环.md)。跨线程回主线唯一正道 `Dispatcher.Dispatch`（`Engine\Engine\Dispatcher.cs:38-64`）。
3. **世界 = Project**：40+ 业务子系统 tick 驱动一切（`Project.FindSubsystem<T>()` 互查、`Dependencies` 声明顺序）；地形总闸 `SubsystemTerrain.ChangeCell:355`。
4. **实体 = 组件袋**：Entity 挂 91 个 Component；物理全在 `ComponentBody`，交互伤害在 `ComponentMiner:636-715`（绕过会丢全套管线）。
5. **方块 = int 值**：contents 位 + data 位编码家族；304 个 Block 类多为止于数据表，异形方块用"预烘变体表"范式（`DoorBlock.cs:21-62`）；行为在 71 个 `SubsystemBlockBehavior`。
6. **存档双轨**：`ValuesDictionary` 硬拆箱（类型不符会崩）+ XML `ApplyOverrides` 静默降级；**Count>0 才落盘**，读端必须给默认值。
7. **数据优先**：`BlocksData.txt`(79 列)/`CraftingRecipes.xml`/`Database.xml`(Creature 模板继承树)/`Clothes.xml`——改数值大多不用写代码。
8. **电力独立 tick**：0.01s 固定步进（100 步/秒）；Simulate 抛异常 = 全电路死。

## 2. Mod 开发快速通道

### 包结构与装载（完整 20 步见 [12页](01-引擎/12-ModAPI与加载链.md)）

- `.scmod` = zip：`modinfo.json`（必需）+ `Assets/**`（**拼写一字不差**，前缀剥掉注册进 ContentManager）+ 根层 `*.dll` + `modsettings.json`（根为数组才生效）+ `icon.webp/png`。
- 扩展名比较**大小写敏感**（`.CSV`/`.DLL` 静默跳过）；0 字节条目当不存在；条目重名整包失败；只认 Deflate/Store。
- **钩子注册窗口 = 装载第 5~10 步之间**；在 `__ModInitialize()` 里注册即安全，错过窗口静默丢弃。

### modinfo.json 陷阱（13 键，写错静默失效——解析 `ModsManager.cs:219-354`）

| 键 | 陷阱 |
|---|---|
| `LoadOrder` | 必须 **JSON 数字**，`"10000"` 字符串 → 静默退 0 |
| `NonPersistentMod` | 必须**字面量 `true`**，`"true"`/1/`"True"` 全视为 false |
| `GameplayImpactLevel` | 大小写敏感，非法值静默退 Cosmetic（合法：Cosmetic/Assist/Turbo/Break/Godmode） |
| `PackageName` | 全局唯一；含 `;`/换行/`survivalcraft`/`fastdebug` → 整包不加载 |
| `Settings` | 必须数组（对象形态被忽略 → 设置面板空） |

### 代码入口（ModLoader 契约）

```csharp
public class MyModLoader : ModLoader {          // public 无参构造必须
    public override void __ModInitialize() {    // 唯一初始化入口（ModLoader.cs:21）
        ModsManager.RegisterHook("钩子名", this); // 重写 virtual 不自动生效，必须注册！
    }
    public override void UpdateComponentBody(...) { ... }  // 等 236 个 virtual 钩子
}
```

- 全部 236 个钩子见 `ModLoader.cs`；派发点全仓搜 `ModsManager.HookAction("名字"`；lambda **return true 就地截断**链。
- **不走钩子表的例外**：`OnLoadingFinished`/`LoadSettings`/`SaveSettings`/`OnXdbLoad`/`ModDispose`/`GetKeyboardMappings`/`GetGamepadMappings`/`GetCameraList`/`OnModSettingChanged`/`GetModFiles`——重写即生效，无需注册。
- **HandleAssembly 四类自动发现**（ModEntity.cs:406-442）：`ModLoader` 子类（实例化+立即 `__ModInitialize`）、`IContentReader` 子类（自定义资源读取器）、`Block` 子类（需 `public static int Index`）、`CreatureType` 子类（类全名 = .xdb 生成规则引用名）。

### 数据驱动（不写代码改游戏——合并 DSL：`new-*` 改 / `Remove`+Guid 删 / 无前缀按 Guid 改）

- `.xdb` 实体合并：`ModsManager.cs:1083-1152`；15 个受保护 GUID 触发人工裁决谈判（`ModsManager.cs:1056-1077`）。
- `.cr` 配方：按"属性全等+文本一致"找同款改写；`.clo` 衣物：按 `Index` 匹配。
- 方块数值：模组 `.csv` 复用原版 79 列解析（`BlocksData.txt` 表头）；多语言：Lang 包 en-US 基表+回退。
- 模组设置：modinfo `Settings` 树（页面/项 JSON，Id 禁 `/`），读值 `ModSettingsManager.Get<T>(包名,页面Id,项Id)`。

### 平台红线

- **HarmonyX**：Windows/Linux/Android 可用；**iOS 无 JIT、网页版完全无 mod**。游戏本体零 Harmony 调用 → 升级改方法后补丁**静默消失**；Reboot 不卸载程序集 → 补丁自判重。
- `JsonModelReader` 已下线（抛异常，`JsonModelReader.cs:98`）——模型用 `.obj`/glTF，`.obj` 必须三角面且 `vt/vn` 齐全。
- 改 dll 必须重启进程（TypeCache 不清）；模组间 dll 引用走 `AssemblyResolve` 回退链（`ModsManager.cs:525-538`）。

## 3. 任务 → 照抄路由（最常用 12 条；全量见 [Mod开发配方.md](Mod开发配方.md)）

| 任务 | 照抄 |
|---|---|
| 注册钩子（标准写法） | `SurvivalCraftModLoader.cs:15-26`（9 条 RegisterHook 一行一个） |
| 新增方块 | `IceBlock.cs`（4 行最简）；异形=预烘变体表 `DoorBlock.cs:21-62` |
| 自定义电力元件 | `GunpowderKegElectricElement.cs:5-12`（11 行最短）；**必须**补进 63 ID 表 `SubsystemElectricBlockBehavior.cs:8-70` |
| 拦截方块变更 | `SubsystemTerrain.ChangeCell:355` + `TerrainChangeCell` 钩子 |
| 加生物（数据） | `Database.xml:707`（Horse_White 继承变体）；生成规则类 `StandardCreatureSpawnRule.cs:34-59` |
| 加配方（数据） | `CraftingRecipes.xml:64-139`（含 Remains 返桶样例） |
| 自定义 AI 行为 | `ComponentWalkAroundBehavior.cs:6`（最简 ComponentBehavior） |
| 伤害/死亡/掉落全链 | `ComponentChaseBehavior.cs:180`→`ComponentMiner.cs:636-715` |
| 自定义弹道 | `Projectile.cs:190/300/525`（独立体系） |
| 相机 | `OrbitCamera.cs:117-167`（继承 BasePerspectiveCamera）+ 注册见 `SurvivalCraftModLoader.cs:41-61` |
| 设置页加按钮 | `SettingsScreen.cs:32-43,86-115`（钩子+AddSettingButton） |
| 世界选项屏接入 | `WorldOptionsScreen.cs:7,250-254`（实现 IWorldOptionsScreen） |

## 4. 查库协议（agent 工作流）

1. 本文件 → 2. 按域读对应主题页（页面地图见 [README](README.md)）→ 3. 页内"快查路由"+"原版范例"表 → 4. 没覆盖 → Grep 源码仓库（https://gitee.com/SC-SPM/SurvivalcraftApi），**把发现回写进对应页面**。
- 各域的坑：每页"坑与对策"节；跨页高频坑已收进下节。
- 页面行号快照日 2026-10-31；源码变更后以实际为准，改完记得回写。

## 5. 高频坑 Top（跨域精选）

| 症状 | 根因 |
|---|---|
| 钩子重写了但不跑 | 没调 `RegisterHook` / 错过窗口 / 名字打错 / 该钩子不走钩子表 |
| 一闪 "Loading failed" 只剩原版 | 某模组 `__ModInitialize` 抛异常连坐全部 → 日志搜 `Handle assembly failed` |
| 资源在、代码不跑 | dll 放进了 `Assets/` / 撞黑名单 / 后缀大写 |
| 设置面板空 | `Settings` 写成对象；Type 没用全限定名 |
| 模组设置读不到值 | path 必须全链（包名+页面Id+项Id）；没 Set 过用 `TryGet` |
| 依赖成环双双禁用 | A↔B 互依赖 → 两边 DependencyError |
| OnBlockAdded 里读邻居是旧的 | 邻居通知延后到 `ProcessModifiedCells:66` |
| Simulate 抛异常 | 全电路死——电力元件必须 try/catch 或保证不抛 |
| 存档数据丢了 | Count==0 不落盘；读端没给默认值 + 硬拆箱崩 |
| 改 dll 重启没变化 | Reboot 不卸载程序集，必须重启进程 |

## 6. 改这个库的规则（agent 必读）

- 五条铁律：**绝对路径+实读行号**（行号必须当日实读）；**零 mod 项目专有内容**（引擎 mod API 机制可以写，具体 mod 项目的类名/路径不行）；页面**自足可读**（无源码也能懂）；单页 ≤350 行；库内链接一律相对路径（主线→明细 `明细/X.md`，明细→主线 `../X.md`）。
- 事实冲突时：源码 > 页面 > 推测；推测标 `[推测]`。
- 新增发现回写对应页面 + 每页"原版范例"表补最典型一条；写完跑 `python tools/build_wiki.py`。
- 本文件 §6 即改库所需的全部铁律；完整页面模板与写作规则存私有笔记库（不随仓库分发）。
