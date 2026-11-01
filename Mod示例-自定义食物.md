# Mod 示例 · 自定义食物（dll+csv+配方三件协作）

> 域: SC引擎 · 更新: 2026-11-01 · 状态: 端到端示例；新增可食用方块"压缩饼干"并配方烤制；行号 2026-11-01 实读

## 目标

新增食物 `HardtackBlock`（压缩饼干，营养值 0.35≈三分之一饱食度条，模型复用原版面包），炉子里 2 面粉烤 1 块。演示 mod 最常见的三件套协作：**dll 注册类 + csv 给数值 + .cr 给配方**。

## 前置知识

- [12-ModAPI与加载链](01-引擎/12-ModAPI与加载链.md)：HandleAssembly 四类自动发现、包结构
- [Mod示例-代码方块](Mod示例-代码方块.md)：dll+csv 协作与 ID 动态分配（本文不重复）
- [数据格式参考](数据格式参考.md)：78 具名列、表头字段名驱动
- [Mod开发配方](Mod开发配方.md)"数据资产"节：配方/营养值的原版底本

## 原理 30 秒

1. **食物=FoodBlock 子类**：`FoodBlock` 是抽象基类（Block/FoodBlock.cs:5），子类只需一个构造调用——`BreadBlock` 全文就 4 行（BreadBlock.cs:3-7）：`base("Models/Bread", Matrix.Identity, Color.White, 242)`，四个参数=模型路径/物品栏姿态/染色/损坏变体值（`GetDamageDestructionValue` 返回它 :58-59，配腐坏行为才用得上）。
2. **营养值是 csv 列，单位是 0~1 小数**：Block 字段 `DefaultNutritionalValue`（Block.cs:169），读取走 `GetNutritionalValue`（:510）——进食链 `ComponentVitalStats.Eat`（ComponentVitalStats.cs:106-149）取它直接加到饱食度上，而 `Food` 属性被 `MathUtils.Saturate` 钳在 0~1（:79-82）。**原版面包=0.5（半条）**，不是整数百分比；写 200 这种整数会一口吃满。进食时满食度 ≥0.98 拒吃（:134-137）、生病只吸收 75%（:146-148）。**mod 还可以挂 `OnVitalStatsEat` 钩子**改食物/直接接管进食（:111-117；ModLoader.cs:2138）。
3. **三件分工**：dll 注册类（HandleAssembly 收 Block 子类，ModEntity.cs:430-433）→ csv 补分类/营养/名字（`BlocksManager.LoadBlocksData` 按表头字段名回写 :1037-1094）→ `.cr` 追加配方（`RequiredHeatLevel`>0 = 要炉子烤）。
4. 模型物品的手持/掉落渲染由 FoodBlock 全包（`DrawBlock` :41-52 画 standalone mesh），零渲染代码。

## 制品

### 目录树（.scmod = zip 容器）

```
example-hardtack.scmod
├── modinfo.json
├── ExampleHardtack.dll      ← zip 根层
└── Assets/
    └── Blocks/
        └── hardtack.csv     ← 营养值/名字/分类
```

### modinfo.json（完整）

```json
{
    "Name": "示例：压缩饼干",
    "Version": "1.0.0",
    "ApiVersion": "1.8",
    "Author": "SC笔记示例",
    "Description": "新增食物压缩饼干，2 面粉炉烤获得。演示 dll+csv+cr 三件协作。",
    "PackageName": "example-hardtack",
    "LoadOrder": 10000,
    "GameplayImpactLevel": "Assist"
}
```

### ExampleHardtack.cs（完整，逐行注明出处）

```csharp
namespace MyCompany.ExampleHardtack {
    // 食物方块：形态照抄 BreadBlock.cs:3-7（全子类就这几行）
    public class HardtackBlock : FoodBlock {
        public static int Index;               // 初值 0 无妨，动态分配后反射回写（BlocksManager.cs:108-119）
        public HardtackBlock() : base("Models/Bread", Matrix.Identity, Color.White, 0) { }
        //                                 ↑复用原版面包模型，零资产    ↑第四参=损坏变体值，本例无腐坏行为传 0
    }
}
```

注意：**这个包没有 ModLoader 类**——纯注册类不需要钩子，HandleAssembly 扫到 Block 子类就完事（ModEntity.cs:430-433）。要用 `OnVitalStatsEat` 之类钩子才需要加 Loader 并 RegisterHook。

### Assets/Blocks/hardtack.csv（完整）

```
Class Name;DefaultCategory;DefaultTextureSlot;DefaultNutritionalValue;DefaultDisplayName
HardtackBlock;Food;;0.35;压缩饼干
```

