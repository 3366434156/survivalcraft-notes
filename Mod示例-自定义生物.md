# Mod 示例 · 自定义生物（纯数据）

> 域: SC引擎 · 更新: 2026-11-01 · 状态: 端到端示例；零 dll——一只 .xdb 搞定新生物+自然生成；行号 2026-11-01 实读

## 目标

新增生物"霜原驼 `MyBeast`"（继承马：改名字/耐揍度/掉落/贴图），并且让它在**新世界的草原/雪原自然生成**。全程纯数据，不写一行 C#；文末附代码路由（老世界生效、自定义生成条件时才需要）。

## 前置知识

- [12-ModAPI与加载链](01-引擎/12-ModAPI与加载链.md)：包结构、装载 20 步（.xdb 在第 13 步前后合并）
- [22-数据资产与Database](01-引擎/22-数据资产与Database.md)：Database.xml 的模板/继承结构
- [03-实体与组件体系](01-引擎/03-实体与组件体系.md)：实体=组件袋；生物常用组件表
- [Mod开发配方](Mod开发配方.md)"数据资产"节：改原版生物数值的行

## 原理 30 秒

1. 装载期 `ModEntity.LoadXdb` 把包内全部 `.xdb` 流式喂给 `ModsManager.CombineDataBase`（ModEntity.cs:321-336），按 **Guid 匹配**合并进引擎数据库：带 `Remove` 属性=删（ModsManager.cs:1113-1121）、带 `new-*` 属性=按 Guid 改属性（:1123-1147）、其余=递归合并，**Guid 对不上就整棵追加**（Modify，:1001-1017）。
2. 新增 EntityTemplate 会被自动打上 `ModSource` 参数（:1094-1108），用于"哪个 mod 加的"归因。
3. 模板装进数据库后按 **Name** 展平成 ValuesDictionary 表（DatabaseManager.cs:31-42）；成员组件**同名即隐式继承**父模板同名成员（DatabaseObject.cs:212-215）——所以只写要改的成员，其余（含 Class 映射）全从马身上继承。
4. **新世界**创建时从 Project 模板展开子系统值（ProjectData.cs:16-24）：把生成规则条目追加进 `CreatureSpawn` 子系统模板的 `CreatureSpawnRules` 参数集（Database.xml:3714-3717），规则就随新世界落盘。
5. 生态模式下 `SubsystemCreatureSpawn.Update` 每 60s（冬季 120s）按适宜度加权随机生成（SubsystemCreatureSpawn.cs:69-90，:1040-1066）；规则条目的 `Class` 键指向规则实现类，在静态注册表里查到后反射构造（:1018-1038）——原版的 `Game.StandardCreatureSpawnRule` 就在表里（游戏自身程序集也走同一扫描，SurvivalCraftModEntity.cs:115-118）。

## 制品

### 目录树（.scmod = zip 容器）

```
example-mybeast.scmod
├── modinfo.json
└── Assets/
    └── Database/
        └── MyBeast.xdb      ← 新生物模板 + 生成规则条目（下面全文）
```

想换自己的贴图：再加 `Assets/Textures/Creatures/MyBeast.png` 并把 xdb 里的 `TextureOverride` 指过去（ContentManager 资源路径=剥掉 `Assets/` 前缀，ModEntity.cs:290-296）。本例直接复用原版白马贴图，零美术资产。

### modinfo.json（完整）

```json
{
    "Name": "示例：霜原驼",
    "Version": "1.0.0",
    "ApiVersion": "1.8",
    "Author": "SC笔记示例",
    "Description": "新增生物霜原驼（继承马）并配置自然生成规则。纯数据无代码。",
    "PackageName": "example-mybeast",
    "LoadOrder": 10000,
    "GameplayImpactLevel": "Assist"
}
```

### Assets/Database/MyBeast.xdb（完整，逐行注明出处）

