# Mod 示例 · 电力元件（带设置页）

> 域: SC引擎 · 更新: 2026-11-01 · 状态: 端到端示例；每行代码注明"照抄自 原版文件:行号"（行号 2026-11-01 实读复核）

## 目标

新增电力元件 `MyThresholdGateBlock`（阈值门）：顶面端口，输入电压档 ≥ 阈值时输出高电平；阈值在**模组设置页**里调（下拉枚举），改动 0.25s 内生效。

## 前置知识

- [15-电学与机构](01-引擎/15-电学与机构.md)"模组自定义电路元件 4 步"：本页是它的完整落地版
- [12-ModAPI与加载链](01-引擎/12-ModAPI与加载链.md)"数据驱动设置层"：Settings 树、Get/TryGet、OnModSettingChanged
- [04-方块系统](01-引擎/04-方块系统.md)：方块注册与 csv 协作；[Mod开发配方](Mod开发配方.md)"电学与机构"节

## 原理 30 秒

- 电路系统按接口判型：方块实现 `IElectricElementBlock` 且**该方块的编号被某个 SubsystemBlockBehavior 接管**时，`UpdateElectricElements` 才会对该格调 `CreateElectricElement`（SubsystemElectricity.cs:630-634）。
- 接管有两条等效路径（15 页"4 步"第 3 步）：**路 A** csv `Behaviors` 列填 `ElectricBlockBehavior`（零 C# 注册）；**路 B** 自写 SubsystemBlockBehavior 子系统并作为 MemberSubsystemTemplate 挂 Project。原版方块走的是 63 编号硬编码表 `SubsystemElectricBlockBehavior.HandledBlocks`（E:\SurvivalcraftAPIProject\Survivalcraft\Subsystem\BlockBehavior\SubsystemElectricBlockBehavior.cs:8-70）——那是原版代码，mod 不可改写；路 A/B 与进该表效果相同，本例走路 A。
- 设置值在 `LoadModSettings`（装载第 17 步）后可读，`Default` 会预填进值表（ModSettingsManager.cs:364）；`OnModSettingChanged` 是**不走钩子表**的例外钩子，重写即生效（ModSettingsManager.cs:315-322）。

## 制品

### 目录树（.scmod = zip 容器）

```
example-thresholdgate.scmod
├── modinfo.json
├── ExampleThresholdGate.dll      ← zip 根层
└── Assets/
    └── Blocks/
        └── thresholdgate.csv     ← Behaviors 列=元件接管登记（路 A）
```

### modinfo.json（完整，含 Settings 数组）

```json
{
    "Name": "示例：可调阈值门",
    "Version": "1.0.0",
    "ApiVersion": "1.8",
    "Author": "SC笔记示例",
    "Description": "输入电压档达到阈值时输出高电平，阈值可在模组设置里调。",
    "PackageName": "example-thresholdgate",
    "LoadOrder": 10000,
    "GameplayImpactLevel": "Turbo",
    "Settings": [
        {
            "Id": "Main",
            "Name": "阈值门",
            "Title": "阈值门",
            "Description": "输入电压档达到阈值时从顶面输出高电平",
            "Items": [
                {
                    "Id": "Threshold",
                    "Type": "MyCompany.ExampleThresholdGate.ThresholdLevels",
                    "Default": "L8",
                    "Name": "输出阈值档位",
                    "Description": "输入电压档 ≥ 该档时输出 15/15"
                }
            ]
        }
    ]
}
```

- `Settings` 必须是数组（对象形态被忽略→面板空）；页面/项 `Id` 禁 `/`（ModSettingsParser.cs:91）；解析树形 JSON 见 ModSettingsParser.cs:31-89。
- `Type` 用**模组自定义枚举全限定名**：类型解析走 `TypeCache.FindType(typeStr, true, false)`（ModSettingsParser.cs:97）——`true` 会跳过系统程序集（TypeCache.cs:87-105 + IsKnownSystemAssembly :70-85），模组程序集在扫描范围内必然命中；`[推测]` 内置基元名（int/bool）经该路径能否命中未实证，示例不依赖。
- `Default:"L8"` 经 `Enum.Parse`（EnumHumanReadableConverter.cs:6）；Widget 省略→枚举默认下拉框 EnumSelectionDialogSettingWidget（ModSettingsParser.cs:25）。
- 设置项多时可整体抽到包根 `modsettings.json`（优先级高于 modinfo 的 Settings，ModEntity.cs:214-227）。