- 列名=Block public 字段名（BlocksManager.cs:1063-1067）；留空 `DefaultTextureSlot`=沿用模型自带贴图（FoodBlock.DrawBlock 里 `GetDefaultTexture(value)` 为 null 时直接画 mesh，FoodBlock.cs:42-47）。
- `Food` 是原版分类（BreadBlock 行第 3 列，BlocksData.txt:216）——进物品栏"食物"页签。
- 想做"吃了有概率生病"：加 `DefaultSicknessProbability` 列（读取点 ComponentVitalStats.cs:127）；想给腐坏：csv 行为列加 `RotBlockBehavior` 并把构造第四参改成腐坏变体值（原版面包=242，即腐面包）。

### 配方：烤制（追加到包内 hardtack.cr）

```xml
<Recipes>
    <Recipe Result="HardtackBlock" ResultCount="1" RequiredHeatLevel="1" a="flour" Description="[0]">
      "a"
      "a"
    </Recipe>
</Recipes>
```

- `RequiredHeatLevel="1"`=需要炉子（数据驱动示例的 0 是徒手合成）；`a="flour"`=面粉（CraftingId，BlocksData.txt FlourBlock 行；原版面包链：麦穗 seeds:5→磨粉→面团加水桶→炉烤，CraftingRecipes.xml:43-51）。
- 无前缀 `<Recipe>`=追加新配方（ModsManager.cs:988-990）。

## 打包清单

1. dll 在 zip 根层；`.csv`/`.cr` 全小写扩展名；文本 UTF-8（12 页包结构节）。
2. 类名 `HardtackBlock` 必须与 csv 第 1 列一字不差（解析按类名匹配，BlocksManager.cs:1056，错=整行 Warning 跳过）。
3. 改 dll 重启整个进程（12 页坑表）。

## 验证（日志锚点 + 游戏内）

| 锚点 | 出处 |
|---|---|
| `[示例：压缩饼干](Version: 1.0.0) Loaded 3 resource files.`（modinfo+dll+csv） | ModEntity.cs:275 |
| `[示例：压缩饼干] Loading .cr crafting recipaedia files.` | ModEntity.cs（文案 en-US.json:491） |
| 游戏内 `Loading .csv blocksdata files.` | ModEntity.cs:309 |

游戏内：物品栏 Food 分类出现"压缩饼干"；2 面粉竖排放炉子里烤出 1 块；拿着按使用键吃（饱食度不满时），饥饿条上涨约 1/3（原版面包 0.5=半条）。失败对照：方块有了但吃了不掉饥饿=csv 列名拼错（`DefaultNutritionalValue` 一个字母都不能差，Warning 在 BlocksManager.cs:1058）；配方不出现=`.cr` 标签/属性名与原版不一致。

## 该示例踩的坑

- **食物能吃但没营养**：csv 列名写错或值 0——进食链判 `num2 > 0f` 才吃（ComponentVitalStats.cs:128），0 直接当"不能吃"。
- **吃饱了没反应**：`Food ≥ 0.98` 拒吃并提示（:134-137），不是 bug。
- **营养值单位想当然**：它是 0~1 小数（0.5=半条，ComponentVitalStats.cs:79-82 Saturate）——写 120 这类整数会**一口吃满**（Saturate 截 1）而不是"很有营养"。
- **手持模型发白/全黑**：`Color.White` 是染色参数不是透明度——染色改 ctor **第三参**（`Color` 类型）；模型路径拼错在 Initialize 时抛 `ContentLoadException`，日志搜模型名。
- **想改"吃"的行为本身**：别改 FoodBlock——挂 `OnVitalStatsEat` 钩子（签名 ModLoader 对应项；`skipVanilla=true` 接管原版逻辑，ComponentVitalStats.cs:111-122）。
- **营养值单位**：0~1 小数，原版面包 0.5、熟肉更高档位见 BlocksData.txt 各行——0.35 是"零食"量级，主食给 0.5+。
- **给它腐坏**：行为列加 `RotBlockBehavior` 后，第四参必须填有效变体值，0 会腐成空气（`GetDamageDestructionValue` 原样返回，FoodBlock.cs:58-59）。

## 快查路由

| 我想… | 去/看 |
|---|---|
| 换自己的模型 | `.obj`/glTF 放 `Assets/Models/`，ctor 第一参改路径（模型规范见 19 页） |
| 查全部食物相关 csv 列 | [数据格式参考](数据格式参考.md) 78 具名列（NutritionalValue/SicknessProbability/CarryAmount…） |
| 不用炉子、徒手合成 | `RequiredHeatLevel="0"`（[Mod示例-数据驱动](Mod示例-数据驱动.md)） |
| 药水/中毒类效果 | 进食链只有营养+生病两轨；自定义效果挂 `OnVitalStatsEat` 后自写 |
| 喂生物/驯服 | `EatPickableBehavior.FoodFactors`（[Mod示例-自定义生物](Mod示例-自定义生物.md)同类机制） |
| 进食链全貌 | ComponentVitalStats.cs:106-149（钩子→营养→病检→满检→音效→饱食度） |