```xml
<Database>
  <!-- 新模板整棵追加（Modify 无 Guid 命中→Add，ModsManager.cs:1014-1016）；
       InheritanceParent=马 Horse 的 Guid（Database.xml:433） -->
  <EntityTemplate Name="MyBeast" Guid="6f2b1a10-0000-4a5b-8c3d-000000000001"
                  InheritanceParent="8907cec4-3a39-4d81-953b-82287de4c871">
    <!-- 同名成员=隐式继承马的同名成员（DatabaseObject.cs:212-215）：
         Class=ComponentCreature 从马身上继承，这里只覆盖要改的参数 -->
    <MemberComponentTemplate Name="Creature" Guid="6f2b1a10-0000-4a5b-8c3d-000000000002">
      <!-- 不写 [...] 就是字面量直接显示；写 [键:值] 会走语言表查找（ComponentCreature.cs:51-56） -->
      <Parameter Name="DisplayName" Guid="6f2b1a10-0000-4a5b-8c3d-000000000003" Value="霜原驼" Type="string" />
    </MemberComponentTemplate>
    <!-- 四足模型组件：只覆盖贴图；ModelName 继承马的 Models/Horse（Database.xml:470） -->
    <MemberComponentTemplate Name="FourLeggedModel" Guid="6f2b1a10-0000-4a5b-8c3d-000000000004">
      <Parameter Name="TextureOverride" Guid="6f2b1a10-0000-4a5b-8c3d-000000000005"
                 Value="Textures/Creatures/Horse_White" Type="string" />
    </MemberComponentTemplate>
    <!-- 韧性（挨打减免）：马的 AttackResilience=30（Database.xml:453），这里加到 45 -->
    <MemberComponentTemplate Name="Health" Guid="6f2b1a10-0000-4a5b-8c3d-000000000006">
      <Parameter Name="AttackResilience" Guid="6f2b1a10-0000-4a5b-8c3d-000000000007" Value="45" Type="float" />
    </MemberComponentTemplate>
    <!-- 掉落：同名参数覆盖马的原条目（LeatherBlock;3;3，Database.xml:487-488）
         格式=方块名;最少;最多[,概率]（第 4 段概率样例 Bear 行 Database.xml:206） -->
    <MemberComponentTemplate Name="Loot" Guid="6f2b1a10-0000-4a5b-8c3d-000000000008">
      <ParameterSet Name="Loot" Guid="6f2b1a10-0000-4a5b-8c3d-000000000009">
        <Parameter Name="1" Guid="6f2b1a10-0000-4a5b-8c3d-00000000000a" Value="LeatherBlock;2;4" Type="string" />
        <Parameter Name="2" Guid="6f2b1a10-0000-4a5b-8c3d-00000000000b" Value="RawMeatBlock;1;3" Type="string" />
      </ParameterSet>
    </MemberComponentTemplate>
  </EntityTemplate>

  <!-- 生成规则：按 Guid 命中 CreatureSpawn 子系统模板（Database.xml:3714），
       再命中其 CreatureSpawnRules 参数集（:3715），规则条目追加进去 -->
  <SubsystemTemplate Guid="b3f8c7e3-ba45-4ba0-8bc6-ffb20e82b57e">
    <ParameterSet Guid="98c19e0b-ff62-4acc-8e58-def30e6257a3">
      <!-- 规则条目=嵌套字典：Class 指向规则类（全名，SubsystemCreatureSpawn.cs:1024-1030）；
           其余键由 StandardCreatureSpawnRule 构造函数读取（StandardCreatureSpawnRule.cs:34-59） -->
      <ParameterSet Name="MyBeast" Guid="6f2b1a10-0000-4a5b-8c3d-00000000000c">
        <Parameter Name="Class" Guid="6f2b1a10-0000-4a5b-8c3d-00000000000d"
                   Value="Game.StandardCreatureSpawnRule" Type="string" />
        <Parameter Name="Name" Guid="6f2b1a10-0000-4a5b-8c3d-00000000000e" Value="MyBeast" Type="string" />
        <Parameter Name="SpawnLocationType" Guid="6f2b1a10-0000-4a5b-8c3d-00000000000f"
                   Value="Surface" Type="Game.SpawnLocationType" />
        <Parameter Name="RandomSpawn" Guid="6f2b1a10-0000-4a5b-8c3d-000000000010" Value="True" Type="bool" />
        <Parameter Name="Count" Guid="6f2b1a10-0000-4a5b-8c3d-000000000011" Value="2" Type="int" />
        <Parameter Name="Suitability" Guid="6f2b1a10-0000-4a5b-8c3d-000000000012" Value="1" Type="float" />
        <!-- 脚下方块类型名白名单（分号分隔，StandardCreatureSpawnRule.cs:51-56，含子类判定 :89-97） -->
        <Parameter Name="Blocks" Guid="6f2b1a10-0000-4a5b-8c3d-000000000013" Value="GrassBlock;SnowBlock" Type="string" />
      </ParameterSet>
    </ParameterSet>
  </SubsystemTemplate>
</Database>
```

