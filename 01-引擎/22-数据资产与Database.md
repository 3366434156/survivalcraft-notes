# 数据资产与Database

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(Database.xml 4647行分段全读+XSD、BlocksData.txt 272行全读、CraftingRecipes.xml 1098行全读、Clothes.xml+XSD、RecoveryProject.xml、NewWorldNames.txt、Atlas.txt、AnimationTemplates 6文件、Animations 5文件、Lang 抽样+计数、UI XML 全清点抽样) · 逐文件明细: [22a-数据资产明细](明细/22a-数据资产明细.md) · 装载链总管: [20-内容与资源管理](20-内容与资源管理.md)

## 一句话定位

Content/Assets 下约 20 族纯数据文件把原版大半设计(1132 个模板对象、258 种方块参数、251 张配方、43 件防具)放进数据而非代码，引擎启动时一次性吃进内存。

## 目录地图

| 符号(类/文件) | 绝对路径 | 职责 |
|---|---|---|
| `Database.xml` | E:\SurvivalcraftAPIProject\Survivalcraft\Content\Assets\Database.xml | 全游戏模板库：实体/组件/子系统/项目模板 + GUID 继承树 |
| `BlocksData.txt` | E:\SurvivalcraftAPIProject\Survivalcraft\Content\Assets\BlocksData.txt | 258 种方块 × 79 列参数表(`;` 分隔) |
| `CraftingRecipes.xml` | E:\SurvivalcraftAPIProject\Survivalcraft\Content\Assets\CraftingRecipes.xml | 16 分类 251 张合成/熔炼配方 |
| `Clothes.xml` | E:\SurvivalcraftAPIProject\Survivalcraft\Content\Assets\Clothes.xml | 43 件防具属性表 |
| TemplatesDatabase(代码侧) | E:\SurvivalcraftAPIProject\EntitySystem\TemplatesDatabase\ | Database/DatabaseObject/ValuesDictionary/XmlDatabaseSerializer |
| `DatabaseManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\DatabaseManager.cs | Database.xml → ValuesDictionary 字典 + 按名建实体 |
| `BlocksManager`(数据段) | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\BlocksManager.cs:1037 | BlocksData.txt 解析反射写入方块字段 |
| `CraftingRecipesManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Managers\CraftingRecipesManager.cs | 配方解码/查找/排序 |
| `SurvivalCraftModEntity` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\SurvivalCraftModEntity.cs:72-138 | 原版"根 mod"的数据入口(Get+Dispose 四连) |
| `LanguageControl` | E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\LanguageControl.cs | Lang/*.json 键值 + Database 文本令牌解析 |
| `TextureAtlasManager` | E:\SurvivalcraftAPIProject\Survivalcraft\Game\TextureAtlasManager.cs:13-22 | Atlases/Atlas.txt 子纹理表消费方 |
| `AnimationTemplateRegistration` | E:\SurvivalcraftAPIProject\Survivalcraft\Animation\AnimationTemplateRegistration.cs:43-51 | AnimationTemplates 目录装载 |

## 核心机制

### 1. Database.xml 模板体系(实体数据域)

文件四段(Database.xsd 定义结构, E:\SurvivalcraftAPIProject\Survivalcraft\Content\Assets\Database.xsd:3-13)：`DatabaseObjectTypes`(10 种对象类型+嵌套/继承规则表) → `Assemblies`(Engine/Survivalcraft) → `DatabaseObjects`(RootGuid=2c273f6a… 的 Folder 树) → `GridViewPresets`(31 个编辑器视图预设) + 空的 `UserTypes`。模板总量：83 EntityTemplate + 114 SubsystemTemplate + 90 ComponentTemplate + 110 MemberSubsystemTemplate + 735 MemberComponentTemplate + 2205 Parameter + 195 ParameterSet + 17 Folder + 2 ProjectTemplate(4647 行)。

- **GUID 体系**：每个对象一个永久 GUID，`InheritanceParent` 属性指向父对象 GUID(跨文件夹跳转，如 Cow→LandAnimal→AICreature→Creature 四级链，Database.xml:46/:645/:176/:602)。对象类型规则(`AllowedInheritanceParents`/`AllowedNestingParents`, Database.xml:3-12)在装载期由 DatabaseObject.ExplicitInheritanceParent setter 校验(EntitySystem\TemplatesDatabase\DatabaseObject.cs:195)。
- **装载链**：LoadingScreen.cs:509 逐 mod 调 `LoadXdb` → SurvivalCraftModEntity.cs:124 `ContentManager.Get<XElement>("Database")`(用后 :125 立刻 Dispose) → LoadingScreen.cs:521 `DatabaseManager.LoadDataBaseFromXml` → `XmlDatabaseSerializer.LoadDatabase`(EntitySystem\TemplatesDatabase\XmlDatabaseSerializer.cs:12)，`:223` 读 InheritanceParent、`:121/:132` 挂 ExplicitInheritanceParent；实体模板逐个 `ValuesDictionary.PopulateFromDatabaseObject` 展开成值字典(ValuesDictionary.cs:107，`:121` 递归嵌套成员)。
- **消费链**：`DatabaseManager.FindEntityValuesDictionary(名字)`(DatabaseManager.cs:47) → `project.CreateEntity(值字典)`(:88)。MemberComponentTemplate 只有 Name+参数，**类名靠 `Class` 参数**：`FindValuesDictionaryForComponent` 用 `TypeCache.FindType(item.GetValue<string>("Class"))`(DatabaseManager.cs:57) 做组件类型匹配。Project 模板(Projects/Abstract, Database.xml:4343)带 109 个 MemberSubsystemTemplate = 一个世界默认挂的全套子系统清单。
- **文本令牌**：参数值 `[DisplayName:1]`/`[Description:N]` 在消费侧拆令牌转 Lang 键，如 ComponentCreature.cs:50-56 → `LanguageControl.GetDatabase("DisplayName","1")`(LanguageControl.cs:367) → Lang/*.json 的 `"Database"` 节(zh-CN.json:4419 起)；配方 Description 同理走 `TryGetBlock("CRDescription:…")`(CraftingRecipesManager.cs:90-93)。
- GridViewPresets/UserTypes **代码零引用**(全库 grep 无命中)——是官方模板编辑器的遗物段；Database.xsd:32 还留着 `Bollean` 拼写错误。

### 2. BlocksData.txt 列契约(方块数据域)

272 行 = 1 表头 + 12 类别分隔行(纯 `;`) + 258 方块行(12 类：Terrain 19/Minerals 16/Plants 31/Construction 31/Items 58/Clothes 1/SpawnerEggs 1/Tools 25/Weapons 17/Fireworks 1/Food 19/Electrics 39)。

- **79 列**：第 1 列=方块类简单名；其余 78 列与 Block 基类+子类的 public 非静态实例字段同名(BlocksManager.cs:1063-1067 反射取列)，**列名集合是 Block 字段面，不是自由文本**。关键列语义见 22a。
- 装载：SurvivalCraftModEntity.cs:72-76 `Get<string>("BlocksData")` 后立刻 Dispose → BlocksManager.LoadBlocksData(BlocksManager.cs:1037)，语法规则(`;` 分隔/空格留默认/`#`=`#类名` 引用/错行整表告警)全解在 [04-方块系统](04-方块系统.md)"csv 数据覆盖"节。
- `CraftingId` 列(第 15 列，值如 `dirt`/`ironingot`)是方块在配方/掉落里的成分标识：`BlocksManager.FindBlocksByCraftingId`(BlocksManager.cs:448) 被配方解码校验(CraftingRecipesManager.cs:111)与掉落解析消费。
- `Behaviors` 列(第 4 列，逗号分隔)决定方块挂哪些 SubsystemXxxBlockBehavior，行为名即 Subsystem 名，与 Database.xml Subsystems/BlockBehaviors 族的 71 个模板同名对应。

### 3. 数据与代码双轨 + mod 覆盖协议

- **双轨分工**：Database.xml 管"实体世界"(生物组件参数/方块实体功能实体/项目子系统清单)，BlocksData.txt 管"方块静态参数"，代码(Block 子类 ctor/Initialize 默认值)是两者的兜底默认层——BlocksData 行只在字段出现时覆盖默认。
- **mod 覆盖三入口**：mod 包内 Assets/ 同名文件经 20 页的 AddOrUpdate 后载覆盖；另有两个专门合并协议——`ModsManager.CombineDataBase`(ModsManager.cs:1079)与 `CombineCr`(:969)/`CombineClo`(:938)：XSD 层定义 `New-`/`Remove`/`r-` 前缀属性(ModsManager.cs:949-983 处理，Database.xsd:70-83、Clothes.xsd 同款)，按 Index/Guid 找旧行做字段级改写或删除。
- **一次性装载**：Database/BlocksData/Clothes/CraftingRecipes 四大件全部"Get→用→Dispose"不驻缓存(SurvivalCraftModEntity.cs:74-137)，常驻的是展开后的内存对象(GameDatabase/BlocksManager 表/配方 List)。

### 4. 其余数据文件速览(逐个明细见 22a)

| 文件 | 结构 | 消费 |
|---|---|---|
| CraftingRecipes.xml | 16 分类节 × 251 `<Recipe>`，ingredients 用小写属性 a/b/c…，元素文本 `"a…"` 网格 | CraftingRecipesManager.cs:18/:59/:85 |
| Clothes.xml | 43 行 `<ClothingData>` 属性表(Index/Slot/ArmorProtection/Insulation/TextureName…) | ClothingBlock.cs:62-64 LoadClo |
| NewWorldNames.txt | 1486 行，一行一个候选世界名 | WorldsManager.cs:29-30 → NewWorldScreen.cs:52 随机取名 |
| RecoveryProject.xml | 61 行最小 Project XML(Guid=GameProject 模板 9e9a67f8) | WorldsManager.cs:81 生成恢复世界，并把出生点改写为区块表首格 |
| Atlases/Atlas.txt | 84 行 `名 x y w h …` UI 图集子纹理表 | TextureAtlasManager.cs:13-22 |
| AnimationTemplates/*.json | 6 个动画层模板(name/layers/blendMode/boneMask) | AnimationTemplateRegistration.cs:43-51 |
| Animations/*.json | 5 个物种驱动器配置(template+layers+driver type/properties) | ComponentModel.cs:349-351 经 Database.xml `AnimationConfigPath` 参数加载(:384-391 建控制器) |
| Lang/*.json | 8 语言 × ~4700 键嵌套字典 | LoadingScreen.cs:330 列举 + ModEntity.cs:169 强制 en-US |
| Dialogs/Screens/Widgets/Styles/*.xml | 48/44/56/21 个 Widget 树/样式 XML | Dialog/*.cs `Get<XElement>("Dialogs/…")`(如 BusyDialog.cs:26)；UI 域见 09/17/18 页 |
| modinfo.json / modinfo-scheme.json | 12/218 行包清单+校验 schema | ModEntity(属 12-ModAPI 域，本页不展开) |

## 坑与对策

- **改了 Database.xml 不生效**：xml 是启动一次性装载(LoadingScreen.cs:521)，改完必须重开进程；运行期改生物参数要经 `ApplyOverrides` 路径(DatabaseManager.cs:91-93)。
- **以为 GridViewPresets/UserTypes 有用**：代码零消费，手工加内容无效——它们只服务官方编辑器。
- **模板继承链断裂**：InheritanceParent 是 GUID 硬引用，删父模板会让子模板展开失败；改库先 grep GUID 再动手。
- **BlocksData 列名拼错只丢一行**：与 04 页 csv 规则一致(BlocksManager.cs:1057-1059)，验收先搜日志 Warning。
- **配方成分写错只有 Log.Error 不中断**：CraftingRecipesManager.cs:59 LoadData 整段 try/catch，坏配方静默消失——配方问题先看日志 Error。
- **[DisplayName:N] 令牌没有对应 Lang 键**：显示为原始令牌串；增实体模板必须同步补 Lang 的 Database 节。
- **bool 大小写**：BlocksData 的 TRUE/FALSE 合法(BooleanHumanReadableConverter.cs:8 OrdinalIgnoreCase)；但**枚举严格大小写**(EnumHumanReadableConverter.cs:8 `Enum.Parse(...,false)`)——04 页"bool 只认 true/false"表述过严，以本页为准。
- **跨页事实**：04 页称 BlocksData "79 列"以 awk NF 实测为准(79)；04 页"304 个方块文件"是代码文件数，数据行是 258，两者不是一回事。

## 原版范例

| 我要做… | 照抄哪里 |
|---|---|
| 加一种生物换色变体 | E:\SurvivalcraftAPIProject\Survivalcraft\Content\Assets\Database.xml:707(Horse_White 只继承 Horse 改贴图/参数)；为什么抄：变体=零代码纯数据 |
| 建生物家族抽象层 | Database.xml:602(Creature)+:645(LandAnimal)+:176(AICreature) 三级基类；为什么抄：公共组件上提、特异性下放的样板 |
| 调生物数值(血/攻击/掉落) | Database.xml:46-110(Cow 的 Health/Miner/Loot/EatPickableBehavior)；为什么抄：ParameterSet 掉落表 `Block;min;max[;概率]` 语法 |
| 刷怪蛋元数据 | Database.xml:182-192(AICreature 的 CreatureEggData ParameterSet)；为什么抄：蛋贴图槽/显示名/营养全在这 |
| 加一种方块的数据行 | BlocksData.txt:6(DirtBlock 行，含 # 自引用掉落)；为什么抄：79 列标准填法与留空默认 |
| 加合成配方 | CraftingRecipes.xml:64-139(Materials 节，含 Remains=EmptyBucketBlock 返桶样例 :69)；为什么抄：`a="seeds:5"` 数量与 `DoughBlock:0` 数据后缀写法 |
| 加防具 | Clothes.xml:2-47(43 条 ClothingData，含金属系 DensityModifier 减速)；为什么抄：Slot/Insulation/Layer 全属性面 |
| 世界恢复存根 | RecoveryProject.xml 全文；为什么抄：最小 Project.xml 只带必要 Subsystem 值 |
| 修 UI 图集 | Atlases/Atlas.txt+TextureAtlasManager.cs:13-22；为什么抄：纯文本子纹理表+运行期 GetSubtexture 回退 |
| 动画分层(走/打/骑/死) | AnimationTemplates/Human.template.json+Animations/Human.json；为什么抄：layer blendMode+boneMask+驱动器参数三级结构 |

## 快查路由

| 我想… | 去/看 |
|---|---|
| 查 Database.xml 某模板在哪个 Folder/行 | 22a 明细"Database.xml 分族清单"；或 grep `Name="模板名"` Database.xml |
| 查某 GUID 指向谁 | grep 该 GUID 于 Database.xml(全文件唯一)；族图谱见 22a |
| 加/改实体模板后如何生效 | 本页机制 1 装载链；mod 侧走 CombineDataBase(ModsManager.cs:1079) |
| 查 BlocksData 某列语义 | 22a"79 列契约表"；字段定义回源 Block.cs:8-181 |
| 配方语法(数量/数据/返桶) | CraftingRecipesManager.cs:85-138 解码器+22a 配方节 |
| 世界里默认有哪些子系统 | Database.xml:4343-4453(Project 模板 109 个 MemberSubsystemTemplate) |
| 文本令牌 [DisplayName:N] 怎么解析 | ComponentCreature.cs:50-56+LanguageControl.cs:367；Lang 的 Database 节 |
| 生物动画参数在哪调 | Database.xml 模型的 MemberComponentTemplate(如 Cow FourLeggedModel :80-88)+Animations/*.json 驱动器 |
| 恢复世界从哪来 | WorldsManager.cs:76-90(RecoveryProject.xml+Chunks.dat TOC) |
| mod 覆盖数据文件的规则 | New-/Remove 属性协议：ModsManager.cs:938-983/:1079；XSD 见 Database.xsd:66-84 |
| 装载次序(Database/BlocksData/Cr/Clo 谁先) | 12-ModAPI与加载链 + 20-内容与资源管理(本页只列数据文件本身) |
| UI XML(Screens/Dialogs/Widgets) 结构 | 09-UI与Widget体系/17-Screen屏幕族/18-Dialog对话框族 |
