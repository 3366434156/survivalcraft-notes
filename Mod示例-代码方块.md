# Mod 示例 · 代码方块（dll）

> 域: SC引擎 · 更新: 2026-11-01 · 状态: 端到端示例；每行代码注明"照抄自 原版文件:行号"（行号 2026-11-01 实读复核）

## 目标

新增一个会发光的矿石方块 `MyGlowOreBlock`（常亮 13 档光照，复用原版贴图槽），编译成 dll 装包；并用 `TerrainChangeCell` 钩子在放置时打一行日志验证代码真的在跑。

## 前置知识

- [12-ModAPI与加载链](01-引擎/12-ModAPI与加载链.md)：`HandleAssembly` 四类自动发现（ModEntity.cs:406-442）、钩子注册窗口=装载第 5~10 步、包结构红线
- [04-方块系统](01-引擎/04-方块系统.md)：注册与 ID 两段分配、虚方法表、csv 与代码协作
- [Mod开发配方](Mod开发配方.md)"方块与地形"节：新增方块/发光方块照抄行

## 原理 30 秒

1. 装载第 6 步 `HandleAssembly` 扫描 dll 全部类型，`Block` 非抽象子类收进 `BlockTypes`（ModEntity.cs:430-433），不需要任何注册调用。
2. `BlocksManager.InitializeBlocks`（:281-405）逐模组 `Activator.CreateInstance`，读 `public static int Index` 作初值（:294-303）；模组方块 `IsIndexDynamic` 默认 true（Block.cs:29）且 `LoadBlocksStaticly` 默认 false（BlocksManager.cs:62）⇒ 一律从 300 号起动态分配（:377-400），分配后**反射回写** `Index` 静态字段（:108-119）。
3. 光照量虚方法 `GetEmittedLightAmount`（Block.cs:508，默认返回字段 `DefaultEmittedLightAmount` :83）在区块光照阶段逐格调用——override 它即可发光。

## 制品

### 目录树（.scmod = zip 容器）

```
example-glowore.scmod
├── modinfo.json
├── ExampleGlowOre.dll        ← 必须在 zip 根层（Assets/ 下的 dll 永不加载，ModEntity.cs:393）
└── Assets/
    └── Blocks/
        └── glowore.csv       ← 给新方块补分类/贴图/名字（代码+csv 协作）
```

### modinfo.json（完整）

```json
{
    "Name": "示例：发光矿石",
    "Version": "1.0.0",
    "ApiVersion": "1.8",
    "Author": "SC笔记示例",
    "Description": "新增常亮矿石方块并演示钩子注册。含代码。",
    "PackageName": "example-glowore",
    "LoadOrder": 10000,
    "GameplayImpactLevel": "Assist"
}
```

### ExampleGlowOre.cs（完整，一个文件两个类）

```csharp
using Engine;                                                  // Log 所在命名空间（E:\SurvivalcraftAPIProject\Engine\Engine\Log.cs:1）

namespace MyCompany.ExampleGlowOre {                           // 自有命名空间防重名（同名类会互相顶替，BlocksManager.cs:307-313）
    public class ExampleGlowOreLoader : ModLoader {            // 契约照抄 ModLoader.cs:10（public 非抽象+public 无参构造，ModEntity.cs:412-421 实例化后立即调 __ModInitialize）
        public override void __ModInitialize() {               // 签名照抄 ModLoader.cs:21；唯一初始化入口，此刻正处钩子注册窗口内
            ModsManager.RegisterHook("TerrainChangeCell", this);   // 形态照抄 SurvivalCraftModLoader.cs:15-26（一行一个）；派发点 SubsystemTerrain.cs:357-366
        }

        public override void TerrainChangeCell(SubsystemTerrain subsystemTerrain, int x, int y, int z, int value, out bool skip) {   // 签名照抄 ModLoader.cs:525
            skip = false;                                      // 照抄 ModLoader.cs:526 默认放行；true=原版 ChangeCell 整段跳过（SubsystemTerrain.cs:363-369），慎用
            if (Terrain.ExtractContents(value) == MyGlowOreBlock.Index) {   // contents=低 10 位（Terrain.cs:64/:311）；Index 已被反射回写为分配 ID（BlocksManager.cs:108-119）
                Log.Information($"MyGlowOreBlock placed at {x},{y},{z}");   // 验证锚点：世界内放一块矿，日志应出现本行
            }
        }
    }

    public class MyGlowOreBlock : CubeBlock {                  // 基类形态照抄 IceBlock.cs:1-5；CubeBlock=最简满格方块（只补两个渲染钩子，CubeBlock.cs:6/:19）
        public static int Index;                               // 形态照抄 IceBlock.cs:3；初值 0 无妨（见上"原理 2"动态分配+回写）；禁写 const——IsLiteral 跳过回写（BlocksManager.cs:112）
        public override int GetEmittedLightAmount(int value) => 13;   // override 形态照抄 CampfireBlock.cs:146-152（常量简化版）；基类声明 Block.cs:508
                                                               // 想按状态分档发光（data>0 才亮）：照抄 CampfireBlock.cs:146-152 全文 min(8+data/2,15)
    }
}
```

### Assets/Blocks/glowore.csv（完整）