规则键速查（全部有默认值，可只写要的；出处 StandardCreatureSpawnRule.cs:34-59）：

| 键 | 默认 | 含义 |
|---|---|---|
| `Name` | 必填 | 生成的实体模板名（=EntityTemplate Name） |
| `SpawnLocationType` | Surface | Surface/Cave/Water（SpawnLocationType.cs:2-6） |
| `RandomSpawn` | false | true=玩家附近随机刷；false=只在新区块刷 |
| `ConstantSpawn` | false | true=走"常驻"限流池（总量 6/12、半径 42，SubsystemCreatureSpawn.cs:57-60） |
| `MinTemperature`/`MaxTemperature` | 0/15 | 竖栏温度区间，超出=适宜度 0 |
| `MinHumidity`/`MaxHumidity` | 0/15 | 竖栏湿度区间 |
| `AboveTopBlock` | false | true=只在地表之上生成 |
| `MinShoreDistance`/`MaxShoreDistance` | ±∞ | 距海岸线距离区间（:102-105） |
| `Suitability` | 1 | 条件满足时的适宜度权重（:49） |
| `Count` | 1 | 每次生成数量（:50） |
| `Blocks` | 空 | 脚下方块类型名白名单（;分隔，空=不限，:51-56） |

## 打包清单

1. 扩展名小写 `.xdb`；无 0 字节条目；条目不重名；文本 UTF-8（12 页包结构节）。
2. **每个新元素都要有全局唯一的新 Guid**（示例用 6f2b1a10-… 段自造）。装载时缺 Guid 会自动补随机值（XmlDatabaseSerializer.cs:219,225-227），但只有写死 Guid 才能被后续 .xdb 按 Guid 二次修改，也避免和其他 mod 撞车。
3. 元素名=数据库对象类型名（`EntityTemplate`/`ParameterSet`/`Parameter`/`SubsystemTemplate`/`Folder`），拼错直接抛异常——`FindDatabaseObjectType(name, true)`（XmlDatabaseSerializer.cs:233）。
4. 想改**原版**生物（不新增）：把 EntityTemplate 换成原版 Guid + `new-Value="新值"` 属性（:1123-1147），别整棵复制。

## 验证

| 锚点 | 出处 |
|---|---|
| `[示例：霜原驼](Version: 1.0.0) Loaded 2 resource files.`（modinfo+xdb） | ModEntity.cs:275 |
| `[示例：霜原驼] Loading .xdb database files.` | ModEntity.cs:328（文案 en-US.json:489） |

游戏内：新建世界（环境行为=**生态群系/Living** 才会刷，SubsystemCreatureSpawn.cs:70）；在草原或雪原走动等待，出现"霜原驼"（白马贴图、显示名霜原驼）；打死掉 2~4 皮革+1~3 生肉。调试捷径：用 `Game.StandardCreatureSpawnRule` 把 `Count` 调大、`Blocks` 留空试生成；或装个创造模式生物蛋（见下"坑"）。

## 该示例踩的坑