### ExampleThresholdGate.cs（完整，一个文件三个类型）

```csharp
using Engine;                                                  // Log 所在命名空间（Engine\Log.cs:1）

namespace MyCompany.ExampleThresholdGate {
    public enum ThresholdLevels { L2 = 2, L4 = 4, L6 = 6, L8 = 8, L10 = 10, L12 = 12, L14 = 14 }   // 设置页下拉选项（枚举成员值=电压档 1..15）

    public class MyThresholdGateBlock : CubeBlock, IElectricElementBlock {   // "CubeBlock + IElectricElementBlock"=15 页 4 步第 1 步；接口 3 成员 IElectricElementBlock.cs:3/:5/:13
        public static int Index;                               // 动态分配+反射回写（BlocksManager.cs:108-119）；禁 const（:112）

        public ElectricElement CreateElectricElement(SubsystemElectricity subsystemElectricity, int value, int x, int y, int z) =>   // 成员签名照抄 IElectricElementBlock.cs:3
            new MyThresholdGateElectricElement(subsystemElectricity, new CellFace(x, y, z, 4));   // 形态照抄 BatteryBlock.cs:96-97（面 4=顶面，建单格元件）

        public ElectricConnectorType? GetConnectorType(SubsystemTerrain terrain, int value, int face, int connectorFace, int x, int y, int z) {   // 形态照抄 BatteryBlock.cs:99-111
            if (face == 4
                && SubsystemElectricity.GetConnectorDirection(4, 0, connectorFace).HasValue) {
                return ElectricConnectorType.Output;           // 只有顶面是输出端口
            }
            return null;
        }

        public int GetConnectionMask(int value) => int.MaxValue;   // 照抄 BatteryBlock.cs:113
    }

    public class MyThresholdGateElectricElement : ElectricElement {   // 基类契约 E:\SurvivalcraftAPIProject\Survivalcraft\ElectricElement\ElectricElement.cs:4（构造重载 :11-20）
        public float m_voltage;                                // 输出缓存，仿 MotionDetectorElectricElement.cs:19/:45

        public MyThresholdGateElectricElement(SubsystemElectricity subsystemElectricity, CellFace cellFace) : base(subsystemElectricity, cellFace) { }   // 照抄 GunpowderKegElectricElement.cs:3

        public override float GetOutputVoltage(int face) => m_voltage;   // 基类虚方法 ElectricElement.cs:22（默认恒 0）；缓存形态仿 MotionDetectorElectricElement.cs:45

        public override bool Simulate() {                      // 基类 ElectricElement.cs:24（默认恒 false）；元件每 10ms 步进被调（15 页传播调用链）
            float old = m_voltage;
            float maxInput = 0f;
            foreach (ElectricConnection connection in Connections) {   // 遍历+读邻居电压形态照抄 ElectricElement.CalculateHighInputsCount :43-51
                if (connection.ConnectorType != ElectricConnectorType.Output
                    && connection.NeighborConnectorType != 0) {
                    maxInput = MathF.Max(maxInput, connection.NeighborElectricElement.GetOutputVoltage(connection.NeighborConnectorFace));
                }
            }
            ModSettingsManager.TryGet(out ThresholdLevels level, ExampleThresholdGateLoader.SettingsPackage, "Main", "Threshold");   // path=包名+页面Id+项Id 全链（ModSettingsManager.cs:244-254）
            m_voltage = maxInput * 15f >= (int)level ? 1f : 0f;   // 电压唯一量=档位/15（15 页电压模型）；IsSignalHigh 阈值 0.5f=第 8 档（ElectricElement.cs:40）
            SubsystemElectricity.QueueElectricElementForSimulation(this, SubsystemElectricity.CircuitStep + 25 + GetHashCode() % 10);   // 周期自续+抖动，仿 MotionDetectorElectricElement.cs:54-55（0.25s 量级，防同帧扎堆）
            return m_voltage != old;                           // 只在值变化时 return true——无条件自续会 CPU 炸（15 页坑表）
        }
    }

    public class ExampleThresholdGateLoader : ModLoader {
        public const string SettingsPackage = "example-thresholdgate";   // 必须与 modinfo 的 PackageName 一字不差（读值 path 第一段）

        public override void __ModInitialize() { }             // 无需注册钩子：本模组只重写不走钩子表的 OnModSettingChanged

        public override void OnModSettingChanged(string[] idPath, object value) {   // 例外钩子重写即生效（12 页）；签名 ModLoader.cs:1976；仅本包的 Loader 被精准分发（ModSettingsManager.cs:315-322）
            Log.Information($"[阈值门] {string.Join("/", idPath)} = {value}");   // idPath=去掉包名后的 ["Main","Threshold"]（ModSettingsManager.cs:312）
        }
    }
}
```