```
Class Name;DefaultCategory;DefaultTextureSlot;DefaultDisplayName
MyGlowOreBlock;Minerals;48;发光矿石
```

- 第 1 列=类名（简单名，解析 BlocksManager.cs:1056）；`Minerals` 是原版矿石分类（BlocksData.txt IronOreBlock 行）；`48`=钻石矿石的 DefaultTextureSlot（同文件 DiamondOreBlock 行第 77 列，实读值）——复用原版图集槽，零贴图资产。
- 这份 csv 同时演示协作方式：注册靠 dll，数值/外观靠 csv；两步都在进世界前完成（12 页装载 12~16 步）。

### csproj 与编译要点

- csproj 模板不在本库收录范围（宁缺毋错）：任何能产出**普通 C# 类库 dll** 的工程都行，引用本机引擎克隆输出的 dll 即可编译（源码仓库 https://gitee.com/SC-SPM/SurvivalcraftApi ）。
- 发布配置编译；`net10.0`（Survivalcraft.csproj:4）。**改代码必须重启整个进程**——Reboot 不卸载程序集、TypeCache 不清（12 页坑表）。

## 打包清单

1. dll 在 zip **根层**；黑名单名 `Survivalcraft.dll`/`Engine.dll`/`EntitySystem.dll` 静默跳过（ModEntity.cs:31 + :393-395，两道都无日志）。
2. 扩展名小写 `.dll`/`.csv`/`.scmod`；无 0 字节条目；条目不重名；Deflate/Store；文本 UTF-8（12 页包结构节）。
3. `__ModInitialize` 抛异常 = 全部非原版模组连坐踢出（12 页坑表）——入口里别做可能抛的事。

## 验证（日志锚点 + 游戏内）

| 锚点 | 出处 |
|---|---|
| `[示例：发光矿石](Version: 1.0.0) Loaded 3 resource files.` | ModEntity.cs:275（modinfo+dll+csv） |
| `[示例：发光矿石] Loading .dll assembly files.` | ModEntity.cs:390 |
| `[示例：发光矿石] Handling assembly [ExampleGlowOre, Version=…, …]`（中括号里=程序集 FullName） | LoadingScreen.cs:281 |
| `[示例：发光矿石] Loading .csv blocksdata files.` | ModEntity.cs:309 |

游戏内：创造模式 `Minerals` 分类出现"发光矿石"；放下后周围被照亮（13 档）；日志出现 `MyGlowOreBlock placed at x,y,z`。失败对照：搜 `Handle assembly failed`（LoadingScreen.cs:288）=入口抛异常连坐；搜 `Warning`（BlocksManager.cs:1058）=csv 类名拼错；方块进世界但全黑 = dll 根本没加载（看有没有 `Handling assembly`）。

## 该示例踩的坑

- **找不到"OnBlockAdded"钩子**：ModLoader 没有同名钩子——Mod 层拦方块变更走 `TerrainChangeCell`（ModLoader.cs:525，本例）；方块自身的增删改回调是 `SubsystemBlockBehavior.OnBlockAdded` 系（SubsystemBlockBehavior.cs:17-21），要自己写 behavior 子系统才接得到（见 15 页"4 步"路 B）。
- **钩子重写了不跑**：没 `RegisterHook`、错过注册窗口、名字打错三者必居其一（12 页坑表）；`TerrainChangeCell` 走钩子表，必须注册。
- **`public static int Index` 写成 const**：回写跳过 IsLiteral（BlocksManager.cs:112），字段永远是 0 → 本例日志判定失灵、跨存档错乱。
- **类名与原版/其他 mod 撞名**：后注册者把先注册者踢出待分配列表（BlocksManager.cs:307-313），存档按类名恢复时互相顶替——类名/命名空间都加自有前缀。
- **在 TerrainChangeCell 里 return true**：钩子 lambda 返回 true 就地截断整条链（12 页）；本例的 `skip=true` 则直接跳过原版 ChangeCell（SubsystemTerrain.cs:367-369），不用别乱置。
- **`#引用` 自己的方块写进 csv**：csv 的 `#类名` 引用的是"解析那一刻"的 BlockIndex，模组方块编号随存档变（04 页坑表）——跨方块引用在 dll 里用 `BlocksManager.GetBlockIndex<T>()`（BlocksManager.cs:188-190）。

## 快查路由

| 我想… | 去/看 |
|---|---|
| 查模组方块为什么没注册 | ModEntity.cs:430-433（扫描条件）+ 04 页"注册与 ID 分配" |
| 查某虚方法该不该 override | 04 页虚方法表（116 虚+2 抽象，带调用方行号） |
| 查全部 236 个钩子 | ModLoader.cs 逐个看注释；派发点全仓搜 `ModsManager.HookAction("名字"` |
| 加异形方块（门/楼梯） | 04 页"渲染套路"：Initialize 预烘变体表（DoorBlock.cs:21-62） |
| 让方块可染色 | PaintedCubeBlock.cs:121/:126-140（IPaintableBlock 位编码） |
| 新方块掉什么/用什么工具挖 | csv 的 DefaultDropContent/RequiredToolLevel 列（示例 1）或 override GetDropValues（Block.cs:426） |