- **老世界不生成**：生成规则条目是"新世界创建时"从模板展开落盘的（ProjectData.cs:16-24）；已存在的世界读的是存档里已固化的 `CreatureSpawnRules`——装 mod 前建的旧世界不会出现新规则。老世界要用代码钩子 `InitializeCreatureTypes`（见下节）。
- **生物一直不刷**：三查——世界是不是生态模式（非 Living 整个子系统不工作，SubsystemCreatureSpawn.cs:70）；附近生物是不是满了（全局上限 26、区域内 3，:54-56）；`Name` 是不是和 EntityTemplate 名一字不差（模板表按 Name 展平，DatabaseManager.cs:40）。
- **实体名撞原版**：模板表按 Name 建字典，重名整库装载崩（DatabaseManager.cs:40 `Add` 重复键抛异常）。新模板名加自有前缀。
- **Category 写成多标志**：`Creature.Category` 必须是单个 2 的幂标志，写 `LandOther, WaterOther` 这类组合值在实体加载时抛异常（ComponentCreature.cs:61-63）。
- **KillVerbs 丢了**：覆盖 `Creature` 成员时别删 KillVerbs——空值同样抛异常（ComponentCreature.cs:58-60）。隐式继承只在"不写该参数"时生效，写空字符串=覆盖成空。
- **生物蛋没有**：蛋的显示由 `CreatureEggData` 参数集控制（AICreature 默认 ShowEgg=True，Database.xml:182-192；Horse_White 的完整覆盖样例 :714-720）。想要自己的蛋照抄 Horse_White 那组参数。
- **模型动物不动**：马的动画是四足代码动画，换贴图没事；若 `ModelName` 指向自己的模型且不是四足绑定，要配 AnimationConfig（配方"AI 与生物"节：四足/鸟/鱼 AnimateCreature 全空实现，ComponentFourLeggedModel.cs:188）。

## 代码路由（可选，两种情况才需要）

**老世界生效 / 完全自定义条件**：dll 里写规则类并挂钩子。

```csharp
public class MyBeastLoader : ModLoader {
    public override void __ModInitialize() {
        ModsManager.RegisterHook("InitializeCreatureTypes", this);   // 派发点 SubsystemCreatureSpawn.cs:1009-1015
    }
    public override void InitializeCreatureTypes(SubsystemCreatureSpawn spawn, List<SubsystemCreatureSpawn.CreatureType> creatureTypes) {   // 签名照抄 ModLoader.cs:481
        var vd = new ValuesDictionary();                             // 键=上表规则键，构造模板样例见 StandardCreatureSpawnRule.cs:34-59
        vd.SetValue("Name", "MyBeast");
        vd.SetValue("RandomSpawn", true);
        creatureTypes.Add(new StandardCreatureSpawnRule(spawn, vd)); // 直接 new 原版规则类喂字典
    }
}
```

规则类若写成 `SubsystemCreatureSpawn.CreatureType` 子类，还会被 `HandleAssembly` 自动收进静态注册表（ModEntity.cs:434-437，键=类全名），此后世界存档的规则条目用 `Class=你的类全名` 也能引用它。

## 快查路由

| 我想… | 去/看 |
|---|---|
| 改原版生物数值（不新增） | 本页"打包清单"第 4 条 + [数据格式参考2](数据格式参考2.md) |
| 加自己的模型/动画 | [19-媒体动画与VR](01-引擎/19-媒体动画与VR.md) + 配方"AI 与生物"节 |
| 自定义生成条件（夜里刷/洞里刷） | 继承 `StandardCreatureSpawnRule` 覆写 `GetSpawnSuitability`（StandardCreatureSpawnRule.cs:61-107） |
| 生物战斗/骑乘/放牧行为 | [Mod开发配方](Mod开发配方.md)"AI 与生物"节 |
| 掉落物格式细节 | [数据格式参考2](数据格式参考2.md)（Database 24 键） |
| 生物世界内生成管线全貌 | [03页](01-引擎/03-实体与组件体系.md) + SubsystemCreatureSpawn.cs（Update→SpawnRandomCreature→SpawnCreature 三级） |