### Assets/Blocks/thresholdgate.csv（完整）

```
Class Name;DefaultCategory;DefaultTextureSlot;DefaultDisplayName;Behaviors
MyThresholdGateBlock;Minerals;33;阈值门;ElectricBlockBehavior
```

- `Behaviors` 列=接管登记：加载时按名字 `FindSubsystem<SubsystemBlockBehavior>("ElectricBlockBehavior")` 绑定（SubsystemBlockBehaviors.cs:21-25）；该名字在 Project 模板里现成存在（Database.xml:3488，其 Class=`Game.SubsystemElectricBlockBehavior` :3489）。
- `33`=铁矿石贴图槽（BlocksData.txt IronOreBlock 行第 77 列，实读值）。其余列含义见示例 1。

## 打包清单

同示例 2：dll 在 zip 根层、黑名单三名（ModEntity.cs:31）、扩展名小写、无 0 字节/重名条目、Deflate/Store、UTF-8；`-c Release`；改代码重启进程。

## 验证（日志锚点 + 游戏内）

| 锚点 | 出处 |
|---|---|
| `[示例：可调阈值门] … Loaded 3 resource files.`（modinfo+dll+csv） | ModEntity.cs:275 |
| `[示例：可调阈值门] Handling assembly […]` / `Loading .csv blocksdata files.` | LoadingScreen.cs:281 / ModEntity.cs:309 |

游戏内：主菜单"模组设置"出现"阈值门"页（解析失败只丢设置不连坐，ModsManager.cs:369-382）。世界里放阈值门→顶面接导线→LED：与 15 档电池相连默认（L8）亮；把电池电压编辑到 5 档（走电池的编辑界面）→灭；设置页把阈值调成 L4 → 0.25s 内 LED 复亮，日志出现 `[阈值门] Main/Threshold = L4`。灭不掉再查 Behaviors 列。

## 该示例踩的坑

- **没写 Behaviors 列**：编号不在 63 项硬编码表（SubsystemElectricBlockBehavior.cs:8-70）又没挂行为列 ⇒ 排队表永远为空，**元件一次都不创建且零报错**（15 页"两条路的底线"）。
- **Simulate 抛异常**：catch 后 rethrow，整局电路全死（SubsystemElectricity.cs:415-423）——内部自 try 或保证不抛。
- **排队用 `CircuitStep - n` 或直接 `CircuitStep`**：被静默丢弃（SubsystemElectricity.cs:357-373）；一律 `CircuitStep + n`。
- **想"改那个 63 编号表"**：它是原版只读代码；Harmony 补丁属另一域（升级即静默消失，12 页），本库推荐路 A/路 B。
- **设置 Type 写 `int`/简单名**：见上 `[推测]`；用模组枚举全限定名最稳（本例），或"Game." 前缀的原版类型（ModSettingsParser.cs:98-99）。
- **读设置用 `Get` 抛 KeyNotFound**：path 必须全链且少一段都不行；保险写法 `TryGet`（ModSettingsManager.cs:244-254）。
- **状态存元件字段**：元件对象按点销毁重建、不入档（15 页"三条存档归宿"）——阈值这类持久值要么每次从设置读（本例），要么写 data。
- **给 OnModSettingChanged 调 RegisterHook**：白注册，它不走钩子表（12 页例外清单）。

## 快查路由

| 我想… | 去/看 |
|---|---|
| 查某原版电方块编号/端口 | SubsystemElectricBlockBehavior.cs:8-70；15 页元件族概览 |
| 查排队/步进为什么不动 | SubsystemElectricity.cs:357-373（静默丢弃）+ 15 页传播调用链 |
| 加多端口语义方向元件 | CounterElectricElement.cs:34-103（GetConnectorDirection 分派，15 页） |
| 防抖/节流执行类 | TrapDoorElectricElement.cs:14-39（上电复位+10 步节流，15 页） |
| 设置项加滑条/文本框 | Widget 值类型默认表（ModSettingsParser.cs:23-29）；滑条属性 MinValue/MaxValue/Granularity（ModSettingItemWidget.cs:283-288） |
| 元件状态持久化 | 15 页"元件状态的三条存档归宿"（data 位/WritePersistentVoltage/自建 behavior） |
